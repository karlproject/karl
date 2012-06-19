import mock
import unittest
from pyramid import testing


class TestErrorPage(unittest.TestCase):
    error = Exception("General Error")
    response = None

    def setUp(self):
        testing.cleanUp()
        self.config = testing.setUp()

    def tearDown(self):
        testing.cleanUp()

    def call_fut(self, context):
        from karl.errorpage import errorpage as fut
        request = testing.DummyRequest(referer='joe mama')
        request.layout_manager = mock.Mock()
        request.registry.settings['system_name'] = 'KARL System'
        return fut(context, request)

    def test_general_error(self):
        response = self.call_fut(Exception("You're doing it wrong!"))
        self.assertEqual(response['error_message'], 'General Error')

    def test_readonly_error(self):
        from ZODB.POSException import ReadOnlyError
        response = self.call_fut(ReadOnlyError())
        self.assertEqual(response['error_message'], 'Site is in Read Only Mode')
        response = self.call_fut(ReadOnlyError)
        self.assertEqual(response['error_message'], 'Site is in Read Only Mode')

    def test_http_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        response = self.call_fut(HTTPNotFound())
        self.assertEqual(response['error_message'], 'Not Found')
        response = self.call_fut(HTTPNotFound)
        self.assertEqual(response['error_message'], 'Not Found')

    def test_not_found(self):
        from pyramid.exceptions import NotFound
        response = self.call_fut(NotFound())
        self.assertEqual(response['error_message'], 'Not Found')
        response = self.call_fut(NotFound)
        self.assertEqual(response['error_message'], 'Not Found')
