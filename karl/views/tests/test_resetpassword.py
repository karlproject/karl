# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import unittest
from zope.testing.cleanup import cleanUp
from repoze.bfg import testing

class ResetRequestViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        from karl.testing import registerSettings
        registerSettings()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.resetpassword import reset_request_view
        return reset_request_view(context, request)

    def test_not_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/reset_request.pt')
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.submit not in form.formdata)
        self.assertEqual(form.is_valid, None)

    def test_unknown_email(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({
            'form.submitted': True,
            'email': 'bogus@example.com',
            })
        form_renderer = testing.registerDummyRenderer(
            'templates/form_reset_request.pt')
        renderer = testing.registerDummyRenderer(
            'templates/reset_request.pt')
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.submit in form.formdata)
        self.assertEqual(form.is_valid, False)
        self.assertEqual(form_renderer.fielderrors,
            {'email':
             'KARL has no account with the email address: bogus@example.com'}
             )

    def test_karl_staff(self):
        from karl.testing import DummyUsers

        context = testing.DummyModel()
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', ['group.KarlStaff'])

        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        testing.registerAdapter(
            DummyProfileSearch, (Interface,), ICatalogSearch)

        request = testing.DummyRequest({
            'form.submitted': True,
            'email': 'me@example.com',
            })
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://login.example.com/resetpassword?email=me%40example.com'
            '&came_from=http%3A%2F%2Fexample.com%2Flogin.html')

    def test_non_staff(self):
        from karl.testing import DummyUsers

        context = testing.DummyModel()
        context.admin_email = 'admin@example.com'
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', [])

        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        profile_search = DummyProfileSearch(None)
        def search_adapter(context):
            return profile_search
        testing.registerAdapter(search_adapter, (Interface,), ICatalogSearch)

        request = testing.DummyRequest({
            'form.submitted': True,
            'email': 'me@example.com',
            })

        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        mailer = DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        response = self._callFUT(context, request)

        self.assertEqual(response.location,
            'http://example.com/reset_sent.html?email=me%40example.com')
        profile = profile_search.profile
        self.assert_(profile.password_reset_key)
        self.assert_(profile.password_reset_time)
        self.assertEqual(len(mailer), 1)
        msg = mailer.pop()
        self.assertEqual(msg.mto, ['me@example.com'])
        self.assertEqual(msg.mfrom, "admin@example.com")
        
        from base64 import decodestring
        url = ('http://example.com/reset_confirm.html?key=%s' % 
             profile.password_reset_key)
        header, body = msg.msg.split("\n\n", 1)
        body = decodestring(body)
        self.assert_(url in body, "%s not in %s" % (url, body))


class ResetSentViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.resetpassword import reset_sent_view
        return reset_sent_view(context, request)

    def test_it(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'email': 'x@example.com'})
        renderer = testing.registerDummyRenderer(
            'templates/reset_sent.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.email, 'x@example.com')


class ResetConfirmViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        from karl.testing import registerSettings
        registerSettings()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.resetpassword import reset_confirm_view
        return reset_confirm_view(context, request)

    def test_bad_key(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'key': '1' * 39})
        renderer = testing.registerDummyRenderer(
            'templates/reset_failed.pt')
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEqual(renderer.api.page_title, 'Password Reset URL Problem')

    def test_not_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'key': '1' * 40})
        renderer = testing.registerDummyRenderer(
            'templates/reset_confirm.pt')
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.submit not in form.formdata)
        self.assertEqual(form.is_valid, None)

    def test_password_mismatch(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'winwinwin',
            })
        form_renderer = testing.registerDummyRenderer(
            'templates/form_reset_confirm.pt')
        renderer = testing.registerDummyRenderer(
            'templates/reset_confirm.pt')
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.submit in form.formdata)
        self.assertEqual(form.is_valid, False)
        self.assertEqual(form_renderer.fielderrors,
            {'password_confirm': u'Fields do not match'})

    def test_no_such_login(self):
        from karl.testing import DummyUsers
        context = testing.DummyModel()
        context.users = DummyUsers()
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        form_renderer = testing.registerDummyRenderer(
            'templates/form_reset_confirm.pt')
        renderer = testing.registerDummyRenderer(
            'templates/reset_confirm.pt')
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.submit in form.formdata)
        self.assertEqual(form.is_valid, False)
        self.assertEqual(form_renderer.fielderrors,
            {'login': 'No such user account exists'})

    def test_no_such_profile(self):
        from karl.testing import DummyUsers
        context = testing.DummyModel()
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', [])
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        form_renderer = testing.registerDummyRenderer(
            'templates/form_reset_confirm.pt')
        renderer = testing.registerDummyRenderer(
            'templates/reset_confirm.pt')
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.submit in form.formdata)
        self.assertEqual(form.is_valid, False)
        self.assertEqual(form_renderer.fielderrors,
            {'login': 'No such profile exists'})

    def test_reset_with_no_key_set(self):
        from karl.testing import DummyUsers
        context = testing.DummyModel()
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['me'] = testing.DummyModel()
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        renderer = testing.registerDummyRenderer(
            'templates/reset_failed.pt')
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEqual(renderer.api.page_title,
            'Password Reset Confirmation Problem')

    def test_reset_key_mismatch(self):
        from karl.testing import DummyUsers
        context = testing.DummyModel()
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['me'] = testing.DummyModel()
        context['profiles']['me'].password_reset_key = '2' * 40
        import datetime
        context['profiles']['me'].password_reset_time = datetime.datetime.now()
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        renderer = testing.registerDummyRenderer(
            'templates/reset_failed.pt')
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEqual(renderer.api.page_title,
            'Password Reset Confirmation Problem')

    def test_reset_attempt_expired(self):
        from karl.testing import DummyUsers
        context = testing.DummyModel()
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['me'] = testing.DummyModel()
        context['profiles']['me'].password_reset_key = '1' * 40
        import datetime
        context['profiles']['me'].password_reset_time = datetime.datetime(
            1990, 1, 1)
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        renderer = testing.registerDummyRenderer(
            'templates/reset_failed.pt')
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEqual(renderer.api.page_title,
            'Password Reset Confirmation Key Expired')

    def test_reset_success(self):
        from karl.testing import DummyUsers
        context = testing.DummyModel()
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['me'] = testing.DummyModel()
        context['profiles']['me'].password_reset_key = '1' * 40
        import datetime
        context['profiles']['me'].password_reset_time = datetime.datetime.now()
        request = testing.DummyRequest({
            'key': '1' * 40,
            'form.submitted': True,
            'login': 'me',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        renderer = testing.registerDummyRenderer(
            'templates/reset_complete.pt')
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEqual(renderer.api.page_title,
            'Password Reset Complete')
        self.assertEqual(renderer.login, 'me')
        self.assertEqual(renderer.password, 'newnewnew')


class DummyProfileSearch:
    def __init__(self, context):
        pass
    def __call__(self, interfaces, email):
        address = email[0]
        return 1, [address], self.resolve
    def resolve(self, docid):
        from karl.testing import DummyProfile
        res = DummyProfile(__name__=docid.split('@')[0], email=docid)
        self.profile = res
        return res
