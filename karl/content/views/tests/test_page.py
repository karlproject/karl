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
from webob.multidict import MultiDict

from zope.interface import Interface
from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

from repoze.bfg.testing import DummyModel
from repoze.bfg.testing import DummyRequest
from repoze.bfg.testing import registerDummyRenderer
from repoze.bfg.testing import registerAdapter
from repoze.bfg.testing import registerEventListener

from repoze.lemonade.testing import registerContentFactory

from karl.models.interfaces import IObjectModifiedEvent

from karl.testing import DummyCatalog
from karl.testing import DummyLayoutProvider
from karl.testing import DummySessions
from karl.testing import DummyTagQuery

from karl.content.interfaces import IPage

class TestAddPageFormController(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        self.context = context

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.page import AddPageFormController
        return AddPageFormController(context, request)

    def test_form_defaults(self):
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults.get('title'), '')
        self.assertEqual(defaults.get('tags'), [])
        self.assertEqual(defaults.get('text'), '')
        self.assertEqual(defaults.get('attachments'), [])

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('text' in fields)
        self.failUnless('attachments' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('text' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Add Page')
        self.failUnless('actions' in response)
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        context = self.context

        # register dummy IPage content factory
        def factory(title, text, description, creator):
            page = DummyModel(title=title, text=text,
                              description=description,
                              creator=creator)
            page['attachments'] = DummyModel()
            return page
        registerContentFactory(factory, IPage)

        # set up attachments
        from karl.content.interfaces import ICommunityFile
        from karl.testing import DummyFile
        registerContentFactory(DummyFile, ICommunityFile)
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r"C:\My Documents\Ha Ha\test2.txt")

        # set up tags infrastructure
        from karl.testing import DummyCommunity
        from karl.testing import DummyTags
        community = DummyCommunity()
        site = community.__parent__.__parent__
        site.sessions = DummySessions()
        site.catalog = DummyCatalog()
        site.tags = DummyTags()
        community['pages'] = context

        # construct converted dict and call handle_submit
        converted = {'title': u'Page Title',
                     'text': u'page text',
                     'tags': [u'foo', u'bar'],
                     'attachments': [attachment1, attachment2],
                     }
        context.ordering = DummyOrdering()
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)

        # make sure everything looks good
        # basic fields
        self.failUnless(u'page-title' in context)
        page = context['page-title']
        self.assertEqual(page.title, u'Page Title')
        self.assertEqual(page.text, u'page text')
        # attachments
        attachments_folder = page['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        self.assertEqual(attachments_folder['test1.txt'].filename,
                         'test1.txt')
        self.assertEqual(attachments_folder['test2.txt'].filename,
                         'test2.txt')
        # ordering
        self.assertEqual(context.ordering.names_added, ['page-title'])
        # tags
        self.assertEqual(site.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])

class TestEditPageFormController(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self.parent = DummyModel(title='dummyparent', sessions=DummySessions())
        self.context = DummyModel(title='dummytitle', text='dummytext')
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _registerTags(self, site):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                        ITagQuery)
        from karl.testing import DummyTags
        site.tags = DummyTags()

    def _makeOne(self, context, request):
        from karl.content.views.page import EditPageFormController
        return EditPageFormController(context, request)

    def test_form_defaults(self):
        context = self.context
        from karl.testing import DummyFile
        context['attachments']['a'] = DummyFile(__name__='1',
                                                mimetype='text/plain')
        controller = self._makeOne(context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults.get('title'), 'dummytitle')
        self.assertEqual(defaults.get('text'), 'dummytext')
        self.assertEqual(len(defaults['attachments']), 1)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('text' in fields)
        self.failUnless('attachments' in fields)

    def test_form_widgets(self):
        self._registerTags(self.parent)
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('text' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit dummytitle')
        self.failUnless('actions' in response)
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/child/')

    def test_handle_submit(self):
        from karl.testing import DummyUpload
        attachment = DummyUpload(filename='newfile.txt')
        converted = {'title': u'New Title',
                     'text': u'New page text.',
                     'tags': [u'foo', u'bar'],
                     'attachments': [attachment],
                     }
        self._registerTags(self.parent)
        from karl.content.interfaces import ICommunityFile
        from karl.testing import DummyFile
        registerContentFactory(DummyFile, ICommunityFile)
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)
        self.failUnless('Page%20edited' in response.location)
        self.failUnless(
            response.location.startswith('http://example.com/child/'))
        self.assertEqual(context.title, u'New Title')
        self.assertEqual(context.text, u'New page text.')
        attachments_folder = context['attachments']
        self.failUnless('newfile.txt' in attachments_folder)
        self.failIf(len(attachments_folder) > 1)
        self.assertEqual(self.parent.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])

class ShowPageViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # When you see:
        #   AttributeError: 'NoneType' object has no attribute 'url'
        # ...it is often because you are pointed at the wrong .pt
        self.template_fn = 'templates/show_page.pt'

        self.parent = DummyModel(title='dummyparent')
        self.context = DummyModel(title='dummytitle', text='dummytext')
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, request):
        from karl.content.views.page import show_page_view
        return show_page_view(context, request)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_it(self):
        self._registerLayoutProvider()
        self._registerTagbox()

        context = self.context
        request = DummyRequest()

        renderer = registerDummyRenderer(self.template_fn)
        self._callFUT(context, request)
        self.assertEqual(renderer.api.page_title, 'dummytitle')
        self.assertEqual(len(renderer.actions), 2)
        self.assertEqual(renderer.actions[0][1], 'edit.html')
        self.assertEqual(renderer.actions[1][1], 'delete.html')

class DummyOrdering(object):
    names_added = []
    
    def add(self, name):
        self.names_added.append(name)
        
