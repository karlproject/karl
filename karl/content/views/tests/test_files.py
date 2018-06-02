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
import mock

from zope.interface import Interface
from zope.interface import taggedValue
from pyramid.testing import cleanUp

from pyramid import testing

from karl.testing import DummyCatalog
from karl.testing import DummyFolderCustomizer
from karl.testing import DummyFolderAddables
from karl.testing import DummyTagQuery
from karl.testing import registerLayoutProvider

import karl.testing

class TestShowFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import show_folder_view
        return show_folder_view(context, request)

    def _register(self, permissions=None):
        from karl.content.views.interfaces import IFileInfo
        karl.testing.registerAdapter(DummyFileInfo, (Interface, Interface),
                                     IFileInfo)
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)

        # Register dummy IFolderAddables
        from karl.views.interfaces import IFolderAddables
        karl.testing.registerAdapter(DummyFolderAddables,
                                     (Interface, Interface),
                                     IFolderAddables)

        if permissions is not None:
            from pyramid.interfaces import IAuthenticationPolicy
            from pyramid.interfaces import IAuthorizationPolicy
            policy = DummySecurityPolicy("userid", permissions=permissions)
            karl.testing.registerUtility(policy, IAuthenticationPolicy)
            karl.testing.registerUtility(policy, IAuthorizationPolicy)

    def _make_community(self):
        # Register dummy catalog search
        # (the folder view needs it for the reorganize widget)
        from karl.models.interfaces import ICatalogSearch
        karl.testing.registerAdapter(DummySearch, (Interface, ),
                                ICatalogSearch)

        # factorize a fake community
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        community = testing.DummyModel(title='thecommunity')
        directlyProvides(community, ICommunity)
        community.catalog = MyDummyCatalog()
        return community

    def test_notcommunityrootfolder(self):
        self._register()
        community = self._make_community()
        folder = testing.DummyModel(title='parent')
        community['files'] = folder
        context = testing.DummyModel(title='thetitle')
        folder['child'] = context
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        actions = response['actions']
        self.assertEqual(len(actions), 6)
        self.assertEqual(actions[0][1], 'add_folder.html')
        self.assertEqual(actions[1][1], 'add_file.html')
        self.assertEqual(actions[2][1][-9:], 'edit.html')
        self.assertEqual(actions[3][1][-11:], 'delete.html')

    def test_communityrootfolder(self):
        from karl.content.interfaces import ICommunityRootFolder
        from zope.interface import directlyProvides
        self._register()
        community = self._make_community()
        context = testing.DummyModel(title='thetitle')
        community['files'] = context
        request = testing.DummyRequest()
        directlyProvides(context, ICommunityRootFolder)
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        actions = response['actions']
        self.assertEqual(len(actions), 4)
        self.assertEqual(actions[0][1], 'add_folder.html')
        self.assertEqual(actions[1][1], 'add_file.html')

    def test_read_only(self):
        root = self._make_community()
        root['files'] = context = testing.DummyModel(title='thetitle')
        root['profiles'] = testing.DummyModel()
        self._register({context: ('view',),})
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        self.assertEqual(response['actions'], [])

    def test_editable_wo_repo(self):
        root = self._make_community()
        root['files'] = context = testing.DummyModel(title='thetitle')
        root['profiles'] = testing.DummyModel()
        self._register({context: ('view', 'edit'),})
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        self.assertEqual(response['actions'], [
            ('Edit', 'http://example.com/files/edit.html'),
            ])
        self.assertEqual(response['trash_url'], None)

    def test_editable_w_repo(self):
        root = self._make_community()
        root.repo = object()
        root['files'] = context = testing.DummyModel(title='thetitle')
        root['profiles'] = testing.DummyModel()
        self._register({context: ('view', 'edit'),})
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        self.assertEqual(response['actions'], [
            ('Edit', 'http://example.com/files/edit.html'),
            ])
        self.assertEqual(response['trash_url'], 'http://example.com/trash')

    def test_deletable(self):
        root = self._make_community()
        root['files'] = context = testing.DummyModel(title='thetitle')
        root['profiles'] = testing.DummyModel()
        self._register({context.__parent__: ('view', 'delete'),})
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        self.assertEqual(response['actions'], [
            ('Delete', 'http://example.com/files/delete.html'),
            ])

    def test_delete_is_for_children_not_container(self):
        root = self._make_community()
        root['files'] = context = testing.DummyModel(title='thetitle')
        root['profiles'] = testing.DummyModel()
        self._register({context: ('view', 'delete'),})
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        self.assertEqual(response['actions'], [])

    def test_creatable(self):
        root = self._make_community()
        root['files'] = context = testing.DummyModel(title='thetitle')
        root['profiles'] = testing.DummyModel()
        self._register({context: ('view', 'create'),})
        request = testing.DummyRequest()
        with mock.patch.object(request, 'static_url', mock.Mock()) as _static_url:
            _static_url.return_value = 'http://foo.bar/boo/static'
            response = self._callFUT(context, request)
        self.assertEqual(response['actions'], [
            ('Add Folder', 'add_folder.html'), ('Add File', 'add_file.html'),
            ('Multi Upload', '')])


class Test_redirect_to_add_form(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.content.views.files import redirect_to_add_form
        return redirect_to_add_form(context, request)

    def test_it(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                         'http://example.com/add_file.html')

class TestAddFolderFormController(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        registerLayoutProvider()

    def tearDown(self):
        testing.tearDown()

    def _register(self):
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # Register dummy IFolderCustomizer
        from karl.content.views.interfaces import IFolderCustomizer
        karl.testing.registerAdapter(DummyFolderCustomizer,
                                     (Interface, Interface),
                                     IFolderCustomizer)

    def _makeOne(self, *arg, **kw):
        from karl.content.views.files import AddFolderFormController
        return AddFolderFormController(*arg, **kw)

    def _registerDummyWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_form_defaults(self):
        workflow = self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], '')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['security_state'], workflow.initial_state)

    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('title' in dict(fields))
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('title' in widgets)

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
        self._register()
        self._registerDummyWorkflow()

        karl.testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        context.tags = DummyTagEngine()
        converted = {
            'title':'a title',
            'security_state': 'private',
            'tags': ['thetesttag'],
            }
        from karl.content.interfaces import ICommunityFolder
        from repoze.lemonade.interfaces import IContentFactory
        karl.testing.registerAdapter(lambda *arg: DummyCommunityFolder,
                                (ICommunityFolder,),
                                IContentFactory)
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/a-title/')
        self.assertEqual(context['a-title'].title, u'a title')
        self.assertEqual(context['a-title'].userid, 'userid')
        self.assertEqual(context.tags.updated,
            [(None, 'userid', ['thetesttag'])])

class TestDeleteFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, delegate):
        from karl.content.views.files import delete_folder_view
        return delete_folder_view(context, request, delegate)

    def test_it(self):
        dummy_calls = []
        def dummy_delete_resource_view(context, request, num_children):
            dummy_calls.append((context, request, num_children))

        context = testing.DummyModel()
        context['foo'] = testing.DummyModel()
        context['bar'] = testing.DummyModel()
        request = 'Dummy'

        self._callFUT(context, request, dummy_delete_resource_view)
        self.assertEqual(dummy_calls, [(context, request, 2)])

