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

import mock
import unittest
from zope.interface import directlyProvides
from pyramid import testing
from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry
from karl.testing import DummySessions

import karl.testing

class ResetRequestFormControllerTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        from karl.testing import registerSettings
        registerSettings()
        from karl.models.interfaces import ISite
        site = testing.DummyModel(sessions=DummySessions())
        directlyProvides(site, ISite)
        self.context = site
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        karl.testing.registerDummyRenderer(
            'karl.views:forms/templates/snippets.pt')

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, context, request):
        from karl.views.resetpassword import ResetRequestFormController
        return ResetRequestFormController(context, request)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = controller.form_fields()
        self.assertEqual(len(fields), 1)
        self.assertEqual('email', fields[0][0])

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.assertEqual(len(widgets), 1)
        self.failUnless('email' in widgets)

    def test___call__(self):
        self.request.layout_manager = lm = mock.Mock()
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, u'Forgot Password Request')
        self.failUnless('blurb_macro' in response)
        lm.use_layout.assert_called_once_with('anonymous')
        self.assertEqual(lm.layout.page_title, u'Forgot Password Request')

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        context = self.context
        request = self.request

        # fake the mailer
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        mailer = DummyMailer()
        karl.testing.registerUtility(mailer, IMailDelivery)

        # fake catalog search
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        karl.testing.registerAdapter(
            DummyProfileSearch, (Interface,), ICatalogSearch)

        # fake a staff user
        from karl.testing import DummyUsers
        context.users = DummyUsers()
        context.users.add('me', 'me', 'password', ['group.KarlStaff'])

        # register dummy renderer for email template
        reg = get_current_registry()
        config = Configurator(reg, autocommit=True)
        renderer = config.testing_add_template(
            'templates/email_reset_password.pt')

        # test w/ staff user
        controller = self._makeOne(context, request)
        converted = {'email': 'me@example.com'}
        response = controller.handle_submit(converted)
        self.failIf(len(mailer))
        self.assertEqual(response.location,
            'http://login.example.com/resetpassword?email=me%40example.com'
            '&came_from=http%3A%2F%2Fexample.com%2Flogin.html')

        # register dummy profile search
        profile_search = DummyProfileSearch(context)
        def search_adapter(context):
            return profile_search
        karl.testing.registerAdapter(
            search_adapter, (Interface,), ICatalogSearch)

        # convert to non-staff user and test again, email should
        # go out this time
        context.users._by_id['me']['groups'] = []
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
            'http://example.com/reset_sent.html?email=me%40example.com')
        profile = profile_search.profile
        self.failUnless(profile.password_reset_key)
        self.failUnless(profile.password_reset_time)
        self.assertEqual(len(mailer), 1)
        msg = mailer.pop()
        self.assertEqual(len(msg.mto), 1)
        self.assertEqual(msg.mto[0], 'me@example.com')
        self.assertEqual(dict(msg.msg._headers)['Subject'],
                         'karl3test Password Reset Request')
        renderer.assert_(login='me', system_name='karl3test')
        self.failUnless(hasattr(renderer, 'reset_url'))
        self.failUnless(renderer.reset_url.startswith(
            'http://example.com/reset_confirm.html?key='), renderer.reset_url)


class ResetSentViewTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.resetpassword import reset_sent_view
        return reset_sent_view(context, request)

    def test_it(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'email': 'x@example.com'})
        renderer = karl.testing.registerDummyRenderer(
            'templates/reset_sent.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.email, 'x@example.com')


class ResetConfirmFormControllerTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        from karl.models.interfaces import ISite
        site = testing.DummyModel(sessions=DummySessions())
        directlyProvides(site, ISite)
        self.context = site
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        karl.testing.registerDummyRenderer(
            'karl.views:forms/templates/snippets.pt')

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, context, request):
        from karl.views.resetpassword import ResetConfirmFormController
        return ResetConfirmFormController(context, request)

    def _setupUsers(self):
        from karl.testing import DummyUsers
        self.context.users = DummyUsers()
        self.context.users.add('me', 'me', 'password', [])

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.assertEqual(len(fields), 2)
        self.failUnless('login' in fields)
        self.failUnless('password' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.assertEqual(len(widgets), 2)
        self.failUnless('login' in widgets)
        self.failUnless('password' in widgets)

    def test___call__bad_key(self):
        # register dummy renderer for the email template
        reg = get_current_registry()
        config = Configurator(reg)
        renderer = config.testing_add_template('templates/reset_failed.pt')

        request = self.request
        request.layout_manager = mock.Mock()
        # no key
        controller = self._makeOne(self.context, request)
        response = controller()
        from pyramid.response import Response
        self.assertEqual(response.__class__, Response)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset URL Problem')

        # reset renderer.api value so we know the test is useful
        renderer = config.testing_add_template('templates/reset_failed.pt')
        # key of wrong length
        request.params['key'] = 'foofoofoo'
        controller = self._makeOne(self.context, request)
        response = controller()
        from pyramid.response import Response
        self.assertEqual(response.__class__, Response)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset URL Problem')

    def test___call__(self):
        request = self.request
        request.layout_manager = mock.Mock()
        request.params['key'] = '0' * 40
        controller = self._makeOne(self.context, request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, u'Reset Password')
        self.failUnless('blurb_macro' in response)
        self.failUnless(response['blurb_macro'])

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit_bad_key(self):
        reg = get_current_registry()
        config = Configurator(reg)
        renderer = config.testing_add_template('templates/reset_failed.pt')
        request = self.request
        request.params['key'] = 'foofoofoo'
        controller = self._makeOne(self.context, request)
        controller.handle_submit({})
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset URL Problem')

    def test_handle_submit_bad_login(self):
        request = self.request
        request.params['key'] = '0' * 40
        self._setupUsers()
        controller = self._makeOne(self.context, request)
        converted = {'login': 'bogus'}
        from pyramid_formish import ValidationError
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        try:
            response = controller.handle_submit(converted)
        except ValidationError, e:
            self.assertEqual(e.errors['login'], 'No such user account exists')

    def test_handle_submit_no_profile(self):
        request = self.request
        request.params['key'] = '0' * 40
        self._setupUsers()
        self.context['profiles'] = testing.DummyModel()
        controller = self._makeOne(self.context, request)
        converted = {'login': 'me'}
        from pyramid_formish import ValidationError
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        try:
            response = controller.handle_submit(converted)
        except ValidationError, e:
            self.assertEqual(e.errors['login'], 'No such profile exists')

    def test_handle_submit_wrong_key(self):
        reg = get_current_registry()
        config = Configurator(reg)
        renderer = config.testing_add_template('templates/reset_failed.pt')
        request = self.request
        request.params['key'] = '0' * 40
        self._setupUsers()
        context = self.context
        context['profiles'] = testing.DummyModel()
        context['profiles']['me'] = testing.DummyModel()
        controller = self._makeOne(context, request)
        converted = {'login': 'me'}
        # first w/ no profile reset key
        response = controller.handle_submit(converted)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset Confirmation Problem')

        # now w/ wrong profile reset key
        renderer = config.testing_add_template('templates/reset_failed.pt')
        context['profiles']['me'].password_reset_key = '1' * 40
        response = controller.handle_submit(converted)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset Confirmation Problem')

    def test_handle_submit_key_expired(self):
        reg = get_current_registry()
        config = Configurator(reg)
        renderer = config.testing_add_template('templates/reset_failed.pt')
        request = self.request
        request.params['key'] = '0' * 40
        self._setupUsers()
        context = self.context
        context['profiles'] = testing.DummyModel()
        profile = context['profiles']['me'] = testing.DummyModel()
        profile.password_reset_key = '0' * 40
        controller = self._makeOne(context, request)
        converted = {'login': 'me'}
        # first w/ no profile reset time
        response = controller.handle_submit(converted)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset Confirmation Key Expired')

        # now w/ expired key
        renderer = config.testing_add_template('templates/reset_failed.pt')
        from karl.views.resetpassword import max_reset_timedelta
        import datetime
        keytime = datetime.datetime.now() - max_reset_timedelta
        profile.password_reset_time = keytime
        response = controller.handle_submit(converted)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset Confirmation Key Expired')

    def test_handle_submit(self):
        reg = get_current_registry()
        config = Configurator(reg)
        renderer = config.testing_add_template('templates/reset_complete.pt')
        request = self.request
        request.params['key'] = '0' * 40
        self._setupUsers()
        context = self.context
        context['profiles'] = testing.DummyModel()
        profile = context['profiles']['me'] = testing.DummyModel()
        profile.password_reset_key = '0' * 40
        controller = self._makeOne(context, request)
        converted = {'login': 'me', 'password': 'secret'}
        import datetime
        keytime = datetime.datetime.now()
        profile.password_reset_time = keytime
        response = controller.handle_submit(converted)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset Complete')
        renderer.assert_(login='me', password='secret')
        self.failUnless(profile.password_reset_key is None)
        self.failUnless(profile.password_reset_time is None)
        user = self.context.users.get(login='me')
        from repoze.who.plugins.zodb.users import get_sha_password
        self.assertEqual(user['password'], get_sha_password('secret'))

    def test_handle_submit_utf8_password(self):
        password = u'password\xe1'
        reg = get_current_registry()
        config = Configurator(reg)
        renderer = config.testing_add_template('templates/reset_complete.pt')
        request = self.request
        request.params['key'] = '0' * 40
        self._setupUsers()
        context = self.context
        context['profiles'] = testing.DummyModel()
        profile = context['profiles']['me'] = testing.DummyModel()
        profile.password_reset_key = '0' * 40
        controller = self._makeOne(context, request)
        converted = {'login': 'me', 'password': password}
        import datetime
        keytime = datetime.datetime.now()
        profile.password_reset_time = keytime
        response = controller.handle_submit(converted)
        self.failUnless(hasattr(renderer, 'api'))
        self.assertEqual(renderer.api.page_title,
                         'Password Reset Complete')
        renderer.assert_(login='me', password=password)
        self.failUnless(profile.password_reset_key is None)
        self.failUnless(profile.password_reset_time is None)
        user = self.context.users.get(login='me')
        from repoze.who.plugins.zodb.users import get_sha_password
        self.assertEqual(user['password'], get_sha_password(password.encode('utf8')))


class DummyProfileSearch:
    def __init__(self, context):
        self.context = context
    def __call__(self, interfaces, email):
        address = email[0]
        return 1, [address], self.resolve
    def resolve(self, docid):
        from karl.testing import DummyProfile
        res = DummyProfile(__name__=docid.split('@')[0], email=docid)
        self.profile = res
        self.context[res.__name__] = res
        return res
