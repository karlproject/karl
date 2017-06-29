import unittest

from pyramid import testing
from karl import testing as karltesting

class Test_make_non_staff(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _call_fut(self, profile, inform_moderators=True):
        from osi.utilities.former_staff import make_non_staff as fut
        return fut(profile, inform_moderators)

    def test_it_dont_inform_moderators(self):
        site = karltesting.DummyModel()
        site['fred'] = profile = karltesting.DummyProfile()
        site.users = karltesting.DummyUsers()
        site.users.add('fred', 'fred', 'password', set(
            ('group.community:Test1:members',
             'group.community:Test2:moderators',
             'group.SomeGroup')))

        self._call_fut(profile, False)

        removed = site.users.removed_groups
        self.failIf(('fred', 'group.SomeGroup') in removed)
        self.failUnless(('fred', 'group.community:Test1:members') in removed)
        self.failUnless(('fred', 'group.community:Test2:moderators')
                        in removed)

    def test_it_inform_moderators(self):
        from pyramid.interfaces import ISettings
        karltesting.registerUtility(karltesting.DummySettings(), ISettings)

        site = karltesting.DummyModel()
        site['fred'] = profile = karltesting.DummyProfile()
        profile.title = 'Fred Flintstone'
        profile.email = 'fred@example.com'
        site['clint'] = moderator = karltesting.DummyProfile()
        moderator.title = 'Clint'
        moderator.email = 'clint@example.com'

        site.users = karltesting.DummyUsers()
        site.users.add('fred', 'fred', 'password', set(
            ('group.community:Test1:members',
             'group.community:Test2:members',
             'group.community:Test2:moderators',
             'group.SomeGroup')))
        site.users.add('clint', 'clint', 'password', set(
            ('group.community:Test1:moderators',
             'group.community:Test2:moderators')))

        site['communities'] = communities = karltesting.DummyModel()
        communities['Test1'] = karltesting.DummyModel(title='Test One')
        communities['Test2'] = karltesting.DummyModel(title='Test Two')

        mailer = karltesting.registerDummyMailer()
        renderer = karltesting.registerDummyRenderer(
            'templates/email_notify_former_staff.pt'
        )

        self._call_fut(profile)

        removed = site.users.removed_groups
        self.failIf(('fred', 'group.SomeGroup') in removed)
        self.failUnless(('fred', 'group.community:Test1:members') in removed)
        self.failUnless(('fred', 'group.community:Test2:moderators')
                        in removed)

        self.assertEqual(len(mailer), 1, mailer)
        sent = mailer[0]
        self.assertEqual(sent.mto, ['Clint <clint@example.com>'])
        self.assertEqual(renderer.name, 'Fred Flintstone')
        self.assertEqual(renderer.communities, [
            {'unremove_url': 'http://offline.example.com/app/communities/Test1'
                             '/members/add_existing.html?user_id=fred',
             'title': 'Test One'},
            {'unremove_url': 'http://offline.example.com/app/communities/Test2'
                             '/members/add_existing.html?user_id=fred',
             'title': 'Test Two'}]
        )
