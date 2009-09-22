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
from webob import MultiDict

from zope.interface import Interface
from zope.testing.cleanup import cleanUp
from repoze.bfg import testing

from repoze.bfg.testing import DummyModel
from repoze.bfg.testing import DummyRequest
from repoze.bfg.testing import registerDummyRenderer
from repoze.bfg.testing import registerAdapter
from repoze.bfg.testing import registerEventListener

from repoze.lemonade.testing import registerContentFactory

from karl.models.interfaces import IObjectModifiedEvent

from karl.testing import DummyCatalog
from karl.testing import DummyFolderAddables
from karl.testing import DummyOrdering
from karl.testing import DummyTagQuery

from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection


class TestAddReferenceManualView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        self.template_fn = 'templates/addedit_referencemanual.pt'

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.references import add_referencemanual_view
        return add_referencemanual_view(context, request)

    def _registerFactory(self):
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description, 
                            creator=creator)
            return rm
        registerContentFactory(factory, IReferenceManual)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_cancel(self):
        request = DummyRequest()
        request.POST = MultiDict({'form.cancel':'1'})
        context = DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_submitted_missing_values(self):
        self._registerLayoutProvider()

        request = DummyRequest(
            params=MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = DummyModel()
        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Missing value')
        self.assertEqual(str(errors['description']), 'Missing value')

    def test_submitted_empty_values(self):
        self._registerLayoutProvider()

        request = DummyRequest(
            params=MultiDict({
                    'form.submitted':'1',
                    'title': '',
                    'description': '',
                    })
            )
        context = DummyModel()
        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Please enter a value')

    def test_submitted_success(self):
        self._registerFactory()
        request = DummyRequest(
            params=MultiDict({
                    'form.submitted':'1',
                    'title':'title',
                    'description':'abc',
                    'tags': 'thetesttag',
                    })
            )
        context = DummyModel()
        context.catalog = DummyCatalog()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/title/')
        self.assertEqual(context['title'].title, 'title')
        self.assertEqual(context['title'].description, 'abc')
        self.assertEqual(context['title'].creator, None)


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

class TestEditReferenceManualView(unittest.TestCase):

    def setUp(self):
        cleanUp()

        self.template_fn = 'templates/addedit_referencemanual.pt'

        self.parent = DummyModel(title='dummyparent')
        self.context = DummyModel(title='dummytitle', 
                                  description='dummydescription')
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.references import edit_referencemanual_view
        return edit_referencemanual_view(context, request)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_notsubmitted(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest()
        request.POST = MultiDict()
        context = self.context

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

        
    def test_submitted_missing_values(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = self.context

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Missing value')

    def test_submitted_invalid(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title': '',
                    })
            )
        context = self.context

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Please enter a value')

    def test_submitted_valid(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title': 'newtitle',
                    'description': 'newdescription',
                    'tags': 'thetesttag',
                    })
            )
        context = self.context

        L = registerEventListener((Interface, IObjectModifiedEvent))

        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)

        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        msg = 'http://example.com/child/?status_message=Reference%20manual%20edited'
        self.assertEqual(response.location, msg)
        self.assertEqual(context.title, 'newtitle')
        self.assertEqual(context.description, 'newdescription')
        self.assertEqual(context.modified_by, 'testeditor')



class TestAddReferenceSectionView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        self.template_fn = 'templates/addedit_referencesection.pt'

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.references import add_referencesection_view
        return add_referencesection_view(context, request)

    def _registerFactory(self):
        def factory(title, description, creator):
            rm = DummyModel(title=title, description=description, 
                            creator=creator)
            return rm
        registerContentFactory(factory, IReferenceSection)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_cancel(self):
        self._registerLayoutProvider()

        request = DummyRequest()
        request.POST = MultiDict({'form.cancel':'1'})
        context = DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_submitted_missing_values(self):
        self._registerLayoutProvider()

        request = DummyRequest(
            params=MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = DummyModel()
        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Missing value')
        self.assertEqual(str(errors['description']), 'Missing value')

    def test_submitted_empty_values(self):
        self._registerLayoutProvider()

        request = DummyRequest(
            params=MultiDict({
                    'form.submitted':'1',
                    'title': '',
                    'description': '',
                    })
            )
        context = DummyModel()
        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Please enter a value')

    def test_submitted_success(self):
        self._registerFactory()
        self._registerLayoutProvider()

        request = DummyRequest(
            params=MultiDict({
                    'form.submitted':'1',
                    'title':'title',
                    'description':'abc',
                    'tags': 'thetesttag',
                    })
            )
        context = DummyModel()
        context.ordering = DummyOrdering()
        context.catalog = DummyCatalog()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/title/')
        self.assertEqual(context['title'].title, 'title')
        self.assertEqual(context['title'].description, 'abc')
        self.assertEqual(context['title'].creator, None)


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

class TestEditReferenceSectionView(unittest.TestCase):

    def setUp(self):
        cleanUp()

        self.template_fn = 'templates/addedit_referencesection.pt'

        self.parent = DummyModel(title='dummyparent')
        self.context = DummyModel(title='dummytitle', 
                                  description='dummydescription')
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.references import edit_referencesection_view
        return edit_referencesection_view(context, request)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = registerAdapter(DummyLayoutProvider, 
                             (Interface, Interface),
                             ILayoutProvider)

    def test_notsubmitted(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest()
        request.POST = MultiDict()
        context = self.context

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

        
    def test_submitted_missing_values(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = self.context

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Missing value')

    def test_submitted_invalid(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title': '',
                    })
            )
        context = self.context

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        errors = renderer.fielderrors
        self.assertEqual(str(errors['title']), 'Please enter a value')

    def test_submitted_valid(self):
        self._registerTagbox()
        self._registerLayoutProvider()

        request = DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title': 'newtitle',
                    'description': 'newdescription',
                    'tags': 'thetesttag',
                    })
            )
        context = self.context

        L = registerEventListener((Interface, IObjectModifiedEvent))

        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)

        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        msg = 'http://example.com/child/?status_message=Reference%20section%20edited'
        self.assertEqual(response.location, msg)
        self.assertEqual(context.title, 'newtitle')
        self.assertEqual(context.description, 'newdescription')
        self.assertEqual(context.modified_by, 'testeditor')



