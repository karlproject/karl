"""
Views related to JSON API for archive to box feature.
"""
import datetime
import functools

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPAccepted
from pyramid.security import Allow
from pyramid.traversal import resource_path
from pyramid.view import view_config

from karl.models.interfaces import (
    ICatalogSearch,
    ICommunities,
    ICommunity,
)
from karl.security.policy import ADMINISTRATOR_PERMS, NO_INHERIT
from karl.views.acl import modify_acl
from karl.utils import coarse_datetime_repr

from .queue import RedisArchiveQueue


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
        return request.json_body.get('action') == action
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
        """
        params = self.request.params
        last_activity = int(params.get('last_activity', 540))
        filter_text = params.get('filter')
        limit = int(params.get('limit', 0))
        offset = int(params.get('offset', 0))

        search = ICatalogSearch(self.context)
        now = datetime.datetime.now()
        timeago = now - datetime.timedelta(days=last_activity)
        count, docids, resolver = search(
            interfaces=[ICommunity],
            content_modified=(None, coarse_datetime_repr(timeago)),
            sort_index='content_modified',
            reverse=True)

        def results(docids=docids, limit=limit, offset=offset):
            if offset and not filter_text:
                docids = docids[offset:]
                offset = 0
            for docid in docids:
                if offset:
                    offset -= 1
                    continue
                community = resolver(docid)
                if (not filter_text or
                    filter_text.lower() in community.title.lower()):
                    yield community
                    if limit:
                        limit -= 1
                        if not limit:
                            break

        route_url = self.request.route_url

        def record(community):
            path = resource_path(community)
            items, _, _ = search(path=path)
            return {
                'id': community.docid,
                'name': community.__name__,
                'title': community.title,
                'last_activity': str(community.content_modified),
                'url': route_url('archive_to_box', traverse=path.lstrip('/')),
                'items': items,
                'status': getattr(community, 'archive_status', None),
            }

        return [record(community) for community in results()]


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
                     'entry': multiline string, log entry},
                    etc...
                ]
            }
        """
        return ['status', self.context.title]


    @box_api_view(
        context=ICommunity,
        #request_method='PATCH',
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

        # Revoke all but admin access to the community
        acl = [(Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
               NO_INHERIT]
        modify_acl(community, acl)

        # Queue the community for copying
        self.queue.queue_for_copy(community)
        community.archive_status = 'copying'

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
        return ['stop', self.context.title]

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
        return ['mothball', self.context.title]
