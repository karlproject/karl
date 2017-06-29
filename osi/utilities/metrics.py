import datetime
from karl.models.interfaces import ICatalogSearch
from karl.content.calendar.utils import next_month
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import IWikiPage
from karl.models.interfaces import IComment
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IIntranet
from karl.models.interfaces import IIntranets
from karl.models.interfaces import IProfile
from karl.utils import coarse_datetime_repr
from karl.utils import find_communities
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_users
from osi.interfaces import IMetricsContainerFolder
from osi.interfaces import IMetricsMonthFolder
from osi.interfaces import IMetricsYearFolder
from pyramid.traversal import model_path
from repoze.workflow import get_workflow

def find_metrics(context):
    return find_site(context).get('metrics', None)

def date_range(year, month):
    """return a tuple of two datetimes suitable for a range query"""
    begin = datetime.datetime(year, month, 1)
    endyear, endmonth = next_month(year, month)
    end = datetime.datetime(endyear, endmonth, 1)

    return coarse_datetime_repr(begin), coarse_datetime_repr(end)

def month_string(integer_month):
    if integer_month < 10:
        return '0%s' % integer_month
    return str(integer_month)

def collect_contenttype_metrics(context, year, month):
    result = {}
    search = ICatalogSearch(context)
    begin, end = date_range(year, month)

    content_types = (
        ('blog', IBlogEntry),
        ('comment', IComment),
        ('folder', ICommunityFolder),
        ('file', ICommunityFile),
        ('wiki', IWikiPage),
        ('event', ICalendarEvent),
        )

    for name, interface in content_types:
        created_count, _, _ = search(creation_date=(begin, end),
                                     interfaces=[interface])
        total_count, _, _ = search(creation_date=(None, end),
                                   interfaces=[interface])
        result[name] = dict(total=total_count,
                            created=created_count,
                            )
    return result

def collect_profile_metrics(context, year, month):
    result = {}
    search = ICatalogSearch(context)
    begin, end = date_range(year, month)

    users = find_users(context)
    staff_set = users.users_in_group('group.KarlStaff')

    _, docids, resolver = search(creation_date=(None, end),
                                 interfaces=[IProfile],
                                 )

    for profile in (resolver(docid) for docid in docids):
        userid = profile.__name__
        created_count, _, _ = search(creation_date=(begin, end),
                                     creator=userid)
        total_count, _, _ = search(creation_date=(None, end),
                                   creator=userid)
        is_staff = userid in staff_set
        result[userid] = dict(total=total_count,
                              created=created_count,
                              is_staff=is_staff,
                              )
    return result

NATIONAL_FOUNDATIONS = set([
    'open-society-foundation-for-albania',
    'open-society-afghanistan',
    'open-society-institute-assistance-foundation-armenia',
    'open-society-institute-assistance-foundation-azerbaijan',
    'open-society-fund-bosnia-and-herzegovina',
    'open-society-initiative-for-eastern-africa',
    'open-society-institute-sofia',
    'open-society-fund-prague',
    'open-estonia-foundation',
    'open-society-georgia-foundation',
    'fundacion-soros-guatemala',
    'fondation-connaissance-et-liberte',
    'arab-regional-office',
    'tifa-foundation-indonesia',
    'soros-foundation-kyrgyzstan',
    'soros-foundation-latvia',
    'soros-foundation-kazakhstan',
    'kosovo-foundation-for-open-society',
    'foundation-open-society-institute-representative-office-montenegro',
    'soros-foundation-moldova',
    'alliance-for-social-dialogue',
    'open-society-forum',
    'foundation-open-society-institute-macedonia',
    'open-society-foundation-for-south-africa',
    'open-society-foundation-bratislava',
    'stefan-batory-foundation',
    'foundation-open-society-institute-pakistan',
    'soros-foundation-romania',
    'open-society-initiative-for-west-africa',
    'international-renaissance-foundation',
    'open-society-institute-assistance-foundation-tajikistan',
    'open-society-initiative-for-southern-africa',
    'fund-for-an-open-society-serbia',
    'open-society-foundation-turkey',
    ])

