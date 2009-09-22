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
from repoze.bfg.testing import registerAdapter

from karl.testing import DummyCatalog
from karl.testing import DummyFolderCustomizer
from karl.testing import DummyFolderAddables
from karl.testing import DummyLayoutProvider
from karl.testing import DummyTagQuery

class TestShowFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import show_folder_view
        return show_folder_view(context, request)

    def _register(self):
        from karl.content.views.interfaces import IFileInfo
        testing.registerAdapter(DummyFileInfo, (Interface, Interface),
                                IFileInfo)
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # Register dummy IFolderAddables
        from karl.views.interfaces import IFolderAddables
        testing.registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def test_notcommunityrootfolder(self):
        self._register()
        self._registerLayoutProvider()

        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        folder = testing.DummyModel(title='parent')
        folder.catalog = {'modified_date': DummyModifiedDateIndex()}
        context = testing.DummyModel(title='thetitle')
        folder['child'] = context
        request = testing.DummyRequest()
        directlyProvides(context, ICommunity)
        renderer  = testing.registerDummyRenderer('templates/show_folder.pt')
        response = self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(len(actions), 5)
        self.assertEqual(actions[0][1], 'add_folder.html')
        self.assertEqual(actions[1][1], 'add_file.html')
        self.assertEqual(actions[2][1], 'edit.html')
        self.assertEqual(actions[3][1], 'delete.html')

    def test_communityrootfolder(self):
        self._register()
        self._registerLayoutProvider()

        from karl.content.interfaces import ICommunityRootFolder
        from zope.interface import directlyProvides
        context = testing.DummyModel(title='thetitle')
        context.catalog = {'modified_date': DummyModifiedDateIndex()}
        request = testing.DummyRequest()
        directlyProvides(context, ICommunityRootFolder)
        renderer  = testing.registerDummyRenderer('templates/show_folder.pt')
        response = self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0][1], 'add_folder.html')
        self.assertEqual(actions[1][1], 'add_file.html')


class TestAddFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import add_folder_view
        return add_folder_view(context, request)

    def _register(self):
        from repoze.bfg import testing
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # Register dummy IFolderCustomizer
        from karl.content.views.interfaces import IFolderCustomizer
        testing.registerAdapter(DummyFolderCustomizer, (Interface, Interface),
                                IFolderCustomizer)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _registerSecurityWorkflow(self):
        workflow = DummyWorkflow()
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security', workflow)

    def test_unsubmitted(self):

        renderer  = testing.registerDummyRenderer('templates/add_folder.pt')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_security_states_with_workflow(self):
        renderer  = testing.registerDummyRenderer('templates/add_folder.pt')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.failUnless(renderer.security_states)

    def test_no_security_states_without_workflow(self):
        renderer  = testing.registerDummyRenderer('templates/add_folder.pt')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        response = self._callFUT(context, request)
        self.failIf(renderer.security_states)

    def test_submitted_invalid(self):

        renderer  = testing.registerDummyRenderer('templates/add_folder.pt')
        context = testing.DummyModel()
        from webob import MultiDict
        request = testing.DummyRequest(MultiDict({'form.submitted':1}))
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        self._register()

        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        context.tags = DummyTagEngine()
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':1,
                    'title':'a title',
                    'security_state': 'private',
                    'tags': 'thetesttag',
                    })
            )
        from karl.content.interfaces import ICommunityFolder
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyCommunityFolder,
                                (ICommunityFolder,),
                                IContentFactory)
        self._registerSecurityWorkflow()

        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/a-title/')
        self.assertEqual(context['a-title'].title, u'a title')
        self.assertEqual(context['a-title'].userid, 'userid')
        self.assertEqual(context.tags.updated,
            [(None, 'userid', ['thetesttag'])])

class TestAddFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        testing.registerUtility(self.mailer, IMailDelivery)

        from karl.content.views.adapters import CommunityFileAlert
        from karl.content.interfaces import ICommunityFile
        from karl.models.interfaces import IProfile
        from repoze.bfg.interfaces import IRequest
        from karl.utilities.interfaces import IAlert
        testing.registerAdapter(CommunityFileAlert,
                                (ICommunityFile, IProfile, IRequest),
                                IAlert)

        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')
        

    def _callFUT(self, context, request):
        from karl.content.views.files import add_file_view
        return add_file_view(context, request)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def test_unsubmitted(self):
        self._registerLayoutProvider()
        self._registerSecurityWorkflow()

        renderer = testing.registerDummyRenderer(
            'templates/add_file.pt')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        self._register()
        self._registerLayoutProvider()

        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1'})
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_file.pt')
        self._callFUT(context, request)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_filename_with_only_symbols(self):
        self._register()
        self._registerLayoutProvider()

        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        fs = DummyFieldStorage()
        fs.filename = '???'
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'file': fs,
                'title': 'a title',
                'sendalert': '0',
                'sharing': 'false',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_file.pt')
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        response = self._callFUT(context, request)
        self.assertEqual(
            renderer.fielderrors, {'file': 'The filename must not be empty'})

    def test_submitted_valid(self):
        self._register()
        self._registerLayoutProvider()

        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'file': DummyFieldStorage(),
                'title': 'a title',
                'sendalert': '0',
                'security_state': 'public',
                'tags': 'thetesttag',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_file.pt')
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/filename/')
        self.assertEqual(context['filename'].title, u'a title')
        self.assertEqual(context['filename'].creator, 'userid')
        self.assertEqual(context['filename'].stream, 'abc')
        self.assertEqual(context['filename'].mimetype, 'x/foo')
        self.assertEqual(context['filename'].filename, 'filename')

        # attempt a duplicate upload
        response = self._callFUT(context, request)
        self.assertEqual(renderer.fielderrors, {
            'file': 'Filename filename already exists in this folder'})

    def test_full_path_filename(self):
        self._register()
        self._registerLayoutProvider()

        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        upload = DummyFieldStorage()
        upload.filename = r"C:\Documents and Settings\My Tests\filename"
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'file': upload,
                'title': 'a title',
                'sendalert': '0',
                'security_state': 'public',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_file.pt')
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/filename/')
        self.assertEqual(context['filename'].title, u'a title')
        self.assertEqual(context['filename'].creator, 'userid')
        self.assertEqual(context['filename'].stream, 'abc')
        self.assertEqual(context['filename'].mimetype, 'x/foo')
        self.assertEqual(context['filename'].filename, 'filename')

        # attempt a duplicate upload
        response = self._callFUT(context, request)
        self.assertEqual(renderer.fielderrors, {
            'file': 'Filename filename already exists in this folder'})

    def test_submitted_valid_alert(self):
        self._register()

        testing.registerDummySecurityPolicy('userid')

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
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'file': DummyFieldStorage(),
                'title': 'a title',
                'sendalert': '1',
                'security_state': 'public',
                })
            )
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/filename/')
        self.assertEqual(context['filename'].title, u'a title')
        self.assertEqual(context['filename'].creator, 'userid')
        self.assertEqual(context['filename'].stream, 'abc')
        self.assertEqual(context['filename'].mimetype, 'x/foo')
        self.assertEqual(context['filename'].filename, 'filename')

        self.assertEqual(3, len(self.mailer))

    def test_submitted_toobig(self):
        self._register()
        self._registerLayoutProvider()

        from karl.testing import DummySettings
        from repoze.bfg.interfaces import ISettings
        settings = DummySettings(upload_limit = '2')
        testing.registerUtility(settings, ISettings)

        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'file': DummyFieldStorage(),
                'title': 'a title',
                'sendalert': '0',
                'security_state': 'public',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/add_file.pt')
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunityFile, ICommunityFile)
        response = self._callFUT(context, request)
        self.assertEqual(renderer.fielderrors, {
            'file': 'File size exceeds upload limit of 2.'})

class TestShowFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import show_file_view
        return show_file_view(context, request)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def test_it(self):
        self._registerLayoutProvider()

        from karl.content.views.interfaces import IFileInfo
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        parent = testing.DummyModel(title='parent')
        context = testing.DummyModel(title='thetitle')
        parent['child'] = context
        request = testing.DummyRequest()
        renderer  = testing.registerDummyRenderer('templates/show_file.pt')

        testing.registerAdapter(DummyFileInfo, (Interface, Interface),
                                IFileInfo)

        response = self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0][1], 'edit.html')
        self.assertEqual(actions[1][1], 'delete.html')

class TestDownloadFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.files import download_file_view
        return download_file_view(context, request)

    def test_it(self):
        context = testing.DummyModel()
        blobfile = DummyBlobFile()
        context.blobfile = blobfile
        context.mimetype = 'x/foo'
        context.filename = 'thefilename'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
#        self.assertEqual(response.headerlist[0],
#               ('Content-Disposition', 'attachment; filename=thefilename'))
        self.assertEqual(response.headerlist[0],
                         ('Content-Type', 'x/foo'))
        self.assertEqual(response.app_iter, blobfile)

class TestEditFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _callFUT(self, context, request):
        from karl.content.views.files import edit_folder_view
        return edit_folder_view(context, request)

    def test_unsubmitted(self):
        self._register()
        self._registerLayoutProvider()

        renderer  = testing.registerDummyRenderer('templates/edit_folder.pt')
        context = testing.DummyModel(title='thefile')
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        self._register()
        self._registerLayoutProvider()

        renderer  = testing.registerDummyRenderer('templates/edit_folder.pt')
        context = testing.DummyModel(title='thetitle')
        from webob import MultiDict
        request = testing.DummyRequest(MultiDict({'form.submitted':1}))
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        self._register()

        from karl.models.interfaces import IObjectModifiedEvent
        context = testing.DummyModel(title='oldtitle')
        context.catalog = DummyCatalog()
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':1,
                    'title':'new title',
                    'security_state': 'private',
                    'tags': 'thetesttag',
                    })
            )
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        msg = 'http://example.com/?status_message=Folder%20changed'
        self.assertEqual(response.location, msg)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.modified_by, 'testeditor')

class DummySecurityWorkflow:
    def __init__(self, context):
        self.context = context

    def setInitialState(self, request, **kw):
        pass

    def updateState(self, request, **kw):
        if kw['sharing']:
            self.context.transition_id = 'private'
        else:
            self.context.transition_id = 'public'

    def getStateMap(self):
        return {}

class TestEditFileView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        testing.registerUtility(self.mailer, IMailDelivery)

        # Register security workflow
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _callFUT(self, context, request):
        from karl.content.views.files import edit_file_view
        return edit_file_view(context, request)

    def test_submitted_invalid(self):
        self._register()
        self._registerLayoutProvider()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context.catalog = DummyCatalog()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                # Empty title will cause a validation error.
                'title': '',
                'file': None,
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/edit_file.pt')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                (ICommunityFile,),
                                IContentFactory)
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        self._register()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context.catalog = DummyCatalog()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'title': 'new title',
                'file': DummyFieldStorage(),
                'security_state': 'public',
                'tags': 'thetesttag',
                })
            )
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                (ICommunityFile,),
                                IContentFactory)
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=File%20changed')
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(context.mimetype, 'x/foo')
        self.assertEqual(context.filename, 'filename')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.stream, 'abc')
        self.assertEqual(context.modified_by, 'testeditor')

    def test_submitted_valid_nofile(self):
        #valid submission but no file, means keep existing. # NO DOCSTRINGS!

        self._register()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context.mimetype = 'old/blah'
        context.filename = 'its_mine'
        context.stream = '11010110101...'
        context.catalog = DummyCatalog()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'title': 'new title',
                'security_state': 'public',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/edit_file.pt')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                (ICommunityFile,),
                                IContentFactory)
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=File%20changed')
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(context.mimetype, 'old/blah')
        self.assertEqual(context.filename, 'its_mine')
        self.assertEqual(context.stream, '11010110101...')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)

    def test_submitted_valid_emptyfile(self):
        #valid submission with an empty input field present, means
        # keep existing. # NO DOCSTRINGS!
        self._register()

        context = DummyFile(title='oldtitle')
        context.__name__ = None
        context.__parent__ = None
        context.mimetype = 'old/blah'
        context.filename = 'its_mine'
        context.stream = '11010110101...'
        context.catalog = DummyCatalog()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'title': 'new title',
                # file is empty
                'file': '',
                'security_state': 'public',
                })
            )
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyCommunityFile,
                                (ICommunityFile,),
                                IContentFactory)
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=File%20changed')
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, u'new title')
        self.assertEqual(context.mimetype, 'old/blah')
        self.assertEqual(context.filename, 'its_mine')
        self.assertEqual(context.stream, '11010110101...')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)

