from __future__ import with_statement

import unittest

from zope.testing.cleanup import cleanUp
from pyramid import testing
import urllib2


class Test_get_last_sync(unittest.TestCase):

    def _callFUT(self, root, url):
        from osi.sync.gsa_sync import get_last_sync
        return get_last_sync(root, url)

    def _makeContext(self, **kw):
        from pyramid.testing import DummyResource
        return DummyResource(**kw)

    def test_wo_mapping(self):
        URL = 'http://example.com/sync.xml'
        root = self._makeContext()
        self.assertEqual(self._callFUT(root, URL), None)

    def test_w_mapping_miss(self):
        URL = 'http://example.com/sync.xml'
        root = self._makeContext(last_gsa_sync={})
        self.assertEqual(self._callFUT(root, URL), None)

    def test_w_mapping_hit(self):
        from datetime import datetime
        NOW = datetime(2013, 7, 29, 17, 22, 43)
        URL = 'http://example.com/sync.xml'
        root = self._makeContext(last_gsa_sync={URL: NOW})
        self.assertEqual(self._callFUT(root, URL), NOW)

class GsaSyncTests(unittest.TestCase):

    def setUp(self):
        cleanUp()
        testing.setUp(request=testing.DummyRequest())

        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        def profile_factory(**kw):
            kw['security_state'] = 'active'
            return testing.DummyModel(**kw)
        registerContentFactory(profile_factory, IProfile)

        from karl.testing import DummyUsers
        self.root = root = testing.DummyModel()
        root.users = DummyUsers()
        root['profiles'] = testing.DummyModel()
        root['people'] = people = testing.DummyModel()
        people['categories'] = categories = testing.DummyModel()
        people.update_indexes = lambda : None
        categories['offices'] = testing.DummyModel()
        categories['entities'] = testing.DummyModel()
        categories['departments'] = testing.DummyModel()
        categories['boards'] = testing.DummyModel()

        from osi.sync import gsa_sync
        self._save_urllib2 = gsa_sync.urllib2
        self.urllib2 = gsa_sync.urllib2 = DummyUrllib2()
        gsa_sync.reindex_peopledirectory = lambda x: None
        gsa_sync.RETRY_SLEEP = 0

        from karl.testing import registerDummyMailer
        registerDummyMailer()

    def tearDown(self):
        cleanUp()
        testing.tearDown()

        from osi.sync import gsa_sync
        gsa_sync.urllib2 = self._save_urllib2

    def _makeOne(self, *args, **kw):
        from osi.sync.gsa_sync import GsaSync
        return GsaSync(*args, **kw)

    def _call_it(self):
        from osi.sync.gsa_sync import GsaSync
        GsaSync(self.root, 'https://example.com/gsa_data.xml')()

    def test_create(self):
        self._call_it()

        profiles = self.root['profiles']
        self.failUnless('crossi' in profiles)
        profile = profiles['crossi']

        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.email, 'user2@example.com')
        self.assertEqual(profile.phone, '212-555-1212')
        self.assertEqual(profile.extension, '')
        self.assertEqual(profile.department, 'Human Resources')
        self.assertEqual(profile.position,
                         'Responsable Bibliotheque Monique Calixte')
        self.assertEqual(profile.organization, 'Open Society Institute')
        self.assertEqual(profile.location, 'Port-au-Prince')
        self.assertEqual(profile.country, 'HT')
        self.assertEqual(profile.websites, ('http://spacelabstudio.com',))
        self.assertEqual(profile.languages, 'Esperanto, Portuguese')
        self.assertEqual(profile.office, 'Fondation Connaissance et Liberte')
        self.assertEqual(profile.room_no, '1001')
        self.assertEqual(profile.home_path, 'offices/national-foundation')
        self.assertEqual(profile.categories['entities'], [
            'open-society-institute',
            ])
        self.assertEqual(profile.categories['offices'], [
            'fondation-connaissance-et-liberte'])
        self.failIf(profile.categories.has_key('departments'))
        self.failIf(profile.categories.has_key('boards'))

        info = self.root.users.get_by_id('crossi')
        info.pop('password')
        self.assertEqual(info, {
            'id': 'crossi',
            'login': 'crossi',
            'groups': set(['group.KarlStaff']),
            })

        categories = self.root['people']['categories']
        offices = categories['offices']
        self.failUnless('fondation-connaissance-et-liberte' in offices)
        office = offices['fondation-connaissance-et-liberte']
        self.assertEqual(office.sync_id, '1062')
        self.assertEqual(self.urllib2.timeout, None)

    def test_create_w_timeout(self):
        gsa = self._makeOne(self.root, 'https://example.com/gsa_data.xml',
                            timeout=15)
        gsa()

        profiles = self.root['profiles']
        self.failUnless('crossi' in profiles)
        profile = profiles['crossi']

        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.email, 'user2@example.com')
        self.assertEqual(profile.phone, '212-555-1212')
        self.assertEqual(profile.extension, '')
        self.assertEqual(profile.department, 'Human Resources')
        self.assertEqual(profile.position,
                         'Responsable Bibliotheque Monique Calixte')
        self.assertEqual(profile.organization, 'Open Society Institute')
        self.assertEqual(profile.location, 'Port-au-Prince')
        self.assertEqual(profile.country, 'HT')
        self.assertEqual(profile.websites, ('http://spacelabstudio.com',))
        self.assertEqual(profile.languages, 'Esperanto, Portuguese')
        self.assertEqual(profile.office, 'Fondation Connaissance et Liberte')
        self.assertEqual(profile.room_no, '1001')
        self.assertEqual(profile.home_path, 'offices/national-foundation')
        self.assertEqual(profile.categories['entities'], [
            'open-society-institute',
            ])
        self.assertEqual(profile.categories['offices'], [
            'fondation-connaissance-et-liberte'])
        self.failIf(profile.categories.has_key('departments'))
        self.failIf(profile.categories.has_key('boards'))

        info = self.root.users.get_by_id('crossi')
        info.pop('password')
        self.assertEqual(info, {
            'id': 'crossi',
            'login': 'crossi',
            'groups': set(['group.KarlStaff']),
            })

        categories = self.root['people']['categories']
        offices = categories['offices']
        self.failUnless('fondation-connaissance-et-liberte' in offices)
        office = offices['fondation-connaissance-et-liberte']
        self.assertEqual(office.sync_id, '1062')
        self.assertEqual(self.urllib2.timeout, 15)

    def test_update(self):
        profiles = self.root['profiles']
        profiles['crossi'] = profile = testing.DummyModel(
            security_state='active')
        profile.firstname = 'Chris'
        profile.lastname = 'Rossi'
        profile.email = 'chris@example.com'
        self.root.users.add('crossi', 'crossi', 'password', set())

        name = 'fondation-connaissance-et-liberte'
        categories = self.root['people']['categories']
        offices = categories['offices']
        offices[name] = office = testing.DummyModel()
        office.sync_id = '1062'
        office['hcard'] = testing.DummyModel()
        office['hcard'].fn = 'FN'

        self._call_it()

        self.failUnless('crossi' in profiles)
        profile = profiles['crossi']

        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.email, 'user2@example.com')

        self.failUnless(name in offices)
        office = offices[name]
        self.assertEqual(office.sync_id, '1062')
        self.failUnless('143 Avenue Christophe, Port-au-Prince' in
                        office.description, office.description)
        self.assertEqual(self.urllib2.timeout, None)

    def test_staff_to_affiliate_back_to_staff(self):
        self._call_it()
        chris = self.root['profiles']['crossi']
        users = self.root.users
        self.assertEqual(chris.room_no, '1001')
        self.failUnless(users.member_of_group('crossi', 'group.KarlStaff'))

        self.urllib2.filename = 'gsa_data2.xml'
        self._call_it()
        self.assertEqual(chris.room_no, '1002')
        self.failIf(users.member_of_group('crossi', 'group.KarlStaff'))

        self.urllib2.filename = 'gsa_data3.xml'
        self._call_it()
        self.assertEqual(chris.room_no, '1002')
        self.failIf(users.member_of_group('crossi', 'group.KarlStaff'))

        self.urllib2.filename = 'gsa_data4.xml'
        self._call_it()
        self.assertEqual(chris.room_no, '1004')
        self.failUnless(users.member_of_group('crossi', 'group.KarlStaff'))

    def test_remove_existing_categories(self):
        self._call_it()
        chris = self.root['profiles']['crossi']
        users = self.root.users
        self.assertEqual(chris.room_no, '1001')
        self.assertEqual(chris.categories,
                         {'entities': ['open-society-institute'],
                          'offices': ['fondation-connaissance-et-liberte']}
                         )

        self.urllib2.filename = 'gsa_data2.xml'
        self._call_it()
        self.assertEqual(chris.room_no, '1002')

        self.assertEqual(chris.categories, {})

    def test_staff_dont_get_categories(self):
        self._call_it()
        chris = self.root['profiles']['crossi']
        users = self.root.users
        self.assertEqual(chris.room_no, '1001')
        self.assertEqual(chris.categories,
                         {'entities': ['open-society-institute'],
                          'offices': ['fondation-connaissance-et-liberte']}
                         )

        self.urllib2.filename = 'gsa_data3.xml'
        self._call_it()
        self.assertEqual(chris.room_no, '1003')

        self.assertEqual(chris.categories, {})

    def test_user_is_not_staff(self):
        self.urllib2.filename = 'gsa_data2.xml'
        self._call_it()
        self.failIf('crossi' in self.root['profiles'])

    def test_create_username_with_spaces(self):
        self._call_it()
        self.failUnless('JohnMcEntirelyCool' in self.root['profiles'])
        info = self.root.users.get_by_id('JohnMcEntirelyCool')
        self.assertEqual(info['login'], 'John McEntirely Cool')
        self.assertEqual(info['id'], 'JohnMcEntirelyCool')

    def test_update_username_with_spaces(self):
        profiles = self.root['profiles']
        profiles['John McEntirely Cool'] = testing.DummyModel(
            security_state='active')
        self.root.users.add('John McEntirely Cool', 'John McEntirely Cool',
                            'password', set())

        self._call_it()
        self.failIf('JohnMcEntirelyCool' in self.root['profiles'])
        self.failUnless('John McEntirely Cool' in self.root['profiles'])
        self.assertEqual(self.root.users.get_by_id('JohnMcEntirelyCool'), None)
        info = self.root.users.get_by_id('John McEntirely Cool')
        self.assertEqual(info['login'], 'John McEntirely Cool')
        self.assertEqual(info['id'], 'John McEntirely Cool')

    def test_update_username_without_spaces(self):
        profiles = self.root['profiles']
        profiles['JohnMcEntirelyCool'] = testing.DummyModel(
            security_state='active')
        self.root.users.add('JohnMcEntirelyCool', 'John McEntirely Cool',
                            'password', set())

        self._call_it()
        self.failUnless('JohnMcEntirelyCool' in self.root['profiles'])
        self.failIf('John McEntirely Cool' in self.root['profiles'])
        self.assertEqual(self.root.users.get_by_id('John McEntirely Cool'),
                         None)
        info = self.root.users.get_by_id('JohnMcEntirelyCool')
        self.assertEqual(info['login'], 'John McEntirely Cool')
        self.assertEqual(info['id'], 'JohnMcEntirelyCool')

    def test_dont_clobber_biography(self):
        profiles = self.root['profiles']
        profiles['crossi'] = profile = testing.DummyModel(
            security_state='active')
        profile.firstname = 'Chris'
        profile.lastname = 'Rossi'
        profile.email = 'chris@example.com'
        profile.biography = 'Born.  Still alive.'
        self.root.users.add('crossi', 'crossi', 'password', set())

        self._call_it()
        self.assertEqual(profile.biography, 'Born.  Still alive.')

    def test_retry_on_server_error(self):
        self.urllib2.errors = 1
        self._call_it()
        self.failUnless('crossi' in self.root['profiles'])

    def test_too_many_server_errors(self):
        from osi.sync.gsa_sync import RETRIES
        self.urllib2.errors = RETRIES + 1
        self.assertRaises(urllib2.HTTPError, self._call_it)

    def test_staff_to_affiliate_drops_community_memberships(self):
        self._call_it()
        chris = self.root['profiles']['crossi']
        users = self.root.users
        users._by_id['crossi']['groups'].add('group.community:Testing:member')
        users._by_id['crossi']['groups'].add(
            'group.community:Testing2:moderator')

        self.urllib2.filename = 'gsa_data2.xml'
        self._call_it()
        self.failUnless(('crossi', 'group.community:Testing:member') in
                        users.removed_groups)
        self.failUnless(('crossi', 'group.community:Testing2:moderator') in
                        users.removed_groups)

    def test_deactivate_user(self):
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security')

        self._call_it()
        users = self.root.users
        self.failIf(users.get_by_id('crossi') is None)
        self.assertEqual(users.removed_users, [])

        self.urllib2.filename = 'gsa_data5.xml'
        self._call_it()
        self.assertEqual(users.removed_users, ['crossi', 'crossi'])
        self.assertEqual(workflow.transitioned[0]['to_state'], 'inactive')

    def test_update_inactive_user(self):
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security')
        self.root['profiles']['crossi'] = profile = testing.DummyModel(
            security_state='inactive')
        self.urllib2.filename = 'gsa_data5.xml'
        self._call_it()
        self.assertEqual(profile.languages, 'Esperanto, Portuguese')
        self.assertEqual(self.root.users.removed_users, [])
        self.assertEqual(len(workflow.transitioned), 0)

    def test_reactivate_user(self):
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security', DummyWorkflow())
        self.root['profiles']['crossi'] = profile = testing.DummyModel(
            security_state='inactive', title='Mr. Handsome',
            email='mr@handsome')
        self.urllib2.filename = 'gsa_data4.xml'
        self._call_it()
        users = self.root.users
        self.assertEqual(profile.languages, 'Esperanto, Portuguese')
        username, login, password, groups = users.added
        self.assertEqual(username, 'crossi')
        self.assertEqual(login, 'crossi')
        self.assertEqual(groups, set(['group.KarlStaff']))
        self.assertEqual(users.removed_users, [])
        self.assertEqual(len(workflow.transitioned), 1)

    def test_create_inactive_user(self):
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security')
        self.urllib2.filename = 'gsa_data5.xml'
        self._call_it()
        users = self.root.users
        username, login, password, groups = users.added
        self.assertEqual(username, 'crossi')
        self.assertEqual(login, 'crossi')
        self.assertEqual(groups, set(['group.KarlStaff']))
        self.assertEqual(users.removed_users, ['crossi'])
        self.assertEqual(workflow.transitioned[0]['to_state'], 'inactive')

class UserProfileImporterTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

        self.root = root = testing.DummyModel()
        self.profiles = profiles = testing.DummyModel()
        root['profiles'] = profiles
        root['people'] = testing.DummyModel()
        root['people']['categories'] = categories = testing.DummyModel()
        categories['entities'] = entities = testing.DummyModel()
        entities['open-society-institute'] = testing.DummyModel(sync_id='123')
        entities['hardees'] = testing.DummyModel(sync_id='456')
        categories['departments'] = departments = testing.DummyModel()
        departments['information-retrieval'] = testing.DummyModel(
            sync_id='321')
        departments['paper-chase'] = testing.DummyModel(sync_id='654')
        categories['boards'] = boards = testing.DummyModel()
        boards['1-x-3'] = testing.DummyModel(sync_id='987')
        categories['offices'] = offices = testing.DummyModel()
        offices['fondation-connaissance-et-liberte'] = testing.DummyModel(
            sync_id='213')
        offices['hand-creme'] = testing.DummyModel(
            sync_id='643')

        from karl.testing import DummyUsers
        root.users = DummyUsers()

    def tearDown(self):
        cleanUp()

    def _target_class(self):
        from osi.sync.gsa_sync import UserProfileImporter
        return UserProfileImporter

    def _make_one(self, fname='test_profile.xml'):
        import os
        import sys
        import lxml.etree
        here = os.path.dirname(sys.modules[__name__].__file__)
        with open(os.path.join(here, 'xml', fname)) as stream:
            doc = lxml.etree.parse(stream)
        return self._target_class()(doc.getroot())

    def test_update(self):
        profile = testing.DummyModel(security_state='active')
        self.profiles['crossi'] = profile
        self.root.users.add('crossi', 'crossi', 'crossi',
                          set(['group.KarlStaff', 'group.KarlKitchenStaff',
                               'group.community.FugaziFanClub']))
        adapter = self._make_one()
        adapter.update(profile)

        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.email, 'user2@example.com')
        self.assertEqual(profile.phone, '212-555-1212')
        self.assertEqual(profile.extension, '123')
        self.assertEqual(profile.department, 'Human Resources')
        self.assertEqual(profile.position,
                         'Responsable Bibliotheque Monique Calixte')
        self.assertEqual(profile.organization, 'Open Society Institute')
        self.assertEqual(profile.location, 'Port-au-Prince')
        self.assertEqual(profile.country, 'HT')
        self.assertEqual(profile.websites, ('http://www.example.com/profile',))
        self.assertEqual(profile.languages, 'Italian, English, Esperanto')
        self.assertEqual(profile.office, 'Fondation Connaissance et Liberte')
        self.assertEqual(profile.room_no, '1234')
        self.assertEqual(profile.biography,
                         'Was born, grew up, is still alive.')
        self.assertEqual(profile.home_path, 'offices/national-foundation')
        self.assertEqual(profile.categories['entities'], [
            'open-society-institute',
            'hardees',
            ])
        self.assertEqual(profile.categories['offices'], [
            'fondation-connaissance-et-liberte',
            'hand-creme',
            ])
        self.assertEqual(profile.categories['departments'], [
            'information-retrieval',
            'paper-chase',
            ])
        self.assertEqual(profile.categories['boards'], [
            '1-x-3',
            ])

        self.assertEqual(self.root.users.get_by_id('crossi'), {
            'id': 'crossi',
            'login': 'crossi',
            'password': 'crossi',
            'groups': set(['group.KarlStaff', 'group.AnotherGroup',
                           'group.community.FugaziFanClub']),
            })

    def test_update_empty_profile(self):
        profile = testing.DummyModel(security_state='active')
        self.profiles['crossi'] = profile
        self.root.users.add('crossi', 'crossi', 'crossi',
                          set(['group.KarlStaff', 'group.KarlKitchenStaff',
                               'group.community.FugaziFanClub']))
        adapter = self._make_one('test_profile-empty_website.xml')
        adapter.update(profile)

        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.email, 'user2@example.com')
        self.assertEqual(profile.sso_id, 'user2@com.example')
        self.assertEqual(profile.phone, '212-555-1212')
        self.assertEqual(profile.extension, '123')
        self.assertEqual(profile.department, 'Human Resources')
        self.assertEqual(profile.position,
                         'Responsable Bibliotheque Monique Calixte')
        self.assertEqual(profile.organization, 'Open Society Institute')
        self.assertEqual(profile.location, 'Port-au-Prince')
        self.assertEqual(profile.country, 'HT')
        self.assertEqual(profile.websites, ())
        self.assertEqual(profile.languages, 'Italian, English, Esperanto')
        self.assertEqual(profile.office, 'Fondation Connaissance et Liberte')
        self.assertEqual(profile.room_no, '1234')
        self.assertEqual(profile.biography,
                         'Was born, grew up, is still alive.')
        self.assertEqual(profile.home_path, 'offices/national-foundation')
        self.assertEqual(profile.categories['entities'], [
            'open-society-institute',
            'hardees',
            ])
        self.assertEqual(profile.categories['offices'], [
            'fondation-connaissance-et-liberte',
            'hand-creme',
            ])
        self.assertEqual(profile.categories['departments'], [
            'information-retrieval',
            'paper-chase',
            ])
        self.assertEqual(profile.categories['boards'], [
            '1-x-3',
            ])

        self.assertEqual(self.root.users.get_by_id('crossi'), {
            'id': 'crossi',
            'login': 'crossi',
            'password': 'crossi',
            'groups': set(['group.KarlStaff', 'group.AnotherGroup',
                           'group.community.FugaziFanClub']),
            })

    def test_create(self):
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        registerContentFactory(testing.DummyModel, Interface)
        adapter = self._make_one()
        adapter.create(self.profiles)

        self.failUnless('crossi' in self.profiles.keys())
        profile = self.profiles['crossi']

        self.assertEqual(profile.__name__, 'crossi')
        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.email, 'user2@example.com')
        self.assertEqual(profile.phone, '212-555-1212')
        self.assertEqual(profile.extension, '123')
        self.assertEqual(profile.department, 'Human Resources')
        self.assertEqual(profile.position,
                         'Responsable Bibliotheque Monique Calixte')
        self.assertEqual(profile.organization, 'Open Society Institute')
        self.assertEqual(profile.location, 'Port-au-Prince')
        self.assertEqual(profile.country, 'HT')
        self.assertEqual(profile.websites, ('http://www.example.com/profile',))
        self.assertEqual(profile.languages, 'Italian, English, Esperanto')
        self.assertEqual(profile.office, 'Fondation Connaissance et Liberte')
        self.assertEqual(profile.room_no, '1234')
        self.assertEqual(profile.biography,
                         'Was born, grew up, is still alive.')
        self.assertEqual(profile.home_path, 'offices/national-foundation')
        self.assertEqual(profile.categories['entities'], [
            'open-society-institute',
            'hardees',
            ])
        self.assertEqual(profile.categories['offices'], [
            'fondation-connaissance-et-liberte',
            'hand-creme',
            ])
        self.assertEqual(profile.categories['departments'], [
            'information-retrieval',
            'paper-chase',
            ])
        self.assertEqual(profile.categories['boards'], [
            '1-x-3',
            ])

        info = self.root.users.get_by_id('crossi')
        info.pop('password')
        self.assertEqual(info, {
            'id': 'crossi',
            'login': 'crossi',
            'groups': set(['group.KarlStaff', 'group.AnotherGroup']),
            })

    def test_empty_profile(self):
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        registerContentFactory(testing.DummyModel, Interface)
        adapter = self._make_one('test_profile2.xml')
        adapter.create(self.profiles)

        self.failUnless('crossi' in self.profiles)
        profile = self.profiles['crossi']
        self.assertEqual(profile.__name__, 'crossi')
        user = self.root.users.get_by_id('crossi')
        self.assertEqual(user['groups'], set([]))

    def test_update_remove_categories(self):
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        def factory(**kw):
            kw['security_state'] = 'active'
            return testing.DummyModel(**kw)
        registerContentFactory(factory, Interface)
        adapter = self._make_one()
        adapter.create(self.profiles)
        profile = self.profiles['crossi']
        self.failUnless(profile.categories['entities'])
        self.failUnless(profile.categories['offices'])
        self.failUnless(profile.categories['departments'])
        self.failUnless(profile.categories['boards'])

        adapter = self._make_one('test_profile2.xml')
        adapter.update(profile)
        self.assertEqual(profile.categories, {})


class PeopleCategoryImporterTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _target_class(self):
        from osi.sync.gsa_sync import PeopleCategoryImporter
        return PeopleCategoryImporter

    def _make_one(self, fname='test_category.xml'):
        import os
        import sys
        import lxml.etree
        here = os.path.dirname(sys.modules[__name__].__file__)
        with open(os.path.join(here, 'xml', fname)) as stream:
            doc = lxml.etree.parse(stream)
        return self._target_class()(doc.getroot())

    def test_update(self):
        from karl.models.peopledirectory import PeopleCategoryItem
        item = PeopleCategoryItem('Temporary Title')
        self._make_one().update(item)

        self.assertEqual(item.title, 'Fondation Connaissance et Liberte')
        self.assertEqual(item.description,
                         '113 Huse St, Beverly Hills, CA 90210')

    def test_create(self):
        context = testing.DummyModel()
        self._make_one('test_category2.xml').create(context)

        self.failUnless('offices' in context)
        offices = context['offices']
        self.failUnless('category-2' in offices)
        item = offices['category-2']
        self.assertEqual(item.title, 'Category 2')
        self.failUnless('<h:div>Port-au-Prince, HT 90210</h:div>' in
                        item.description)
        self.assertEqual(item.sync_id, '1062')

    def test_empty_category(self):
        context = testing.DummyModel()
        self._make_one('test_category3.xml').create(context)
        office = context['offices']['category-3']
        self.assertEqual(office.sync_id, '1062')
        self.assertEqual(office.title, 'Category 3')

