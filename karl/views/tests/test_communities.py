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
from zope.testing.cleanup import cleanUp
from repoze.bfg import testing
from karl import testing as karltesting

class ShowCommunitiesViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.communities import show_communities_view
        return show_communities_view(context, request)

    def test_it(self):
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from karl.models.adapters import CatalogSearch
        catalog = karltesting.DummyCatalog({1:'/foo'})
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)
        context = testing.DummyModel()
        context.catalog = catalog
        foo = testing.DummyModel()
        testing.registerModels({'/foo':foo})
        request = testing.DummyRequest(
            params={'titlestartswith':'A'})
        renderer = testing.registerDummyRenderer('templates/communities.pt')
        self._callFUT(context, request)
        self.assertEqual(len(renderer.communities), 1)
        self.assertEqual(renderer.communities[0].context, foo)
        self.failUnless(renderer.communities)
        self.failUnless(renderer.actions)

    def test_my_communities(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from karl.models.adapters import CatalogSearch
        catalog = karltesting.DummyCatalog({1:'/foo'})
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)
        testing.registerDummySecurityPolicy('admin',
                                            ['group.community:yum:bar'])
        context = testing.DummyModel()
        yum = testing.DummyModel()
        context['yum'] = yum
        yum.title = 'Yum!'
        context.catalog = catalog
        foo = testing.DummyModel()
        testing.registerModels({'/foo':foo})
        request = testing.DummyRequest(
            params={'titlestartswith':'A'})
        renderer = testing.registerDummyRenderer('templates/communities.pt')
        self._callFUT(context, request)
        self.assertEqual(len(renderer.communities), 1)
        self.assertEqual(renderer.communities[0].context, foo)
        self.failUnless(renderer.communities)
        self.failUnless(renderer.actions)
        self.failUnless(renderer.my_communities[0].context, yum)

class AddCommunityViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self._register()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.communities import add_community_view
        return add_community_view(context, request)

    def _register(self):
        from karl.views.interfaces import IToolAddables
        testing.registerAdapter(DummyToolAddables, (Interface, Interface),
                                IToolAddables)
    def _registerDummyWorkflow(self):
        wf = DummyWorkflow()
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_cancelled(self):
        context = testing.DummyModel()
        from webob import MultiDict
        request = testing.DummyRequest()
        request.POST = request.params = MultiDict({'form.cancel':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_not_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = request.params = MultiDict({})
        renderer = testing.registerDummyRenderer(
            'templates/add_community.pt')
        workflow = self._registerDummyWorkflow()
        self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        context = testing.DummyModel()
        from webob import MultiDict
        request = testing.DummyRequest(MultiDict({'form.submitted':1}))
        renderer = testing.registerDummyRenderer(
            'templates/add_community.pt')
        from karl.models.interfaces import IToolFactory
        testing.registerUtility(None, IToolFactory, name='mytoolfactory')
        workflow = self._registerDummyWorkflow()
        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_community_exists(self):
        workflow = self._registerDummyWorkflow()
        context = testing.DummyModel()
        context['thecommunity'] = testing.DummyModel()
        from webob import MultiDict
        request = testing.DummyRequest(
            params = MultiDict({'form.submitted':1,
                      'title':u'thecommunity',
                      'description':'thedescription',
                      'text':'thetext',
                      'blog': 'Blog',
                      'security_state':'public',
                      }),
            )
        response = self._callFUT(context, request)
        self.failUnless(response.location.startswith(
            'http://example.com/?status_message=The%20name'))
        self.assertEqual(workflow.transitioned, [])
        
    def test_submitted_public(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ISite
        from webob import MultiDict
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.interfaces import IContentFactory
        context = testing.DummyModel()
        directlyProvides(context, ISite)
        tags = context.tags = testing.DummyModel()
        _tagged = []
        def _update(item, user, tags):
            _tagged.append((item, user, tags))
        tags.update = _update
        testing.registerDummySecurityPolicy('userid')
        workflow = self._registerDummyWorkflow()
        request = testing.DummyRequest(
            params = MultiDict({
                      'form.submitted':1,
                      'title':u'Thetitle yo',
                      'description':'thedescription',
                      'text':'thetext',
                      'blog': 'Blog',
                      'security_state': 'private',
                      'tags': 'foo',
                      }),
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_community.pt')
        testing.registerAdapter(lambda *arg: DummyCommunity, (ICommunity,),
                                IContentFactory)
        dummy_tool_factory = DummyToolFactory()
        testing.registerUtility(dummy_tool_factory, IToolFactory, name='blog')
        context.users = karltesting.DummyUsers({})
        context.catalog = karltesting.DummyCatalog({1:'/foo'})
        result = self._callFUT(context, request)
        rl = 'http://example.com/thetitle-yo/members/add_existing.html'
        self.failUnless(result.location.startswith(rl))
        community = context['thetitle-yo']
        self.assertEqual(community.title, 'Thetitle yo')
        self.assertEqual(community.description, 'thedescription')
        self.assertEqual(community.text, 'thetext')
        self.assertEqual(
            context.users.added_groups, 
            [('userid', 'moderators'), ('userid', 'members') ] 
        )
        self.assertEqual(dummy_tool_factory.added, True)
        self.assertEqual(len(_tagged), 1)
        self.assertEqual(_tagged[0][0], None)
        self.assertEqual(_tagged[0][1], 'userid')
        self.assertEqual(_tagged[0][2], ['foo'])
        self.assertEqual(workflow.transitioned[0]['to_state'], 'private')

    def test_submitted_private(self):
        context = testing.DummyModel()
        testing.registerDummySecurityPolicy('userid')
        from webob import MultiDict
        workflow = self._registerDummyWorkflow()
        request = testing.DummyRequest(
            params = MultiDict({'form.submitted':1,
                      'title':u'Thetitle yo',
                      'description':'thedescription',
                      'text':'thetext',
                      'blog': 'Blog',
                      'security_state':'public',
                      }),
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_community.pt')
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyCommunity, (ICommunity,),
                                IContentFactory)
        dummy_tool_factory = DummyToolFactory()
        testing.registerUtility(dummy_tool_factory, IToolFactory, name='blog')
        context.users = karltesting.DummyUsers({})
        context.catalog = karltesting.DummyCatalog({1:'/foo'})
        result = self._callFUT(context, request)
        rl = 'http://example.com/thetitle-yo/members/add_existing.html'
        self.failUnless(result.location.startswith(rl))
        community = context['thetitle-yo']
        self.assertEqual(community.title, 'Thetitle yo')
        self.assertEqual(community.description, 'thedescription')
        self.assertEqual(community.text, 'thetext')
        self.assertEqual(
            context.users.added_groups, 
            [('userid', 'moderators'), ('userid', 'members') ] 
        )
        self.assertEqual(dummy_tool_factory.added, True)
        self.assertEqual(workflow.transitioned[0]['to_state'], 'public')

class TestGetCommunityGroups(unittest.TestCase):
    def _callFUT(self, principals):
        from karl.views.communities import get_community_groups
        return get_community_groups(principals)

    def test_it(self):
        principals = [
            'a',
            'group.community:yo:members',
            'group.community:yo:other_role'
            ]
        groups = self._callFUT(principals)
        self.assertEqual(groups, [('yo', 'members'), ('yo', 'other_role')])

class TestGetMyCommunities(unittest.TestCase):
    def _callFUT(self, context, request):
        from karl.views.communities import get_my_communities
        return get_my_communities(context, request)

    def test_no_overflow(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        context['yo'] = yo
        context['yi'] = yi
        request = testing.DummyRequest()
        testing.registerDummySecurityPolicy(
            'foo',
            groupids=[
            'group.community:yo:members',
            'group.community:yo:moderators',
            'group.community:yi:moderators',
            'group.community:yang:moderators'
            ]
            )
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].context, yi)
        self.assertEqual(result[1].context, yo)
        
    def test_overflow(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        context['yo'] = yo
        context['yi'] = yi
        request = testing.DummyRequest()
        testing.registerDummySecurityPolicy(
            'foo',
            groupids=[
            'group.community:yo:members',
            'group.community:yo:moderators',
            'group.community:yi:moderators',
            'group.community:yang:moderators'
            ]
            )
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].context, yi)
        
class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyCommunity:
    def __init__(self, title, description, text, creator):
        self.title = title
        self.description = description
        self.text = text
        self.creator = creator
        self.members_group_name = 'members'
        self.moderators_group_name = 'moderators'

class DummyLetterManager:
    def __init__(self, context):
        self.context = context
        
    def get_info(self, request):
        return {}

class DummyToolFactory:
    def __init__(self, present=False):
        self.present = present
        self.added = False

    def add(self, context, request):
        self.added = True

class DummySecurityWorkflow:
    def __init__(self, context):
        self.context = context

    def setInitialState(self, request, **kw):
        self.context.sharing = kw['sharing']

    def execute(self, request, transition_id):
        self.context.transition_id = transition_id

class DummyToolAddables(DummyAdapter):
    def __call__(self):
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.listitem import get_listitems
        return get_listitems(IToolFactory)

class DummyWorkflow:
    state_attr = 'security_state'
    initial_state = 'initial'
    def __init__(self, state_info=('public', 'private')):
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

        