class TestAddFileFormController(unittest.TestCase):
    def setUp(self):
        cleanUp()
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request, check_upload_size=None):
        from karl.content.views.files import AddFileFormController
        controller = AddFileFormController(context, request)
        if check_upload_size is not None:
            controller.check_upload_size = check_upload_size
        return controller

    def _register(self):
        from karl.models.interfaces import ITagQuery
        from karl.content.views.interfaces import IShowSendalert
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)
        karl.testing.registerAdapter(DummyShowSendalert, (Interface, Interface),
                                     IShowSendalert)

        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        karl.testing.registerUtility(self.mailer, IMailDelivery)

        from karl.content.views.adapters import CommunityFileAlert
        from karl.content.interfaces import ICommunityFile
        from karl.models.interfaces import IProfile
        from pyramid.interfaces import IRequest
        from karl.utilities.interfaces import IAlert
        karl.testing.registerAdapter(CommunityFileAlert,
                                     (ICommunityFile, IProfile, IRequest),
                                     IAlert)

    def _registerDummyWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        return request

    def _makeContext(self):
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        return context

    def test_form_defaults(self):
        self._register()
        workflow = self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], '')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['file'], None)
        self.assertEqual(defaults['sendalert'], True)
        self.assertEqual(defaults['security_state'], workflow.initial_state)

    def test_form_defaults_w_community_sendalert_default(self):
        from karl.testing import DummyCommunity
        self._register()
        workflow = self._registerDummyWorkflow()
        community = DummyCommunity()
        community.sendalert_default = False
        context = community['testing'] = self._makeContext()
        community.__parent__.__parent__.sessions = context.__dict__.pop(
                                                        'sessions')
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], '')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['file'], None)
        self.assertEqual(defaults['sendalert'], False)
        self.assertEqual(defaults['security_state'], workflow.initial_state)

    def test_form_fields(self):
        self._register()
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        fields = dict(controller.form_fields())
        self.failUnless('tags' in fields)
        self.failUnless('security_state' in fields)
        self.failUnless('title' in fields)
        self.failUnless('file' in fields)
        self.failUnless('sendalert' in fields)

    def test_form_widgets(self):
        self._register()
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True,
                                           'sendalert':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('file' in widgets)
        self.failUnless('title' in widgets)
        self.failUnless('sendalert' in widgets)
        self.failUnless('tags' in widgets)

    def test___call__(self):
        self._register()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('api' in response)
        self.failUnless('layout' in response)
        self.failUnless(response['api'].page_title)

    def test_handle_cancel(self):
        self._register()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit_filename_with_only_symbols(self):
        from pyramid_formish import ValidationError
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        self._register()

        karl.testing.registerDummySecurityPolicy('userid')
        context = self._makeContext()
        context.catalog = DummyCatalog()
        from schemaish.type import File as SchemaFile
        fs = SchemaFile(None, None, '???')
        request = self._makeRequest()
        converted = {
            'file': fs,
            'title': 'a title',
            'sendalert': '0',
            'security_state': 'private',
            'tags':[],
            }
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        controller = self._makeOne(context, request)
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_valid(self):
        from schemaish.type import File as SchemaFile
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        self._register()

        karl.testing.registerDummySecurityPolicy('userid')
        context = self._makeContext()
        context.catalog = DummyCatalog()
        fs = SchemaFile('abc', 'filename', 'x/foo')
        converted = {
            'file': fs,
            'title': 'a title',
            'sendalert': False,
            'security_state': 'public',
            'tags':['thetesttag'],
            }
        request = self._makeRequest()
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/filename/')
        self.assertEqual(context['filename'].title, u'a title')
        self.assertEqual(context['filename'].creator, 'userid')
        self.assertEqual(context['filename'].stream, 'abc')
        self.assertEqual(context['filename'].mimetype, 'x/foo')
        self.assertEqual(context['filename'].filename, 'filename')

        # attempt a duplicate upload
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/filename-1/')
        self.assertEqual(context['filename-1'].title, u'a title')
        self.assertEqual(context['filename-1'].creator, 'userid')
        self.assertEqual(context['filename-1'].stream, 'abc')
        self.assertEqual(context['filename-1'].mimetype, 'x/foo')
        self.assertEqual(context['filename-1'].filename, 'filename')

    def test_handle_submit_filename_with_only_symbols_and_smartquote(self):
        from pyramid_formish import ValidationError
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        self._register()

        karl.testing.registerDummySecurityPolicy('userid')
        context = self._makeContext()
        context.catalog = DummyCatalog()
        from schemaish.type import File as SchemaFile
        fs = SchemaFile(None, None, u'??\u2019')
        request = self._makeRequest()
        converted = {
            'file': fs,
            'title': 'a title',
            'sendalert': '0',
            'security_state': 'private',
            'tags':[],
            }
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        controller = self._makeOne(context, request)
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_full_path_filename(self):
        from schemaish.type import File as SchemaFile
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        self._register()

        karl.testing.registerDummySecurityPolicy('userid')
        context = self._makeContext()
        context.catalog = DummyCatalog()
        fs = SchemaFile('abc', r"C:\Documents and Settings\My Tests\filename",
                        'x/foo')
        converted = {
            'file': fs,
            'title': 'a title',
            'sendalert': False,
            'security_state': 'public',
            'tags':['thetesttag'],
            }
        request = self._makeRequest()
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/filename/')
        self.assertEqual(context['filename'].title, u'a title')
        self.assertEqual(context['filename'].creator, 'userid')
        self.assertEqual(context['filename'].stream, 'abc')
        self.assertEqual(context['filename'].mimetype, 'x/foo')
        self.assertEqual(context['filename'].filename, 'filename')

        # attempt a duplicate upload
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/filename-1/')
        self.assertEqual(context['filename-1'].title, u'a title')
        self.assertEqual(context['filename-1'].creator, 'userid')
        self.assertEqual(context['filename-1'].stream, 'abc')
        self.assertEqual(context['filename-1'].mimetype, 'x/foo')
        self.assertEqual(context['filename-1'].filename, 'filename')


    def test_handle_submit_valid_alert(self):
        self._register()

        karl.testing.registerDummySecurityPolicy('userid')

        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        from karl.testing import DummyProfile
        context = testing.DummyModel(title='title')
        directlyProvides(context, ICommunity)
        context.member_names = set(['a', 'b'])
        context.moderator_names = set(['c'])
        profiles = context["profiles"] = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["b"] = DummyProfile()
        profiles["c"] = DummyProfile()
        profiles["userid"] = DummyProfile()

        context.catalog = DummyCatalog()
        context.sessions = DummySessions()
        request = self._makeRequest()
        from schemaish.type import File as SchemaFile
        fs = SchemaFile('abc', 'filename', 'x/foo')
        converted = {
            'file': fs,
            'title': 'a title',
            'sendalert': True,
            'security_state': 'public',
            'tags':[],
            }
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        controller = self._makeOne(context, request)
        karl.testing.registerDummyRenderer(
            'karl.content.views:templates/email_community_file_alert.pt')
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/filename/')
        self.assertEqual(context['filename'].title, u'a title')
        self.assertEqual(context['filename'].creator, 'userid')
        self.assertEqual(context['filename'].stream, 'abc')
        self.assertEqual(context['filename'].mimetype, 'x/foo')
        self.assertEqual(context['filename'].filename, 'filename')

        self.assertEqual(3, len(self.mailer))

    def test_submitted_toobig(self):
        self._register()

        from pyramid_formish import ValidationError

        def check_upload_size(*args):
            raise ValidationError(file='TEST VALIDATION ERROR')

        karl.testing.registerDummySecurityPolicy('userid')
        context = self._makeContext()
        context.catalog = DummyCatalog()
        request = self._makeRequest()
        from schemaish.type import File as SchemaFile
        fs = SchemaFile('abc', 'filename', 'x/foo')
        converted = {
            'file': fs,
            'title': 'a title',
            'sendalert': False,
            'security_state': 'public',
            'tags':[],
            }
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        controller = self._makeOne(context, request, check_upload_size)
        self.assertRaises(ValidationError, controller.handle_submit, converted)

class TestShowFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import show_file_view
        return show_file_view(context, request)

    def _make_community(self):
        # factorize a fake community
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        community = testing.DummyModel(title='thecommunity')
        directlyProvides(community, ICommunity)
        community.catalog = MyDummyCatalog()
        return community

    def test_editable_wo_repo(self):
        from karl.content.views.interfaces import IFileInfo
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)
        root = self._make_community()
        parent = root['files'] = testing.DummyModel(title='parent')
        context = parent['child'] = testing.DummyModel(title='thetitle')
        context.filename = 'thefilename'
        request = testing.DummyRequest()
        renderer  = karl.testing.registerDummyRenderer('templates/show_file.pt')

        karl.testing.registerAdapter(DummyFileInfo, (Interface, Interface),
                                IFileInfo)

        self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0][1][-9:], 'edit.html')
        self.assertEqual(actions[1][1][-11:], 'delete.html')
        self.assertEqual(actions[2][1][-13:], 'advanced.html')

    def test_unicode_filename(self):
        from karl.content.views.interfaces import IFileInfo
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)
        root = self._make_community()
        parent = root['files'] = testing.DummyModel(title='parent')
        context = parent['child'] = testing.DummyModel(title='thetitle')
        context.filename = u'Bases T\xe9cnicas y anexos.pdf'
        request = testing.DummyRequest()
        renderer  = karl.testing.registerDummyRenderer('templates/show_file.pt')

        karl.testing.registerAdapter(DummyFileInfo, (Interface, Interface),
                                IFileInfo)

        self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0][1][-9:], 'edit.html')
        self.assertEqual(actions[1][1][-11:], 'delete.html')
        self.assertEqual(actions[2][1][-13:], 'advanced.html')

    def test_editable_w_repo(self):
        from karl.content.views.interfaces import IFileInfo
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)
        root = self._make_community()
        root.repo = object()
        parent = root['files'] = testing.DummyModel(title='parent')
        context = parent['child'] = testing.DummyModel(title='thetitle')
        context.filename = 'thefilename'
        request = testing.DummyRequest()
        renderer = karl.testing.registerDummyRenderer('templates/show_file.pt')

        karl.testing.registerAdapter(DummyFileInfo, (Interface, Interface),
                                     IFileInfo)

        self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(len(actions), 4)
        self.assertEqual(actions[0][1][-9:], 'edit.html')
        self.assertEqual(actions[1][1][-11:], 'delete.html')
        self.assertEqual(actions[2][1][-13:], 'advanced.html')
        self.assertEqual(actions[3][1][-12:], 'history.html')


class TestPreviewFile(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        from karl.content.views.files import preview_file
        context = testing.DummyModel()
        request = testing.DummyRequest({'version_num': '2'})
        response = preview_file(context, request)
        self.assertEqual(response,
            {'url': 'http://example.com/download_preview?version_num=2'})


class TestDownloadFilePreview(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def call_fut(self, context, request):
        from karl.content.views.files import download_file_preview as fut
        return fut(context, request)

    def test_it(self):
        context = testing.DummyModel(docid=1)
        context.repo = DummyArchive()
        request = testing.DummyRequest({'version_num': '2'})
        response = self.call_fut(context, request)
        self.assertEqual(response.body, 'TESTING')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.content_type, 'x-application/testing')

    def test_it_notfound(self):
        from pyramid.httpexceptions import HTTPNotFound
        context = testing.DummyModel(docid=1)
        context.repo = DummyArchive()
        request = testing.DummyRequest({'version_num': '3'})
        self.assertRaises(HTTPNotFound, self.call_fut, context, request)


class DummyArchive(object):
    from cStringIO import StringIO
    version_num = 2
    blobs = {'blob': StringIO('TESTING')}
    attrs = {'mimetype': 'x-application/testing',
             'filename': 'testing.test'}

    def history(self, docid):
        assert docid == 1
        yield self


class TestDownloadFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import download_file_view
        return download_file_view(context, request)

    def test_view(self):
        context = testing.DummyModel()
        blobfile = DummyBlobFile()
        context.blobfile = blobfile
        context.mimetype = 'x/foo'
        context.filename = 'thefilename'
        context.size = 42
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.headerlist[0],
                         ('Content-Type', 'x/foo'))
        self.assertEqual(response.headerlist[1],
                         ('Content-Length', '42'))
        self.assertEqual(response.app_iter, blobfile)

    def test_mimetype_is_unicode_for_some_reason(self):
        context = testing.DummyModel()
        blobfile = DummyBlobFile()
        context.blobfile = blobfile
        context.mimetype = u'x/foo'
        context.filename = 'thefilename'
        context.size = 42
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        _, content_type = response.headerlist[0]
        self.assertTrue(isinstance(content_type, str))

    def test_save(self):
        context = testing.DummyModel()
        blobfile = DummyBlobFile()
        context.blobfile = blobfile
        context.mimetype = 'x/foo'
        context.filename = 'thefilename'
        context.size = 42
        request = testing.DummyRequest(params=dict(save=1))
        response = self._callFUT(context, request)
        self.assertEqual(response.headerlist[0],
                         ('Content-Type', 'x/foo'))
        self.assertEqual(response.headerlist[1],
                         ('Content-Length', '42'))
        self.assertEqual(response.headerlist[2],
                         ('Content-Disposition',
                          'attachment; filename="thefilename"'))
        self.assertEqual(response.app_iter, blobfile)

    def test_save_filename_has_tabs_and_newlines(self):
        context = testing.DummyModel()
        blobfile = DummyBlobFile()
        context.blobfile = blobfile
        context.mimetype = 'x/foo'
        context.filename = 'the\nfile\tname'
        context.size = 42
        request = testing.DummyRequest(params=dict(save=1))
        response = self._callFUT(context, request)
        self.assertEqual(response.headerlist[0],
                         ('Content-Type', 'x/foo'))
        self.assertEqual(response.headerlist[1],
                         ('Content-Length', '42'))
        self.assertEqual(response.headerlist[2],
                         ('Content-Disposition',
                          'attachment; filename="the file name"'))
        self.assertEqual(response.app_iter, blobfile)

