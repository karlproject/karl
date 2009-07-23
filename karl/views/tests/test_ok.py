import unittest
from repoze.bfg import testing

class TestOKView(unittest.TestCase):
    def _callFUT(self, context, request):
        from karl.views.ok import ok
        return ok(context, request)

    def test_it(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.body, 'OK')
        self.assertEqual(response.status, '200 OK')
        
    