class DummyUrllib2(object):
    filename = 'gsa_data.xml'
    errors = 0
    HTTPError = urllib2.HTTPError

    def urlopen(self, url, data=None, timeout=None):
        if self.errors > 0:
            import urllib2
            self.errors -= 1
            raise urllib2.HTTPError(url, 500, 'Server Error', [], None)
        self.data = data
        self.timeout = timeout

        import sys
        import os
        here = os.path.dirname(sys.modules[__name__].__file__)
        f = open(os.path.join(here, self.filename))
        return DummyHttpConnection(f)

class DummyHttpConnection(object):

    def __init__(self, f, headers=None):
        self.f = f
        if headers is None:
            headers = {
                'Date': 'Wed, 14 Oct 2009 20:50:01 GMT',
                }
        self.headers = headers

    def read(self, size=None):
        return self.f.read(size)

    def info(self):
        return self

    def getheader(self, name):
        return self.headers[name]

class DummyWorkflow:
    def __init__(self):
        self.transitioned = []

    def transition_to_state(self, content, request, to_state, context=None,
                            guards=(), skip_same=True):
        content.security_state = to_state
        self.transitioned.append({'to_state':to_state, 'content':content,
                                  'request':request, 'guards':guards,
                                  'context':context, 'skip_same':skip_same})
