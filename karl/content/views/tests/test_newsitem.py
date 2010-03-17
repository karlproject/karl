# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import unittest

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing
from karl.testing import DummySessions

class AddNewsItemFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self._register()
        context = testing.DummyModel(sessions=DummySessions())
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider, 
                                     (Interface, Interface),
                                     ILayoutProvider)

    def _makeOne(self, context, request):
        from karl.content.views.newsitem import AddNewsItemFormController
        return AddNewsItemFormController(context, request)

    def test_form_defaults(self):
        from karl.content.views.newsitem import _now
        prenow = _now()
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        for field, value in defaults.items():
            if field != 'publication_date':
                self.failIf(value)
        self.failUnless(defaults['publication_date'] > prenow)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('text' in fields)
        self.failUnless('attachments' in fields)
        self.failUnless('photo' in fields)
        self.failUnless('caption' in fields)
        self.failUnless('publication_date' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('text' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)
        self.failUnless('photo' in widgets)
        self.failUnless('caption' in widgets)
        self.failUnless('publication_date' in widgets)

    def test____call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Add News Item')
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        site = testing.DummyModel(sessions=DummySessions())
        directlyProvides(site, ISite)
        from karl.testing import DummyCatalog
        from karl.models.adapters import CatalogSearch
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        site.catalog = DummyCatalog()
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        context = self.context
        site['newsfolder'] = context
        tags = DummyTags()
        site.tags = tags
        controller = self._makeOne(context, self.request)
        from karl.content.views.newsitem import _now
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r'C:\My Documents\Ha Ha\test2.txt')
        photo = DummyUpload(filename='test.jpg',
                            mimetype='image/jpeg',
                            data=dummy_photo)
        now = _now()
        converted = {
            'title': 'Foo',
            'text': 'text',
            'publication_date': now,
            'caption': 'caption',
            'tags': ['tag1', 'tag2'],
            'attachments': [attachment1, attachment2],
            'photo': photo
            }
        from karl.content.interfaces import INewsItem
        from karl.models.interfaces import IImageFile
        from karl.content.interfaces import ICommunityFile
        from karl.views.tests.test_file import DummyImageFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyNewsItem, INewsItem)
        registerContentFactory(DummyImageFile, IImageFile)
        registerContentFactory(DummyFile, ICommunityFile)
        response = controller.handle_submit(converted)
        newsitem_url = 'http://example.com/newsfolder/foo/'
        self.assertEqual(response.location, newsitem_url)
        self.failUnless('foo' in context)
        newsitem = context['foo']
        self.assertEqual(newsitem.title, 'Foo')
        self.assertEqual(newsitem.text, 'text')
        self.assertEqual(newsitem.publication_date, now)
        self.assertEqual(newsitem.caption, 'caption')
        self.failUnless('attachments' in newsitem)
        attachments_folder = newsitem['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        self.assertEqual(attachments_folder['test1.txt'].filename,
                         'test1.txt')
        self.assertEqual(attachments_folder['test2.txt'].filename,
                         'test2.txt')
        self.failUnless('photo.jpg' in newsitem)
        self.failUnless(len(newsitem['photo.jpg'].stream.read()) > 0)
        self.assertEqual(site.tags._called_with[1]['tags'],
                         ['tag1', 'tag2'])

class EditNewsItemFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self._register()
        context = DummyNewsItem(sessions=DummySessions())
        context.title = 'Foo'
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider, 
                                     (Interface, Interface),
                                     ILayoutProvider)

    def _makeOne(self, context, request):
        from karl.content.views.newsitem import EditNewsItemFormController
        return EditNewsItemFormController(context, request)

    def test_form_defaults(self):
        context = self.context
        context.text = 'text'
        context.caption = 'caption'
        from karl.content.views.newsitem import _now
        now = _now()
        context.publication_date = now
        attachment1 = DummyFile(mimetype="text/plain")
        attachment2 = DummyFile(mimetype="text/html")
        context['attachments']['test1.txt'] = attachment1
        context['attachments']['test2.html'] = attachment2
        photo = DummyFile(mimetype='image/jpeg')
        context['photo.jpg'] = photo
        controller = self._makeOne(context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'Foo')
        self.assertEqual(defaults['text'], 'text')
        self.assertEqual(defaults['caption'], 'caption')
        self.assertEqual(defaults['publication_date'], now)
        self.assertEqual(len(defaults['attachments']), 2)
        attachnames = [a.filename for a in defaults['attachments']]
        self.failUnless('test1.txt' in attachnames)
        self.failUnless('test2.html' in attachnames)
        self.assertEqual(defaults['photo'].filename, 'photo.jpg')
        self.assertEqual(defaults['photo'].mimetype, 'image/jpeg')

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('text' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)
        self.failUnless('photo' in widgets)
        self.failUnless('caption' in widgets)
        self.failUnless('publication_date' in widgets)

    def test_handle_submit(self):
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        site = testing.DummyModel(sessions=DummySessions())
        directlyProvides(site, ISite)
        from karl.testing import DummyCatalog
        from karl.models.adapters import CatalogSearch
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        site.catalog = DummyCatalog()
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        context = self.context
        site['newsitem'] = context
        tags = DummyTags()
        site.tags = tags
        controller = self._makeOne(context, self.request)
        from karl.content.views.newsitem import _now
        now = _now()
        simple = {
            'title': 'NewFoo',
            'text': 'text',
            'caption': 'caption',
            'publication_date': now
            }
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r'C:\My Documents\Ha Ha\test2.txt')
        photo = DummyUpload(filename='test.jpg',
                            mimetype='image/jpeg',
                            data=dummy_photo)
        converted = {
            'tags': ['tag1', 'tag2'],
            'attachments': [attachment1, attachment2],
            'photo': photo,
            }
        converted.update(simple)
        from karl.models.interfaces import IImageFile
        from karl.content.interfaces import ICommunityFile
        from karl.views.tests.test_file import DummyImageFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyImageFile, IImageFile)
        registerContentFactory(DummyFile, ICommunityFile)
        response = controller.handle_submit(converted)
        msg = "?status_message=News%20Item%20edited"
        self.assertEqual(response.location,
                         'http://example.com/newsitem/%s' % msg)
        for field, value in simple.items():
            self.assertEqual(getattr(context, field), value)
        attachments_folder = context['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        self.assertEqual(attachments_folder['test1.txt'].filename,
                         'test1.txt')
        self.assertEqual(attachments_folder['test2.txt'].filename,
                         'test2.txt')
        self.failUnless('photo.jpg' in context)
        self.assertEqual(site.tags._called_with[1]['tags'],
                         ['tag1', 'tag2'])
        
class DummyNewsItem(testing.DummyModel):
    def __init__(self, *args, **kwargs):
        testing.DummyModel.__init__(self, *args, **kwargs)
        self["attachments"] = testing.DummyModel()
        
    def get_photo(self):
        return self.get("photo.jpg", None)
    
class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyTagQuery(DummyAdapter):
    tagswithcounts = []
    docid = 'ABCDEF01'

class DummyTags:
    def update(self, *args, **kw):
        self._called_with = (args, kw)

class DummyFile:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.size = 0
