import mock
import unittest
from pyramid import testing

import karl.testing

class TestForbidden(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.forbidden import forbidden
        return forbidden(context, request)

    def test_call_with_authenticated_user(self):
        karl.testing.registerDummySecurityPolicy('user')
        request = testing.DummyRequest()
        request.layout_manager = mock.Mock()
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        renderer = karl.testing.registerDummyRenderer('templates/forbidden.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(renderer.homepage_url, 'http://example.com/')
        self.assertEqual(renderer.login_form_url,
                         'http://example.com/login.html')

    def test_redirected_from_login_form(self):
        context = testing.DummyModel()
        environ = {}
        environ['HTTP_REFERER'] = '/login.html'
        request = testing.DummyRequest(environ=environ)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        location = response.headerlist[2][1]
        self.assertEqual(location,
                         'http://example.com/login.html'
                         '?reason=Bad+username+or+password'
                         '&came_from=http%3A%2F%2Fexample.com')

    def test_plain_old_no_credentials_from_homepage(self):
        context = testing.DummyModel()
        environ = {}
        request = testing.DummyRequest(environ=environ)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        location = response.headerlist[2][1]
        self.assertEqual(location,
                         'http://example.com/login.html?'
                         'came_from=http%3A%2F%2Fexample.com')

    def test_plain_old_no_credentials_from_nonhomepage(self):
        context = testing.DummyModel()
        environ = {}
        request = testing.DummyRequest(environ=environ)
        request.url = 'http://example.com/elsewhere'
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        location = response.headerlist[2][1]
        self.assertEqual(location,
                         'http://example.com/login.html?'
                         'reason=Not+logged+in&'
                         'came_from=http%3A%2F%2Fexample.com%2Felsewhere')

