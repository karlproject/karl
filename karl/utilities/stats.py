import datetime

from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.models.interfaces import ICatalogSearch
from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IWikiPage
from karl.models.interfaces import IComment
from karl.models.interfaces import ICommunity

from karl.utils import coarse_datetime_repr
from karl.utils import find_catalog
from karl.utils import find_community
from karl.utils import find_communities
from karl.utils import find_profiles
from karl.utils import find_tags
from karl.utils import find_users

from repoze.lemonade.content import get_content_type
from repoze.lemonade.content import is_content
from repoze.workflow import get_workflow

THIRTY_DAYS = datetime.timedelta(days=30)

COMMUNITY_COLUMNS = [
    'community',
    'id',
    'security_state',
    'members',
    'moderators',
    'last_activity',
    'create_date',
    'wiki_pages',
    'blog_entries',
    'comments',
    'files',
    'calendar_events',
    'community_tags',
    'percent_engaged',
]

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
            from pyramid.traversal import resource_path
            if IWikiPage.providedBy(node):
                stats['wiki_pages'] += 1
            elif IBlogEntry.providedBy(node):
                stats['blog_entries'] += 1
            elif IComment.providedBy(node):
                stats['comments'] += 1
            elif ICommunityFile.providedBy(node):
                stats['files'] += 1
            elif ICalendarEvent.providedBy(node):
                stats['calendar_events'] += 1

            created = getattr(node, 'created', None)
            if created is not None and now - created < THIRTY_DAYS:
                creator = getattr(node, 'creator', None)
                if creator is not None:
                    if creator not in active_users:
                        active_users[creator] = 1
                    else:
                        active_users[creator] += 1

            if hasattr(node, '__getitem__') and hasattr(node, 'values'):
                for child in node.values():
                    count(child)

            if hasattr(node, '_p_deactivate'):
                node._p_deactivate()

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

        if stats['members'] != 0:
            engaged_users = len([v for v in active_users.values() if v >= 2])
            stats['percent_engaged'] = 100.0 * engaged_users / stats['members']
        else:
            stats['percent_engaged'] = 0

        yield stats

PROFILE_COLUMNS = [
    'first_name',
    'last_name',
    'userid',
    'date_created',
    'is_staff',
    'num_communities',
    'num_communities_moderator',
    'location',
    'department',
    'roles',
    'num_documents',
    'num_tags',
    'documents_this_month',
]

def collect_profile_stats(context):
    """
    Returns an iterator where for each user profile a dict is returned with the
    following keys::

        + first_name
        + last_name
        + userid
        + date_created
        + is_staff
        + num_communities
        + num_communities_moderator
        + location
        + department
        + roles
        + num_documents
        + num_tags
        + documents_this_month
    """
    communities = find_communities(context)
    search = ICatalogSearch(context)
    profiles = find_profiles(context)
    users = find_users(context)

    # Collect community membership
    membership = {}
    moderatorship = {}
    for community in communities.values():
        for name in community.member_names:
            if name not in membership:
                membership[name] = 1
            else:
                membership[name] += 1
        for name in community.moderator_names:
            if name not in moderatorship:
                moderatorship[name] = 1
            else:
                moderatorship[name] += 1

    for profile in profiles.values():
        info = users.get_by_id(profile.__name__)
        if info is not None:
            groups = info['groups']
        else:
            groups = []
        name = profile.__name__
        stats = dict(
            first_name=profile.firstname,
            last_name=profile.lastname,
            userid=name,
            date_created=profile.created,
            location=profile.location,
            department=profile.department,
            is_staff='group.KarlStaff' in groups,
            roles=','.join(groups),
            num_communities=membership.get(name, 0),
            num_communities_moderator=moderatorship.get(name, 0),
        )

        count, docids, resolver = search(creator=name)
        stats['num_documents'] = count

        begin = coarse_datetime_repr(datetime.datetime.now() - THIRTY_DAYS)
        count, docids, resolver = search(
            creator=name, creation_date=(begin, None),
        )
        stats['documents_this_month'] = count

        tags = find_tags(context)
        stats['num_tags'] = len(tags.getTags(users=(name,)))

        yield stats

def user_activity_report(context, ids=None):
    """
    Returns a generator which iterates over user profiles yielding rows where
    each row is a tuple of (username, community, last_activity) where
    `last_activity` is the most recent activity for that user in that
    community.  If ids is not specified, report will be generated for all user
    profiles.  Otherwise, the report will only be generated for the given
    profiles.
    """
    if ids is None:
        profiles = find_profiles(context)
        ids = sorted(profiles.keys())
    else:
        ids = sorted(ids)

    search = ICatalogSearch(context)
    for id in ids:
        # communities[community_name] = (community, last_activity_date)
        communities = {}
        count, docids, resolver = search(creator=id)
        for docid in docids:
            doc = resolver(docid)
            created = getattr(doc, 'created', None)
            community = find_community(doc)
            if community is None:
                continue

            name = community.__name__
            if name not in communities:
                communities[name] = (community, created)
                continue

            last_activity = communities[name][1]
            if created > last_activity:
                communities[name] = (community, created)

        for name in sorted(communities.keys()):
            community, last_activity = communities[name]
            yield id, community, last_activity
