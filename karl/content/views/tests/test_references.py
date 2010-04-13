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

from zope.interface import Interface
from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

from repoze.bfg.testing import DummyModel
from repoze.bfg.testing import DummyRequest
from repoze.bfg.testing import registerDummyRenderer
from repoze.bfg.testing import registerAdapter

from repoze.lemonade.testing import registerContentFactory

from karl.testing import DummyCatalog
from karl.testing import DummyFolderAddables
from karl.testing import DummyOrdering
from karl.testing import DummyTagQuery

from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection


class AddReferenceManualFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        self.context = testing.DummyModel()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.references import AddReferenceManualFormController
        return AddReferenceManualFormController(context, request)

    def _registerFactory(self):
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description, 
                            creator=creator)
            return rm
        registerContentFactory(factory, IReferenceManual)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('description' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('description' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Add Reference Manual')
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        context = self.context
        converted = {'title': u'Ref Manual Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'ref manual description',
                     }

        self._registerFactory()

        # set up tags infrastructure
        from karl.testing import DummyTags
        context.tags = DummyTags()
        context.catalog = DummyCatalog()

        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)

        self.failUnless(u'ref-manual-title' in context)
        manual = context[u'ref-manual-title']
        self.assertEqual(manual.title, u'Ref Manual Title')
        self.assertEqual(manual.description, u'ref manual description')
        self.assertEqual(context.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class ShowReferenceManualViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # When you see:
        #   AttributeError: 'NoneType' object has no attribute 'url'
        # ...it is often because you are pointed at the wrong .pt
        self.template_fn = 'templates/show_referencemanual.pt'

        self.parent = DummyModel(title='dummyparent')
        self.context = DummyModel(title='dummytitle', text='dummytext')
        self.context.ordering = DummyOrdering()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, request):
        from karl.content.views.references import show_referencemanual_view
        return show_referencemanual_view(context, request)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerAddables(self):
        from karl.views.interfaces import IFolderAddables
        registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_it(self):
        self._registerTagbox()
        self._registerAddables()
        self._registerLayoutProvider()

        context = self.context
        request = DummyRequest()

        renderer = registerDummyRenderer(self.template_fn)
        self._callFUT(context, request)
        self.assertEqual(renderer.api.page_title, 'dummytitle')


class EditReferenceManualFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        parent = DummyModel(title='dummyparent')
        context = DummyModel(title='dummytitle', 
                             description='dummydescription')
        parent['dummytitle'] = context
        self.parent = parent
        self.context = context
        request = DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.references import EditReferenceManualFormController
        return EditReferenceManualFormController(context, request)

    def _registerTags(self, site):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                        ITagQuery)
        from karl.testing import DummyTags
        site.tags = DummyTags()

    def test_form_defaults(self):
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'dummytitle')
        self.assertEqual(defaults['description'], 'dummydescription')

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('description' in fields)

    def test_form_widgets(self):
        self._registerTags(self.parent)
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('description' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title,
                         'Edit dummytitle')
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location,
                         'http://example.com/dummytitle/')

    def handle_submit(self):
        converted = {'title': u'New Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'new description',
                     }
        self._registerTags(self.parent)
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)
        self.failUnless('Reference%20manual%20edited' in
                        response.location)
        self.failUnless(response.location.startswith(
            'http://example.com/dummytitle/'))
        self.assertEqual(context.title, u'New Title')
        self.assertEqual(context.description, u'new description')
        self.assertEqual(self.parent.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class AddReferenceSectionFormControllerTests(unittest.TestCase):
    # Most of this controller code is shared w/ the add reference
    # manual form controller, so here we are only testing the
    # differences
    def setUp(self):
        cleanUp()
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        self.context = testing.DummyModel()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.references import AddReferenceSectionFormController
        return AddReferenceSectionFormController(context, request)

    def _registerFactory(self):
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description, 
                            creator=creator)
            return rm
        registerContentFactory(factory, IReferenceSection)

    def test_handle_submit(self):
        context = self.context
        converted = {'title': u'Ref Section Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'ref section description',
                     }

        self._registerFactory()

        # set up tags infrastructure
        from karl.testing import DummyTags
        context.tags = DummyTags()
        context.catalog = DummyCatalog()
        # set up ordering
        context.ordering = DummyOrdering()

        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)

        self.failUnless(u'ref-section-title' in context)
        manual = context[u'ref-section-title']
        self.assertEqual(manual.title, u'Ref Section Title')
        self.assertEqual(manual.description, u'ref section description')
        self.assertEqual(context.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class ShowReferenceSectionViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # When you see:
        #   AttributeError: 'NoneType' object has no attribute 'url'
        # ...it is often because you are pointed at the wrong .pt
        self.template_fn = 'templates/show_referencesection.pt'

        self.parent = DummyModel(title='dummyparent')
        self.parent.ordering = DummyOrdering()
        self.context = DummyModel(title='dummytitle', text='dummytext')
        self.context.ordering = DummyOrdering()
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, request):
        from karl.content.views.references import show_referencesection_view
        return show_referencesection_view(context, request)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerAddables(self):
        from karl.views.interfaces import IFolderAddables
        registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_it(self):
        self._registerAddables()
        self._registerTagbox()
        self._registerLayoutProvider()

        context = self.context
        request = DummyRequest()

        renderer = registerDummyRenderer(self.template_fn)
        self._callFUT(context, request)
        self.assertEqual(renderer.api.page_title, 'dummytitle')


class EditReferenceSectionFormControllerTests(unittest.TestCase):
    # this form controller shares nearly all of its code w/ the
    # edit reference manual form controller, so only the parts that
    # are different are tested here.
    def setUp(self):
        cleanUp()
        parent = DummyModel(title='dummyparent')
        context = DummyModel(title='dummytitle', 
                             description='dummydescription')
        parent['dummytitle'] = context
        self.parent = parent
        self.context = context
        request = DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.references import EditReferenceSectionFormController
        return EditReferenceSectionFormController(context, request)

    def _registerTags(self, site):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                        ITagQuery)
        from karl.testing import DummyTags
        site.tags = DummyTags()

    def handle_submit(self):
        converted = {'title': u'New Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'new description',
                     }
        self._registerTags(self.parent)
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)
        self.failUnless('Reference%20section%20edited' in
                        response.location)
        self.failUnless(response.location.startswith(
            'http://example.com/dummytitle/'))
        self.assertEqual(context.title, u'New Title')
        self.assertEqual(context.description, u'new description')
        self.assertEqual(self.parent.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])
