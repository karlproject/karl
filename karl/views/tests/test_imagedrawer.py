import unittest
from repoze.bfg import testing

from zope.testing.cleanup import cleanUp

class Test_breadcrumbs(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _call_fut(self, obj, request):
        from karl.views.imagedrawer import breadcrumbs
        return breadcrumbs(obj, request)

    def test_no_community(self):
        request = testing.DummyRequest()
        root = testing.DummyModel(title='Root')
        foo = root['foo'] = testing.DummyModel(title='Foo')
        bar = foo['bar'] = testing.DummyModel(title='Bar')
        self.assertEqual(self._call_fut(bar, request), [
            {'title': 'Root', 'href': 'http://example.com/'},
            {'title': 'Foo', 'href': 'http://example.com/foo/'},
            {'title': 'Bar', 'href': 'http://example.com/foo/bar/'}
        ])

    def test_community(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        request = testing.DummyRequest()
        root = testing.DummyModel(title='Root')
        foo = root['foo'] = testing.DummyModel(title='Foo')
        directlyProvides(foo, ICommunity)
        bar = foo['bar'] = testing.DummyModel(title='Bar')
        self.assertEqual(self._call_fut(bar, request), [
            {'title': 'Foo', 'href': 'http://example.com/foo/'},
            {'title': 'Bar', 'href': 'http://example.com/foo/bar/'}
        ])

class Test_get_image_info(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        import datetime
        from karl.models.interfaces import ICommunity
        from karl.content.interfaces import IImage
        from karl.views.imagedrawer import get_image_info
        from zope.interface import directlyProvides
        request = testing.DummyRequest()
        root = testing.DummyModel()
        profiles = root['profiles'] = testing.DummyModel()
        chris = profiles['chris'] = testing.DummyModel(title='Chris Rossi')
        community = root['community'] = testing.DummyModel(title='FooBar')
        directlyProvides(community, ICommunity)
        image = community['foo.jpg'] = testing.DummyModel()
        image.creator = 'chris'
        image.title = 'Foo'
        image.image_size = (69, 42)
        image.size = 1234
        image.modified = datetime.datetime(2010, 3, 23, 15, 13, 23)
        directlyProvides(image, IImage)

        info = get_image_info(image, request)
        self.assertEqual(info['name'], 'foo.jpg')
        self.assertEqual(info['title'], 'Foo')
        self.assertEqual(info['author_name'], 'Chris Rossi')
        self.assertEqual(
            info['image_url'],
            'http://example.com/community/foo.jpg/thumb/400x400.jpg'
        )
        self.assertEqual(
            info['thumbnail_url'],
            'http://example.com/community/foo.jpg/thumb/85x85.jpg'
        )
        self.assertEqual(info['image_width'], 69)
        self.assertEqual(info['image_height'], 42)
        self.assertEqual(info['image_size'], 1234)
        self.assertEqual(info['last_modified'], image.modified.ctime())
        self.assertEqual(info['location'], [
            {'title': 'FooBar',
             'href': 'http://example.com/community/'},
            {'title': 'Foo',
             'href': 'http://example.com/community/foo.jpg/'},
        ])

class Test_batch_images(unittest.TestCase):
    def setUp(self):
        cleanUp()

        batch = [
            testing.DummyModel(title='A'),
            testing.DummyModel(title='B'),
        ]

        class DummyBatcher(object):
            def __call__(self, context, request, creator, community,
                    batch_start, batch_size):
                self.called = (context, request, creator, community,
                    batch_start, batch_size)
                return dict(entries=batch,
                    batch_start=batch_start,
                    batch_size=batch_size,
                    total=5)

        self.batcher = DummyBatcher()

        def dummy_get_info(image, request):
            return dict(title=image.title)

        self.make_record = dummy_get_info

    def tearDown(self):
        cleanUp()

    def _call_fut(self, context, request):
        from karl.views.imagedrawer import batch_images
        return batch_images(context, request, self.make_record, self.batcher)

    def test_global_search(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(batch['records'][0]['title'], 'A')
        self.assertEqual(batch['records'][1]['title'], 'B')
        self.assertEqual(batch['start'], 0)
        self.assertEqual(batch['totalRecords'], 5)
        self.assertEqual(self.batcher.called, (context, request, None, None, 0, 12))

    def test_search_by_creator(self):
        request = testing.DummyRequest(params={'creator': 'chris'})
        context = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(
            self.batcher.called, (context, request, 'chris', None, 0, 12)
        )

    def test_search_by_community(self):
        root = testing.DummyModel()
        community = root['foo'] = testing.DummyModel()
        request = testing.DummyRequest(params={'community': '/foo'})
        context = community['bar'] = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(
            self.batcher.called, (context, request, None, community, 0, 12)
        )

class Test_drawer_dialog_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def dummy_batcher(self, context, request):
        return ['foo', 'bar']

    def _call_fut(self, context, request):
        from karl.views.imagedrawer import drawer_dialog_view
        return drawer_dialog_view(context, request, self.dummy_batcher)

    def test_it(self):
        import simplejson
        renderer = testing.registerDummyRenderer(
            'templates/imagedrawer_dialog_snippet.pt'
        )
        renderer.string_response = 'template body'
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['dialog_snippet'], 'template body')
        self.assertEqual(data['images_info'], ['foo', 'bar'])

class Test_drawer_data_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def dummy_batcher(self, context, request):
        return ['foo', 'bar']

    def _call_fut(self, context, request):
        from karl.views.imagedrawer import drawer_data_view
        return drawer_data_view(context, request, self.dummy_batcher)

    def test_it(self):
        import simplejson
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], ['foo', 'bar'])

class Test_drawer_upload_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(testing.DummyModel, ICommunityFile)

        from zope.interface import Interface
        from repoze.workflow.testing import registerDummyWorkflow
        self.workflow = DummyWorkflow()
        registerDummyWorkflow('security', self.workflow, Interface)

    def dummy_batcher(self, context, request):
        return ['foo', 'bar']

    def dummy_make_record(self, context, request):
        return dict(title='Foo')

    def dummy_check_upload_size(*args):
        pass

    def tearDown(self):
        cleanUp()

    def _make_context(self):
        context = testing.DummyModel()
        context.get_attachments = lambda: context
        return context

    def _call_fut(self, context, request):
        from karl.views.imagedrawer import drawer_upload_view
        return drawer_upload_view(
            context, request,
            self.dummy_check_upload_size,
            self.dummy_make_record,
            self.dummy_batcher
        )

    def test_upload_ok(self):
        import simplejson
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload()
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['upload_image_info'], {'title': 'Foo'})
        self.assertEqual(data['images_info'], ['foo', 'bar'])

        image = context['test.jpg']
        self.assertEqual(image.title, 'test.jpg')
        self.assertEqual(image.stream.getvalue(), 'TESTDATA')
        self.assertEqual(image.mimetype, 'image/jpeg')
        self.assertEqual(image.filename, 'test.jpg')
        self.assertEqual(image.creator, 'chris')
        self.assertEqual(self.workflow.initialized, [image,])

    def test_upload_tempfolder(self):
        import simplejson
        testing.registerDummySecurityPolicy('chris')
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload()
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['upload_image_info'], {'title': 'Foo'})
        self.assertEqual(data['images_info'], ['foo', 'bar'])

        image = context['TEMP'].values()[0]
        self.assertEqual(image.title, 'test.jpg')
        self.assertEqual(image.stream.getvalue(), 'TESTDATA')
        self.assertEqual(image.mimetype, 'image/jpeg')
        self.assertEqual(image.filename, 'test.jpg')
        self.assertEqual(image.creator, 'chris')
        self.assertEqual(self.workflow.initialized, [image,])

    def test_no_upload(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': testing.DummyModel(),
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
                         u'You must select a file before clicking Upload.')
        self.failUnless(transaction.isDoomed())

    def test_bad_upload(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': testing.DummyModel(
                    filename='', file=None, type=None
                ),
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'], u'The filename must not be empty')
        self.failUnless(transaction.isDoomed())

    def test_duplicate_filename(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        context['test.jpg'] = testing.DummyModel()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
                         u'Filename test.jpg already exists in this folder')
        self.failUnless(transaction.isDoomed())

    def test_no_permission(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris', permissive=False)
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
                         u'You do not have permission to upload files here.')
        self.failUnless(transaction.isDoomed())

class DummyUpload(object):
    filename = 'test.jpg'
    type = 'image/jpeg'

    @property
    def file(self):
        from cStringIO import StringIO
        return StringIO('TESTDATA')

class DummyWorkflow(object):
    def __init__(self):
        self.initialized = []

    def initialize(self, doc):
        self.initialized.append(doc)
