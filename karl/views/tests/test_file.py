import unittest

from cStringIO import StringIO

from zope.interface import implements
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

from karl.models.tests.test_image import one_pixel_jpeg
from karl.models.interfaces import IImageFile

class TestServeFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.file import serve_file_view
        return serve_file_view(context, request)

    def test_it(self):
        context = DummyImageFile()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.headerlist[0],
                         ('Content-Type', 'image/jpeg'))
        self.assertEquals(response.headerlist[1],
                          ('Content-Length', str(context.size)))
        
        response_body = ''.join(response.app_iter)
        self.assertEqual(response_body, context.data)

class DummyImageFile(object):
    implements(IImageFile)

    extension = "jpg"
    def __init__(self, stream=None, mimetype="image/jpeg"):
        self.mimetype = mimetype
        if stream is not None:
            self.data = stream.read()
        else:
            self.data = one_pixel_jpeg
        self.size = len(self.data)
        
    @property
    def stream(self):
        return StringIO(self.data)
    
    def upload(self, stream):
        self.data = stream.read()