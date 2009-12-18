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

        
