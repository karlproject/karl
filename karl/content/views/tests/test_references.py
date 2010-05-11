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


class AddReferenceManualFormControllerTests(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _makeOne(self, context=None, request=None):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from karl.content.views.references \
            import AddReferenceManualFormController
        if context is None:
            context = DummyModel()
        if request is None:
            request = DummyRequest()
            request.environ['repoze.browserid'] = '1'
        return AddReferenceManualFormController(context, request)

    def _registerFactory(self):
        from repoze.bfg.testing import DummyModel
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IReferenceManual
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description,
                            creator=creator)
            return rm
        registerContentFactory(factory, IReferenceManual)

    def test_form_fields(self):
        controller = self._makeOne()
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('description' in fields)

    def test_form_widgets(self):
        controller = self._makeOne()
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('description' in widgets)

    def test___call__(self):
        controller = self._makeOne()
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Add Reference Manual')
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)

    def test_handle_cancel(self):
        controller = self._makeOne()
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import DummyCatalog
        from karl.testing import DummyTags
        context = DummyModel()
        converted = {'title': u'Ref Manual Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'ref manual description',
                     }

        self._registerFactory()

        # set up tags infrastructure
        context.tags = DummyTags()
        context.catalog = DummyCatalog()

        controller = self._makeOne(context=context)
        response = controller.handle_submit(converted)

        self.failUnless(u'ref-manual-title' in context)
        manual = context[u'ref-manual-title']
        self.assertEqual(manual.title, u'Ref Manual Title')
        self.assertEqual(manual.description, u'ref manual description')
        self.assertEqual(context.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class ShowReferenceManualViewTests(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _callFUT(self, context=None, request=None):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from karl.testing import DummyCatalog
        from karl.testing import DummyOrdering
        from karl.content.views.references import show_referencemanual_view

        if context is None:
            parent = DummyModel(title='dummyparent',
                                catalog = DummyCatalog(),
                               )
            context = DummyModel(title='dummytitle',
                                 text='dummytext',
                                 ordering = DummyOrdering(),
                                )
            parent['child'] = context

        if request is None:
            request = DummyRequest()

        return show_referencemanual_view(context, request)

    def _registerTagbox(self):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ITagQuery
        from karl.testing import DummyTagQuery

        registerAdapter(DummyTagQuery, (Interface, Interface),
                        ITagQuery)

    def _registerAddables(self):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.views.interfaces import IFolderAddables
        from karl.testing import DummyFolderAddables

        registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerLayoutProvider(self):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider

        registerAdapter(DummyLayoutProvider, (Interface, Interface),
                        ILayoutProvider)

    def test_it(self):
        from repoze.bfg.testing import registerDummyRenderer
        self._registerTagbox()
        self._registerAddables()
        self._registerLayoutProvider()

        # XXX
        renderer = registerDummyRenderer('templates/show_referencemanual.pt')
        self._callFUT()
        self.assertEqual(renderer.api.page_title, 'dummytitle')


class EditReferenceManualFormControllerTests(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _makeContext(self):
        from repoze.bfg.testing import DummyModel
        parent = DummyModel(title='dummyparent')
        context = DummyModel(title='dummytitle',
                             description='dummydescription')
        parent['dummytitle'] = context
        return parent, context

    def _makeOne(self, context=None, request=None):
        from repoze.bfg.testing import DummyRequest
        from karl.content.views.references \
            import EditReferenceManualFormController
        if context is None:
            parent, context = self._makeContext()
        if request is None:
            request = DummyRequest()
            request.environ['repoze.browserid'] = '1'
        return EditReferenceManualFormController(context, request)

    def _registerTags(self, site):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ITagQuery
        from karl.testing import DummyTagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                        ITagQuery)
        from karl.testing import DummyTags
        site.tags = DummyTags()

    def test_form_defaults(self):
        controller = self._makeOne()
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'dummytitle')
        self.assertEqual(defaults['description'], 'dummydescription')

    def test_form_fields(self):
        controller = self._makeOne()
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('description' in fields)

    def test_form_widgets(self):
        parent, context = self._makeContext()
        self._registerTags(parent)
        controller = self._makeOne(context)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('description' in widgets)

    def test___call__(self):
        controller = self._makeOne()
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title,
                         'Edit dummytitle')
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)

    def test_handle_cancel(self):
        controller = self._makeOne()
        response = controller.handle_cancel()
        self.assertEqual(response.location,
                         'http://example.com/dummytitle/')

    def handle_submit(self):
        converted = {'title': u'New Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'new description',
                     }
        self._registerTags(self.parent)
        parent, context = self._makeContext()
        controller = self._makeOne(context)

        response = controller.handle_submit(converted)
        # XXX test reseponse type, location?

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
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _makeOne(self, context, request=None):
        from repoze.bfg.testing import DummyRequest
        from karl.content.views.references \
            import AddReferenceSectionFormController
        if request is None:
            request = DummyRequest()
            request.environ['repoze.browserid'] = '1'
        return AddReferenceSectionFormController(context, request)

    def _registerFactory(self):
        from repoze.bfg.testing import DummyModel
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IReferenceSection
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description,
                            creator=creator)
            return rm
        registerContentFactory(factory, IReferenceSection)

    def test_handle_submit(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import DummyTags
        from karl.testing import DummyCatalog
        from karl.testing import DummyOrdering

        self._registerFactory()

        context = DummyModel(tags = DummyTags(),
                             catalog = DummyCatalog(),
                             ordering = DummyOrdering(),
                            )

        converted = {'title': u'Ref Section Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'ref section description',
                     }


        controller = self._makeOne(context)
        response = controller.handle_submit(converted)
        # XXX:  test response type, location?

        self.failUnless(u'ref-section-title' in context)
        manual = context[u'ref-section-title']
        self.assertEqual(manual.title, u'Ref Section Title')
        self.assertEqual(manual.description, u'ref section description')
        self.assertEqual(context.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class ShowReferenceSectionViewTests(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _makeContext(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import DummyCatalog
        from karl.testing import DummyOrdering
        parent = DummyModel(title='dummyparent',
                            ordering = DummyOrdering(),
                            catalog = DummyCatalog(),
                           )
        context = DummyModel(title='dummytitle',
                             text='dummytext',
                             ordering = DummyOrdering(),
                            )
        context['attachments'] = DummyModel()
        parent['child'] = context
        return parent, context

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _callFUT(self, context=None, request=None):
        from repoze.bfg.testing import DummyRequest
        from karl.content.views.references import show_referencesection_view
        if context is None:
            parent, context = self._makeContext()
        if request is None:
            request = DummyRequest()
        return show_referencesection_view(context, request)

    def _registerTagbox(self):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ITagQuery
        from karl.testing import DummyTagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerAddables(self):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.views.interfaces import IFolderAddables
        from karl.testing import DummyFolderAddables
        registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerLayoutProvider(self):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def test_it(self):
        from repoze.bfg.testing import registerDummyRenderer
        self._registerAddables()
        self._registerTagbox()
        self._registerLayoutProvider()

        # XXX
        renderer = registerDummyRenderer('templates/show_referencesection.pt')
        self._callFUT()
        self.assertEqual(renderer.api.page_title, 'dummytitle')


class EditReferenceSectionFormControllerTests(unittest.TestCase):
    # this form controller shares nearly all of its code w/ the
    # edit reference manual form controller, so only the parts that
    # are different are tested here.
    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _makeContext(self):
        from repoze.bfg.testing import DummyModel
        parent = DummyModel(title='dummyparent')
        context = DummyModel(title='dummytitle',
                             description='dummydescription')
        parent['dummytitle'] = context
        return parent, context

    def _makeOne(self, context, request=None):
        from repoze.bfg.testing import DummyRequest
        from karl.content.views.references \
            import EditReferenceSectionFormController
        if request is None:
            request = DummyRequest()
            request.environ['repoze.browserid'] = '1'
        return EditReferenceSectionFormController(context, request)

    def _registerTags(self, site):
        from zope.interface import Interface
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ITagQuery
        from karl.testing import DummyTagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                        ITagQuery)
        from karl.testing import DummyTags
        site.tags = DummyTags()

    def handle_submit(self):
        converted = {'title': u'New Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'new description',
                     }
        parent, context = self._makeContext()
        self._registerTags(parent)
        controller = self._makeOne(context)
        response = controller.handle_submit(converted)
        # XXX test response type, location?

        self.failUnless('Reference%20section%20edited' in
                        response.location)
        self.failUnless(response.location.startswith(
            'http://example.com/dummytitle/'))
        self.assertEqual(context.title, u'New Title')
        self.assertEqual(context.description, u'new description')
        self.assertEqual(self.parent.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])
