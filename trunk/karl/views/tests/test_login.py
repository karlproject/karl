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

class TestLoginView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.login import login_view
        return login_view(context, request)

    def test_endswith_login_html(self):
        request = testing.DummyRequest({'came_from':'/login.html'})
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from, '/')
        self.assertEqual(renderer.app_url, 'http://example.com')
        
    def test_not_endswith_login_htmnl(self):
        request = testing.DummyRequest({'came_from':'/somewhere.html'})
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.came_from, '/somewhere.html')
        self.assertEqual(renderer.app_url, 'http://example.com')

    def test_forgets_when_auth_tkt_not_None(self):
        request = testing.DummyRequest({'came_from':'/somewhere.html'})
        plugin = DummyAuthenticationPlugin()
        request.environ['repoze.who.plugins'] = {'auth_tkt':plugin}
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/login.pt')
        response = self._callFUT(context, request)
        self.assertEqual(dict(response.headers),
                         dict([('Content-Type', 'text/html; charset=UTF-8'),
                              ('Content-Length', '0'), ('a', '1')]))

_marker = object()

class TestLogoutView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, reason=_marker):
        from karl.views.login import logout_view
        if reason is not _marker:
            return logout_view(context, request, reason)
        return logout_view(context, request)

    def test_w_default_reason(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')
        headers = dict(response.headers)
        self.assertEqual(headers['X-Authorization-Failure-Reason'],
                         'Logged out')

    def test_w_explicit_reason(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        response = self._callFUT(context, request, reason='testing')
        self.assertEqual(response.status, '401 Unauthorized')
        headers = dict(response.headers)
        self.assertEqual(headers['X-Authorization-Failure-Reason'], 'testing')
        
class DummyAuthenticationPlugin(object):
    def forget(self, environ, identity):
        return [('a', '1')]
    
