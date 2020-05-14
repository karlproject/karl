"""
Views related to JSON API for archive to box feature.
"""
import datetime
import functools
import logging
import uuid

import newt.db.search

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPAccepted, HTTPBadRequest
from pyramid.security import Allow
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from pyramid.traversal import resource_path
from pyramid.url import urlencode
from pyramid.view import view_config
from repoze.workflow import get_workflow

from karl.models.interfaces import (
    ICatalogSearch,
    ICommunities,
    ICommunity,
    ISite,
)
from karl.content.interfaces import (
    ICommunityFile,
    ICalendarCategory,
    IBlog,
    ICalendar,
    ICommunityRootFolder,
    IWiki,
    IWikiPage,
    IBlogEntry,
)
from karl.security.policy import VIEW
from karl.views.acl import modify_acl
from karl.utils import coarse_datetime_repr

from .client import BoxClient, find_box
from .queue import RedisArchiveQueue

logger = logging.getLogger(__name__)


pseudo_communities = {'Network News': 'offices/files/network-news'}

# Work around for lack of 'view_defaults' in earlier version of Pyramid
box_api_view = functools.partial(
    view_config,
    route_name='archive_to_box',
    permission='administer',
    renderer='json')


def action(action):
    """
    Custom predicate that examines the value of an 'action' sent in a JSON
    payload.
    """
    def predicate(context, request):
        try:
            return request.json_body.get('action') == action
        except ValueError:
            return False
    return predicate


