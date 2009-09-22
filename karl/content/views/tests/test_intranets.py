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
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing
from webob import MultiDict
from karl.testing import DummyUsers
from karl.testing import DummyCatalog

class TestShowIntranetsView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.intranets import show_intranets_view
        return show_intranets_view(context, request)

    def test_it(self):
        from zope.interface import directlyProvides
        from zope.interface import alsoProvides
        from karl.models.interfaces import ISite
        from karl.models.interfaces import IIntranets
        renderer = testing.registerDummyRenderer('templates/show_intranets.pt')
        context = testing.DummyModel(title='Intranets')
        directlyProvides(context, IIntranets)
        alsoProvides(context, ISite)
        request = testing.DummyRequest()
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 1)

class AddIntranetViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.intranets import add_intranet_view
        return add_intranet_view(context, request)

    def test_cancelled(self):
        context = testing.DummyModel()
        request = testing.DummyRequest(params={'form.cancel':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_not_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/add_intranet.pt')
        from karl.models.interfaces import IToolFactory
        testing.registerUtility(None, IToolFactory, name='mytoolfactory')
        self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        context = testing.DummyModel()
        request = testing.DummyRequest(MultiDict({'form.submitted':1}))
        renderer = testing.registerDummyRenderer(
            'templates/add_intranet.pt')
        from karl.models.interfaces import IToolFactory
        testing.registerUtility(None, IToolFactory, name='mytoolfactory')
        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        from zope.interface import directlyProvides
        from zope.interface import alsoProvides
        from karl.models.interfaces import ISite
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IToolFactory
        from karl.models.interfaces import IIntranets
        from repoze.lemonade.interfaces import IContentFactory

        context = testing.DummyModel()
        directlyProvides(context, ISite)
        alsoProvides(context, ICommunity)
        alsoProvides(context, IIntranets)
        testing.registerDummySecurityPolicy('userid')

        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':1,
                    'title':'sometitle',
                    'description':'somedescription',
                    'city': 'city',
                    'right_portlets':'',
                    'middle_portlets':'',
                    'country':'country',
                    'zipcode':'zipcode',
                    'telephone':'telephone',
                    'state':'state',
                    'address':'address',
                    'navigation':'navigation',
                    'feature':'',
                    })
            )
        testing.registerUtility(None, IToolFactory, name='mytoolfactory')
        testing.registerAdapter(lambda *arg: DummyCommunity, (ICommunity,),
                                IContentFactory)
        from karl.testing import registerSecurityWorkflow
        registerSecurityWorkflow()
        dummy_tool_factory = DummyToolFactory()
        testing.registerUtility(dummy_tool_factory, IToolFactory, name='blog')
        context.users = DummyUsers({})
        context.catalog = DummyCatalog({1:'/foo'})

        response = self._callFUT(context, request)
        msg = 'http://example.com/?status_message=Intranet%20added'
        self.failUnless(response.location, msg)


class EditIntranetRootViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from karl.testing import registerTagbox
        registerTagbox()
        from karl.views.interfaces import IToolAddables
        from zope.interface import Interface
        testing.registerAdapter(DummyToolAddables, (Interface, Interface),
                                IToolAddables)

    def _registerSecurityWorkflow(self):
        workflow = DummyWorkflow()
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security', workflow)

    def _callFUT(self, context, request):
        from karl.content.views.intranets import edit_intranet_root_view
        return edit_intranet_root_view(context, request)

    def test_not_submitted(self):
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.testing import registerListItem
        tool_factory = DummyToolFactory(present=True)
        registerListItem(IToolFactory, tool_factory, 'foo')
        context = testing.DummyModel()
        context.__name__ = 'Community'
        context.title = 'thetitle'
        context.description = 'thedescription'
        context.text = 'text'
        context.feature = 'zzz'
        context.default_tool = 'overview'
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        renderer = testing.registerDummyRenderer(
            'templates/edit_intranet_root.pt')
        self._register()
        self._registerSecurityWorkflow()
        self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fieldvalues['title'], 'thetitle')
        self.assertEqual(renderer.fieldvalues['feature'], 'zzz')

    def test_submitted_invalid(self):
        from webob import MultiDict
        context = testing.DummyModel(title='oldtitle',
                                     default_tool='overview')
        context.__name__ = 'Community'
        request = testing.DummyRequest(MultiDict({'form.submitted':'1',
                                                  'default_tool':'foo'}))
        renderer = testing.registerDummyRenderer(
            'templates/edit_intranet_root.pt')
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.testing import registerListItem
        tool_factory = DummyToolFactory(present=True)
        registerListItem(IToolFactory, tool_factory, 'foo')
        self._register()
        self._registerSecurityWorkflow()
        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid_sharingchange(self):
        from webob import MultiDict
        from zope.interface import Interface
        from repoze.bfg.testing import registerDummySecurityPolicy
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from karl.testing import DummyCatalog
        registerDummySecurityPolicy('userid')
        context = testing.DummyModel(
            title='oldtitle', description='oldescription')
        context.__acl__ = ['a']
        context.staff_acl = ['1']
        context.catalog = DummyCatalog()
        request = testing.DummyRequest(
            params = MultiDict({'form.submitted':1,
                      'title':u'Thetitle yo',
                      'description':'thedescription',
                      'text':'thetext',
                      'feature':'',
                      'security_state':'public',
                      'default_tool': 'files',
                      }),
            )
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                            IObjectWillBeModifiedEvent))
        self._register()
        workflow = self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.title, u'Thetitle yo')
        self.assertEqual(context.description, 'thedescription')
        self.assertEqual(context.text, 'thetext')
        self.assertEqual(context.default_tool, 'files')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)
        self.assertEqual(workflow.transitioned[0]['to_state'], 'public')

    def test_submitted_valid_nosharingchange(self):
        from webob import MultiDict
        from zope.interface import Interface
        from repoze.bfg.testing import registerDummySecurityPolicy
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from karl.testing import DummyCatalog
        registerDummySecurityPolicy('userid')
        context = testing.DummyModel(
            title='oldtitle', description='oldescription')
        context.__acl__ = ['a']
        context.staff_acl = ['1']
        context.catalog = DummyCatalog()
        request = testing.DummyRequest(
            params = MultiDict({'form.submitted':1,
                      'title':u'Thetitle yo',
                      'description':'thedescription',
                      'text':'thetext',
                      'feature':'',
                      'security_state':'private',
                      'default_tool': 'files',
                      'tags': 'thetesttag',
                      }),
            )
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                            IObjectWillBeModifiedEvent))
        self._register()
        workflow = self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.title, u'Thetitle yo')
        self.assertEqual(context.description, 'thedescription')
        self.assertEqual(context.text, 'thetext')
        self.assertEqual(context.default_tool, 'files')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)
        self.assertEqual(workflow.transitioned[0]['to_state'], 'private')

    def test_submitted_changetools(self):
        from webob import MultiDict
        from repoze.bfg.testing import registerDummySecurityPolicy
        from karl.models.interfaces import IToolFactory
        from karl.testing import DummyCatalog
        registerDummySecurityPolicy('userid')
        context = testing.DummyModel(title='oldtitle')
        context.catalog = DummyCatalog()
        request = testing.DummyRequest(
            params = MultiDict({'form.submitted':1,
                      'title':u'Thetitle yo',
                      'description':'thedescription',
                      'text':'thetext',
                      'feature':'',
                      'security_state':'private',
                      'calendar':'calendar',
                      'default_tool': 'overview',
                      }),
            )
        blog_tool_factory = DummyToolFactory(present=True)
        testing.registerUtility(blog_tool_factory, IToolFactory, name='blog')
        calendar_tool_factory = DummyToolFactory(present=False)
        self._register()
        self._registerSecurityWorkflow()
        testing.registerUtility(calendar_tool_factory, IToolFactory,
                                name='calendar')
        response = self._callFUT(context, request)
        self.assertEqual(blog_tool_factory.removed, True)
        self.assertEqual(calendar_tool_factory.added, True)


class DummyAdapter:
    url = 'someurl'
    title = 'sometitle'
    tabs = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyFilesTool:
    title = 'Dummy Files Tool'


class DummyCommunity:
    def __init__(self, title, description, text, creator):
        self.title = title
        self.description = description
        self.text = text
        self.creator = creator
        self.members_group_name = 'members'
        self.moderators_group_name = 'moderators'
        self.files = DummyFilesTool()

    def get(self, key, default):
        return getattr(self, key)

class DummyToolFactory:
    def __init__(self, present=False):
        self.present = present

    def add(self, context, request):
        self.added = True

    def remove(self, context, request):
        self.removed = True

    def is_present(self, context, request):
        return self.present

class DummyToolAddables(DummyAdapter):
    def __call__(self):
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.listitem import get_listitems
        return get_listitems(IToolFactory)

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

    def initialize(self, content):
        self.initialized = True
    
    def transition_to_state(self, content, request, to_state, context=None,
                            guards=(), skip_same=True):
        self.transitioned.append({'to_state':to_state, 'content':content,
                                  'request':request, 'guards':guards,
                                  'context':context, 'skip_same':skip_same})

    def state_of(self, content):
        return getattr(content, self.state_attr, None)
