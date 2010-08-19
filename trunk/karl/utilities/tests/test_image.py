import unittest

from repoze.bfg import testing
import karl.testing
from zope.testing.cleanup import cleanUp

class Test_thumb_url(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        from zope.interface import directlyProvides
        from karl.content.interfaces import IImage
        from karl.utilities.image import thumb_url
        context = karl.testing.DummyModel()
        directlyProvides(context, IImage)
        request = testing.DummyRequest()
        url = thumb_url(context, request, (300, 300))
        self.assertEqual(url, 'http://example.com/thumb/300x300.jpg')

class Test_get_images_batch(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _call_fut(self, context, request, **search_params):
        from karl.utilities.image import get_images_batch
        return get_images_batch(context, request, **search_params)

    def test_defaults(self):
        from karl.content.interfaces import IImage
        context = testing.DummyModel()
        request = testing.DummyRequest()
        batcher = DummyBatcher()
        params = dict(batcher=batcher)
        self._call_fut(context, request, **params)

        self.failIf('path' in batcher)
        self.failIf('creator' in batcher)
        self.assertEqual(batcher.context, context)
        self.assertEqual(batcher.request, request)
        self.assertEqual(batcher['interfaces'], [IImage,])
        self.assertEqual(batcher['allowed'], {'query': [], 'operator': 'or'})
        self.assertEqual(batcher['sort_index'], 'creation_date')
        self.assertEqual(batcher['reverse'], True)
        self.assertEqual(batcher['batch_start'], 0)
        self.assertEqual(batcher['batch_size'], 12)

    def test_non_defaults(self):
        from karl.content.interfaces import IImage
        testing.registerDummySecurityPolicy('chris')
        context = testing.DummyModel()
        community = context['community'] = testing.DummyModel()
        request = testing.DummyRequest()
        batcher = DummyBatcher()
        params = dict(
            community=community,
            creator='chris',
            sort_index='foo_index',
            reverse=False,
            batch_start=20,
            batch_size=10,
            batcher=batcher,
        )
        self._call_fut(context, request, **params)

        self.assertEqual(batcher.context, context)
        self.assertEqual(batcher.request, request)
        self.assertEqual(batcher['interfaces'], [IImage,])
        self.assertEqual(
            batcher['allowed'],
            {'query': ['system.Everyone', 'system.Authenticated', 'chris'],
             'operator': 'or'}
        )
        self.assertEqual(batcher['sort_index'], 'foo_index')
        self.assertEqual(batcher['reverse'], False)
        self.assertEqual(batcher['batch_start'], 20)
        self.assertEqual(batcher['batch_size'], 10)
        self.assertEqual(batcher['path'], community)
        self.assertEqual(batcher['creator'], 'chris')

class Test_relocated_temp_images(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _call_fut(self, context, request):
        from karl.utilities.image import relocate_temp_images
        return relocate_temp_images(context, request)

    def test_it(self):
        from zope.interface import directlyProvides
        from karl.content.interfaces import IImage
        root = testing.DummyModel()
        tempfolder = root['TEMP'] = DummyTempFolder()
        image = tempfolder['1234'] = testing.DummyModel(
            filename='kids.png'
        )
        directlyProvides(image, IImage)
        doc = root['doc'] = testing.DummyModel(
            text='Hey, check out this picture of my kids! '
                 '<img alt="My Kids"'
                 '     src="http://example.com/TEMP/1234/thumb/300x300.jpg"'
                 '     width="300" height="200"/>'
                 ' - Doting Father'
                 '<img alt="My Kids"'
                 '     src="http://example.com/TEMP/1234/thumb/300x300.jpg"'
                 '     width="300" height="200"/>'
        )
        doc.get_attachments = lambda: doc

        self._call_fut(doc, testing.DummyRequest())
        self.failIf('1234' in tempfolder)
        self.failUnless('kids.png' in doc)
        self.assertEqual(doc.text,
                'Hey, check out this picture of my kids! '
                '<img alt="My Kids"'
                '     src="http://example.com/doc/kids.png/thumb/300x300.jpg"'
                '     width="300" height="200"/>'
                ' - Doting Father'
                '<img alt="My Kids"'
                '     src="http://example.com/doc/kids.png/thumb/300x300.jpg"'
                '     width="300" height="200"/>')
        self.failUnless(tempfolder.cleanedup)

class DummyTempFolder(testing.DummyModel):
    cleanedup = False

    def cleanup(self):
        self.cleanedup = True

class DummyBatcher(dict):
    def __call__(self, context, request, **search_params):
        self.context = context
        self.request = request
        self.update(search_params)
