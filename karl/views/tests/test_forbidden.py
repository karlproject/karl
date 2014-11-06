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
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        renderer = self._callFUT(context, request)
        self.assertEqual(request.response.status, '200 OK')
        self.assertEqual(renderer['homepage_url'], 'http://example.com/')
        self.assertEqual(renderer['login_form_url'],
                         'http://example.com/login.html')

    def test_plain_old_no_credentials(self):
        context = testing.DummyModel()
        environ = {}
        request = testing.DummyRequest(environ=environ)
        response = self._callFUT(context, request)
        self.assertEqual(request.response.status, '200 OK')
        self.assertEqual(response['login_form_url'],
                         'http://example.com/login.html?reason=Not+logged+in')
        self.assertEqual(request.session['came_from'], 'http://example.com')