class TestThumbnailView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _get_context(self):
        # A little easier to do an integration test here.
        from pkg_resources import resource_stream
        from karl.content.models.files import CommunityFile
        return CommunityFile(
            'Title',
            resource_stream('karl.content.models.tests', 'test.jpg'),
            'image/jpeg',
            'test.jpg',
            'chris',
        )

    def _callFUT(self, context, request):
        from karl.content.views.files import thumbnail_view
        return thumbnail_view(context, request)

    def test_it(self):
        import PIL.Image
        from cStringIO import StringIO
        context = self._get_context()
        request = testing.DummyRequest()
        request.subpath = ('300x200.jpg',)

        response = self._callFUT(context, request)
        self.assertEqual(response.content_type, 'image/jpeg')
        image = PIL.Image.open(StringIO(response.body))
        self.assertEqual(image.size, (137, 200))

    def test_it_no_subpath(self):
        context = self._get_context()
        request = testing.DummyRequest()

        from pyramid.exceptions import NotFound
        self.assertRaises(NotFound, self._callFUT, context, request)

    def test_it_bad_subpath(self):
        context = self._get_context()
        request = testing.DummyRequest()
        request.subpath = ('fooxbar.jpg',)

        from pyramid.exceptions import NotFound
        self.assertRaises(NotFound, self._callFUT, context, request)

class TestEditFolderFormController(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        registerLayoutProvider()

    def tearDown(self):
        testing.tearDown()

    def _register(self):
        from karl.models.interfaces import ITagQuery
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # Register dummy IFolderCustomizer
        from karl.content.views.interfaces import IFolderCustomizer
        karl.testing.registerAdapter(DummyFolderCustomizer, (Interface, Interface),
                                IFolderCustomizer)

    def _makeOne(self, *arg, **kw):
        from karl.content.views.files import EditFolderFormController
        return EditFolderFormController(*arg, **kw)

    def _registerDummyWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_form_defaults(self):
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        context.title = 'title'
        context.security_state = 'private'
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'title')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['security_state'], 'private')

    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('title' in dict(fields))
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        self._register()
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('title' in widgets)

    def test___call__(self):
        context = testing.DummyModel()
        context.title = 'title'
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        self._register()
        from karl.models.interfaces import IObjectModifiedEvent
        request = testing.DummyRequest()
        context = testing.DummyModel(title='oldtitle')
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        converted = {
            'title':'new title',
            'security_state': 'private',
            'tags': ['thetesttag'],
            }
        L = karl.testing.registerEventListener(
            (Interface, IObjectModifiedEvent))
        karl.testing.registerDummySecurityPolicy('testeditor')
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        msg = 'http://example.com/?status_message=Folder+changed'
        self.assertEqual(response.location, msg)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.modified_by, 'testeditor')

class TestEditFileFormController(unittest.TestCase):
    def setUp(self):
        cleanUp()
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.files import EditFileFormController
        return EditFileFormController(context, request)

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        return request

    def _makeContext(self):
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        return context

    def _register(self):
        from karl.models.interfaces import ITagQuery
        from karl.content.views.interfaces import IShowSendalert
        karl.testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                     ITagQuery)
        karl.testing.registerAdapter(DummyShowSendalert, (Interface, Interface),
                                     IShowSendalert)

        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        karl.testing.registerUtility(self.mailer, IMailDelivery)

    def _registerDummyWorkflow(self):
        # Register security workflow
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_form_defaults(self):
        self._register()
        self._registerDummyWorkflow()
        context = self._makeContext()
        context.title = 'title'
        context.security_state = 'private'
        context.tags = []
        context.filename = 'thefile'
        context.mimetype = 'text/xml'
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'title')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['security_state'], 'private')
        self.assertEqual(defaults['file'].filename, 'thefile')
        self.assertEqual(defaults['file'].mimetype, 'text/xml')

    def test_form_fields(self):
        self._register()
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        schema = dict(fields)
        self.failUnless('title' in schema)
        self.failUnless('tags' in schema)
        self.failUnless('security_state' in schema)
        self.failUnless('tags' in schema)

    def test_form_widgets(self):
        self._register()
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True,
                                           'sendalert':True})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('security_state' in widgets)
        self.failUnless('tags' in widgets)

    def test___call__(self):
        context = self._makeContext()
        context.title = 'title'
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('api' in response)
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')

    def test_handle_cancel(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit_valid(self):
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        from schemaish.type import File as SchemaFile
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory

        self._register()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context._extracted_data = 'old'
        context.sessions = DummySessions()
        context.catalog = DummyCatalog()
        directlyProvides(context, ISite)
        converted = {
            'title': 'new title',
            'file': SchemaFile('abc', 'filename', 'x/foo'),
            'security_state': 'public',
            'tags': ['thetesttag'],
            }
        karl.testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                     (ICommunityFile,),
                                     IContentFactory)
        L = karl.testing.registerEventListener(
            (Interface, IObjectModifiedEvent))
        karl.testing.registerDummySecurityPolicy('testeditor')
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=File+changed')
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(context.mimetype, 'x/foo')
        self.assertEqual(context.filename, 'filename')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.stream, 'abc')
        self.assertEqual(context.modified_by, 'testeditor')
        self.assertEqual(context._extracted_data, None)

    def test_handle_submit_valid_nofile_noremove(self):
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        from schemaish.type import File as SchemaFile
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory

        self._register()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context.mimetype = 'old/type'
        context.filename = 'old_name'
        context.stream = 'old'
        context._extracted_data = 'old'
        context.sessions = DummySessions()
        context.catalog = DummyCatalog()
        directlyProvides(context, ISite)
        converted = {
            'title': 'new title',
            'file': SchemaFile(None, None, None),
            'security_state': 'public',
            'tags': ['thetesttag'],
            }
        karl.testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                (ICommunityFile,),
                                IContentFactory)
        L = karl.testing.registerEventListener(
            (Interface, IObjectModifiedEvent))
        karl.testing.registerDummySecurityPolicy('testeditor')
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=File+changed')
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(context.mimetype, 'old/type')
        self.assertEqual(context.filename, 'old_name')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.stream, 'old')
        self.assertEqual(context.modified_by, 'testeditor')
        self.assertEqual(context._extracted_data, 'old')

    def test_handle_submit_valid_nofile_withremove(self):
        from pyramid_formish import ValidationError
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        from schemaish.type import File as SchemaFile
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory

        self._register()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context.mimetype = 'old/type'
        context.filename = 'old_name'
        context.stream = 'old'
        context.sessions = DummySessions()
        context.catalog = DummyCatalog()
        directlyProvides(context, ISite)
        converted = {
            'title': 'new title',
            'file': SchemaFile(None, None, None, metadata={'remove':True}),
            'security_state': 'public',
            'tags': ['thetesttag'],
            }
        karl.testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                (ICommunityFile,),
                                IContentFactory)
        karl.testing.registerDummySecurityPolicy('testeditor')
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        self.assertRaises(ValidationError, controller.handle_submit, converted)

class TestAdvancedFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()
        registerLayoutProvider()
        karl.testing.registerDummyRenderer('karl.views:templates/formfields.pt')

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import advanced_folder_view
        return advanced_folder_view(context, request)

    def test_render(self):
        context = testing.DummyModel(title='Dummy')
        request = testing.DummyRequest()
        renderer = karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")

    def test_render_reference_manual(self):
        from karl.content.interfaces import IReferencesFolder
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, IReferencesFolder)
        request = testing.DummyRequest()
        renderer = karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")
        self.assertEqual(renderer.selected, 'reference_manual')

    def test_render_network_news(self):
        from karl.content.views.interfaces import INetworkNewsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, INetworkNewsMarker)
        request = testing.DummyRequest()
        renderer = karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")
        self.assertEqual(renderer.selected, 'network_news')

    def test_render_network_events(self):
        from karl.content.views.interfaces import INetworkEventsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, INetworkEventsMarker)
        request = testing.DummyRequest()
        renderer = karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")
        self.assertEqual(renderer.selected, 'network_events')

    def test_cancel(self):
        context = testing.DummyModel(title='Dummy')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.cancel': '1',
                })
            )
        response = self._callFUT(context, request)
        self.assertEqual(response.location, "http://example.com/")

    def test_submit_no_marker(self):
        context = testing.DummyModel(title='Dummy')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                })
            )
        renderer = karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")

    def test_submit_reference_manual(self):
        context = testing.DummyModel(title='Dummy')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'reference_manual',
                })
            )
        karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        from karl.content.views.interfaces import INetworkEventsMarker
        self.failUnless(IReferencesFolder.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))

    def test_submit_network_news(self):
        context = testing.DummyModel(title='Dummy')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_news',
                })
            )
        karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        from karl.content.views.interfaces import INetworkEventsMarker
        self.failIf(IReferencesFolder.providedBy(context))
        self.failUnless(INetworkNewsMarker.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))

    def test_submit_network_events(self):
        context = testing.DummyModel(title='Dummy')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_events',
                })
            )
        karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        from karl.content.views.interfaces import INetworkEventsMarker
        self.failIf(IReferencesFolder.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.failUnless(INetworkEventsMarker.providedBy(context))

    def test_submit_change_to_reference_manual(self):
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        from karl.content.views.interfaces import INetworkEventsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, INetworkNewsMarker)
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'reference_manual',
                })
            )
        karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        self.failUnless(IReferencesFolder.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))

    def test_submit_change_to_network_news(self):
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        from karl.content.views.interfaces import INetworkEventsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, INetworkEventsMarker)
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_news',
                })
            )
        karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        self.failIf(IReferencesFolder.providedBy(context))
        self.failUnless(INetworkNewsMarker.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))

    def test_submit_change_to_network_events(self):
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        from karl.content.views.interfaces import INetworkEventsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, IReferencesFolder)
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_events',
                })
            )
        karl.testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        self.failIf(IReferencesFolder.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.failUnless(INetworkEventsMarker.providedBy(context))


class TestAjaxFileUploadView(unittest.TestCase):
    "Multiupload"

    def setUp(self):
        cleanUp()

        from karl.content.views import files as module_under_test
        self._saved_transaction_module = module_under_test.transaction
        self.transaction = DummyTransactionModule()
        module_under_test.transaction = self.transaction

        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICommunityFile
        from karl.content.models.files import CommunityFile
        registerContentFactory(CommunityFile, ICommunityFile)

        from zope.interface import Interface
        from repoze.workflow.testing import registerDummyWorkflow
        self.workflow = DummyWorkflow()
        registerDummyWorkflow('security', self.workflow, Interface)

    def tearDown(self):
        cleanUp()

        from karl.content.views import files as module_under_test
        module_under_test.transaction = self._saved_transaction_module

    def _make_context(self):
        context = testing.DummyModel()
        ###context.get_attachments = lambda: context
        return context

    def _call_fut(self, context, request):
        from karl.content.views.files import ajax_file_upload_view
        return ajax_file_upload_view(
            context, request,
        )

    def test_upload_ok(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file = context['testfile.txt']
        self.assertEqual(file.title, 'testfile.txt')
        self.assertEqual(file.mimetype, 'text/plain')
        self.assertEqual(file.filename, 'testfile.txt')
        self.assertEqual(file.creator, 'chris')
        self.assertEqual(file.size, 1000)
        self.assertEqual(len(file.blobfile.open().read()), 1000)
        self.assertEqual(self.workflow.initialized_list, [file,])

    def test_image_ok(self):
        # An image is somewhat special, so it's worth to test it.
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyImageUpload(),
                'client_id': 'ABCDEF',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'test.jpg',
            })

        file = context['test.jpg']
        self.assertEqual(file.title, 'test.jpg')
        self.assertEqual(file.mimetype, 'image/jpeg')
        self.assertEqual(file.filename, 'test.jpg')
        self.assertEqual(file.creator, 'chris')
        self.assertEqual(file.size, 244)
        self.assertEqual(len(file.blobfile.open().read()), 244)
        self.assertEqual(self.workflow.initialized_list, [file ,])

    def test_mandatory_parameters_missing_file(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                ## NO 'file': DummyUpload(),
                'client_id': 'ABCDEF',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'',
             u'error':
                u'Wrong parameters, `file` and `client_id` are mandatory'})
        self.failUnless(self.transaction.doomed)  # assert that doom was called

    def test_mandatory_parameters_missing_client_id(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                ## NO 'client_id': 'ABCDEF',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'',
             u'error':
                u'Wrong parameters, `file` and `client_id` are mandatory'})
        self.failUnless(self.transaction.doomed)  # assert that doom was called

    def test_multiple(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'result': u'OK', u'filename': u'f1.txt'})

        file1 = context['TEMP']['PLUPLOAD-ABCDEF1']
        self.assertEqual(file1.title, 'f1.txt')
        self.assertEqual(file1.mimetype, 'text/plain')
        self.assertEqual(file1.filename, 'f1.txt')
        self.assertEqual(file1.creator, 'chris')
        self.assertEqual(file1.size, 1000)
        self.assertEqual(len(file1.blobfile.open().read()), 1000)
        self.assertEqual(self.workflow.initialized_list, [])

        self.failUnless(hasattr(file1, '__client_file_id__'))
        self.failUnless(hasattr(file1, '__transaction_parent__'))

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f2.txt'),
                'client_id': 'ABCDEF2',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'result': u'OK', u'filename': u'f2.txt'})

        file2 = context['TEMP']['PLUPLOAD-ABCDEF2']
        self.assertEqual(file2.title, 'f2.txt')
        self.assertEqual(file2.mimetype, 'text/plain')
        self.assertEqual(file2.filename, 'f2.txt')
        self.assertEqual(file2.creator, 'chris')
        self.assertEqual(file2.size, 1000)
        self.assertEqual(len(file2.blobfile.open().read()), 1000)
        self.assertEqual(self.workflow.initialized_list, [])

        self.failUnless(hasattr(file2, '__client_file_id__'))
        self.failUnless(hasattr(file2, '__transaction_parent__'))

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f3.txt'),
                'client_id': 'ABCDEF3',
                'end_batch': '["ABCDEF1", "ABCDEF2"]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'f3.txt',
            })

        self.assertEqual(context['f1.txt'], file1)

        self.assertEqual(context['f2.txt'], file2)

        file3 = context['f3.txt']
        self.assertEqual(file3.title, 'f3.txt')
        self.assertEqual(file3.mimetype, 'text/plain')
        self.assertEqual(file3.filename, 'f3.txt')
        self.assertEqual(file3.creator, 'chris')
        self.assertEqual(file3.size, 1000)
        self.assertEqual(len(file3.blobfile.open().read()), 1000)

        self.assertEqual(self.workflow.initialized_list, [file1, file2, file3])
        self.assertEqual(list(context['TEMP'].keys()), [])

        # security guards all removed
        self.failUnless(not hasattr(file1, '__client_file_id__'))
        self.failUnless(not hasattr(file1, '__transaction_parent__'))
        self.failUnless(not hasattr(file2, '__client_file_id__'))
        self.failUnless(not hasattr(file2, '__transaction_parent__'))
        self.failUnless(not hasattr(file3, '__client_file_id__'))
        self.failUnless(not hasattr(file3, '__transaction_parent__'))

    def test_tolerate_doomed_retried_batch(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'f1.txt',
            })
        self.assertEqual(list(context['TEMP'].keys()), ['PLUPLOAD-ABCDEF1'])

        # this batch is now doomed and client retries - with the same id.
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'result': u'OK', u'filename': u'f1.txt'})
        self.assertEqual(list(context['TEMP'].keys()), ['PLUPLOAD-ABCDEF1'])
        # - it just overwrites the object: this is ok. (It is for sure
        # from the same client.)

    def test_security_assertions(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'f1.txt',
            })

        file1 = context['TEMP']['PLUPLOAD-ABCDEF1']

        # client id mismatch: bad. Smells like bad intention.
        self.assertEqual(file1.__client_file_id__, 'ABCDEF1')
        file1.__client_file_id__ = 'h4x3r'

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f2.txt'),
                'client_id': 'ABCDEF2',
                'end_batch': '["ABCDEF1"]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'',
             u'error': u'Inconsistent client file id',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False

        # Another one
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f3.txt'),
                'client_id': 'ABCDEF3',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'f3.txt',
            })

        file1 = context['TEMP']['PLUPLOAD-ABCDEF3']

        # parent changes during the transaction: very bad.
        self.assertEqual(file1.__transaction_parent__, context)
        file1.__transaction_parent__ = 'h4x3r'

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f4.txt'),
                'client_id': 'ABCDEF4',
                'end_batch': '["ABCDEF3"]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'ABCDEF3',
             u'error': u'Inconsistent batch transaction',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False

        # Another one
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f5.txt'),
                'client_id': 'ABCDEF5',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'f5.txt',
            })

        file1 = context['TEMP']['PLUPLOAD-ABCDEF5']

        # the security credentials change during the batch: very very bad.
        karl.testing.registerDummySecurityPolicy('paul')

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f6.txt'),
                'client_id': 'ABCDEF6',
                'end_batch': '["ABCDEF5"]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'ABCDEF5',
             u'error': u'Inconsistent ownership',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False

    def test_chunks_onechunk(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'chunks': '1',
                'chunk': '0',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file = context['testfile.txt']
        self.assertEqual(file.title, 'testfile.txt')
        self.assertEqual(file.mimetype, 'text/plain')
        self.assertEqual(file.filename, 'testfile.txt')
        self.assertEqual(file.creator, 'chris')
        self.assertEqual(file.size, 1000)
        self.assertEqual(len(file.blobfile.open().read()), 1000)
        self.assertEqual(self.workflow.initialized_list, [file,])

    def test_chunks(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'chunks': '3',
                'chunk': '0',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file1 = context['TEMP']['PLUPLOAD-ABCDEF']
        self.assertEqual(file1.title, 'testfile.txt')
        self.assertEqual(file1.mimetype, 'text/plain')
        self.assertEqual(file1.filename, 'testfile.txt')
        self.assertEqual(file1.creator, 'chris')
        self.assertEqual(file1.size, 1000)
        self.assertEqual(len(file1.blobfile.open().read()), 1000)
        self.assertEqual(self.workflow.initialized_list, [])

        self.failUnless(hasattr(file1, '__chunks__'))
        self.failUnless(hasattr(file1, '__chunk__'))

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'chunks': '3',
                'chunk': '1',
            }
        )

        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        self.assertEqual(file1.size, 2000)
        self.assertEqual(len(file1.blobfile.open().read()), 2000)
        self.assertEqual(self.workflow.initialized_list, [])

        self.failUnless(hasattr(file1, '__chunks__'))
        self.failUnless(hasattr(file1, '__chunk__'))

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'chunks': '3',
                'chunk': '2',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        self.assertEqual(context['testfile.txt'], file1)

        self.assertEqual(file1.size, 3000)
        self.assertEqual(len(file1.blobfile.open().read()), 3000)
        self.assertEqual(self.workflow.initialized_list, [file1])

        # check that the chunk info is removed
        self.failUnless(not hasattr(file1, '__chunks__'))
        self.failUnless(not hasattr(file1, '__chunk__'))

    def test_chunking_parameters(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'chunks': '1',
                'chunk': '-1',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'',
             u'error': u'Chunking inconsistency, `chunk` out of range',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'chunks': '2',
                'chunk': '2',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'',
             u'error': u'Chunking inconsistency, `chunk` out of range',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False

    def test_chunking_inconsistency(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
                'chunks': '3',
                'chunk': '0',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'f1.txt',
            })

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
                'chunks': '3',
                'chunk': '2',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'client_id': u'ABCDEF1',
             u'error': u'Chunking inconsistency, wrong chunk order',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False

    def test_lost_tempfile(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f1.txt'),
                'client_id': 'ABCDEF1',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'result': u'OK',
             u'filename': u'f1.txt',
            })

        #file1 = context['TEMP']['PLUPLOAD-ABCDEF1']
        # now the file is lost somehow:
        del context['TEMP']['PLUPLOAD-ABCDEF1']

        request = testing.DummyRequest(
            params={
                'file': DummyUpload(filename='f2.txt'),
                'client_id': 'ABCDEF2',
                'end_batch': '["ABCDEF1"]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {'client_id': 'ABCDEF1',
             'error': "Inconsistent transaction, lost a file "
                      "(temp_id='PLUPLOAD-ABCDEF1') "})

    def test_unique_filenames(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(),
                'client_id': 'ABCDEF',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file = context['testfile.txt']
        self.assertEqual(file.title, 'testfile.txt')
        self.assertEqual(file.mimetype, 'text/plain')
        self.assertEqual(file.filename, 'testfile.txt')
        self.assertEqual(file.creator, 'chris')
        self.assertEqual(file.size, 1000)
        self.assertEqual(len(file.blobfile.open().read()), 1000)


        # another one, same filename
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(IMAGE_DATA=2000 * '1'),
                'client_id': 'ABCDEF2',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file2 = context['testfile-1.txt']
        self.assertEqual(file2.title, 'testfile-1.txt')
        self.assertEqual(file.mimetype, 'text/plain')
        self.assertEqual(file2.filename, 'testfile-1.txt')
        self.assertEqual(file2.creator, 'chris')
        self.assertEqual(file2.size, 2000)
        self.assertEqual(len(file2.blobfile.open().read()), 2000)

        # another one, same filename
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(IMAGE_DATA=3000 * '2'),
                'client_id': 'ABCDEF3',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file3 = context['testfile-2.txt']
        self.assertEqual(file3.title, 'testfile-2.txt')
        self.assertEqual(file3.filename, 'testfile-2.txt')
        self.assertEqual(file3.size, 3000)
        self.assertEqual(len(file3.blobfile.open().read()), 3000)


        # another one, same filename
        request = testing.DummyRequest(
            params={
                'file': DummyUpload(IMAGE_DATA=4000 * '3'),
                'client_id': 'ABCDEF4',
                'end_batch': '[]',
            }
        )
        data = self._call_fut(context, request)
        self.assertEqual(data,
            {u'batch_completed': True,
             u'result': u'OK',
             u'filename': u'testfile.txt',
            })

        file4 = context['testfile-3.txt']
        self.assertEqual(file4.title, 'testfile-3.txt')
        self.assertEqual(file4.filename, 'testfile-3.txt')
        self.assertEqual(file4.size, 4000)
        self.assertEqual(len(file4.blobfile.open().read()), 4000)

        self.assertEqual(self.workflow.initialized_list,
                         [file, file2, file3, file4])


class FakeParams(dict):
    # this is a dict, so we just stub getall on it.
    def getall(self, key):
        return self.get(key)

class TestAjaxFileReorganizeDeleteView(unittest.TestCase):
    "Grid reorganize - delete"
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _call_fut(self, context, request):
        from karl.content.views.files import ajax_file_reorganize_delete_view
        return ajax_file_reorganize_delete_view(context, request)

    def _make_context(self):
        context = testing.DummyModel()
        ###context.get_attachments = lambda: context
        return context

    def test_delete_one(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()

        context['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt'],
            })
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'deleted': 1, u'result': u'OK'})
        self.assertEqual(context.keys(), [])

    def test_delete_zero(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': [],
            })
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'deleted': 0, u'result': u'OK'})
        self.assertEqual(context.keys(), [])


    def test_delete_multiple(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()

        context['f1.txt'] = testing.DummyModel(title='a file')
        context['f2.txt'] = testing.DummyModel(title='a file')
        context['f3.txt'] = testing.DummyModel(title='a file')
        context['f4.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt', 'f2.txt', 'f3.txt'],
            })
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'deleted': 3, u'result': u'OK'})
        self.assertEqual(context.keys(), ['f4.txt'])


    def test_tolerates_missing(self):
        karl.testing.registerDummySecurityPolicy('chris')
        context = self._make_context()

        context['f1.txt'] = testing.DummyModel(title='a file')
        context['f2.txt'] = testing.DummyModel(title='a file')
        # There is no f3.txt.
        context['f4.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt', 'f2.txt', 'f3.txt'],
            })
        )
        data = self._call_fut(context, request)
        self.assertEqual(data, {u'deleted': 2, u'result': u'OK'})
        self.assertEqual(context.keys(), ['f4.txt'])