class TestAdvancedFolderView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        self._registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _callFUT(self, context, request):
        from karl.content.views.files import advanced_folder_view
        return advanced_folder_view(context, request)

    def test_render(self):
        context = testing.DummyModel(title='Dummy')
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")

    def test_render_reference_manual(self):
        from karl.content.interfaces import IReferencesFolder
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, IReferencesFolder)
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")
        self.assertEqual(renderer.selected, 'reference_manual')

    def test_render_network_news(self):
        from karl.content.views.interfaces import INetworkNewsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, INetworkNewsMarker)
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")
        self.assertEqual(renderer.selected, 'network_news')

    def test_render_network_events(self):
        from karl.content.views.interfaces import INetworkEventsMarker
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='Dummy')
        alsoProvides(context, INetworkEventsMarker)
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")
        self.assertEqual(renderer.selected, 'network_events')

    def test_cancel(self):
        context = testing.DummyModel(title='Dummy')
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.cancel': '1',
                })
            )
        response = self._callFUT(context, request)
        self.assertEqual(response.location, "http://example.com/")

    def test_submit_no_marker(self):
        context = testing.DummyModel(title='Dummy')
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.post_url, "http://example.com/advanced.html")

    def test_submit_reference_manual(self):
        context = testing.DummyModel(title='Dummy')
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'reference_manual',
                })
            )
        renderer = testing.registerDummyRenderer(
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
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_news',
                })
            )
        renderer = testing.registerDummyRenderer(
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
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_events',
                })
            )
        renderer = testing.registerDummyRenderer(
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
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'reference_manual',
                })
            )
        renderer = testing.registerDummyRenderer(
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
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_news',
                })
            )
        renderer = testing.registerDummyRenderer(
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
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'marker': 'network_events',
                })
            )
        renderer = testing.registerDummyRenderer(
            'templates/advanced_folder.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         "http://example.com/?status_message=Marker+changed")

        self.failIf(IReferencesFolder.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.failUnless(INetworkEventsMarker.providedBy(context))

class TestGetUploadMimetype(unittest.TestCase):
    def _callFUT(self, fieldstorage):
        from karl.content.views.files import get_upload_mimetype
        return get_upload_mimetype(fieldstorage)

    def test_good_upload(self):
        fieldstorage = DummyFieldStorage()
        mimetype = self._callFUT(fieldstorage)
        self.assertEqual(mimetype, "x/foo")

    def test_fix_broken_upload(self):
        fieldstorage = DummyFieldStorage()
        fieldstorage.type = 'application/x-download'
        fieldstorage.filename = 'file.pdf'
        mimetype = self._callFUT(fieldstorage)
        self.assertEqual(mimetype, "application/pdf")

    def test_cant_fix_broken_upload(self):
        fieldstorage = DummyFieldStorage()
        fieldstorage.type = 'application/x-download'
        fieldstorage.filename = 'somefile'
        mimetype = self._callFUT(fieldstorage)
        self.assertEqual(mimetype, "application/x-download")

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

class DummyFieldStorage:
    file = 'abc'
    filename = 'filename'
    type = 'x/foo'

class DummyFileInfo(object):
    def __init__(self, item, request):
        self.title = 'title'
        self.url = 'url'
        self.mimeinfo = {'small_icon_name': 'folder_small.gif', 'title': 'Folder'}
        self.modified = '12/12/2008'

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
