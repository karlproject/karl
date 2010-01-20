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
from zope.interface import implements

from repoze.bfg import testing

class TestRedirectToFrontPage(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.wiki import redirect_to_front_page
        return redirect_to_front_page(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        front_page = testing.DummyModel()
        context = testing.DummyModel()
        context['front_page'] = front_page
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/front_page/')

class TestAddWikiPageFormController(unittest.TestCase):
    def _makeOne(self, context, request):
        from karl.content.views.wiki import AddWikiPageFormController
        return AddWikiPageFormController(context, request)
    
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_form_defaults(self):
        workflow = self._registerSecurityWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], '')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['text'], '')
        self.assertEqual(defaults['sendalert'], True)
        self.assertEqual(defaults['security_state'], workflow.initial_state)
        
    def test_form_fields(self):
        self._registerSecurityWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        self._registerSecurityWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('tags' in widgets)

    def test___call__(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('page_title' in response)
        self.failUnless('api' in response)

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from karl.testing import DummyCatalog
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IWikiPage
        from karl.utilities.interfaces import IAlerts
        converted = {
            'title':'wikipage',
            'text':'text',
            'sendalert':True,
            'security_state':'public',
            'tags': 'thetesttag',
            }
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        registerContentFactory(DummyWikiPage, IWikiPage)
        testing.registerDummySecurityPolicy('userid')
        class Alerts(object):
            def __init__(self):
                self.emitted = []

            def emit(self, context, request):
                self.emitted.append((context, request))
        alerts = Alerts()
        testing.registerUtility(alerts, IAlerts)
        self._registerSecurityWorkflow()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        wikipage = context['wikipage']
        self.assertEqual(wikipage.title, 'wikipage')
        self.assertEqual(wikipage.text, 'text')
        self.assertEqual(wikipage.creator, 'userid')
        self.assertEqual(
            response.location,
            'http://example.com/wikipage/?status_message=Wiki%20Page%20created')
        self.assertEqual(len(alerts.emitted), 1)

class TestShowWikipageView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.wiki import show_wikipage_view
        return show_wikipage_view(context, request)

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def test_frontpage(self):
        self._register()
        renderer = testing.registerDummyRenderer('templates/show_wikipage.pt')
        context = testing.DummyModel()
        context.__name__ = 'front_page'
        context.title = 'Page'
        from karl.testing import DummyCommunity
        context.__parent__ = DummyCommunity()
        request = testing.DummyRequest()
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 1)
        self.assertEqual(renderer.actions[0][1], 'edit.html')
        # Front page should not have backlink breadcrumb thingy
        self.assert_(renderer.backto is False)

    def test_otherpage(self):
        self._register()
        renderer = testing.registerDummyRenderer('templates/show_wikipage.pt')
        context = testing.DummyModel(title='Other Page')
        context.__parent__ = testing.DummyModel(title='Front Page')
        context.__parent__.__name__ = 'front_page'
        context.__name__ = 'other_page'
        request = testing.DummyRequest()
        from webob.multidict import MultiDict
        request.params = request.POST = MultiDict()
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 2)
        self.assertEqual(renderer.actions[0][1], 'edit.html')
        self.assertEqual(renderer.actions[1][1], 'delete.html')
        # Backlink breadcrumb thingy should appear on non-front-page
        self.assert_(renderer.backto is not False)

class TestEditWikiPageFormController(unittest.TestCase):
    def _makeOne(self, context, request):
        from karl.content.views.wiki import EditWikiPageFormController
        return EditWikiPageFormController(context, request)
    
    def setUp(self):
        cleanUp()


    def tearDown(self):
        cleanUp()

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def _registerAlert(self):
        # Register WikiPageAlert adapter
        from karl.models.interfaces import IProfile
        from karl.content.interfaces import IWikiPage
        from karl.content.views.adapters import WikiPageAlert
        from karl.utilities.interfaces import IAlert
        from repoze.bfg.interfaces import IRequest
        testing.registerAdapter(WikiPageAlert,
                                (IWikiPage, IProfile, IRequest),
                                IAlert)

    def test_form_defaults(self):
        self._register()
        self._registerSecurityWorkflow()
        context = testing.DummyModel(title='title', text='text',
                                     security_state='public')
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'title')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['text'], 'text')
        self.assertEqual(defaults['security_state'], 'public')
        
    def test_form_fields(self):
        self._register()
        self._registerSecurityWorkflow()
        context = testing.DummyModel(title='', text='')
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        self._register()
        self._registerSecurityWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('tags' in widgets)

    def test___call__(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('page_title' in response)
        self.failUnless('api' in response)

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from karl.testing import DummyCatalog
        self._register()
        converted = {
            'text':'text',
            'title':'oldtitle',
            'sendalert': True,
            'security_state': 'public',
            'tags': 'thetesttag',
            }
        context = testing.DummyModel(title='oldtitle')
        context.text = 'oldtext'

        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(
            response.location,
            'http://example.com/?status_message=Wiki%20Page%20edited')
        self.assertEqual(context.text, 'text')
        self.assertEqual(context.modified_by, 'testeditor')

    def test_handle_submit_titlechange(self):
        from karl.testing import DummyCatalog
        self._register()
        converted = {
            'text':'text',
            'title':'newtitle',
            'sendalert': True,
            'security_state': 'public',
            'tags': 'thetesttag',
            }
        context = testing.DummyModel(title='oldtitle')
        context.text = 'oldtext'
        def change_title(newtitle):
            context.title = newtitle
        context.change_title = change_title
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(
            response.location,
            'http://example.com/?status_message=Wiki%20Page%20edited')
        self.assertEqual(context.text, 'text')
        self.assertEqual(context.modified_by, 'testeditor')
        self.assertEqual(context.title, 'newtitle')
        

from karl.content.interfaces import IWikiPage

class DummyWikiPage:
    implements(IWikiPage)
    def __init__(self, title, text, description, creator):
        self.title = title
        self.text = text
        self.description = description
        self.creator = creator

class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyTagQuery(DummyAdapter):
    tagswithcounts = []
    docid = 'ABCDEF01'

class DummyWorkflow:
    state_attr = 'security_state'
    initial_state = 'initial'
    def __init__(self, state_info=[
        {'name':'public', 'transitions':['private']},
        {'name':'private', 'transitions':['public']},
        ]):
        self.transitioned = []
        self._state_info = state_info

    def state_info(self, context, request):
        return self._state_info
    
    def transition_to_state(self, content, request, to_state, context=None,
                            guards=(), skip_same=True):
        self.transitioned.append({'to_state':to_state, 'content':content,
                                  'request':request, 'guards':guards,
                                  'context':context, 'skip_same':skip_same})

    def state_of(self, content):
        return getattr(content, self.state_attr, None)

    def initialize(self, content):
        self.initialized = content
