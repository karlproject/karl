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

from karl import testing as karltesting

class EditCommunityViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from zope.interface import Interface
        from karl.security.interfaces import ISecurityWorkflow
        testing.registerAdapter(DummySecurityWorkflow, (Interface,),
                                ISecurityWorkflow)
        from karl.views.interfaces import IToolAddables
        testing.registerAdapter(DummyToolAddables, (Interface, Interface),
                                IToolAddables)

    def _callFUT(self, context, request):
        from karl.views.community import edit_community_view
        return edit_community_view(context, request)

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
        context.default_tool = 'overview'
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict({})
        renderer = testing.registerDummyRenderer(
            'templates/edit_community.pt')
        self._register()
        self._callFUT(context, request)
        self.assertEqual(renderer.fielderrors, {})
        self.assertEqual(renderer.fieldvalues['title'], 'thetitle')

    def test_submitted_invalid(self):
        from webob import MultiDict
        context = testing.DummyModel(title='oldtitle',
                                     default_tool='overview')
        context.__name__ = 'Community'
        request = testing.DummyRequest(MultiDict({'form.submitted':'1',
                                                  'default_tool':'foo'}))
        renderer = testing.registerDummyRenderer(
            'templates/edit_community.pt')
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.testing import registerListItem
        tool_factory = DummyToolFactory(present=True)
        registerListItem(IToolFactory, tool_factory, 'foo')
        self._register()
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
                      'sharing':False,
                      'default_tool': 'files',
                      }),
            )
        request.POST = request.params
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                            IObjectWillBeModifiedEvent))
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_community.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.title, u'Thetitle yo')
        self.assertEqual(context.description, 'thedescription')
        self.assertEqual(context.text, 'thetext')
        self.assertEqual(context.default_tool, 'files')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)
        self.assertEqual(context.transition_id, 'public')

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
                      'sharing':True,
                      'default_tool': 'files',
                      }),
            )
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                            IObjectWillBeModifiedEvent))
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_community.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.title, u'Thetitle yo')
        self.assertEqual(context.description, 'thedescription')
        self.assertEqual(context.text, 'thetext')
        self.assertEqual(context.default_tool, 'files')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)
        self.assertEqual(context.transition_id, 'private')

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
                      'sharing':True,
                      'calendar':'calendar',
                      'default_tool': 'overview',
                      }),
            )
        blog_tool_factory = DummyToolFactory(present=True)
        testing.registerUtility(blog_tool_factory, IToolFactory, name='blog')
        calendar_tool_factory = DummyToolFactory(present=False)
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_community.pt')
        testing.registerUtility(calendar_tool_factory, IToolFactory,
                                name='calendar')
        response = self._callFUT(context, request)
        self.assertEqual(blog_tool_factory.removed, True)
        self.assertEqual(calendar_tool_factory.added, True)

class ShowCommunityViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _callFUT(self, context, request):
        from karl.views.community import show_community_view
        self._register()
        return show_community_view(context, request)

    def test_it(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        context = testing.DummyModel(title='thetitle')
        directlyProvides(context, ICommunity)
        context.member_names = context.moderator_names = set()
        foo = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/community.pt')
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import IGridEntryInfo
        from karl.models.adapters import CatalogSearch
        catalog = karltesting.DummyCatalog({1:'/foo'})
        testing.registerModels({'/foo':foo})
        context.catalog = catalog
        testing.registerAdapter(DummyGridEntryAdapter, (Interface, Interface),
                                IGridEntryInfo)
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 3)
        self.assertEqual(renderer.actions, [
            ('Edit', 'edit.html'),
            ('Join', 'join.html'),
            ('Delete', 'delete.html'),
        ])
        recent_items = renderer.recent_items

    def test_already_member(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        context = testing.DummyModel(title='thetitle')
        context.member_names = set(('userid',))
        context.moderator_names = set()
        directlyProvides(context, ICommunity)
        foo = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/community.pt')
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import IGridEntryInfo
        from karl.models.adapters import CatalogSearch
        catalog = karltesting.DummyCatalog({1:'/foo'})
        testing.registerModels({'/foo':foo})
        context.catalog = catalog
        testing.registerAdapter(DummyGridEntryAdapter, (Interface, Interface),
                                IGridEntryInfo)
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        testing.registerDummySecurityPolicy('userid')
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 2)
        self.assertEqual(renderer.actions, [
            ('Edit', 'edit.html'),
            ('Delete', 'delete.html'),
        ])
        
class RedirectCommunityViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.community import redirect_community_view
        return redirect_community_view(context, request)
    
    def test_it(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        context = testing.DummyModel()
        directlyProvides(context, ICommunity)
        context.default_tool = 'murg'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/murg')
        
    def test_it_notool(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        context = testing.DummyModel()
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/view.html')
        
class JoinCommunityViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.community import join_community_view
        return join_community_view(context, request)
    
    def test_show_form(self):
        c = karltesting.DummyCommunity()
        site = c.__parent__.__parent__
        profiles = site["profiles"] = testing.DummyModel()
        profiles["user"] = karltesting.DummyProfile()
        renderer = testing.registerDummyRenderer("templates/join_community.pt")
        testing.registerDummySecurityPolicy("user")
        request = testing.DummyRequest()
        self._callFUT(c, request)
        self.assertEqual(renderer.profile, profiles["user"])
        self.assertEqual(renderer.community, c)
        self.assertEqual(
            renderer.post_url, 
            "http://example.com/communities/community/join.html"
        )
        
    def test_submit_form(self):
        #from zope.interface import Interface
        #from karl.models.interfaces import ICommunityInfo
        #testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                #ICommunityInfo)
        testing.registerDummyRenderer("templates/join_community.pt")
        
        c = karltesting.DummyCommunity()
        c.moderator_names = set(["moderator1", "moderator2"])
        site = c.__parent__.__parent__
        profiles = site["profiles"] = testing.DummyModel()
        profiles["user"] = karltesting.DummyProfile()
        profiles["moderator1"] = karltesting.DummyProfile()
        profiles["moderator2"] = karltesting.DummyProfile()

        from repoze.sendmail.interfaces import IMailDelivery
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery) 
        
        testing.registerDummySecurityPolicy("user")
        request = testing.DummyRequest({
            "form.submitted": "1",
            "message": "Message text.",
        })
        response = self._callFUT(c, request)

        self.assertEqual(response.location,
            "http://example.com/communities/community/?status_message=Your+request+has+been+sent+to+the+moderators.")
        self.assertEqual(len(mailer), 1)
        msg = mailer.pop()
        self.assertEqual(msg.mto, ["moderator1@x.org", 
                                   "moderator2@x.org"])
        self.assertEqual(msg.mfrom, "user@x.org")
        
class DeleteCommunityViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.community import delete_community_view
        return delete_community_view(context, request)

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import ICatalogSearch
        from karl.models.adapters import CatalogSearch
        testing.registerAdapter(DummyAdapter, (Interface, Interface),
                                ICommunityInfo)
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)

    def test_not_confirmed(self):
        from karl.testing import registerLayoutProvider
        registerLayoutProvider()

        request = testing.DummyRequest()
        context = testing.DummyModel(title='oldtitle')
        context.__name__  = 'thename'
        context.catalog = karltesting.DummyCatalog({})
        context.users = karltesting.DummyUsers({})
        renderer = testing.registerDummyRenderer('templates/delete_resource.pt')
        self._register()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')

    def test_confirmed(self):
        request = testing.DummyRequest({'confirm':'1'})
        context = testing.DummyModel(title='oldtitle')
        parent = DummyParent()
        parent['thename'] = context
        parent.catalog = karltesting.DummyCatalog({})
        parent.users = karltesting.DummyUsers({})
        renderer = testing.registerDummyRenderer('templates/delete_resource.pt')
        self._register()
        testing.registerDummySecurityPolicy('userid')
        response = self._callFUT(context, request)
        self.assertEqual(parent.deleted, 'thename')
        self.assertEqual(response.location, 'http://example.com/')

class DummyToolFactory:
    def __init__(self, present=False):
        self.present = present

    def add(self, context, request):
        self.added = True

    def remove(self, context, request):
        self.removed = True

    def is_present(self, context, request):
        return self.present

class DummyParent(testing.DummyModel):
    def __delitem__(self, name):
        self.deleted = name

class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyTagQuery(DummyAdapter):
    tagswithcounts = []
    docid = 'ABCDEF01'

class DummySecurityWorkflow:
    def __init__(self, context):
        self.context = context

    def updateState(self, **kw):
        if kw['sharing']:
            self.context.transition_id = 'private'
        else:
            self.context.transition_id = 'public'

    def getStateMap(self):
        return {}

class DummyGridEntryAdapter(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
class DummyToolAddables(DummyAdapter):
    def __call__(self):
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.listitem import get_listitems
        return get_listitems(IToolFactory)
