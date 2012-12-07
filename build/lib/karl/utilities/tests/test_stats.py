import unittest
from pyramid import testing
import karl.testing

class TestCommunityStats(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        from karl.utilities import stats
        self._save_datetime = stats.datetime
        stats.datetime = DummyDateTime()

    def tearDown(self):
        testing.cleanUp()

        from karl.utilities import stats
        stats.datetime = self._save_datetime

    def _call_fut(self, context):
        from karl.utilities.stats import collect_community_stats as fut
        return fut(context)

    def _mk_dummy_site(self):
        import datetime
        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import ICalendarEvent
        from karl.content.interfaces import ICommunityFile
        from karl.content.interfaces import IWikiPage
        from karl.models.interfaces import IComment
        from karl.testing import DummyCommunity
        from karl.testing import DummyModel
        from karl.testing import DummyRoot
        from repoze.workflow.testing import registerDummyWorkflow
        from repoze.workflow.testing import DummyWorkflow
        from zope.interface import directlyProvides

        site = DummyRoot()
        site.tags = DummyTags()
        communities = site['communities'] = DummyModel()

        big_endians = communities['big_endians'] = DummyCommunity()
        big_endians.title = 'Big Endians'
        big_endians.member_names = ['fred', 'martin', 'daniela']
        big_endians.moderator_names = ['fred', 'daniela']
        big_endians.created = datetime.datetime(2010, 5, 12, 2, 42)
        big_endians.creator = 'daniela'
        big_endians.content_modified = datetime.datetime(2010, 6, 12, 2, 42)
        big_endians.__custom_acl__ = True

        content = big_endians['wiki1'] = DummyModel()
        content.created = datetime.datetime(2010, 5, 12, 3, 42)
        content.creator = 'daniela'
        directlyProvides(content, IWikiPage)

        content = big_endians['wiki2'] = DummyModel()
        content.created = datetime.datetime(1975, 7, 7, 7, 23)
        content.creator = 'fred'
        directlyProvides(content, IWikiPage)

        little_endians = communities['little_endians'] = DummyCommunity()
        little_endians.title = 'Little Endians'
        little_endians.member_names = ['dusty', 'roberta', 'nina']
        little_endians.moderator_names = ['nina']
        little_endians.created = datetime.datetime(2010, 5, 13, 6, 23)
        little_endians.creator = 'nina'
        little_endians.content_modified = datetime.datetime(
            2010, 6, 12, 3, 42
        )
        little_endians._p_deactivate = lambda: None
        little_endians.state = 'public'

        content = little_endians['blog1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'nina'
        directlyProvides(content, IBlogEntry)

        content['comment1'] = DummyModel()
        content = content['comment1']
        content.created = datetime.datetime.now()
        content.creator = 'roberta'
        directlyProvides(content, IComment)

        content = little_endians['file1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'dusty'
        directlyProvides(content, ICommunityFile)

        content = little_endians['event1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'dusty'
        directlyProvides(content, ICalendarEvent)

        registerDummyWorkflow('security', DummyWorkflow())

        return site

    def test_it(self):
        import datetime
        report = list(self._call_fut(self._mk_dummy_site()))
        report.sort(key=lambda x: x['id'])
        self.assertEqual(len(report), 2)
        row = report.pop(0)
        self.assertEqual(row['community'], 'Big Endians')
        self.assertEqual(row['id'], 'big_endians')
        self.assertEqual(row['members'], 3)
        self.assertEqual(row['moderators'], 2)
        self.assertEqual(row['last_activity'], datetime.datetime(
            2010, 6, 12, 2, 42
        ))
        self.assertEqual(row['create_date'], datetime.datetime(
            2010, 5, 12, 2, 42
        ))
        self.assertEqual(row['security_state'], 'custom')
        self.assertEqual(row['wiki_pages'], 2)
        self.assertEqual(row['blog_entries'], 0)
        self.assertEqual(row['comments'], 0)
        self.assertEqual(row['files'], 0)
        self.assertEqual(row['calendar_events'], 0)
        self.assertEqual(row['community_tags'], 2)
        self.assertAlmostEqual(row['percent_engaged'], 33.33333333)

        row = report.pop(0)
        self.assertEqual(row['community'], 'Little Endians')
        self.assertEqual(row['id'], 'little_endians')
        self.assertEqual(row['members'], 3)
        self.assertEqual(row['moderators'], 1)
        self.assertEqual(row['last_activity'], datetime.datetime(
            2010, 6, 12, 3, 42
        ))
        self.assertEqual(row['create_date'], datetime.datetime(
            2010, 5, 13, 6, 23
        ))
        self.assertEqual(row['security_state'], 'public')
        self.assertEqual(row['wiki_pages'], 0)
        self.assertEqual(row['blog_entries'], 1)
        self.assertEqual(row['comments'], 1)
        self.assertEqual(row['files'], 1)
        self.assertEqual(row['calendar_events'], 1)
        self.assertEqual(row['community_tags'], 1)
        self.assertAlmostEqual(row['percent_engaged'], 66.666666666)

    def test_community_with_no_members(self):
        import datetime
        site = self._mk_dummy_site()
        site['communities']['big_endians'].member_names = set()
        site['communities']['big_endians'].moderator_names = set()
        report = list(self._call_fut(site))
        report.sort(key=lambda x: x['id'])
        self.assertEqual(len(report), 2)
        row = report.pop(0)
        self.assertEqual(row['community'], 'Big Endians')
        self.assertEqual(row['id'], 'big_endians')
        self.assertEqual(row['members'], 0)
        self.assertEqual(row['moderators'], 0)
        self.assertEqual(row['last_activity'], datetime.datetime(
            2010, 6, 12, 2, 42
        ))
        self.assertEqual(row['create_date'], datetime.datetime(
            2010, 5, 12, 2, 42
        ))
        self.assertEqual(row['security_state'], 'custom')
        self.assertEqual(row['wiki_pages'], 2)
        self.assertEqual(row['blog_entries'], 0)
        self.assertEqual(row['comments'], 0)
        self.assertEqual(row['files'], 0)
        self.assertEqual(row['calendar_events'], 0)
        self.assertEqual(row['community_tags'], 2)
        self.assertAlmostEqual(row['percent_engaged'], 0.0)

class TestProfileStats(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        self.registerCatalogSearch()

    def tearDown(self):
        testing.cleanUp()

    def registerCatalogSearch(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        karl.testing.registerAdapter(DummySearchAdapter, (Interface, Interface),
                                     ICatalogSearch)
        karl.testing.registerAdapter(DummySearchAdapter, (Interface,),
                                     ICatalogSearch)

    def _call_fut(self, context):
        from karl.utilities.stats import collect_profile_stats as fut
        return fut(context)

    def _mk_context(self):
        import datetime
        from karl.testing import DummyCommunity
        from karl.testing import DummyModel
        from karl.testing import DummyProfile
        from karl.testing import DummyRoot
        from karl.testing import registerCatalogSearch

        site = DummyRoot()
        site.users = DummyUsers()
        site.tags = DummyTags()
        profiles = site['profiles'] = DummyModel()

        chet = profiles['chet'] = DummyProfile(
            firstname='Chet',
            lastname='Baker',
            created=datetime.datetime(2010, 5, 12, 2, 43),
            location='bathroom',
            department='Crooning',
        )

        chuck = profiles['chuck'] = DummyProfile(
            firstname='Chuck',
            lastname='Mangione',
            created=datetime.datetime(2010, 5, 12, 2, 42),
            location='kitchen',
            department='Blowing',
        )

        chuck = profiles['admin'] = DummyProfile(
            firstname='System',
            lastname='User',
            created=datetime.datetime(2010, 5, 12, 2, 42),
            location='The Machine',
            department='Big Brother',
        )

        communities = site['communities'] = DummyModel()
        dandies = communities['dandies'] = DummyModel()
        dandies.member_names = ['chet', 'chuck']
        dandies.moderator_names = ['chuck']

        loners = communities['loners'] = DummyModel()
        loners.member_names = ['chet']
        loners.moderator_names = ['chet']

        lads = communities['lads'] = DummyModel()
        lads.member_names = ['chet', 'chip', 'charlie']
        lads.moderator_names = ['chet', 'chip']

        return site

    def test_it(self):
        import datetime
        context = self._mk_context()
        report = list(self._call_fut(context))
        report.sort(key=lambda x: x['userid'])
        self.assertEqual(len(report), 3)

        row = report.pop(0)
        self.assertEqual(row['first_name'], 'System')
        self.assertEqual(row['last_name'], 'User')
        self.assertEqual(row['userid'], 'admin')
        self.assertEqual(row['date_created'], datetime.datetime(
            2010, 5, 12, 2, 42
        ))
        self.assertEqual(row['is_staff'], False)
        self.assertEqual(row['num_communities'], 0)
        self.assertEqual(row['num_communities_moderator'], 0)
        self.assertEqual(row['location'], 'The Machine')
        self.assertEqual(row['department'], 'Big Brother')
        self.assertEqual(row['roles'], '')
        self.assertEqual(row['num_documents'], 0)
        self.assertEqual(row['num_tags'], 0)
        self.assertEqual(row['documents_this_month'], 0)

        row = report.pop(0)
        self.assertEqual(row['first_name'], 'Chet')
        self.assertEqual(row['last_name'], 'Baker')
        self.assertEqual(row['userid'], 'chet')
        self.assertEqual(row['date_created'], datetime.datetime(
            2010, 5, 12, 2, 43
        ))
        self.assertEqual(row['is_staff'], False)
        self.assertEqual(row['num_communities'], 3)
        self.assertEqual(row['num_communities_moderator'], 2)
        self.assertEqual(row['location'], 'bathroom')
        self.assertEqual(row['department'], 'Crooning')
        self.assertEqual(row['roles'], 'group.Smoove')
        self.assertEqual(row['num_documents'], 4)
        self.assertEqual(row['num_tags'], 2)
        self.assertEqual(row['documents_this_month'], 2)

        row = report.pop(0)
        self.assertEqual(row['first_name'], 'Chuck')
        self.assertEqual(row['last_name'], 'Mangione')
        self.assertEqual(row['userid'], 'chuck')
        self.assertEqual(row['date_created'], datetime.datetime(
            2010, 5, 12, 2, 42
        ))
        self.assertEqual(row['is_staff'], True)
        self.assertEqual(row['num_communities'], 1)
        self.assertEqual(row['num_communities_moderator'], 1)
        self.assertEqual(row['location'], 'kitchen')
        self.assertEqual(row['department'], 'Blowing')
        self.assertEqual(row['roles'], 'group.KarlStaff,group.BrassPlayers')
        self.assertEqual(row['num_documents'], 56)
        self.assertEqual(row['num_tags'], 1)
        self.assertEqual(row['documents_this_month'], 5)

class TestUserActivityReport(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        self._mk_site()

    def tearDown(self):
        testing.cleanUp()

    def registerCatalogSearch(self, search_adapter):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        karl.testing.registerAdapter(search_adapter, (Interface,),
                                     ICatalogSearch)

    def _mk_site(self):
        from karl.models.interfaces import ICommunity
        from karl.testing import DummyCommunity
        from karl.testing import DummyModel
        from karl.testing import DummyRoot
        from zope.interface import directlyProvides

        search_results = {
            'daniela': [],
            'stough': [],
            'fred': [],
        }

        self.site = site = DummyRoot()
        communities = site['communities'] = DummyModel()

        profiles = site['profiles'] = DummyModel()
        profiles['daniela'] = DummyModel()
        profiles['stough'] = DummyModel()
        profiles['fred'] = DummyModel()

        big_endians = communities['big_endians'] = DummyCommunity()
        self.big_endians = big_endians
        directlyProvides(big_endians, ICommunity)

        content = big_endians['wiki1'] = DummyModel()
        content.created = datetime.datetime(2010, 5, 12, 3, 42)
        search_results['daniela'].append(content)

        content = big_endians['wiki2'] = DummyModel()
        content.created = datetime.datetime(1975, 7, 7, 7, 23)
        search_results['fred'].append(content)

        little_endians = communities['little_endians'] = DummyCommunity()
        self.little_endians = little_endians
        directlyProvides(little_endians, ICommunity)

        content = little_endians['blog1'] = DummyModel()
        content.created = datetime.datetime(2010, 5, 12, 3, 43)
        search_results['stough'].append(content)

        content['comment1'] = DummyModel()
        content = content['comment1']
        content.created = datetime.datetime(2010, 5, 12, 3, 44)
        search_results['stough'].append(content)

        content['comment2'] = DummyModel()
        content = content['comment2']
        content.created = datetime.datetime(2010, 5, 12, 3, 45)
        search_results['daniela'].append(content)

        self.registerCatalogSearch(DummySearchAdapterFactory(search_results))

    def _call_fut(self, context, ids=None):
        from karl.utilities.stats import user_activity_report as fut
        return fut(context, ids)

    def test_it(self):
        from datetime import datetime
        results = list(self._call_fut(self.site))
        self.assertEqual(len(results), 4)
        self.assertEqual(
            results[0],
            ('daniela', self.big_endians, datetime(2010, 5, 12, 3, 42))
        )
        self.assertEqual(
            results[1],
            ('daniela', self.little_endians, datetime(2010, 5, 12, 3, 45))
        )
        self.assertEqual(
            results[2],
            ('fred', self.big_endians, datetime(1975, 7, 7, 7, 23))
        )
        self.assertEqual(
            results[3],
            ('stough', self.little_endians, datetime(2010, 5, 12, 3, 44))
        )

    def test_it_with_ids(self):
        from datetime import datetime
        results = list(self._call_fut(self.site, ('stough', 'fred')))
        self.assertEqual(len(results), 2)
        self.assertEqual(
            results[0],
            ('fred', self.big_endians, datetime(1975, 7, 7, 7, 23))
        )
        self.assertEqual(
            results[1],
            ('stough', self.little_endians, datetime(2010, 5, 12, 3, 44))
        )

class DummyTags(object):
    communities = {
        'big_endians': ['cute', 'clever'],
        'little_endians': ['crooners'],
    }

    users = {
        'chuck': ['bigtime',],
        'chet': ['ladies', 'man'],
    }

    def getTags(self, users=None, community=None):
        if community is not None:
            return self.communities.get(community, [])
        elif users is not None:
            assert len(users) == 1
            return self.users.get(users[0], [])

class DummySearchAdapter(object):
    creators = {
        'chet': (4, 2),
        'chuck': (56, 5),
        'admin': (0, 0),
    }

    def __init__(self, context):
        pass

    def __call__(self, **kw):
        count = 0
        if 'creator' in kw:
            creator = kw['creator']
            if 'creation_date' in kw:
                count = self.creators[creator][1]
            else:
                count = self.creators[creator][0]

        return count, None, None

def DummySearchAdapterFactory(results):
    """
    Results is a mapping of creator to list of documents.
    """
    class DummySearchAdapter2(object):
        def __init__(self, context):
            pass

        def __call__(self, **kw):
            creator = kw['creator']
            content = results[creator]
            return len(content), content, lambda x: x

    return DummySearchAdapter2

class DummyUsers(object):
    users = {
        'chuck': {
            'groups': ['group.KarlStaff', 'group.BrassPlayers'],
        },
        'chet': {
            'groups': ['group.Smoove'],
        },
    }

    def get_by_id(self, id):
        return self.users.get(id)

import datetime
class DummyDateTime(object):
    _now = datetime.datetime(2010, 6, 7, 8, 9)

    @property
    def datetime(self):
        return self

    def __call__(self, *args):
        return datetime.datetime(*args)

    def now(self):
        return self._now
