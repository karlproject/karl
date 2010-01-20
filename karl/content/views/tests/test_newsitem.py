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

class AddNewsItemViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self._register()

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

    def _callFUT(self, context, request):
        from karl.content.views.newsitem import add_newsitem_view
        return add_newsitem_view(context, request)

    def test_notsubmitted(self):
        context = testing.DummyModel()
        context["attachments"] = testing.DummyModel()
        request = testing.DummyRequest()
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        renderer = testing.registerDummyRenderer(
            'templates/addedit_newsitem.pt')
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        
    def test_submitted_invalid(self):
        context = testing.DummyModel()
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1'})
                    )
        renderer = testing.registerDummyRenderer(
            'templates/addedit_newsitem.pt')
        self._callFUT(context, request)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)
        
    def test_submitted_invalid_notitle(self):
        context = testing.DummyModel()
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1',
                    #'title': '',
                    'text': 'text',})
                    )
        renderer = testing.registerDummyRenderer(
            'templates/addedit_newsitem.pt')
        self._callFUT(context, request)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)
        
    def test_submitted_alreadyexists(self):
        from webob.multidict import MultiDict
        from karl.testing import DummyCatalog
        from karl.content.interfaces import INewsItem
        from repoze.lemonade.testing import registerContentFactory

        registerContentFactory(DummyNewsItem, INewsItem)
        context = testing.DummyModel()
        foo = testing.DummyModel()
        context['foo'] = foo
        tags = DummyTags()
        self.tags = tags
        context.catalog = DummyCatalog()
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('sendalert', 'true'),
                    ('sharing', False),
                    ('photo', None),
                    ('caption', 'caption'),
                    ('publication_date', '3/21/2009 18:30',)
                    ])
            )

        response = self._callFUT(context, request)
        self.assertEqual(response.location, 
                         'http://example.com/foo-1/')

        response = self._callFUT(context, request)
        self.assertEqual(response.location, 
                         'http://example.com/foo-2/')

        response = self._callFUT(context, request)
        self.assertEqual(response.location, 
                         'http://example.com/foo-3/')

    def test_submitted_valid(self):
        context = testing.DummyModel()
        tags = DummyTags()
        self.tags = tags
        from karl.testing import DummyCatalog
        context.catalog = DummyCatalog()
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('photo', None),
                    ('caption', 'caption'),
                    ('publication_date', '3/21/2009 18:30'),
                    ])
            )
        from karl.content.interfaces import INewsItem
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyNewsItem, INewsItem)
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/foo/')
        
    def test_submitted_valid_attachments(self):
        context = testing.DummyModel()
        tags = DummyTags()
        self.tags = tags
        from karl.testing import DummyCatalog
        context.catalog = DummyCatalog()
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename="test2.txt")
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('attachment', attachment1),
                    ('attachment', attachment2),
                    ('sharing', False),
                    ('photo', None),
                    ('caption', 'caption'),
                    ('publication_date', '3/21/2009 18:30'),
                    ])
            )
        from karl.content.interfaces import INewsItem
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyNewsItem, INewsItem)
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(DummyFile, ICommunityFile)

        response = self._callFUT(context, request)
        self.assertEqual(response.location, "http://example.com/foo/")
        self.failUnless(context['foo'])
        
    def test_upload_photo(self):
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        from karl.models.interfaces import IImageFile
        from karl.views.tests.test_file import DummyImageFile
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import INewsItem
        registerContentFactory(DummyNewsItem, INewsItem)
        registerContentFactory(DummyImageFile, IImageFile)
        from webob.multidict import MultiDict
        request = testing.DummyRequest(MultiDict([
            ("form.submitted", "1"),
            ("photo", DummyUpload(
                filename="test.jpg",
                mimetype="image/jpeg",
                data=dummy_photo)),
            ("title", "foo"),
            ("text", "text"),
            ("caption", "caption"),
            ("publication_date", "3/21/2009 18:30",)
            ]
        ))

        from karl.testing import DummyCatalog
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        response = self._callFUT(context, request)
        
        self.assertEqual(context["foo"]["photo.jpg"].stream.read(), 
                         dummy_photo)
        self.assertEqual(response.location, 
                         'http://example.com/foo/')
         
class EditNewsItemViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self._register()

        import datetime
        self.now = datetime.datetime.now()
        self.news_item = DummyNewsItem(
            title="Title",
            text="Some Text",
            publication_date=self.now,
            creator="user1",
            caption=None,
        )
        
        parent = testing.DummyModel()
        parent["foo"] = self.news_item
        
        from karl.testing import DummyCatalog
        parent.catalog = DummyCatalog()
        
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
        
        self.renderer = testing.registerDummyRenderer(
            'templates/addedit_newsitem.pt')

        from repoze.lemonade.testing import registerContentFactory
        from karl.views.tests.test_file import DummyImageFile
        from karl.models.interfaces import IImageFile
        registerContentFactory(DummyImageFile, IImageFile)
        
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(DummyFile, ICommunityFile)
        
    def _callFUT(self, context, request):
        from karl.content.views.newsitem import edit_newsitem_view
        return edit_newsitem_view(context, request)
    
    def test_not_submitted(self):
        request = testing.DummyRequest()
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._callFUT(self.news_item, request)
        self.assertEqual(self.news_item.title, "Title")
        self.assertEqual(self.news_item.text, "Some Text")
        self.assertEqual(self.news_item.publication_date, self.now)
        self.assertEqual(self.news_item.creator, "user1")
        
    def test_submitted_invalid(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            MultiDict([
                ("form.submitted", "1"),
            ])
        )
        self._callFUT(self.news_item, request)
        self.failUnless(self.renderer.fielderrors)
                 
    def test_submitted_valid(self):
        import datetime
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            MultiDict([
                ("form.submitted", "1"),
                ("title", "New Title"),
                ("text", "New Text"),
                ("publication_date", "7/7/1975 7:45"),
                ("photo", None),
                ("caption", None),
                ('tags', 'thetesttag'),
            ])
        )
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(self.news_item, request)
        fielderrors = getattr(self.renderer, "fielderrors", None)
        self.failUnless(fielderrors is None, fielderrors)
        self.assertEqual(response.location, 
            "http://example.com/foo/?status_message=News%20Item%20edited")
        self.assertEqual(self.news_item.title, "New Title")
        self.assertEqual(self.news_item.text, "New Text")
        self.assertEqual(self.news_item.publication_date, 
                         datetime.datetime(1975, 7, 7, 7, 45))
        self.failIf(self.news_item.get_photo())
        self.assertEqual(self.news_item.modified_by, 'testeditor')
        
    def test_upload_photo(self):
        from webob.multidict import MultiDict
        from karl.testing import DummyUpload
        request = testing.DummyRequest(
            MultiDict([
                ("form.submitted", "1"),
                ("title", "New Title"),
                ("text", "New Text"),
                ("publication_date", "7/7/1975 7:45"),
                ("photo", DummyUpload(
                    filename="whatever.jpg",
                    mimetype="image/jpeg",
                    data="This is an image.")),
                ("caption", None),
            ])
        )
        response = self._callFUT(self.news_item, request)
        self.assertEqual(response.location, 
            "http://example.com/foo/?status_message=News%20Item%20edited")
        photo = self.news_item.get_photo()
        self.failIf(photo is None)
        self.assertEqual(photo.stream.read(), "This is an image.")
        
    def test_replace_photo(self):
        from webob.multidict import MultiDict
        from karl.testing import DummyUpload
        from karl.views.tests.test_file import DummyImageFile
        self.news_item["photo.jpg"] = DummyImageFile()
        request = testing.DummyRequest(
            MultiDict([
                ("form.submitted", "1"),
                ("title", "New Title"),
                ("text", "New Text"),
                ("publication_date", "7/7/1975 7:45"),
                ("photo", DummyUpload(
                    filename="whatever.jpg",
                    mimetype="image/jpeg",
                    data="This is another image.")),
                ("caption", None),
            ])
        )
        self.assertNotEqual(self.news_item.get_photo().stream.read(),
                            "This is another image.")
        response = self._callFUT(self.news_item, request)
        self.assertEqual(response.location, 
            "http://example.com/foo/?status_message=News%20Item%20edited")
        photo = self.news_item.get_photo()
        self.failIf(photo is None)
        self.assertEqual(photo.stream.read(), "This is another image.")
        
    def test_delete_photo(self):
        from webob.multidict import MultiDict
        from karl.views.tests.test_file import DummyImageFile
        self.news_item["photo.jpg"] = DummyImageFile()
        request = testing.DummyRequest(
            MultiDict([
                ("form.submitted", "1"),
                ("title", "New Title"),
                ("text", "New Text"),
                ("publication_date", "7/7/1975 7:45"),
                ("photo", None),
                ("photo_delete", "1"),
                ("caption", None),
            ])
        )
        self.failUnless(self.news_item.get_photo())
        response = self._callFUT(self.news_item, request)
        self.assertEqual(response.location, 
            "http://example.com/foo/?status_message=News%20Item%20edited")
        photo = self.news_item.get_photo()
        self.failUnless(photo is None)
    
    def test_upload_attachments(self):
        from webob.multidict import MultiDict
        from karl.testing import DummyUpload
        request = testing.DummyRequest(
            MultiDict([
                ("form.submitted", "1"),
                ("title", "New Title"),
                ("text", "New Text"),
                ("publication_date", "7/7/1975 7:45"),
                ("photo", None),
                ("attachment", DummyUpload(
                    filename="whatever.txt",
                    mimetype="text/plain",
                    data="This is an attachment.")),
                ("attachment", DummyUpload(
                    filename="whatever.pdf",
                    mimetype="application/pdf",
                    data="This is another attachment.")),
                ("caption", None),
            ])
        )
        response = self._callFUT(self.news_item, request)
        self.assertEqual(response.location, 
            "http://example.com/foo/?status_message=News%20Item%20edited")

        attachments = self.news_item["attachments"].values()
        self.assertEqual(len(attachments), 2)
        attachments.sort(key=lambda x: x.filename)
        
        attachment = attachments.pop(0)
        self.assertEqual(attachment.stream.read(), "This is another attachment.")
        self.assertEqual(attachment.filename, "whatever.pdf")
        self.assertEqual(attachment.mimetype, "application/pdf")

        attachment = attachments.pop(0)
        self.assertEqual(attachment.stream.read(), "This is an attachment.")
        self.assertEqual(attachment.filename, "whatever.txt")
        self.assertEqual(attachment.mimetype, "text/plain")

        
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
