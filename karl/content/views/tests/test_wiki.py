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

class TestAddWikipageView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        testing.registerUtility(self.mailer, IMailDelivery)

        # Register WikiPageAlert adapter
        from karl.models.interfaces import IProfile
        from karl.content.interfaces import IWikiPage
        from karl.content.views.adapters import WikiPageAlert
        from karl.utilities.interfaces import IAlert
        from repoze.bfg.interfaces import IRequest
        testing.registerAdapter(WikiPageAlert,
                                (IWikiPage, IProfile, IRequest),
                                IAlert)

        # Create dummy site skel
        from karl.testing import DummyCommunity
        self.community = DummyCommunity()
        self.site = self.community.__parent__.__parent__
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        self.profiles = testing.DummyModel()
        self.site["profiles"] = self.profiles
        from karl.testing import DummyProfile
        self.profiles["a"] = DummyProfile()
        self.profiles["b"] = DummyProfile()
        self.profiles["c"] = DummyProfile()
        self.profiles["userid"] = DummyProfile()
        for profile in self.profiles.values():
            profile["alerts"] = testing.DummyModel()

        self.community.member_names = set(["b", "c",])
        self.community.moderator_names = set(["a",])

        self.wiki = testing.DummyModel()
        self.community["wiki"] = self.wiki


    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.wiki import add_wikipage_view
        return add_wikipage_view(context, request)

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def test_get_with_no_title(self):
        renderer = testing.registerDummyRenderer(
            'templates/add_wikipage.pt')
        request = testing.DummyRequest()
        from webob import MultiDict
        request.params = request.POST = MultiDict()
        context = testing.DummyModel()
        self._registerSecurityWorkflow()
        self.assertRaises(ValueError, self._callFUT, context, request)

    def test_notsubmitted_withtitle(self):
        renderer = testing.registerDummyRenderer(
            'templates/add_wikipage.pt')
        from webob import MultiDict
        params = MultiDict({
                    'title': 'yo!',
                    })
        request = testing.DummyRequest()
        request.POST = request.params = params
        context = testing.DummyModel()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_valid(self):
        renderer = testing.registerDummyRenderer(
            'templates/add_wikipage.pt')
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title':'wikipage',
                    'text':'text',
                    'sendalert':True,
                    'security_state':'public',
                    'tags': 'thetesttag',
                    })
            )
        context = self.wiki
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IWikiPage
        registerContentFactory(DummyWikiPage, IWikiPage)
        testing.registerDummySecurityPolicy('userid')
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        wikipage = context['wikipage']
        self.assertEqual(wikipage.title, 'wikipage')
        self.assertEqual(wikipage.text, 'text')
        self.assertEqual(wikipage.creator, 'userid')
        self.assertEqual(response.location,
                         'http://example.com/communities/community/wiki/wikipage/?status_message=Wiki%20Page%20created')

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
        from webob import MultiDict
        request.params = request.POST = MultiDict()
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 2)
        self.assertEqual(renderer.actions[0][1], 'edit.html')
        self.assertEqual(renderer.actions[1][1], 'delete.html')
        # Backlink breadcrumb thingy should appear on non-front-page
        self.assert_(renderer.backto is not False)

class TestEditWikipageView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.wiki import edit_wikipage_view
        return edit_wikipage_view(context, request)

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def test_notsubmitted(self):
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_wikipage.pt')
        request = testing.DummyRequest()
        from webob import MultiDict
        request.params = request.POST = MultiDict()
        context = testing.DummyModel(__name__ = 'Page',
                                     title = 'title',
                                     text = 'text',
                                     )
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_wikipage.pt')
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = testing.DummyModel(title='oldtitle', __name__='Page',
                                     text='thetext'
                                     )
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        from karl.testing import DummyCatalog
        self._register()
        renderer = testing.registerDummyRenderer('templates/edit_wikipage.pt')
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'text':'text',
                    'title':'oldtitle',
                    'sendalert': True,
                    'security_state': 'public',
                    'tags': 'thetesttag',
                    })
            )
        context = testing.DummyModel(title='oldtitle')
        context.text = 'oldtext'

        context.catalog = DummyCatalog()
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Wiki%20Page%20edited')
        self.assertEqual(context.text, 'text')
        self.assertEqual(context.modified_by, 'testeditor')

    def test_submitted_valid_titlechange(self):
        from karl.testing import DummyCatalog
        self._register()
        renderer = testing.registerDummyRenderer('templates/edit_wikipage.pt')
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'text':'text',
                    'title':'newtitle',
                    'sendalert': True,
                    'security_state': 'public',
                    })
            )
        context = testing.DummyModel(title='oldtitle')
        context.text = 'oldtext'
        def change_title(newtitle):
            context.title = newtitle
        context.change_title = change_title
        context.catalog = DummyCatalog()
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Wiki%20Page%20edited')
        self.assertEqual(context.text, 'text')
        self.assertEqual(context.modified_by, 'testeditor')
        self.assertEqual(context.title, 'newtitle')

    def test_submitted_invalid_titlechange(self):
        self._register()
        renderer = testing.registerDummyRenderer('templates/edit_wikipage.pt')
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'text':'text',
                    'title':'newtitle',
                    'sendalert': True,
                    'security_state': 'public',
                    })
            )
        context = testing.DummyModel(title='oldtitle')
        context.text = 'oldtext'
        def change_title(newtitle):
            raise ValueError('boo')
        context.change_title = change_title
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

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

class DummySecurityWorkflow:
    def __init__(self, context):
        self.context = context

    def setInitialState(self, request, **kw):
        pass

    def updateState(self, request, **kw):
        pass

    def getStateMap(self):
        return {}

