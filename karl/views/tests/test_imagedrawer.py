import unittest
from pyramid import testing

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
            '/community/foo.jpg/thumb/800x800.jpg'
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
                    batch_start, batch_size, sort_index=None, reverse=False):
                self.called = (context, request, creator, community,
                    batch_start, batch_size, sort_index, reverse)
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
        request = testing.DummyRequest(params={'source': 'allkarl'})
        context = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(batch['records'][0]['title'], 'A')
        self.assertEqual(batch['records'][1]['title'], 'B')
        self.assertEqual(batch['start'], 0)
        self.assertEqual(batch['totalRecords'], 5)
        self.assertEqual(
            self.batcher.called,
            (context, request, None, None, 0, 12, None, False)
        )

    def test_global_search_reverse(self):
        request = testing.DummyRequest(
            params={'source': 'allkarl', 'reverse': 1})
        context = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(batch['records'][0]['title'], 'A')
        self.assertEqual(batch['records'][1]['title'], 'B')
        self.assertEqual(batch['start'], 0)
        self.assertEqual(batch['totalRecords'], 5)
        self.assertEqual(
            self.batcher.called,
            (context, request, None, None, 0, 12, None, True)
        )

    def test_global_search_w_sort_index(self):
        request = testing.DummyRequest(
            params={'source': 'allkarl', 'sort_on': 'foobar'})
        context = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(batch['records'][0]['title'], 'A')
        self.assertEqual(batch['records'][1]['title'], 'B')
        self.assertEqual(batch['start'], 0)
        self.assertEqual(batch['totalRecords'], 5)
        self.assertEqual(
            self.batcher.called,
            (context, request, None, None, 0, 12, 'foobar', False)
        )

    def test_search_by_creator(self):
        testing.registerDummySecurityPolicy('admin')
        request = testing.DummyRequest(params={'source': 'myrecent'}) # My Recent
        context = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(
            # XXX the test are run as admin, so this is what we search for
            self.batcher.called,
            (context, request, 'admin', None, 0, 12, None, False)
        )

    def test_search_by_community(self):
        root = testing.DummyModel()
        community = root['foo'] = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(community, ICommunity)
        request = testing.DummyRequest(params={'source': 'thiscommunity'})  # This Community
        context = community['bar'] = testing.DummyModel()
        batch = self._call_fut(context, request)
        self.assertEqual(
            self.batcher.called,
            (context, request, None, '/foo', 0, 12, None, False)
        )

    def test_search_bad_sources(self):
        """Test that the non-image sources are rejected."""
        root = testing.DummyModel()
        community = root['foo'] = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(community, ICommunity)
        #
        # External source is not accepted:
        request = testing.DummyRequest(params={'source': 'external'})
        context = community['bar'] = testing.DummyModel()
        self.assertRaises(AssertionError,
            self._call_fut, context, request)
        #
        # Upload source is not accepted:
        request = testing.DummyRequest(params={'source': 'uploadnew'})
        context = community['bar'] = testing.DummyModel()
        self.assertRaises(AssertionError,
            self._call_fut, context, request)



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
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['dialog_snippet'][:123],
            u'<div>\n\n  <div class="ui-widget-header ui-corner-all ui-helper-clearfix tiny-imagedrawer-panel tiny-imagedrawer-panel-top">\n'
        )
        # the default source has no image
        self.assert_('images_info' not in data)

    def test_download_tabs(self):
        import simplejson
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params={
                'source': 'myrecent',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['dialog_snippet'][:123],
            u'<div>\n\n  <div class="ui-widget-header ui-corner-all ui-helper-clearfix tiny-imagedrawer-panel tiny-imagedrawer-panel-top">\n'
        )
        # download tabs have images_info included
        self.assertEqual(data['images_info'], ['foo', 'bar'])

        request = testing.DummyRequest(
            params={
                'source': 'thiscommunity',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['dialog_snippet'][:123],
            u'<div>\n\n  <div class="ui-widget-header ui-corner-all ui-helper-clearfix tiny-imagedrawer-panel tiny-imagedrawer-panel-top">\n'
        )
        # download tabs have images_info included
        self.assertEqual(data['images_info'], ['foo', 'bar'])

        request = testing.DummyRequest(
            params={
                'source': 'allkarl',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['dialog_snippet'][:123],
            u'<div>\n\n  <div class="ui-widget-header ui-corner-all ui-helper-clearfix tiny-imagedrawer-panel tiny-imagedrawer-panel-top">\n'
        )
        # download tabs have images_info included
        self.assertEqual(data['images_info'], ['foo', 'bar'])

class Test_drawer_data_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

        batch = [
            testing.DummyModel(title='foo'),
            testing.DummyModel(title='bar'),
        ]

        class DummyGetImagesBatch(object):
            def __call__(self, context, request, **search_params):
                self.called = (context, request, search_params)
                return dict(
                    entries = batch,
                    batch_start = search_params['batch_start'],
                    batch_size = search_params['batch_size'],
                    total = 5)
        self.dummy_get_images_batch = DummyGetImagesBatch()

        def dummy_get_images_info(image, request):
            return image.title
        self.dummy_get_images_info = dummy_get_images_info

        from karl.views.imagedrawer import batch_images
        def wrapped_batch_images(*arg, **kw):
            kw['get_image_info'] = self.dummy_get_images_info
            kw['get_images_batch'] = self.dummy_get_images_batch
            return batch_images(*arg, **kw)

        self.dummy_batch_images = wrapped_batch_images


    def tearDown(self):
        cleanUp()

    def _call_fut(self, context, request):
        from karl.views.imagedrawer import drawer_data_view
        return drawer_data_view(context, request, self.dummy_batch_images)

    def test_it(self):
        import simplejson
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params={
                'source': 'myrecent',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 0,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 5,
            'start': 0,
            'records': ['foo', 'bar'],
            })

        # ask a batch from the 1st (or nth) image
        request = testing.DummyRequest(
            params={
                'source': 'myrecent',
                'start': '1',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 1,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 5,
            'start': 1,
            'records': ['foo', 'bar'], # no problem... just bad faking
            })

    def test_including_replace_image(self):
        ## if we are replacing, the passed-in image url
        ## is added as a fake 1th element.
        import simplejson
        from karl.content.interfaces import IImage
        from zope.interface import directlyProvides
        context = testing.DummyModel()
        image = context['boo.jpg'] = testing.DummyModel()
        image.title = 'Boo'
        directlyProvides(image, IImage)

        request = testing.DummyRequest(
            params={
                'include_image_url': '/boo.jpg',
                'source': 'myrecent',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 0,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 6,
            'start': 0,
            'records': ['Boo', 'foo', 'bar'],
            })

        # if we don't ask for the 0th index: it's not
        # added, but the sizes and indexes are aligned.
        request = testing.DummyRequest(
            params={
                'include_image_url': '/boo.jpg',
                'source': 'myrecent',
                'start': '1',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 0,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 6,
            'start': 1,
            'records': ['foo', 'bar'],
            })

    def test_including_replace_image_urlview(self):
        import simplejson
        from karl.content.interfaces import IImage
        from zope.interface import directlyProvides
        context = testing.DummyModel()
        image = context['boo.jpg'] = testing.DummyModel()
        image.title = 'Boo'
        directlyProvides(image, IImage)

        # It is expected for the url path to continue beyond
        # the context object. (thumbnail, or a specific view)
        request = testing.DummyRequest(
            params={
                'include_image_url': '/boo.jpg/what/ever',
                'source': 'myrecent',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 0,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 6,
            'start': 0,
            'records': ['Boo', 'foo', 'bar'],
            })

    def test_including_replace_image_fulldomain(self):
        import simplejson
        from karl.content.interfaces import IImage
        from zope.interface import directlyProvides
        context = testing.DummyModel()
        image = context['boo.jpg'] = testing.DummyModel()
        image.title = 'Boo'
        directlyProvides(image, IImage)

        # It must also work, when the image url is
        # a full domain. This happens on IE.
        # XXX The server should _not_ check the domain
        # at all, simply use the path.

        # XXX For a reason unknown, this test passes even
        # if the traverse the full domain instead of just the
        # path... while, the same thing fails in "real life" on IE.
        # So, this test probably does not test what it should...
        request = testing.DummyRequest(
            params={
                'include_image_url': 'http://lcd.tv:9876/boo.jpg/thumb',
                'source': 'myrecent',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 0,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 6,
            'start': 0,
            'records': ['Boo', 'foo', 'bar'],
            })

    def test_including_replace_image_fail(self):
        import simplejson
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params={
                'include_image_url': '/badimage',
                'source': 'myrecent',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.dummy_get_images_batch.called,
            (context, request, {
                'community': None,
                'batch_start': 0,
                'batch_size': 12,
                'creator': None
                }))
        data = simplejson.loads(response.body)
        self.assertEqual(data['images_info'], {
            'totalRecords': 5,
            'start': 0,
            'records': ['foo', 'bar'],
            })

class Test_drawer_upload_view(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICommunityFile
        from karl.content.models.files import CommunityFile
        registerContentFactory(CommunityFile, ICommunityFile)

        from zope.interface import Interface
        from repoze.workflow.testing import registerDummyWorkflow
        self.workflow = DummyWorkflow()
        registerDummyWorkflow('security', self.workflow, Interface)

    def dummy_batcher(self, context, request):
        return ['foo', 'bar']

    def dummy_make_record(self, context, request, thumb_size=None):
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
                'file': DummyUpload(),
                'title': 'Title',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['upload_image_info'], {'title': 'Foo'})
        self.assert_('images_info' not in data)

        image = context['test.jpg']
        self.assertEqual(image.title, 'Title')
        self.assert_(len(image.image().fp.read()) > 0)
        self.assertEqual(image.mimetype, 'image/jpeg')
        self.assertEqual(image.filename, 'test.jpg')
        self.assertEqual(image.creator, 'chris')
        self.assertEqual(self.workflow.initialized, [image,])

    def test_upload_notitle_ok(self):
        import simplejson
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['upload_image_info'], {'title': 'Foo'})
        self.assert_('images_info' not in data)

        image = context['test.jpg']
        self.assertEqual(image.title, 'test.jpg')
        self.assert_(len(image.image().fp.read()) > 0)
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
                'file': DummyUpload(),
                'title': 'Title',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['upload_image_info'], {'title': 'Foo'})
        self.assert_('images_info' not in data)

        image = context['TEMP'].values()[0]
        self.assertEqual(image.title, 'Title')
        self.assert_(len(image.image().fp.read()) > 0)
        self.assertEqual(image.mimetype, 'image/jpeg')
        self.assertEqual(image.filename, 'test.jpg')
        self.assertEqual(image.creator, 'chris')
        self.failUnless(hasattr(image, 'modified'))
        self.assertEqual(self.workflow.initialized, [])

    def test_no_upload(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': testing.DummyModel(),
                'title': 'Title',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
                         u'You must select a file before clicking Upload.')
        self.failUnless(transaction.isDoomed())

    def test_missing_input(self):
        """Input is missing from the posted form"""
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'title': 'Title',
                },
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
                         u'You must select a file before clicking Upload.')
        self.failUnless(transaction.isDoomed())

    def test_no_filename(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params = {
                'file': DummyUpload(
                    filename = '',
                ),
                'title': 'Title',
            },
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'], u'The filename must not be empty')
        self.failUnless(transaction.isDoomed())

    def test_wrong_mimetype(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params = {
                'file': DummyUpload(
                    type = 'not/animage',
                ),
                'title': 'Title',
            },
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
            u'File test.jpg is not an image')
        self.failUnless(transaction.isDoomed())

    def test_wrong_imagedata(self):
        import simplejson
        import transaction
        testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params = {
                'file': DummyUpload(
                    IMAGE_DATA = 'NOT_AN_IMAGE',
                ),
                'title': 'Title',
            },
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
            u'File test.jpg is not an image')
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
                'title': 'Title',
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
                'title': 'Title',
            }
        )
        response = self._call_fut(context, request)
        self.assertEqual(response.status, '200 OK')
        data = simplejson.loads(response.body)
        self.assertEqual(data['error'],
                         u'You do not have permission to upload files here.')
        self.failUnless(transaction.isDoomed())

# An 1x1px png (should be jpeg, in fact)
import binascii
IMAGE_DATA = binascii.unhexlify(
            '89504e470d0a1a0a0000000d49484452000000010000000108060000001f' +
            '15c4890000000467414d410000b18f0bfc610500000006624b474400ff00' +
            'ff00ffa0bda793000000097048597300000b1200000b1201d2dd7efc0000' +
            '000976704167000000010000000100c7955fed0000000d4944415408d763' +
            'd8b861db7d00072402f7f7d926c80000002574455874646174653a637265' +
            '61746500323031302d30352d31385432303a30343a34322b30323a3030e1' +
            '1f35f60000002574455874646174653a6d6f6469667900323031302d3035' +
            '2d31385432303a30343a34322b30323a303090428d4a0000000049454e44' +
            'ae426082')

class DummyUpload(object):
    filename = 'test.jpg'
    type = 'image/jpeg'
    IMAGE_DATA = IMAGE_DATA

    def __init__(self, **kw):
        self.__dict__.update(kw)

    @property
    def file(self):
        from cStringIO import StringIO
        return StringIO(self.IMAGE_DATA)

class DummyWorkflow(object):
    def __init__(self):
        self.initialized = []

    def initialize(self, doc):
        self.initialized.append(doc)
