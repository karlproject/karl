import unittest
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

class TestForbidden(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.forbidden import forbidden
        return forbidden(context, request)

    def test_call_with_r_who_identity_in_environ(self):
        environ = {}
        environ['repoze.who.identity'] = '1'
        request = testing.DummyRequest(environ=environ)
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/forbidden.pt')
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

