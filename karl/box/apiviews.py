"""
Views related to JSON API for archive to box feature.
"""
import functools

from pyramid.view import view_config

from karl.models.interfaces import ICommunities

from .client import (
    BoxArchive,
    BoxClient,
)


# Work around for lack of 'view_defaults' in earlier version of Pyramid
box_api_view = functools.partial(
    view_config,
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
        name='to_archive',
        request_method='GET')
    def get_communities_to_archive(self):
        """
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

        Results are ordered by ???

        Returns a list of objects, with each object containing the following
        keys:

            + id: docid of the community.
            + name: The name of the community (URL name).
            + title: The title (display name) of the community.
            + url: URL of the community.
            + items: integer count of number documents in this community.
            + status: workflow state with regards to archive process
            + actions: List of actions available on the community. A list of
                       objects where each contains the keys: `name`,
                       `description`, and `url`
        """