def find_user_info(profile, staff_set, wf):
    is_staff = profile.__name__ in staff_set
    is_core_office = profile.organization == 'Open Society Institute'
    categories = getattr(profile, 'categories', {}) or {}
    entities = set(categories.get('entities', []))
    is_national_foundation = bool(entities & NATIONAL_FOUNDATIONS)

    # we use a heurisitic to determine whether the user is a former staff or an
    # affiliate we use the convention that if the position starts with 'Former '
    # then the user is former staff
    if is_staff:
        is_former = is_affiliate = False
    else:
        position = profile.position or ''
        if position.startswith('Former '):
            is_former = True
            is_affiliate = False
        else:
            is_former = False
            is_affiliate = True

    state = wf.state_of(profile)
    is_active = state == 'active'

    return dict(
        staff = is_staff,
        core_office = is_core_office,
        national_foundation = is_national_foundation,
        former = is_former,
        affiliate = is_affiliate,
        active = is_active,
        )

def calc_user_totals(total, docids, resolver, staff_set, get_workflow):
    result = dict(
        staff = 0,
        core_office = 0,
        national_foundation = 0,
        former = 0,
        affiliate = 0,
        active = 0,
        total = total,
        )

    wf = get_workflow(IProfile, 'security')

    for docid in docids:
        profile = resolver(docid)
        if profile is not None:
            user_info = find_user_info(profile, staff_set, wf)
            for attribute, should_include in user_info.items():
                if should_include:
                    result[attribute] = result[attribute] + 1

    return result

def collect_user_metrics(context, year, month, get_workflow=get_workflow):
    # get_workflow is for testing
    result = {}
    search = ICatalogSearch(context)
    begin, end = date_range(year, month)

    users = find_site(context).users
    staff_set = users.users_in_group('group.KarlStaff')

    created_count, docids, resolver = search(creation_date=(begin, end),
                                             interfaces=[IProfile])

    created_user_info = calc_user_totals(created_count, docids, resolver,
                                         staff_set, get_workflow)

    total_count, docids, resolver = search(creation_date=(None, end),
                                           interfaces=[IProfile])
    total_user_info = calc_user_totals(total_count, docids, resolver,
                                       staff_set, get_workflow)

    result['created'] = created_user_info
    result['total'] = total_user_info

    return result

def collect_community_metrics(context, year, month):
    created = {}
    total = {}
    search = ICatalogSearch(context)
    begin, end = date_range(year, month)

    def make_type_counter(community):
        path = model_path(community)
        def count(content_type, creation_date):
            n, _, _ = search(path=path,
                             interfaces=[content_type],
                             creation_date=creation_date)
            return n
        def count_type(content_type):
            return (count(content_type, (begin, end)),
                    count(content_type, (None, end)))
        return count_type


    _, docids, resolver = search(interfaces=[ICommunity],
                                 creation_date=(None, end))
    for community in (resolver(docid) for docid in docids):

        if IIntranets.providedBy(community) or IIntranet.providedBy(community):
            # the offices container and the offices themselves provide
            # the ICommunity interface. we want to filter those out
            # from this list.
            continue

        communityid = community.__name__
        count_type = make_type_counter(community)

        # count created/totals (_c, _t suffix) for content types
        wikis_c, wikis_t = count_type(IWikiPage)
        blogs_c, blogs_t = count_type(IBlogEntry)
        comments_c, comments_t = count_type(IComment)
        files_c, files_t = count_type(ICommunityFile)
        events_c, events_t = count_type(ICalendarEvent)

        created[communityid] = dict(
            title = community.title,
            members = len(community.member_names),
            moderators = len(community.moderator_names),
            created = community.created,
            security_state = community.security_state,
            last_activity = community.content_modified,
            wikis = wikis_c,
            blogs = blogs_c,
            comments = comments_c,
            files = files_c,
            events = events_c,
            total = wikis_c + blogs_c + comments_c + files_c + events_c,
            )

        total[communityid] = dict(
            title = community.title,
            members = len(community.member_names),
            moderators = len(community.moderator_names),
            created = community.created,
            security_state = community.security_state,
            last_activity = community.content_modified,
            wikis = wikis_t,
            blogs = blogs_t,
            comments = comments_t,
            files = files_t,
            events = events_t,
            total = wikis_t + blogs_t + comments_t + files_t + events_t,
            )

    return dict(created=created, total=total)