class ArchiveToBoxAPI(object):
    """
    Views related to JSON API for archive to box feature.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def queue(self):
        return RedisArchiveQueue.from_settings(self.request.registry.settings)

    get_communities_to_archive_sql = """
    select (state->>'docid')::bigint as id,
           state->>'__name__' as name,
           state->>'title' as title,
           (state->>'content_modified')::timestamp::text as last_activity,
           get_path(state) as path,
           (select count(*)
            from newt sn natural join karlex
            where karlex.community_zoid = newt.zoid
                  and
                  interfaces(sn.class_name) &&
                    array[
                      'karl.content.interfaces.IBlogEntry',
                      'karl.content.interfaces.ICommunityFile',
                      'karl.content.interfaces.ICalendarCategory',
                      'karl.content.interfaces.IBlog',
                      'karl.content.interfaces.ICalendar',
                      'karl.content.interfaces.ICommunityRootFolder',
                      'karl.content.interfaces.IWiki',
                      'karl.content.interfaces.IWikiPage'
                    ]
            ) as items,
           state->>'archive_status' as status
    from newt
    where interfaces(class_name) && array['karl.models.interfaces.ICommunity']
          and coalesce(state->>'archive_status', '') != 'archived'
          and (state->>'content_modified')::timestamp < (now() - interval %s)
          and state->>'__name__' is not null
    """

    @box_api_view(
        context=ICommunities,
        request_method='GET')
    def get_communities_to_archive(self):
        """
        GET: /arc2box/communities/

        Returns a list of communities eligible to be archived.  Accepts the
        following query parameters, none of which are required:

            + last_activity: Integer number of days. Will only include
              communities with no updates younger than given number of days.
              Default is 540 days (roughly 18 months).
            + filter: Text used as a filter on the communitie's title.  Only
              matching communities will be returned.  By default, no filtering
              is done.
            + limit: Integer number of results to return.  Default is to return
              all results.
            + offset: Integer index of first result to return. For use in
              conjunction with `limit` in order to batch results.

        Results are ordered by time of last activity, oldest first.

        Returns a list of objects, with each object containing the following
        keys:

            + id: docid of the community.
            + name: The name of the community (URL name).
            + title: The title (display name) of the community.
            + last_activity: Time of last activity on this community.
            + url: URL of the community.
            + items: integer count of number documents in this community.
            + status: workflow state with regards to archive process,

        The possible values of `status` are:

            + null: The community is in normal mode, not currently in any
                    archive state.
            + "copying": The archiver is in the process of copying community
                         content to Box.
            + "reviewing": The archiver has finished copying community content
                           to Box and is ready for an administrator to review
                           the content in Box before proceeding.
            + "removing": The archiver is in the process of removing content
                          from the community.  A transition to this state is
                          the point of no return.
            + "archived": The archiver has copied all community content to the
                          Box archive and removed the content from Karl. The
                          community is mothballed.
            + "exception": An exception has occurred while processing this
                           community.
        """
        params = self.request.params
        last_activity = str(params.get('last_activity', 540)) + ' days'
        filter_text = params.get('filter')
        limit = int(params.get('limit', 0))
        offset = int(params.get('offset', 0))

        sql = self.get_communities_to_archive_sql
        params = (last_activity,)

        if filter_text:
            sql += "\n  and position(lower(%s) in lower(state->>'title')) > 0"
            params += (filter_text,)

        sql += "\norder by state->>'content_modified' desc"
        if offset:
            sql += "\noffset %s"
            params += (offset,)
        if limit:
            sql += "\nlimit %s"
            params += (limit,)

        route_url = self.request.route_url
        logger.info('arc2box: Got communities')

        try:
            results = [
                dict(id=id, name=name, title=title, last_activity=last_activity,
                     url=route_url('archive_to_box', traverse=path.strip('/')),
                     items=items, status=status)
                for (id, name, title, last_activity, path, items, status)
                in newt.db.search.query_data(self.context, sql, *params)
                ]
        except AttributeError:
            logger.debug("arc2box: newtdb crash on %s  --- %s" % (sql, str(params)))
            results = []

        root = find_root(self.context)
        for path in pseudo_communities.values():
            result = find_resource(root, path)
            resource_path = 'communities' + path
            url = self.request.resource_url(root, *resource_path.split('/'))
            name = "pseudo-community?path=%s" % path
            logger.info('arc2box: Including pseudo-community %s' % url)
            results.append(dict(name=name, title=result.title,
                last_activity=result.modified.isoformat(), url=url,
                items=len(result.keys()), status=None))

        return results


    @box_api_view(
        context=ICommunity,
        request_method='GET',
    )
    def community_status(self):
        """
        GET /arc2box/communities/<community>/

        Returns:

            {
                'status': null or string archive state (see above),
                'log': [
                    {'timestamp': timestamp of log entry,
                     'message': multiline string, log entry,
                     'level': logging level, one of 'debug', 'info', 'warn',
                              'error', 'critical'},
                    etc...
                ]
            }
        """
        # In later versions of Pyramid you can register a new JSON renderer
        # with an adapter for datetime objects.  That would be preferable to
        # doing this.
        community = self.context
        log = map(dict, getattr(community, 'archive_log', ()))
        for entry in log:
            entry['timestamp'] = entry['timestamp'].isoformat()

        logger.info('arc2box: Get loginfo for community: ' +
                  community.title)
        return {
            'status': getattr(community, 'archive_status', None),
            'log': log,
        }

    @box_api_view(
        context=ICommunity,
        request_method='PATCH',
        custom_predicates=(action('copy'),),
    )
    def copy(self):
        """
        PATCH /arc2box/communities/<community>/
        {"action": "copy"}

        Tell the archiver to start copying content from this community to box.
        The community must not already be in any archive state.  This operation
        will place the community in the 'copying' state.  The archiver  will
        place the community into the 'reviewing' state at the completion of the
        copy operation.

        Returns a status of '202 Accepted'.
        """
        community = self.context

        # For all but KarlAdmin, reduce access to VIEW only
        acl = []
        for allow, who, what in community.__acl__:
            if allow == Allow and who != 'group.KarlAdmin':
                what = (VIEW,)
            acl.append((allow, who, what))
        modify_acl(community, acl)

        # Queue the community for copying
        self.queue.queue_for_copy(community)
        community.archive_status = 'copying'

        logger.info('arc2box: copy community: ' + community.title)
        return HTTPAccepted()

    @box_api_view(
        context=ICommunities,
        request_method='PATCH',
        name='pseudo-community',
        custom_predicates=(action('copy'),),
    )
    def copy_pseudo(self):
        path = self.request.params.get('path', None)
        if path is None:
            return HTTPNotFound
        root = find_root(self.context)
        community = find_resource(root, path)

        # For all but KarlAdmin, reduce access to VIEW only
        acl = []
        for allow, who, what in community.__acl__:
            if allow == Allow and who != 'group.KarlAdmin':
                what = (VIEW,)
            acl.append((allow, who, what))
        modify_acl(community, acl)

        # Queue the community for copying
        self.queue.queue_for_copy(community)
        community.archive_status = 'copying'

        logger.info('arc2box: copy pseudo community: ' + community.title)
        return HTTPAccepted()

    @box_api_view(
        context=ICommunity,
        request_method='PATCH',
        custom_predicates=(action('stop'),),
    )
    def stop(self):
        """
        PATCH /arc2box/communities/<community>/
        {"action": "stop"}

        Tell the archiver to stop copying content from this community to box
        and to take the community out of the 'copying' state.  The community
        must be in the 'copying' or 'reviewing' state.  The community will
        return to normal operation and will not be in any archiving state.
        """
        community = self.context
        status = getattr(community, 'archive_status', None)
        if status not in ('copying', 'reviewing', 'exception'):
            return HTTPBadRequest(
                "Community must be in 'copying' or 'reviewing' state.")

        # Restore normal ACL for workflow state
        wf = get_workflow(ICommunity, 'security', community)
        wf.reset(community)
        del community.__custom_acl__

        # If still in the copy queue, the archiver will skip this community
        del community.archive_status
        community.archive_copied = None

        logger.info('arc2box: stop community: ' + community.title)
        return HTTPAccepted()

    @box_api_view(
        context=ICommunity,
        request_method='PATCH',
        custom_predicates=(action('mothball'),),
    )
    def mothball(self):
        """
        PATCH /arc2box/communities/<community>/
        {"action": "mothball"}

        Tell the archiver to remove all content from the community in Karl.
        This operation cannot be stopped or reversed. The community must be in
        the 'reviewing' state.  This operation will place the community into
        the 'removing' state.  The archiver will place the community into the
        'archived' state at the completion of the mothball operation.
        """
        community = self.context
        status = getattr(community, 'archive_status', None)
        if status != 'reviewing':
            return HTTPBadRequest(
                "Community must be in 'reviewing' state.")

        # Queue the community for mothball
        self.queue.queue_for_mothball(community)
        community.archive_status = 'removing'

        logger.info('arc2box: mothball community: ' + community.title)
        return HTTPAccepted()