class TestAjaxFileReorganizeMovetoView(unittest.TestCase):
    "Grid reorganize - move to"

    def setUp(self):
        cleanUp()

        from karl.content.views import files as module_under_test
        self._saved_transaction_module = module_under_test.transaction
        self.transaction = DummyTransactionModule()
        module_under_test.transaction = self.transaction

    def tearDown(self):
        cleanUp()

        from karl.content.views import files as module_under_test
        module_under_test.transaction = self._saved_transaction_module

    def _call_fut(self, context, request):
        from karl.content.views.files import ajax_file_reorganize_moveto_view
        return ajax_file_reorganize_moveto_view(context, request)

    def _make_community(self):
        # factorize a fake community
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        community = testing.DummyModel(title='thecommunity')
        directlyProvides(community, ICommunity)

        folder = testing.DummyModel(title='parent')
        community['files'] = folder

        return community


    def test_move_one(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 1,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), [])
        self.assertEqual(folder2.keys(), ['f1.txt'])


    def test_move_zero(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': [],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 0,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), ['f1.txt'])
        self.assertEqual(folder2.keys(), [])


    def test_move_multiple(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')
        folder1['f2.txt'] = testing.DummyModel(title='a file')
        folder1['f3.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt', 'f2.txt', 'f3.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 3,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), [])
        self.assertEqual(set(folder2.keys()),
                         set(['f1.txt', 'f2.txt', 'f3.txt']))


    def test_mandatory_parameters(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt'],
                ## NO 'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'error': u'Wrong parameters, `target_folder` is mandatory',
             u'result': u'ERROR',
             u'filename': u'*',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False


    def test_missing_file(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt', 'f2.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'error':
              u"File f2.txt not found in source folder (KeyError('f2.txt',))",
             u'result': u'ERROR',
             u'filename': u'f2.txt',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False


    def test_cant_delete_file(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']

        class DummyModelThatFailsDelete(testing.DummyModel):
            def __delitem__(self, name):
                raise KeyError(name)

        folder1 = rootfolder['folder1'] = DummyModelThatFailsDelete(
            title='a folder')
        rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'error':
                u"Unable to delete file f1.txt from source folder "
                u"(KeyError('f1.txt',))",
             u'result': u'ERROR',
             u'filename': u'f1.txt',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False


    def test_cant_add_file(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']

        class DummyModelThatFailsSetitem(testing.DummyModel):
            def __setitem__(self, name, value):
                raise KeyError(name)

        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        rootfolder['folder2'] = DummyModelThatFailsSetitem(
                                                            title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'error':
                u"Cannot move to target folder "
                u"<a href=\"http://example.com/files/folder2/\">/folder2</a> "
                u"(KeyError('f1.txt',))",
             u'result': u'ERROR',
             u'filename': u'f1.txt',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False


    def test_same_target(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt'],
                'target_folder': '/folder1',
            })
        )
        data = self._call_fut(folder1, request)

        # This actually works.
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder1/',
             u'moved': 1,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder1',
            })

        self.assertEqual(folder1.keys(), ['f1.txt'])
        self.assertEqual(folder2.keys(), [])


    def test_move_folder(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['folder1a'] = testing.DummyModel(title='a folder')
        folder1['folder1a']['f1.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['folder1a'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 1,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), [])
        self.assertEqual(folder2.keys(), ['folder1a'])
        self.assertEqual(folder2['folder1a'].keys(), ['f1.txt'])


    def test_move_folder_to_itself(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['folder1a'] = testing.DummyModel(title='a folder')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['folder1a'],
                'target_folder': '/folder1/folder1a',
            })
        )
        data = self._call_fut(folder1, request)

        self.assertEqual(data,
            {u'error': u'Cannot move a folder into itself',
             u'result': u'ERROR',
             u'filename': u'folder1a',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False


    def test_move_folder_to_itself_deeply(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['folder1a'] = testing.DummyModel(title='a folder')
        folder1['folder1a']['folder1aa'] = testing.DummyModel(title='a folder')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['folder1a'],
                'target_folder': '/folder1/folder1a/folder1aa',
            })
        )
        data = self._call_fut(folder1, request)

        self.assertEqual(data,
            {u'error': u'Cannot move a folder into itself',
             u'result': u'ERROR',
             u'filename': u'folder1a',
            })
        self.failUnless(self.transaction.doomed)  # assert that doom was called
        self.transaction.doomed = False


    def test_canonical_names(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        folder1['NAME.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['NAME.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 1,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), [])
        # filename canonized. (eg small caps...)
        self.assertEqual(folder2.keys(), ['name.txt'])


    def test_unique_names(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        file1 = folder1['f1.txt'] = testing.DummyModel(title='a file')
        file2 = folder1['f2.txt'] = testing.DummyModel(title='a file')
        file3 = folder1['f3.txt'] = testing.DummyModel(title='a file')

        # ... but some files exist already in the target
        folder2['f1.txt'] = testing.DummyModel(title='a file')
        folder2['f1-1.txt'] = testing.DummyModel(title='a file')
        folder2['f1-2.txt'] = testing.DummyModel(title='a file')
        folder2['f2.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt', 'f2.txt', 'f3.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 3,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), [])
        self.assertEqual(set(folder2.keys()),
                         set(['f1.txt', 'f1-1.txt', 'f1-2.txt', 'f1-3.txt',
                              'f2.txt', 'f2-1.txt',
                              'f3.txt']))
        self.assertEqual(file1, folder2['f1-3.txt'])
        self.assertEqual(file2, folder2['f2-1.txt'])
        self.assertEqual(file3, folder2['f3.txt'])


    def test_unique_names_changes_properties(self):
        karl.testing.registerDummySecurityPolicy('chris')
        community = self._make_community()
        rootfolder = community['files']
        folder1 = rootfolder['folder1'] = testing.DummyModel(title='a folder')
        folder2 = rootfolder['folder2'] = testing.DummyModel(title='a folder')

        file1 = folder1['f1.txt'] = testing.DummyModel(
                                            title='f1.txt', filename='f1.txt')
        file2 = folder1['f2.txt'] = testing.DummyModel(
                                            title='SOMEONE CHANGED ME',
                                            filename='f2.txt')

        # ... but some files exist already in the target
        folder2['f1.txt'] = testing.DummyModel(title='a file')
        folder2['f2.txt'] = testing.DummyModel(title='a file')

        request = testing.DummyRequest(
            params=FakeParams({
                'file[]': ['f1.txt', 'f2.txt'],
                'target_folder': '/folder2',
            })
        )
        data = self._call_fut(folder1, request)
        self.assertEqual(data,
            {u'targetFolderUrl': u'http://example.com/files/folder2/',
             u'moved': 2,
             u'result': u'OK',
             u'targetFolderTitle': u'a folder',
             u'targetFolder': u'/folder2',
            })

        self.assertEqual(folder1.keys(), [])
        self.assertEqual(set(folder2.keys()), set(['f1.txt', 'f1-1.txt',
                'f2.txt', 'f2-1.txt']))
        self.assertEqual(file1, folder2['f1-1.txt'])
        self.assertEqual(file2, folder2['f2-1.txt'])

        # names are mangled if the title has not changed
        self.assertEqual(file1.title, 'f1-1.txt')
        self.assertEqual(file1.filename, 'f1-1.txt')

        # title is mangled differently, in case someone has changed it
        # from the upload original
        self.assertEqual(file2.title, 'SOMEONE CHANGED ME - 1')
        self.assertEqual(file2.filename, 'f2-1.txt')



# An 1x1px png (should be jpeg, in fact)
import binascii
IMAGE_DATA = binascii.unhexlify(
            '89504e470d0a1a0a0000000d49484452000000010000000108060000001f' +
            '15c4890000000467414d410000b18f0bfc610500000006624b474400ff00' +
            'ff00ffa0bda793000000097048597300000b1200000b1201d2dd7efc0000' +
            '000976704167000000010000000100c7955fed0000000d4944415408d763' +
            'd8b861db7d00072402f7f7d926c80000002574455874646174653a637265' +
            '61746500323031302d30352d31385432303a30343a34322b30323a3030e1' +
            '1f35f60000002574455874646174653a6d6f6469667900323031302d3035' +
            '2d31385432303a30343a34322b30323a303090428d4a0000000049454e44' +
            'ae426082')

class DummyUpload(object):
    filename = 'testfile.txt'
    type = 'text/plain'
    IMAGE_DATA = 1000 * '0'

    def __init__(self, **kw):
        self.__dict__.update(kw)
        from cStringIO import StringIO
        self._file = StringIO(self.IMAGE_DATA)

    @property
    def file(self):
        return self._file

class DummyImageUpload(DummyUpload):
    filename = 'test.jpg'
    type = 'image/jpeg'
    IMAGE_DATA = IMAGE_DATA

class DummyTransactionModule(object):
    doomed = False

    def doom(self):
        self.doomed = True


from zope.interface import implements

class DummyBlobFile:
    def open(self):
        return self

class DummyCommunityFolder:
    def __init__(self, title, userid):
        self.title = title
        self.userid = userid

from karl.content.interfaces import ICommunityFile
class DummyCommunityFile(testing.DummyModel):
    implements(ICommunityFile)
    size = 3

class DummyFile(testing.DummyModel):
    size = 3
    def upload(self, stream):
        self.stream = stream

class DummyFileInfo(object):
    def __init__(self, item, request):
        self.title = 'title'
        self.url = 'url'
        self.mimeinfo = {'small_icon_name': 'folder_small.gif', 'title': 'Folder'}
        self.modified = '12/12/2008'
        self.modified_by_title = 'user name'
        self.modified_by_url = '/profiles/user'

class DummyModifiedDateIndex:
    def discriminator(self, obj, default):
        return obj.modified

class DummyTagEngine:
    def __init__(self):
        self.updated = []
    def update(self, item, user, tags):
        self.updated.append((item, user, tags))

class DummyWorkflow:
    state_attr = 'security_state'
    initial_state = 'initial'
    def __init__(self, state_info=[
        {'name':'public', 'transitions':['private']},
        {'name':'private', 'transitions':['public']},
        ]):
        self.transitioned = []
        self._state_info = state_info
        self.initialized_list = []

    def state_info(self, context, request):
        return self._state_info

    def initialize(self, content):
        self.initialized = True
        self.initialized_list.append(content)

    def transition_to_state(self, content, request, to_state, context=None,
                            guards=(), skip_same=True):
        self.transitioned.append({'to_state':to_state, 'content':content,
                                  'request':request, 'guards':guards,
                                  'context':context, 'skip_same':skip_same})

    def state_of(self, content):
        return getattr(content, self.state_attr, None)

class DummySessions(dict):
    def get(self, name, default=None):
        if name not in self:
            self[name] = {}
        return self[name]

class DummyShowSendalert(object):
    def __init__(self, context, request):
        pass
    show_sendalert = True

from pyramid.security import Authenticated
from pyramid.security import Everyone

class DummySecurityPolicy:
    """ A standin for both an IAuthentication and IAuthorization policy """
    def __init__(self, userid=None, groupids=(), permissions=None):
        self.userid = userid
        self.groupids = groupids
        self.permissions = permissions or {}

    def authenticated_userid(self, request):
        return self.userid

    def effective_principals(self, request):
        effective_principals = [Everyone]
        if self.userid:
            effective_principals.append(Authenticated)
            effective_principals.append(self.userid)
            effective_principals.extend(self.groupids)
        return effective_principals

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []

    def permits(self, context, principals, permission):
        if context in self.permissions:
            permissions = self.permissions[context]
            return permission in permissions
        return False

    def principals_allowed_by_permission(self, context, permission):
        return self.effective_principals(None)


class IDummyContent(Interface):
    taggedValue('name', 'dummy')

class DummyContent(testing.DummyModel):
    implements(IDummyContent)
    title = 'THE TITLE'

dummycontent = DummyContent()

class DummySearch:
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        return 1, [1], lambda x: dummycontent

class MyDummyCatalog(dict):
    def __init__(self):
        self['modified_date'] = DummyModifiedDateIndex()
        class DocumentMap(object):
            def address_for_docid(self, id):
                return '/files/foo/bar'
        self.document_map = DocumentMap()
