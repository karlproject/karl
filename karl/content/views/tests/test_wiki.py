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

import datetime
import mock
import unittest
from pyramid.testing import cleanUp
from zope.interface import implements

from pyramid import testing

import karl.testing

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

class Test_redirect_to_add_form(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.content.views.wiki import redirect_to_add_form
        return redirect_to_add_form(context, request)

    def test_it(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                         'http://example.com/add_wikipage.html')

class TestAddWikiPageFormController(unittest.TestCase):
    def _makeOne(self, context, request):
        from karl.content.views.wiki import AddWikiPageFormController
        return AddWikiPageFormController(context, request)

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
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
        self.failUnless('api' in response)
        self.failUnless(response['api'].page_title)

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
        karl.testing.registerDummySecurityPolicy('userid')
        class Alerts(object):
            def __init__(self):
                self.emitted = []

            def emit(self, context, request):
                self.emitted.append((context, request))
        alerts = Alerts()
        karl.testing.registerUtility(alerts, IAlerts)
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
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)

    def test_frontpage(self):
        self._register()
        context = testing.DummyModel()
        context.__name__ = 'front_page'
        context.title = 'Page'
        from karl.testing import DummyCommunity
        context.__parent__ = DummyCommunity()
        request = testing.DummyRequest()
        request.layout_manager = mock.Mock()
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 2)
        self.assertEqual(response['actions'][0][1], 'edit.html')
        # Front page should not have backlink breadcrumb thingy
        self.assert_(response['backto'] is False)

    def test_otherpage(self):
        self._register()
        context = testing.DummyModel(title='Other Page')
        context.__parent__ = testing.DummyModel(title='Front Page')
        context.__parent__.__name__ = 'front_page'
        context.__name__ = 'other_page'
        request = testing.DummyRequest()
        request.layout_manager = mock.Mock()
        from webob.multidict import MultiDict
        request.params = request.POST = MultiDict()
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 3)
        self.assertEqual(response['actions'][0][1], 'edit.html')
        self.assertEqual(response['actions'][1][1], 'delete.html')
        # Backlink breadcrumb thingy should appear on non-front-page
        self.assert_(response['backto'] is not False)

    def test_otherpage_w_repo(self):
        self._register()
        context = testing.DummyModel(title='Other Page')
        context.__parent__ = testing.DummyModel(title='Front Page')
        context.__parent__.__name__ = 'front_page'
        context.__name__ = 'other_page'
        context.repo = object()
        request = testing.DummyRequest()
        request.layout_manager = mock.Mock()
        from webob.multidict import MultiDict
        request.params = request.POST = MultiDict()
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 3)
        self.assertEqual(response['actions'][0][1], 'edit.html')
        self.assertEqual(response['actions'][1][1], 'delete.html')
        # Backlink breadcrumb thingy should appear on non-front-page
        self.assert_(response['backto'] is not False)


class TestShowWikitocView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.wiki import show_wikitoc_view
        return show_wikitoc_view(context, request)

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)

        from karl.models.interfaces import ICatalogSearch
        karl.testing.registerAdapter(DummySearch, (Interface, ),
                                     ICatalogSearch)


    def test_frontpage(self):
        self._register()
        context = DummyWikiPage()
        context.__name__ = 'front_page'
        context.title = 'Page'
        from karl.testing import DummyCommunity
        context.__parent__ = DummyCommunity()
        from karl.testing import DummyCatalog
        context.__parent__.catalog = DummyCatalog()
        request = testing.DummyRequest()
        request.layout_manager = mock.Mock(
            layout=mock.Mock(head_data={})
            )
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 0)
        self.assertEqual(response['backto'], False)
        self.assertEqual(response['head_data'],
            '<script type="text/javascript">\nwindow._karl_client_data = '
            '{"wikitoc": {"items": [{"name": "WIKIPAGE", "author": "", "tags": '
            '[], "modified": "2011-08-20T00:00:00", "author_name": "", '
            '"created": "2011-08-20T00:00:00", "title": "", "id": '
            '"id_WIKIPAGE", "profile_url": "http://example.com/"}]}};\n'
            '</script>')

    def test_otherpage(self):
        self._register()
        context = DummyWikiPage(title='Other Page')
        context.__name__ = 'other_page'
        from karl.testing import DummyCommunity
        context.__parent__ = DummyCommunity()
        from karl.testing import DummyCatalog
        context.__parent__.catalog = DummyCatalog()
        request = testing.DummyRequest()
        from webob.multidict import MultiDict
        request.params = request.POST = MultiDict()
        request.layout_manager = mock.Mock(
            layout=mock.Mock(head_data={})
            )
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 0)
        self.assertEqual(response['backto'], {
            'href': 'http://example.com/communities/community/',
            'title': u'Dummy Communit\xe0',
            })
        self.assertEqual(response['head_data'],
            '<script type="text/javascript">\nwindow._karl_client_data = '
            '{"wikitoc": {"items": [{"name": "WIKIPAGE", "author": "", "tags": '
            '[], "modified": "2011-08-20T00:00:00", "author_name": "", '
            '"created": "2011-08-20T00:00:00", "title": "", "id": '
            '"id_WIKIPAGE", "profile_url": "http://example.com/"}]}};\n'
            '</script>')


