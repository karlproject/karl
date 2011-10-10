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
from pyramid import testing

import karl.testing

class TestLoginView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.login import login_view
        return login_view(context, request)

    def test_GET_came_from_endswith_login_html_relative(self):
        request = testing.DummyRequest({'came_from':'/login.html'})
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from, 'http://example.com/')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_GET_came_from_endswith_login_html_absolute(self):
        request = testing.DummyRequest({'came_from':
                                            'http://example.com/login.html'})
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from, 'http://example.com/')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_GET_came_from_endswith_logout_html_relative(self):
        request = testing.DummyRequest({'came_from':'/logout.html'})
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from, 'http://example.com/')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_GET_came_from_endswith_logout_html_absolute(self):
        request = testing.DummyRequest({'came_from':
                                            'http://example.com/logout.html'})
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from, 'http://example.com/')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_GET_came_from_other_relative(self):
        request = testing.DummyRequest({'came_from':'/somewhere.html'})
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from,
                         'http://example.com/somewhere.html')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_GET_came_from_other_absolute(self):
        request = testing.DummyRequest({'came_from':
                                         'http://example.com/somewhere.html'})
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from,
                         'http://example.com/somewhere.html')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_GET_forget_headers_when_auth_tkt_not_None(self):
        request = testing.DummyRequest({'came_from':'/somewhere.html'})
        plugin = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'auth_tkt':plugin}
        context = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(dict(response.headers),
                         dict([('Content-Type', 'text/html; charset=UTF-8'),
                              ('Content-Length', '0'), ('a', '1')]))
        self.assertEqual(plugin._forget_called,
                         (request.environ, {}))

    def test_POST_no_login_in_form(self):
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['password'] = 'password'
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/login.html')

    def test_POST_no_password_in_form(self):
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/login.html')

    def test_POST_no_authentication_plugins(self):
        from pyramid.httpexceptions import HTTPFound
        from urlparse import urlsplit
        try:
            from urlparse import parse_qsl
        except ImportError: # Python < 2.6
            from cgi import parse_qsl
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        (_, _, path, query, _) = urlsplit(response.location)
        self.assertEqual(path, '/login.html')
        query = dict(parse_qsl(query, 1, 1))
        self.assertEqual(query['came_from'], 'http://example.com')
        self.assertEqual(query['reason'], 'No authenticatable users')

    def test_POST_w_plugins_miss(self):
        from pyramid.httpexceptions import HTTPFound
        from urlparse import urlsplit
        try:
            from urlparse import parse_qsl
        except ImportError: # Python < 2.6
            from cgi import parse_qsl
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        zodb = DummyAuthenticationPlugin()
        #zodb._userid = 'zodb'
        impostor = DummyAuthenticationPlugin()
        #impostor._userid = 'impostor'
        request.environ['repoze.who.plugins'] = {'zodb': zodb,
                                                 'zodb_impersonate': impostor,
                                                }
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        (_, _, path, query, _) = urlsplit(response.location)
        self.assertEqual(path, '/login.html')
        query = dict(parse_qsl(query, 1, 1))
        self.assertEqual(query['came_from'], 'http://example.com')
        self.assertEqual(query['reason'], 'Bad username or password')
        self.assertEqual(zodb._auth_called,
                         (request.environ,
                          {'login': 'login', 'password': 'password'}))
        self.assertEqual(impostor._auth_called,
                         (request.environ,
                          {'login': 'login', 'password': 'password'}))

    def test_POST_w_plugins_zodb_hit_no_came_from_w_profile(self):
        from datetime import datetime
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        zodb = DummyAuthenticationPlugin()
        zodb._userid = 'zodb'
        impostor = DummyAuthenticationPlugin()
        #impostor._userid = 'impostor'
        auth_tkt = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'zodb': zodb,
                                                 'zodb_impersonate': impostor,
                                                 'auth_tkt': auth_tkt,
                                                }
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        profile = context['profiles']['zodb'] = testing.DummyModel()
        before = datetime.utcnow()
        response = self._callFUT(context, request)
        after = datetime.utcnow()
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com')
        self.assertEqual(zodb._auth_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                          'repoze.who.userid': 'zodb'}))
        self.assertEqual(impostor._auth_called, None)
        self.assertEqual(auth_tkt._auth_called, None)
        self.assertEqual(auth_tkt._remember_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'repoze.who.userid': 'zodb'}))
        headers = dict(response.headers)
        self.assertEqual(headers['Faux-Header'], 'Faux-Value')
        self.failUnless(before <= profile.last_login_time <= after)

    def test_POST_w_plugins_impostor_hit_w_came_from_no_profile(self):
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        request.POST['came_from'] = '/somewhere.html'
        zodb = DummyAuthenticationPlugin()
        #zodb._userid = 'zodb'
        impostor = DummyAuthenticationPlugin()
        impostor._userid = 'impostor'
        auth_tkt = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'zodb': zodb,
                                                 'zodb_impersonate': impostor,
                                                 'auth_tkt': auth_tkt,
                                                }
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                         'http://example.com/somewhere.html')
        self.assertEqual(zodb._auth_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                          'repoze.who.userid': 'impostor'}))
        self.assertEqual(impostor._auth_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                          'repoze.who.userid': 'impostor'}))
        self.assertEqual(auth_tkt._auth_called, None)
        self.assertEqual(auth_tkt._remember_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'repoze.who.userid': 'impostor'}))
        headers = dict(response.headers)
        self.assertEqual(headers['Faux-Header'], 'Faux-Value')

    def test_POST_w_zodb_hit_w_max_age(self):
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        request.POST['max_age'] = '100'
        zodb = DummyAuthenticationPlugin()
        zodb._userid = 'zodb'
        impostor = DummyAuthenticationPlugin()
        #impostor._userid = 'impostor'
        auth_tkt = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'zodb': zodb,
                                                 'zodb_impersonate': impostor,
                                                 'auth_tkt': auth_tkt,
                                                }
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com')
        self.assertEqual(zodb._auth_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'max_age': 100,
                           'repoze.who.userid': 'zodb'}))
        self.assertEqual(impostor._auth_called, None)
        self.assertEqual(auth_tkt._auth_called, None)
        self.assertEqual(auth_tkt._remember_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'max_age': 100,
                           'repoze.who.userid': 'zodb'}))
        headers = dict(response.headers)
        self.assertEqual(headers['Faux-Header'], 'Faux-Value')

    def test_POST_w_zodb_hit_w_max_age_unicode(self):
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        request.POST['max_age'] = u'100'
        zodb = DummyAuthenticationPlugin()
        zodb._userid = 'zodb'
        impostor = DummyAuthenticationPlugin()
        #impostor._userid = 'impostor'
        auth_tkt = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'zodb': zodb,
                                                 'zodb_impersonate': impostor,
                                                 'auth_tkt': auth_tkt,
                                                }
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com')
        self.assertEqual(zodb._auth_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'max_age': 100,
                           'repoze.who.userid': 'zodb'}))
        self.assertEqual(impostor._auth_called, None)
        self.assertEqual(auth_tkt._auth_called, None)
        self.assertEqual(auth_tkt._remember_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'max_age': 100,
                           'repoze.who.userid': 'zodb'}))
        headers = dict(response.headers)
        self.assertEqual(headers['Faux-Header'], 'Faux-Value')

    def test_POST_w_zodb_hit_w_max_age_no_auth_tkt_plugin(self):
        from pyramid.httpexceptions import HTTPFound
        request = testing.DummyRequest()
        request.POST['form.submitted'] = 1
        request.POST['login'] = 'login'
        request.POST['password'] = 'password'
        request.POST['max_age'] = '100'
        zodb = DummyAuthenticationPlugin()
        zodb._userid = 'zodb'
        impostor = DummyAuthenticationPlugin()
        #impostor._userid = 'impostor'
        request.environ['repoze.who.plugins'] = {'zodb': zodb,
                                                 'zodb_impersonate': impostor,
                                                }
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com')
        self.assertEqual(zodb._auth_called,
                         (request.environ,
                          {'login': 'login',
                           'password': 'password',
                           'max_age': 100,
                           'repoze.who.userid': 'zodb'}))
        self.assertEqual(impostor._auth_called, None)
        headers = dict(response.headers)
        self.failIf('Faux-Header' in headers)

