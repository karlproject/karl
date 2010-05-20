import datetime

from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IWikiPage
from karl.models.interfaces import IComment
from karl.models.interfaces import ICommunity

from karl.utils import find_communities
from karl.utils import find_tags

from repoze.lemonade.content import get_content_type
from repoze.lemonade.content import is_content
from repoze.workflow import get_workflow

THIRTY_DAYS = datetime.timedelta(days=30)

def collect_community_stats(context):
    """
    Returns an iterator of dicts where for each community in the site a dict
    is returned containing the following keys::

      + 'community': The community's full title.
      + 'id': The community's name, used in the path to the community.
      + 'security state': The name of the community's current security state.
        Will be 'custom' if acl has been manually changed with edit_acl.html.
      + 'members': Total number of members, including moderators.
      + 'moderators': Number of moderators.
      + 'last_activity': Date of last time some content was added to or edited
         in this community.
      + 'create_date': Date community was created.
      + 'wiki_pages': Number of wiki pages in this community.
      + 'blog_entries': Number of blog entries in this community.
      + 'comments': Number of comments in this community.
      + 'files': Number of files in this community.
      + 'calendar_events': Number of calendar events in this community.
      + 'community_tags': Number of tags used in this community.  Includes tags
        on content contained by the community.
      + 'percent_engaged': Percentage of community members that have
        contributed 2 items or more in the last 30 days.
    """
    now = datetime.datetime.now()
    communities = find_communities(context)
    for community in communities.values():
        stats = dict(
            community=community.title,
            id=community.__name__,
            members=len(community.member_names),
            moderators=len(community.moderator_names),
            last_activity=community.content_modified,
            create_date=community.created,
            wiki_pages=0,
            blog_entries=0,
            comments=0,
            files=0,
            calendar_events=0,
        )

        active_users = {}

        def count(node):
            if IWikiPage.providedBy(node):
                stats['wiki_pages'] += 1
            elif IBlogEntry.providedBy(node):
                stats['blog_entries'] += 1
            elif IComment.providedBy(node):
                stats['comments'] += 1
            elif ICommunityFile.providedBy(node):
                stats['files'] += 1
            elif ICommunityFile.providedBy(node):
                stats['calendar_events'] += 1

            created = getattr(node, 'created', None)
            if created is not None and now - created < THIRTY_DAYS:
                creator = node.creator
                if creator not in active_users:
                    active_users[creator] = 1
                else:
                    active_users[creator] += 1

            if hasattr(node, '__getitem__') and hasattr(node, 'keys'):
                for key in node.keys():
                    count(node[key])

        count(community)

        tags = find_tags(context)
        stats['community_tags'] = len(tags.getTags(
            community=community.__name__
        ))

        if hasattr(community, '__custom_acl__'):
            stats['security_state'] = 'custom'
        else:
            workflow = get_workflow(ICommunity, 'security', community)
            stats['security_state'] = workflow.state_of(community)

        engaged_users = len([v for v in active_users.values() if v >= 2])
        stats['percent_engaged'] = 100.0 * engaged_users / stats['members']

        yield stats