class TestEditWikiPageFormController(unittest.TestCase):
    def _makeOne(self, context, request):
        from karl.content.views.wiki import EditWikiPageFormController
        return EditWikiPageFormController(context, request)

    def setUp(self):
        cleanUp()


    def tearDown(self):
        cleanUp()

    def _register(self):
        from pyramid import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
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
        from pyramid.interfaces import IRequest
        karl.testing.registerAdapter(WikiPageAlert,
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
        from karl.testing import DummyRoot
        self._register()
        site = DummyRoot()
        context = testing.DummyModel()
        context.title = 'title'
        site['foo'] = context
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')

    def test_handle_cancel(self):
        self._register()
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
        L = karl.testing.registerEventListener(
            (Interface, IObjectModifiedEvent))
        karl.testing.registerDummySecurityPolicy('testeditor')
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
        L = karl.testing.registerEventListener(
            (Interface, IObjectModifiedEvent))
        karl.testing.registerDummySecurityPolicy('testeditor')
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

    def test__call__lock(self):
        from karl.utilities import lock
        from karl.testing import DummyRoot
        self._register()
        site = DummyRoot()
        context = testing.DummyModel()
        context.title = 'title'
        site['foo'] = context
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless(context.lock)

    def test_handle_cancel_lock(self):
        from datetime import datetime
        self._register()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        context.lock = {'time': datetime.now()}
        response = controller.handle_cancel()
        self.failIf(context.lock)

    def test_handle_submit_lock(self):
        from datetime import datetime
        from karl.testing import DummyCatalog
        self._register()
        converted = {
            'text':'text',
            'title':'title',
            'sendalert': False,
            'security_state': 'public',
            'tags': 'thetesttag',
            }
        context = testing.DummyModel(title='oldtitle')
        request = testing.DummyRequest()
        def change_title(newtitle):
            context.title = newtitle
        context.change_title = change_title
        context.catalog = DummyCatalog()

        controller = self._makeOne(context, request)
        context.lock = {'time': datetime.now()}
        response = controller.handle_submit(converted)
        self.failIf(context.lock)


class Test_preview_wikipage_view(unittest.TestCase):

    def setUp(self):
        cleanUp()

        from karl.content.views import wiki
        self._save_transaction = wiki.transaction
        wiki.transaction = DummyTransactionManager()

    def tearDown(self):
        cleanUp()

        from karl.content.views import wiki
        wiki.transaction = self._save_transaction

    def _callFUT(self, context, request):
        from karl.content.views.wiki import preview_wikipage_view as fut
        return fut(context, request, WikiPage=DummyWikiPage)

    def test_front_page(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        context = testing.DummyModel(docid=5)
        directlyProvides(context, ICommunity)
        context.title = 'Foo'
        context.__name__ = 'front_page'
        context.repo = DummyArchive()
        context['profiles'] = profiles = testing.DummyModel()
        profiles['fred'] = testing.DummyModel(title='Fred')
        request = testing.DummyRequest(params={'version_num': '2'})
        response = self._callFUT(context, request)
        self.assertEqual(response['author'], 'Fred')
        self.assertEqual(response['title'], 'Foo Community Wiki Page')
        self.assertEqual(response['body'], 'COOKED: Reverted 2')

    def test_non_front_page(self):
        context = testing.DummyModel(docid=5)
        context.title = 'Foo'
        context.__name__ = 'foo'
        context.repo = DummyArchive()
        context['profiles'] = profiles = testing.DummyModel()
        profiles['fred'] = testing.DummyModel(title='Fred')
        request = testing.DummyRequest(params={'version_num': '2'})
        response = self._callFUT(context, request)
        self.assertEqual(response['author'], 'Fred')
        self.assertEqual(response['title'], 'Title 2')
        self.assertEqual(response['body'], 'COOKED: Reverted 2')

    def test_no_such_version(self):
        from pyramid.exceptions import NotFound
        context = testing.DummyModel(docid=5)
        context.title = 'Foo'
        context.__name__ = 'foo'
        context.repo = DummyArchive()
        context['profiles'] = profiles = testing.DummyModel()
        profiles['fred'] = testing.DummyModel(title='Fred')
        request = testing.DummyRequest(params={'version_num': '3'})
        self.assertRaises(NotFound, self._callFUT, context, request)


class TestUnlockView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, userid=None):
        from karl.content.views.wiki import unlock_wiki_view
        return unlock_wiki_view(context, request, userid)

    def test_get(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(302, response.status_int)
        self.assertEqual('http://example.com/', response.location)

    def test_post_has_lock(self):
        from datetime import datetime
        context = testing.DummyModel()
        request = testing.DummyRequest(post={})
        context.lock = {'time': datetime.now(), 'userid': 'foo'}
        response = self._callFUT(context, request, userid='foo')
        self.assertEqual(200, response.status_int)
        self.failIf(context.lock)

    def test_post_does_not_have_lock(self):
        from datetime import datetime
        context = testing.DummyModel()
        request = testing.DummyRequest(post={})
        context.lock = {'time': datetime.now(), 'userid': 'foo'}
        response = self._callFUT(context, request, userid='bar')
        self.assertEqual(200, response.status_int)
        self.failUnless(context.lock)


from karl.content.interfaces import IWikiPage

class DummyWikiPage:
    implements(IWikiPage)
    __name__ = 'WIKIPAGE'
    def __init__(self, title='', text='', description='', creator=''):
        self.title = title
        self.text = text
        self.description = description
        self.creator = creator
        self.created = datetime.datetime(2011, 8, 20)
        self.modified = datetime.datetime(2011, 8, 20)

    def get_attachments(self):
        return self

    def revert(self, version):
        self.text = 'Reverted %d' % version.version_num
        self.title = 'Title %d' % version.version_num

    def cook(self, request):
        return 'COOKED: ' + self.text


dummywikipage = DummyWikiPage()

class DummySearch:
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        return 1, [1], lambda x: dummywikipage


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

class DummyArchive(object):

    def history(self, docid):
        import datetime
        return [Dummy(
            version_num=2,
            user='fred',
            archive_time=datetime.datetime(2010, 5, 12, 2, 42),
        )]

class Dummy(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

class DummyTransactionManager(object):
    def doom(self):
        pass