_marker = object()

class TestLogoutView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request, reason=_marker):
        from karl.views.login import logout_view
        if reason is not _marker:
            return logout_view(context, request, reason)
        return logout_view(context, request)

    def test_w_default_reason(self):
        request = testing.DummyRequest()
        plugin = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'auth_tkt':plugin}
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        headers = dict(response.headers)
        self.assertEqual(
            headers['Location'],
            'http://example.com/login.html?reason=Logged+out'
            '&came_from=http%3A%2F%2Fexample.com%2F')
        self.assertEqual(plugin._forget_called,
                         (request.environ, {}))

    def test_w_explicit_reason(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        response = self._callFUT(context, request, reason='testing')
        self.assertEqual(response.status, '302 Found')
        headers = dict(response.headers)
        self.assertEqual(
            headers['Location'],
            'http://example.com/login.html?reason=testing'
            '&came_from=http%3A%2F%2Fexample.com%2F')


class DummyAuthenticationPlugin(object):
    _auth_called = _remember_called = _forget_called = _userid = None

    def authenticate(self, environ, credentials):
        self._auth_called = (environ, credentials)
        return self._userid

    def remember(self, environ, credentials):
        self._remember_called = (environ, credentials)
        return [('Faux-Header', 'Faux-Value')]

    def forget(self, environ, identity):
        self._forget_called = (environ, identity)
        return [('a', '1')]
