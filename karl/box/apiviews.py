"""
Views related to JSON API for archive to box feature.
"""
import functools

from pyramid.view import view_config

from karl.models.interfaces import ICommunities, ICommunity

from .client import (
    BoxArchive,
    BoxClient,
)


# Work around for lack of 'view_defaults' in earlier version of Pyramid
box_api_view = functools.partial(
    view_config,
    route_name='archive_to_box',
    permission='administer',
    renderer='JSON')


class ArchiveToBoxAPI(object):
    """
    Views related to JSON API for archive to box feature.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

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


    @box_api_view(
        context=ICommunity,
        request_method='PUT',
        request_parameter='action=copy',
    )
    def copy(self):
        """
        PUT /arc2box/communities/<community>/?action=copy

        Tell the archiver to start copying content from this community to box.
        The community must not already be in any archive state.  This operation
        will place the community in the 'copying' state.  The archiver  will
        place the community into the 'removing' state at the completion of the
        copy operation.
        """

    @box_api_view(
        context=ICommunity,
        request_method='PUT',
        request_parameter='action=stop',
    )
    def stop(self):
        """
        PUT /arc2box/communities/<community>/?action=stop

        Tell the archiver to stop copying content from this community to box
        and to take the community out of the 'copying' state.  The community
        must be in the 'copying' or 'reviewing' state.  The community will
        return to normal operation and will not be in any archiving state.
        """

    @box_api_view(
        context=ICommunity,
        request_method='PUT',
        request_parameter='action=mothball',
    )
    def mothball(self):
        """
        PUT /arc2box/communities/<community>/?action=mothball

        Tell the archiver to remove all content from the community in Karl.
        This operation cannot be stopped or reversed. The community must be in
        the 'reviewing' state.  This operation will place the community into
        the 'removing' state.  The archiver will place the community into the
        'archived' state at the completion of the mothball operation.
        """
