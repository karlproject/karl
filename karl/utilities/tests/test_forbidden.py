import unittest
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

class TestForbidden(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.utilities.forbidden import Forbidden
        return Forbidden

    def _makeOne(self):
        return self._getTargetClass()()

    def test_call_with_r_who_identity_in_environ(self):
        from webob import Request
        environ = Request.blank('/').environ
        environ['repoze.who.identity'] = '1'
        attrs = {'context':testing.DummyModel(), 'view_name':''}
        environ['webob.adhoc_attrs'] = attrs
        utility = self._makeOne()
        renderer = testing.registerDummyRenderer('templates/forbidden.pt')
        start_response = DummyStartResponse()
        body = utility(environ, start_response)
        self.assertEqual(start_response.status, '403 Forbidden')
        self.assertEqual(renderer.homepage_url, 'http://localhost/')

    def test_redirected_from_login_form(self):
        from webob import Request
        environ = Request.blank('/').environ
        attrs = {'context':testing.DummyModel(), 'view_name':''}
        environ['webob.adhoc_attrs'] = attrs
        environ['HTTP_REFERER'] = '/login.html'
        utility = self._makeOne()
        start_response = DummyStartResponse()
        body = utility(environ, start_response)
        self.assertEqual(start_response.status, '302 Found')
        location = start_response.headers[0][1]
        self.assertEqual(location, 
                         'http://localhost/login.html'
                         '?reason=Bad+username+or+password'
                         '&came_from=http%3A%2F%2Flocalhost%2F')

    def test_plain_old_no_credentials_homepage(self):
        from webob import Request
        environ = Request.blank('/').environ
        attrs = {'context':testing.DummyModel(), 'view_name':''}
        environ['webob.adhoc_attrs'] = attrs
        utility = self._makeOne()
        start_response = DummyStartResponse()
        body = utility(environ, start_response)
        self.assertEqual(start_response.status, '302 Found')
        location = start_response.headers[0][1]
        self.assertEqual(location,
                         'http://localhost/login.html?'
                         'came_from=http%3A%2F%2Flocalhost%2F')
                                                   
    def test_plain_old_no_credentials_nonhomepage(self):
        from webob import Request
        environ = Request.blank('/elsewhere').environ
        attrs = {'context':testing.DummyModel(), 'view_name':''}
        environ['webob.adhoc_attrs'] = attrs
        utility = self._makeOne()
        start_response = DummyStartResponse()
        body = utility(environ, start_response)
        self.assertEqual(start_response.status, '302 Found')
        location = start_response.headers[0][1]
        self.assertEqual(location,
                         'http://localhost/login.html?'
                         'reason=Not+logged+in&'
                         'came_from=http%3A%2F%2Flocalhost%2Felsewhere')

class DummyStartResponse:
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers
        
        
