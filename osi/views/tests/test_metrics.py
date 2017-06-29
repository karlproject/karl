import unittest

from pyramid import testing
from karl import testing as karltesting

class ContainerViewTest(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        renderer = karltesting.registerDummyRenderer(
            "karl.views:templates/generic_layout.pt")

    def tearDown(self):
        testing.cleanUp()

    def test_root_container_view(self):
        from osi.views.metrics import container_view
        context = testing.DummyModel()
        context['1985'] = testing.DummyModel()
        request = testing.DummyRequest()
        result = container_view(context, request)
        self.assertEqual(['1985'], result['years'])

    def test_year_view(self):
        from osi.views.metrics import year_view
        context = testing.DummyModel('1985')
        context['01'] = testing.DummyModel()
        request = testing.DummyRequest()
        result = year_view(context, request)
        self.assertEqual([{'name': 'Jan', 'num': '01'}],
                         result['months_data'])

    def test_month_view(self):
        from osi.views.metrics import month_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        result = month_view(context, request)
        self.assertEqual(302, result.status_int)
        self.assertEqual('http://example.com/contenttype.html',
                         result.location)


class YearViewTest(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        renderer = karltesting.registerDummyRenderer(
            "karl.views:templates/generic_layout.pt")

    def tearDown(self):
        testing.cleanUp()

    def test_contenttype(self):
        from osi.views.metrics import year_contenttype_view
        context = testing.DummyModel('1985')
        context['01'] = sample_folder(1)
        context['02'] = sample_folder(2)
        request = testing.DummyRequest()
        result = year_contenttype_view(context, request)
        self.assertEqual(['Jan', 'Feb'], result['months'])
        self.assertEqual('1985', result['year'])
        blog = result['contenttypes'][0]
        self.assertEqual({'months': [{'created': 1, 'total': 4},
                                     {'created': 2, 'total': 8}],
                          'name': 'blog'},
                         blog)

    def test_users(self):
        from osi.views.metrics import year_users_view
        context = testing.DummyModel('1985')
        context['10'] = sample_folder(1)
        context['11'] = sample_folder(2)
        request = testing.DummyRequest()
        result = year_users_view(context, request)
        self.assertEqual('1985', result['year'])
        self.assertEqual([{'month': 'Oct',
                           'total': {'active': 8,
                                     'affiliate': 6,
                                     'core_office': 4,
                                     'former': 12,
                                     'national_foundation': 2,
                                     'staff': 14,
                                     'total': 10}},
                          {'month': 'Nov',
                           'total': {'active': 16,
                                     'affiliate': 12,
                                     'core_office': 8,
                                     'former': 24,
                                     'national_foundation': 4,
                                     'staff': 28,
                                     'total': 20}}],
                         result['months_data'])

    def test_profiles(self):
        from osi.views.metrics import year_profiles_view
        context = testing.DummyModel('1985')
        context['03'] = sample_folder(1)
        context['04'] = sample_folder(2)
        request = testing.DummyRequest()
        result = year_profiles_view(context, request)
        self.assertEqual(['Mar', 'Apr'], result['months'])
        self.assertEqual('1985', result['year'])
        profile = result['profiles'][0]
        self.failUnless(profile['is_staff'])
        self.assertEqual({'is_staff': True,
                          'months': [{'created': '', 'is_staff': False},
                                     {'created': 2, 'is_staff': True,
                                      'total': 8}],
                          'name': u'marty'},
                         profile)

    def test_communities(self):
        from osi.views.metrics import year_communities_view
        context = testing.DummyModel('1985')
        context['03'] = sample_folder(1)
        context['04'] = sample_folder(2)
        request = testing.DummyRequest()
        result = year_communities_view(context, request)
        self.assertEqual('1985', result['year'])
        self.assertEqual(['Mar', 'Apr'], result['months'])
        self.assertEqual([{'months': [0, 32], 'name': 'Delorean'},
                          {'months': [16, 0], 'name': 'Capacitor'}],
                         result['communities'])


class MonthViewTest(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        renderer = karltesting.registerDummyRenderer(
            "karl.views:templates/generic_layout.pt")

    def tearDown(self):
        testing.cleanUp()

    def test_contenttype(self):
        from osi.views.metrics import month_contenttype_view
        year = testing.DummyModel('1985')
        month = sample_folder(3)
        year['01'] = month
        request = testing.DummyRequest()
        result = month_contenttype_view(month, request)
        self.assertEqual([{'created': 3, 'name': 'blog', 'total': 12},
                          {'created': 3, 'name': 'comment', 'total': 12},
                          {'created': 3, 'name': 'event', 'total': 12},
                          {'created': 3, 'name': 'file', 'total': 12},
                          {'created': 3, 'name': 'folder', 'total': 12},
                          {'created': 3, 'name': 'wiki', 'total': 12}],
                         result['contenttypes'])

    def test_profiles(self):
        from osi.views.metrics import month_profiles_view
        year = testing.DummyModel('1985')
        month = sample_folder(2)
        year['02'] = month
        request = testing.DummyRequest()
        result = month_profiles_view(month, request)
        self.assertEqual([{'created': 2, 'is_staff': True, 'name': u'marty'}],
                         result['profiles'])

    def test_users(self):
        from osi.views.metrics import month_users_view
        year = testing.DummyModel('1985')
        month = sample_folder(4)
        year['04'] = month
        request = testing.DummyRequest()
        result = month_users_view(month, request)
        self.assertEqual({'active': 32,
                          'affiliate': 24,
                          'core_office': 16,
                          'former': 48,
                          'national_foundation': 8,
                          'staff': 56,
                          'total': 40},
                         result['userdata'])

    def test_communities(self):
        from osi.views.metrics import month_communities_view
        year = testing.DummyModel('1985')
        month = sample_folder(1)
        year['03'] = month
        request = testing.DummyRequest()
        result = month_communities_view(month, request)
        date = '1985/02/03'
        self.assertEqual([{'blogs': 3,
                           'comments': 5,
                           'created': date,
                           'last_activity': date,
                           'security_state': 'private',
                           'events': 1,
                           'files': 2,
                           'members': 2,
                           'moderators': 1,
                           'title': 'Capacitor',
                           'total': 16,
                           'wikis': 4}],
                         result['communities'])


def sample_folder(multiplier):
    from repoze.folder import Folder
    from zope.interface import alsoProvides
    from osi.interfaces import IMetricsMonthFolder
    f = Folder()
    alsoProvides(f, IMetricsMonthFolder)
    f.contenttypes = sample_content_types(multiplier)
    username = u'marty' if multiplier % 2 == 0 else u'mcfly'
    f.profiles = sample_profiles(username, multiplier)
    commid, commtitle = (('delorean', 'Delorean') if multiplier % 2 == 0
                         else ('flux', 'Capacitor'))
    f.communities = sample_communities(commid, commtitle, multiplier)
    f.users = sample_users(multiplier)
    return f

def sample_content_types(x=1):
    sample_count = dict(total=4 * x, created=1 * x)
    return {
        'wiki': sample_count,
        'comment': sample_count,
        'blog': sample_count,
        'file': sample_count,
        'folder': sample_count,
        'event': sample_count,
        }

def sample_profiles(username, x=1):
    sample_count = {
        'total': 4 * x,
        'created': 1 * x,
        'is_staff': x % 2 == 0,
        }
    return {username: sample_count}

def sample_communities(commid, title, x=1):
    from datetime import datetime
    date = datetime(1985, 2, 3)
    security_state = 'public' if x % 2 == 0 else 'private'
    sample_created_count = {
        'files': 2 * x,
        'blogs': 3 * x,
        'created': date,
        'last_activity': date,
        'security_state': security_state,
        'comments': 5 * x,
        'moderators': 1 * x,
        'members': 2 * x,
        'wikis': 4 * x,
        'events': 1 * x,
        'total': 16 * x,
        'title': title,
        }
    sample_total_count = dict(
        [(k, v * 3 if isinstance(v, int) else v)
         for k, v in sample_created_count.items()])

    return dict(
        created={commid: sample_created_count},
        total={commid: sample_total_count},
        )

def sample_users(x=1):
    sample_created_count = {
        'national_foundation': 1 * x,
        'core_office': 2 * x,
        'affiliate': 3 * x,
        'active': 4 * x,
        'total': 5 * x,
        'former': 6 * x,
        'staff': 7 * x,
        }
    sample_total_count = dict(
        [(k, v * 2) for k, v in sample_created_count.items()])

    return dict(
        created=sample_created_count,
        total=sample_total_count,
        )
