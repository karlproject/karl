import unittest

from karl import testing

class Test_adduser(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        self.root = root = testing.DummyModel()
        root.users = testing.DummyUsers()
        root['profiles'] = testing.DummyModel()

        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        registerContentFactory(testing.DummyProfile, IProfile)

        from repoze.workflow.testing import registerDummyWorkflow
        self.wf = registerDummyWorkflow('security')

    def tearDown(self):
        testing.cleanUp()

    def fut(self):
        from karl.scripts.adduser import adduser
        return adduser

    def test_add_user(self):
        root = self.root
        users = root.users
        self.fut()(root, 'chris', 'secret')
        self.assertEqual(users.get_by_id('chris'), {
            'id': 'chris',
            'login': 'chris',
            'password': 'secret',
            'groups': ['group.KarlAdmin']
        })

        profile = root['profiles']['chris']
        self.assertEqual(profile.firstname, 'System')
        self.assertEqual(profile.lastname, 'User')
        self.assertEqual(self.wf.initialized, [profile])

    def test_add_existing_user(self):
        root = self.root
        root.users.add('chris', 'chris', 'password', [])
        self.assertRaises(ValueError, self.fut(), root, 'chris', 'secret')

    def test_add_existing_profile(self):
        root = self.root
        root['profiles']['chris'] = testing.DummyProfile()
        self.assertRaises(ValueError, self.fut(), root, 'chris', 'secret')
