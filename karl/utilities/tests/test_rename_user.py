import unittest

from zope.testing.cleanup import cleanUp
from repoze.bfg import testing
import karl.testing as karltesting

class Test_rename_user(unittest.TestCase):
    def setUp(self):
        cleanUp()

        self.root = root = karltesting.DummyModel()
        root['profiles'] = profiles = karltesting.DummyModel()
        root.users = karltesting.DummyUsers()

        root['a'] = a = karltesting.DummyModel(creator='chris')
        root['b'] = b = karltesting.DummyModel(modified_by='chris')

        class DummySearchAdapter(object):
            def __init__(self, context):
                pass

            def __call__(self, **kw):
                resolver = lambda x: root.get(x)
                if kw.get('creator') == 'chris':
                    return 1, ['a'], resolver
                if kw.get('modified_by') == 'chris':
                    return 1, ['b'], resolver
                return 0, [], resolver

        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummySearchAdapter, (Interface, Interface),
                                ICatalogSearch)
        testing.registerAdapter(DummySearchAdapter, (Interface,),
                                ICatalogSearch)

        root.catalog = catalog = karltesting.DummyModel()
        catalog['creator'] =  DummyCatalogIndex()
        catalog['modified_by'] =  DummyCatalogIndex()

    def tearDown(self):
        cleanUp()

    def call_fut(self, old_name, new_name, merge=False, out=None):
        from karl.utilities.rename_user import rename_user as fut
        return fut(self.root, old_name, new_name, merge, out)

    def test_old_profile_does_not_exist(self):
        self.root.users.add('chris', 'chris', 'password', set())
        self.assertRaises(ValueError, self.call_fut, 'chris', 'rodrigo')

    def test_new_user_already_exists(self):
        self.root.users.add('chris', 'chris', 'password', set())
        self.root['profiles']['chris'] = karltesting.DummyProfile()
        self.root.users.add('rodrigo', 'rodrigo', 'password', set())
        self.assertRaises(ValueError, self.call_fut, 'chris', 'rodrigo')

    def test_new_profile_already_exists(self):
        self.root.users.add('chris', 'chris', 'password', set())
        self.root['profiles']['chris'] = karltesting.DummyProfile()
        self.root['profiles']['rodrigo'] = karltesting.DummyProfile()
        self.assertRaises(ValueError, self.call_fut, 'chris', 'rodrigo')

    def test_merge_new_user_does_not_exist(self):
        self.root.users.add('chris', 'chris', 'password', set())
        self.root['profiles']['chris'] = karltesting.DummyProfile()
        self.assertRaises(ValueError, self.call_fut, 'chris', 'rodrigo',
                          merge=True)

    def test_merge_new_profile_does_not_exist(self):
        self.root.users.add('chris', 'chris', 'password', set())
        self.root['profiles']['chris'] = karltesting.DummyProfile()
        self.root.users.add('rodrigo', 'rodrigo', 'password', set())
        self.assertRaises(ValueError, self.call_fut, 'chris', 'rodrigo',
                          merge=True)

    def test_rename_user(self):
        users = self.root.users
        profiles = self.root['profiles']
        users.add('chris', 'chris', 'password', set(('group1', 'group2')))
        profiles['chris'] = karltesting.DummyProfile()

        self.call_fut('chris', 'rodrigo')
        self.failIf('chris' in profiles)
        self.failUnless('rodrigo' in profiles)
        self.assertEqual(users.removed_users, ['chris'])
        self.assertEqual(users.get_by_id('rodrigo'),
                         {'id': 'rodrigo', 'login': 'rodrigo',
                           'password': 'password', 'groups':
                           set(('group1', 'group2'))})

        catalog = self.root.catalog
        self.assertEqual(catalog['creator'].reindexed, [('a', 'a')])
        self.assertEqual(catalog['modified_by'].reindexed, [('b', 'b')])

    def test_rename_old_user_does_not_exist(self):
        users = self.root.users
        profiles = self.root['profiles']
        profiles['chris'] = karltesting.DummyProfile()

        self.call_fut('chris', 'rodrigo', out=DummyOutputStream())
        self.failIf('chris' in profiles)
        self.failUnless('rodrigo' in profiles)
        self.assertEqual(users.get_by_id('rodrigo'), None)

        catalog = self.root.catalog
        self.assertEqual(catalog['creator'].reindexed, [('a', 'a')])
        self.assertEqual(catalog['modified_by'].reindexed, [('b', 'b')])

    def test_merge_user(self):
        users = self.root.users
        profiles = self.root['profiles']
        users.add('chris', 'chris', 'password', set(('group1', 'group2')))
        profiles['chris'] = karltesting.DummyProfile()
        users.add('rodrigo', 'rodrigo', 'password', set(('group3',)))
        profiles['rodrigo'] = karltesting.DummyProfile()

        self.call_fut('chris', 'rodrigo', True, DummyOutputStream())
        self.failIf('chris' in profiles)
        self.failUnless('rodrigo' in profiles)
        self.assertEqual(users.removed_users, ['chris'])
        self.assertEqual(users.added_groups,
                         [('rodrigo', 'group1'), ('rodrigo', 'group2')])
        catalog = self.root.catalog
        self.assertEqual(catalog['creator'].reindexed, [('a', 'a')])
        self.assertEqual(catalog['modified_by'].reindexed, [('b', 'b')])

    def test_merge_old_user_does_not_exist(self):
        users = self.root.users
        profiles = self.root['profiles']
        profiles['chris'] = karltesting.DummyProfile()
        profiles['rodrigo'] = karltesting.DummyProfile()

        self.call_fut('chris', 'rodrigo', True, DummyOutputStream())
        self.failIf('chris' in profiles)
        self.failUnless('rodrigo' in profiles)
        catalog = self.root.catalog
        self.assertEqual(catalog['creator'].reindexed, [('a', 'a')])
        self.assertEqual(catalog['modified_by'].reindexed, [('b', 'b')])

class DummyCatalogIndex(object):
    def __init__(self):
        self.reindexed = []

    def reindex_doc(self, docid, doc):
        self.reindexed.append((docid, doc.__name__))

class DummyOutputStream(object):
    def write(self, bytes):
        pass
