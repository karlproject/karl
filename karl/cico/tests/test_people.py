from __future__ import with_statement

import unittest
from zope.testing.cleanup import cleanUp
from repoze.bfg import testing


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
        from karl.cico.people import UserProfileImporter
        return UserProfileImporter

    def _make_one(self, fname='test_profile.xml'):
        import os
        import sys
        import lxml.etree
        here = os.path.dirname(sys.modules[__name__].__file__)
        with open(os.path.join(here, 'xml', fname)) as stream:
            doc = lxml.etree.parse(stream)
        return self._target_class()(doc.getroot())

    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.cico.interfaces import IContentIn
        self.failUnless(verifyClass(IContentIn, self._target_class()))

    def test_object_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.cico.interfaces import IContentIn
        self.failUnless(verifyObject(IContentIn, self._make_one()))

    def test_update(self):
        profile = testing.DummyModel()
        self.profiles['crossi'] = profile
        self.root.users.add('crossi', 'crossi', 'crossi',
                          set(['group.KarlStaff', 'group.KarlKitchenStaff']))
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
        self.assertEqual(profile.website, 'http://karl.example.com/profile')
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

        self.assertEqual(self.root.users.get_by_id('crossi'), {
            'id': 'crossi',
            'login': 'crossi',
            'password': 'password',
            'groups': set(['group.KarlStaff', 'group.AnotherGroup']),
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
        self.assertEqual(profile.website, 'http://karl.example.com/profile')
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

        self.assertEqual(self.root.users.get_by_id('crossi'), {
            'id': 'crossi',
            'login': 'crossi',
            'password': 'password',
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
        self.assertEqual(user['password'], 'password')
        self.assertEqual(user['groups'], set([]))


class PeopleCategoryImporterTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _target_class(self):
        from karl.cico.people import PeopleCategoryImporter
        return PeopleCategoryImporter

    def _make_one(self, fname='test_category.xml'):
        import os
        import sys
        import lxml.etree
        here = os.path.dirname(sys.modules[__name__].__file__)
        with open(os.path.join(here, 'xml', fname)) as stream:
            doc = lxml.etree.parse(stream)
        return self._target_class()(doc.getroot())

    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.cico.interfaces import IContentIn
        self.failUnless(verifyClass(IContentIn, self._target_class()))

    def test_object_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.cico.interfaces import IContentIn
        self.failUnless(verifyObject(IContentIn, self._make_one()))

    def test_update(self):
        from karl.peopledir.models.category import PeopleCategoryItem
        item = PeopleCategoryItem('Temporary Title', sync_id='1062')
        self._make_one().update(item)

        self.assertEqual(item.title, 'Fondation Connaissance et Liberte')
        self.assertEqual(item.description,
                         '113 Huse St, Beverly Hills, CA 90210')
        self.assertEqual(item.sync_id, '1062')

    def test_create(self):
        context = {}
        self._make_one().create(context)

        self.failUnless('offices' in context)
        offices = context['offices']
        self.failUnless('fondation-connaissance-et-liberte' in offices)
        item = offices['fondation-connaissance-et-liberte']
        self.assertEqual(item.title, 'Fondation Connaissance et Liberte')
        self.assertEqual(item.description,
                         '113 Huse St, Beverly Hills, CA 90210')
        self.assertEqual(item.sync_id, '1062')

    def test_empty_category(self):
        context = {}
        self._make_one('test_category3.xml').create(context)
        office = context['offices']['category-3']
        self.assertEqual(office.sync_id, '1062')
        self.assertEqual(office.title, 'Category 3')
