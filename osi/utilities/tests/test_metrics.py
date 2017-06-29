import unittest

from pyramid import testing
from karl import testing as karltesting

class TestUtilities(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def test_find_metrics_none(self):
        from osi.utilities.metrics import find_metrics
        site = karltesting.DummyModel()
        result = find_metrics(site)
        self.failUnless(result is None)

    def test_find_metrics(self):
        from osi.utilities.metrics import find_metrics
        site = karltesting.DummyModel()
        metrics = karltesting.DummyModel()
        site['metrics'] = metrics
        result = find_metrics(site)
        self.failUnless(result is metrics)

    def test_date_range(self):
        from osi.utilities.metrics import date_range
        begin, end = date_range(2012, 1)
        self.assertEqual(13253760, begin)
        self.assertEqual(13280544, end)

    def test_month_string(self):
        from osi.utilities.metrics import month_string
        self.assertEqual('07', month_string(7))
        self.assertEqual('11', month_string(11))

class TestMetricsCollection(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def test_contenttype(self):
        from osi.utilities.metrics import collect_contenttype_metrics
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch

        karltesting.registerAdapter(DummyContentTypeSearch, (Interface),
                                    ICatalogSearch)
        result = collect_contenttype_metrics(None, 1985, 1)
        self.assertEqual(
            {'blog': {'created': 1, 'total': 2},
             'comment': {'created': 1, 'total': 2},
             'event': {'created': 1, 'total': 2},
             'file': {'created': 1, 'total': 2},
             'folder': {'created': 1, 'total': 2},
             'wiki': {'created': 1, 'total': 2}},
            result)

    def test_profile(self):
        from osi.utilities.metrics import collect_profile_metrics
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch

        karltesting.registerAdapter(DummyProfileSearch, (Interface),
                                    ICatalogSearch)
        dummy_users = DummyUsers()
        site = karltesting.DummyModel()
        site.users = dummy_users

        result = collect_profile_metrics(site, 1985, 1)
        self.assertEqual(
            {'biff': {'created': 1, 'is_staff': False, 'total': 2},
             'george': {'created': 1, 'is_staff': True, 'total': 2}},
            result)

    def test_user_metrics(self):
        from osi.utilities.metrics import collect_user_metrics
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch

        karltesting.registerAdapter(DummyUserSearch, (Interface),
                                    ICatalogSearch)
        dummy_users = DummyUsers()
        site = karltesting.DummyModel()
        site.users = dummy_users

        result = collect_user_metrics(site, 1985, 1, DummyWorkflow)
        self.assertEqual(
            {'created': {'active': 2,
                         'affiliate': 2,
                         'core_office': 0,
                         'former': 0,
                         'national_foundation': 1,
                         'staff': 1,
                         'total': 3},
             'total': {'active': 3,
                       'affiliate': 2,
                       'core_office': 1,
                       'former': 1,
                       'national_foundation': 1,
                       'staff': 1,
                       'total': 4}},
            result)

    def test_community_metrics(self):
        from osi.utilities.metrics import collect_community_metrics
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch

        karltesting.registerAdapter(DummyCommunitySearch, (Interface),
                                    ICatalogSearch)

        site = karltesting.DummyModel()
        result = collect_community_metrics(site, 1985, 1)
        self.assertEqual(
            {'created': {u'flux': {'blogs': 2,
                                   'comments': 7,
                                   'created': 1985,
                                   'last_activity': 1985,
                                   'security_state': 'public',
                                   'events': 3,
                                   'files': 5,
                                   'members': 3,
                                   'moderators': 2,
                                   'title': u'Flux Capacitor',
                                   'total': 21,
                                   'wikis': 4}},
             'total': {u'flux': {'blogs': 4,
                                 'comments': 14,
                                 'created': 1985,
                                 'last_activity': 1985,
                                 'security_state': 'public',
                                 'events': 6,
                                 'files': 10,
                                 'members': 3,
                                 'moderators': 2,
                                 'title': u'Flux Capacitor',
                                 'total': 42,
                                 'wikis': 8}}},
            result)


identity = lambda x:x

class DummyWorkflow(object):
    def __init__(self, content_type, type):
        pass
    def state_of(self, profile):
        if profile.__name__ == u'george':
            return 'active'
        elif profile.__name__ == u'biff':
            return 'inactive'
        elif profile.__name__ == u'doc':
            return 'active'
        elif profile.__name__ == u'marty':
            return 'active'
        raise Exception('Unexpected profile')

class DummyContentTypeSearch(object):
    def __init__(self, context):
        self.context = context
    def __call__(self, **kw):
        creation_date = kw.pop('creation_date', None)
        if creation_date is not None:
            begin, end = creation_date
            if begin is not None and end is not None:
                return 1, [1], None
            else:
                return 2, [1, 2], None
        raise Exception('unexpected kwargs')


class DummyUsers(object):
    def __init__(self):
        pass
    def users_in_group(self, group):
        return ('george',)


class DummyProfileSearch(object):
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        if 'interfaces' in kw:
            return 2, [DummyProfile('george'),
                       DummyProfile('biff')], identity
        creation_date = kw.pop('creation_date', None)
        if creation_date is not None:
            begin, end = creation_date
            if begin is not None:
                return 1, None, None
            else:
                return 2, None, None
        raise Exception('unexpected kwargs')


class DummyProfile(object):
    def __init__(self, name, **kw):
        self.__name__ = name
        self.__dict__.update(kw)


class DummyUserSearch(object):
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        profiles = [
            DummyProfile(u'george',
                         organization=u'flux',
                         position=u'father'),
            DummyProfile(u'biff',
                         organization=u'flux',
                         position=u'bully'),
            DummyProfile(u'doc',
                         organization=u'flux',
                         position=u'scientist',
                         categories=dict(
                    entities=['open-society-forum'])),
            ]
        begin, end = kw['creation_date']
        if begin is not None:
            return 3, profiles, identity
        profiles.append(
            DummyProfile(u'marty',
                         organization=u'Open Society Institute',
                         position=u'Former student'))
        return 4, profiles, identity

class DummyCommunity(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

class DummyCommunitySearch(object):
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        from karl.models.interfaces import ICommunity
        communities = [
            DummyCommunity(__name__=u'flux',
                           title=u'Flux Capacitor',
                           member_names=[u'marty', u'george', u'biff'],
                           moderator_names=[u'marty', u'george'],
                           security_state='public',
                           content_modified=1985,
                           created=1985)
            ]
        interfaces = kw['interfaces']
        interface = interfaces[0]
        if interface == ICommunity:
            return 1, communities, identity

        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import ICalendarEvent
        from karl.content.interfaces import ICommunityFile
        from karl.content.interfaces import IWikiPage
        from karl.models.interfaces import IComment

        begin, end = kw['creation_date']

        result = {
            IBlogEntry: 2,
            ICalendarEvent: 3,
            ICommunityFile: 5,
            IWikiPage: 4,
            IComment: 7,
            }
        n = result[interface]
        if begin is None:
            return 2 * n, [], None
        else:
            return n, [], None
