import unittest
from pyramid.request import Request
from pyramid import testing


class TestErrorPage(unittest.TestCase):
    error = Exception("General Error")
    response = None

    def setUp(self):
        testing.cleanUp()
        self.config = testing.setUp()

    def tearDown(self):
        testing.cleanUp()

    def make_one(self):
        def application(environ, start_response):
            if self.response:
                return self.response(environ, start_response)
            raise self.error

        from karl.errorpage import ErrorPageFilter
        return ErrorPageFilter(application, None, 'static', 'home')

    def test_general_error(self):
        renderer = self.config.testing_add_renderer(
            'karl.views:templates/wsgi_errormsg.pt')
        request = Request.blank('/')
        request.get_response(self.make_one())
        self.assertEqual(renderer.error_message, 'General Error')

    def test_general_error_w_template(self):
        request = Request.blank('/')
        response = request.get_response(self.make_one())
        self.assertTrue('General Error' in response.body)

    def test_general_error_w_template_and_unicode(self):
        self.error = Exception(u'Happy\xa0Times'.encode('utf8'))
        request = Request.blank('/')
        response = request.get_response(self.make_one())
        self.assertTrue('General Error' in response.body)

    def test_readonly_error(self):
        from ZODB.POSException import ReadOnlyError
        self.error = ReadOnlyError()
        renderer = self.config.testing_add_renderer(
            'karl.views:templates/wsgi_errormsg.pt')
        request = Request.blank('/')
        request.get_response(self.make_one())
        self.assertEqual(renderer.error_message, 'Site is in Read Only Mode')

    def test_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        self.response = HTTPNotFound()
        renderer = self.config.testing_add_renderer(
            'karl.views:templates/wsgi_errormsg.pt')
        request = Request.blank('/')
        request.get_response(self.make_one())
        self.assertEqual(renderer.error_message, 'Not Found')

    def test_500_response(self):
        from pyramid.httpexceptions import HTTPServerError
        self.response = HTTPServerError()
        renderer = self.config.testing_add_renderer(
            'karl.views:templates/wsgi_errormsg.pt')
        request = Request.blank('/')
        request.get_response(self.make_one())
        self.assertEqual(renderer.error_message, 'General Error')


