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
from pyramid import testing
from karl import testing as karltesting


def _checkCookie(request_or_response, target):
    from karl.views.communities import _VIEW_COOKIE
    header = ('Set-Cookie',
              '%s=%s; Path=/' % (_VIEW_COOKIE, target))
    headerlist = getattr(request_or_response, 'headerlist', None)
    if headerlist is None:
        headerlist = getattr(request_or_response, 'response_headerlist')
    assert header in headerlist


class Test_show_communities_view(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import show_communities_view
        return show_communities_view(context, request)

    def _checkResponse(self, response, target):
        from pyramid.httpexceptions import HTTPFound
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, target)

    def test_no_cookie(self):
        from pyramid.url import resource_url
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self._checkResponse(response,
                            resource_url(context, request, 'active_communities.html'))

    def test_w_cookie(self):
        from karl.views.communities import _VIEW_COOKIE
        COOKIES = {_VIEW_COOKIE: 'active'}
        from pyramid.url import resource_url
        context = testing.DummyModel()
        request = testing.DummyRequest(cookies=COOKIES)
        response = self._callFUT(context, request)
        self._checkResponse(response,
                            resource_url(context, request,
                                        'active_communities.html'))


class _Show_communities_helper:
    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from karl.models.adapters import CatalogSearch
        testing.registerAdapter(DummyCommunityInfoAdapter,
                                (Interface, Interface),
                                ICommunityInfo)
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)


