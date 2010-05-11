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

class TestBase:

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

class ShowTestBase(TestBase):

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

    def _callFUT(self, context=None, request=None):
        from repoze.bfg.testing import DummyRequest
        if context is None:
            parent, context = self._makeContext()
        if request is None:
            request = DummyRequest()
        return self._getFUT()(context, request)

class ShowReferenceManualViewTests(ShowTestBase, unittest.TestCase):

    def _getFUT(self):
        from karl.content.views.references import show_referencemanual_view
        return show_referencemanual_view

    def test_it(self):
        from repoze.bfg.testing import registerDummyRenderer
        self._registerTagbox()
        self._registerAddables()
        self._registerLayoutProvider()

        # XXX
        renderer = registerDummyRenderer('templates/show_referencemanual.pt')
        self._callFUT()
        self.assertEqual(renderer.api.page_title, 'dummytitle')


class ShowReferenceSectionViewTests(ShowTestBase, unittest.TestCase):

    def _getFUT(self):
        from karl.content.views.references import show_referencesection_view
        return show_referencesection_view

    def test_it(self):
        from repoze.bfg.testing import registerDummyRenderer
        self._registerAddables()
        self._registerTagbox()
        self._registerLayoutProvider()

        # XXX
        renderer = registerDummyRenderer('templates/show_referencesection.pt')
        self._callFUT()
        self.assertEqual(renderer.api.page_title, 'dummytitle')


class AddReferenceFCBaseTests(TestBase, unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.views.references import AddReferenceFCBase
        return AddReferenceFCBase

    def _makeOne(self, context=None, request=None):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        if context is None:
            context = DummyModel()
        if request is None:
            request = DummyRequest()
            request.environ['repoze.browserid'] = '1'
        base = self._getTargetClass()(context, request)
        base.page_title = 'Add Reference FC Base'
        return base

    def _registerFactory(self, controller):
        from repoze.bfg.testing import DummyModel
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        class IDummy(Interface):
            pass
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description,
                            creator=creator)
            return rm
        controller.content_iface = IDummy
        registerContentFactory(factory, IDummy)

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
        self.assertEqual(response['api'].page_title, 'Add Reference FC Base')
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)

    def test_handle_cancel(self):
        controller = self._makeOne()
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import DummyCatalog
        from karl.testing import DummyOrdering
        from karl.testing import DummyTags
        context = DummyModel(tags = DummyTags(),
                             catalog = DummyCatalog(),
                             ordering = DummyOrdering(),
                            )
        converted = {'title': u'Ref Manual Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'ref manual description',
                     }
        controller = self._makeOne(context=context)
        self._registerFactory(controller)
        response = controller.handle_submit(converted)

        self.failUnless(u'ref-manual-title' in context)
        manual = context[u'ref-manual-title']
        self.assertEqual(manual.title, u'Ref Manual Title')
        self.assertEqual(manual.description, u'ref manual description')
        self.assertEqual(context.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])

class AddReferenceManualFormControllerTests(unittest.TestCase):

    def test_attrributes(self):
        from karl.content.interfaces import IReferenceManual
        from karl.content.views.references \
            import AddReferenceManualFormController as klass
        self.assertEqual(klass.page_title, "Add Reference Manual")
        self.assertEqual(klass.content_iface, IReferenceManual)
 

class AddReferenceSectionFormControllerTests(TestBase, unittest.TestCase):

    def test_attrributes(self):
        from karl.content.interfaces import IReferenceSection
        from karl.content.views.references \
            import AddReferenceSectionFormController as klass
        self.assertEqual(klass.page_title, "Add Reference Section")
        self.assertEqual(klass.content_iface, IReferenceSection)


class EditReferenceFCBaseTests(TestBase, unittest.TestCase):

    def _makeOne(self, context=None, request=None):
        from repoze.bfg.testing import DummyRequest
        from karl.content.views.references import EditReferenceFCBase
        if context is None:
            parent, context = self._makeContext()
        if request is None:
            request = DummyRequest()
            request.environ['repoze.browserid'] = '1'
        base =  EditReferenceFCBase(context, request)
        base.success_msg = 'BASE'
        return base

    def _makeContext(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import DummyCatalog
        parent = DummyModel(title='dummyparent',
                            catalog=DummyCatalog(),
                           )
        context = DummyModel(title='dummytitle',
                             description='dummydescription',
                            )
        parent['dummytitle'] = context
        return parent, context

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

    def test_handle_submit(self):
        converted = {'title': u'New Title',
                     'tags': [u'foo', u'bar'],
                     'description': u'new description',
                     }
        parent, context = self._makeContext()
        self._registerTags(parent)
        controller = self._makeOne(context)

        response = controller.handle_submit(converted)
        # XXX test reseponse type, location?

        self.assertEqual(response.location,
                        'http://example.com/dummytitle/?status_message=BASE')
        self.assertEqual(context.title, u'New Title')
        self.assertEqual(context.description, u'new description')
        self.assertEqual(parent.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class EditReferenceManualFormControllerTests(unittest.TestCase):

    def test_attrributes(self):
        from karl.content.views.references \
            import EditReferenceManualFormController as klass
        self.assertEqual(klass.success_msg, 'Reference%20manual%20edited')


class EditReferenceSectionFormControllerTests(unittest.TestCase):

    def test_attrributes(self):
        from karl.content.views.references \
            import EditReferenceSectionFormController as klass
        self.assertEqual(klass.success_msg, 'Reference%20section%20edited')
