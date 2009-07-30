import unittest

class TestAddNoCacheHeaders(unittest.TestCase):
    def _callFUT(self, event):
        from karl.handlers import add_no_cache_headers
        return add_no_cache_headers(event)

    def test_it_no_header(self):
        headers = []
        response = DummyResponse(headers)
        event = DummyEvent(response)
        self._callFUT(event)
        self.assertEqual(
            headers,
            [('Cache-Control','max-age=0, must-revalidate, no-cache, no-store')]
        )

    def test_it_with_header(self):
        headers = [('Cache-Control', 'abc')]
        response = DummyResponse(headers)
        event = DummyEvent(response)
        self._callFUT(event)
        self.assertEqual(headers, [('Cache-Control', 'abc')])

class DummyEvent:
    def __init__(self, response):
        self.response = response

class DummyResponse:
    def __init__(self, headerlist):
        self.headerlist = headerlist
        