class Test_show_all_communities_view(_Show_communities_helper,
                                     unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import show_all_communities_view
        return show_all_communities_view(context, request)

    def test_wo_groups(self):
        self._register()
        context = testing.DummyModel()
        profiles = context['profiles'] = testing.DummyModel()
        profiles[None] = testing.DummyModel()
        context.catalog = karltesting.DummyCatalog({1:'/foo'})
        foo = testing.DummyModel()
        testing.registerModels({'/foo':foo})
        request = testing.DummyRequest(
            params={'titlestartswith':'A'})
        info = self._callFUT(context, request)
        communities = info['communities']
        self.assertEqual(len(communities), 1)
        self.assertEqual(communities[0].context, foo)
        self.failUnless(communities)
        self.failUnless(info['actions'])
        _checkCookie(request, 'all')

    def test_w_groups(self):
        self._register()
        testing.registerDummySecurityPolicy('admin',
                                            ['group.community:yum:bar'])
        context = testing.DummyModel()
        profiles = context['profiles'] = testing.DummyModel()
        profiles['admin'] = testing.DummyModel()
        yum = testing.DummyModel()
        context['yum'] = yum
        yum.title = 'Yum!'
        context.catalog = karltesting.DummyCatalog({1:'/foo'})
        foo = testing.DummyModel()
        testing.registerModels({'/foo':foo})
        request = testing.DummyRequest(
            params={'titlestartswith':'A'})
        info = self._callFUT(context, request)
        communities = info['communities']
        self.assertEqual(len(communities), 1)
        self.assertEqual(communities[0].context, foo)
        self.failUnless(communities)
        self.failUnless(info['actions'])
        _checkCookie(request, 'all')


class Test_show_active_communities_view(_Show_communities_helper,
                                        unittest.TestCase):
    _old_TODAY = None

    def setUp(self):
        super(Test_show_active_communities_view, self).setUp()
        self._set_TODAY(None)

    def tearDown(self):
        super(Test_show_active_communities_view, self).tearDown()
        self._set_TODAY(None)
 
    def _set_TODAY(self, when):
        import karl.views.communities as MUT
        MUT._TODAY, self._old_TODAY = when, MUT._TODAY
        
    def _callFUT(self, context, request):
        from karl.views.communities import show_active_communities_view
        return show_active_communities_view(context, request)

    def test_excludes_inactive(self):
        from datetime import datetime
        from datetime import timedelta
        from karl.utils import coarse_datetime_repr
        now = datetime.now()
        today = now.today()
        six_months_ago = today - timedelta(days=180)
        self._set_TODAY(today)
        self._register()
        context = testing.DummyModel()
        profiles = context['profiles'] = testing.DummyModel()
        profiles[None] = testing.DummyModel()
        catalog = context.catalog = karltesting.DummyCatalog(
                                      {1: '/foo', 2: '/bar'})
        foo = testing.DummyModel(content_modified=now - timedelta(1))
        bar = testing.DummyModel(content_modified=now - timedelta(32))
        testing.registerModels({'/foo': foo,
                                '/bar': bar,
                               })
        request = testing.DummyRequest()

        info = self._callFUT(context, request)

        self.assertEqual(len(catalog.queries), 1)
        query = catalog.queries[0]
        self.assertEqual(query['content_modified'],
                         (coarse_datetime_repr(six_months_ago), None))

        communities = info['communities']
        self.assertEqual(len(communities), 2)
        self.assertEqual(communities[0].context, foo)
        self.assertEqual(communities[1].context, bar)
        self.failUnless(info['actions'])
        _checkCookie(request, 'active')


class Test_get_community_groups(unittest.TestCase):

    def _callFUT(self, principals):
        from karl.views.communities import get_community_groups
        return get_community_groups(principals)

    def test_ignores_non_groups(self):
        principals = [
            'a',
            'group.community:yo:members',
            'group.community:yo:other_role'
            ]
        groups = self._callFUT(principals)
        self.assertEqual(groups, [('yo', 'members'), ('yo', 'other_role')])

class Test_jquery_set_preferred_view(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import jquery_set_preferred_view
        return jquery_set_preferred_view(context, request)

    def test_jquery_set_preferred_view(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = None
        request = testing.DummyRequest()
        request.params = RequestParamsWithGetall()
        request.params['preferred[]'] = ['Yi']
        testing.registerDummySecurityPolicy(
            'foo',
            [
            'group.community:yo:members',
            'group.community:yo:moderators',
            'group.community:yi:moderators',
            ]
            )
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['my_communities'][0].context, yi)

class Test_jquery_clear_preferred_view(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import jquery_clear_preferred_view
        return jquery_clear_preferred_view(context, request)

    def test_jquery_clear_preferred_view(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = ['Yi']
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
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['preferred'], None)
        self.assertEqual(len(result['my_communities']), 2)

class Test_jquery_list_preferred_view(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import jquery_list_preferred_view
        return jquery_list_preferred_view(context, request)

    def test_jquery_list_preferred_view(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = ['Yi']
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
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['preferred'], ['Yi'])
        self.assertEqual(len(result['my_communities']), 1)

    def test_jquery_list_preferred_view_with_none(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = None
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
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['preferred'], None)
        self.assertEqual(len(result['my_communities']), 2)

    def test_jquery_list_preferred_view_with_empty(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = []
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
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['preferred'], [])
        self.assertEqual(len(result['my_communities']), 2)

class Test_jquery_edit_preferred_view(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import jquery_edit_preferred_view
        return jquery_edit_preferred_view(context, request)

    def test_jquery_edit_preferred_view(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = ['Yi']
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
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['preferred'], ['Yi'])
        self.assertEqual(len(result['my_communities']), 2)

class Test_jquery_list_my_communities_view(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import jquery_list_my_communities_view
        return jquery_list_my_communities_view(context, request)

    def test_jquery_list_my_communities_view(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        communities = context['communities'] = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        communities['yo'] = yo
        communities['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = ['Yi']
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
        testing.registerAdapter(DummyAdapterWithTitle, (Interface, Interface),
                                ICommunityInfo)
        result = self._callFUT(context, request)
        self.assertEqual(result['preferred'], ['Yi'])
        self.assertEqual(result['show_all'], True)
        self.assertEqual(len(result['my_communities']), 2)

class Test_get_preferred_communities(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import get_preferred_communities
        return get_preferred_communities(context, request)

    def test_get_preferred_communities(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        context['yo'] = yo
        context['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = ['yo']
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
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'yo')

    def test_get_preferred_communities_old_profile(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        context['yo'] = yo
        context['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
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
        self.assertEqual(result, None)

class Test_set_preferred_communities(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request, communities):
        from karl.views.communities import set_preferred_communities
        set_preferred_communities(context, request, communities)

    def test_set_preferred_communities(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        from karl.views.communities import get_preferred_communities
        context = testing.DummyModel()
        yo = testing.DummyModel()
        yo.title = 'Yo'
        yi = testing.DummyModel()
        yi.title = 'Yi'
        context['yo'] = yo
        context['yi'] = yi
        profiles = context['profiles'] = testing.DummyModel()
        foo = profiles['foo'] = testing.DummyModel()
        foo.preferred_communities = None
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
        communities = ['yi']
        self._callFUT(context, request, communities)
        result = get_preferred_communities(context, request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'yi')

class Test_get_my_communities(_Show_communities_helper, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.communities import get_my_communities
        return get_my_communities(context, request)

    def test_no_overflow(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        profiles = context['profiles'] = testing.DummyModel()
        profiles['foo'] = testing.DummyModel()
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
        
    def test_w_overflow(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel()
        profiles = context['profiles'] = testing.DummyModel()
        profiles['foo'] = testing.DummyModel()
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


class DummyAdapterWithTitle:

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.title = context.title


class DummyCommunityInfoAdapter(DummyAdapter):
    @property
    def member(self):
        return self.context._is_member

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


class RequestParamsWithGetall(dict):

    def getall(self, key):
        return self[key]

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
