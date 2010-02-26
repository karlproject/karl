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
from zope.interface import directlyProvides
from zope.interface import alsoProvides

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

from karl.testing import DummyCatalog
from karl.testing import DummyLayoutProvider
from karl.testing import DummyProfile

class TestShowForumsView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import show_forums_view
        return show_forums_view(context, request)

    def _register(self):
        d1 = 'Wednesday, January 28, 2009 08:32 AM'
        def dummy(date, flavor):
            return d1
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)


    def test_it_empty(self):
        self._register()
        context = testing.DummyModel()
        context.title = 'abc'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/show_forums.pt')
        self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(actions[0][0], 'Add Forum')

    def test_it_full(self):
        self._register()
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummySearchAdapter, (Interface),
                                ICatalogSearch)
        context = testing.DummyModel()
        context['forum'] = testing.DummyModel()
        context['forum'].title = 'forum'
        context.title = 'abc'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/show_forums.pt')
        self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(actions[0][0], 'Add Forum')
        self.assertEqual(len(renderer.forum_data), 1)

class TestShowForumView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import show_forum_view
        return show_forum_view(context, request)

    def _register(self):
        d1 = 'Wednesday, January 28, 2009 08:32 AM'
        def dummy(date, flavor):
            return d1
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        testing.registerAdapter(DummyLayoutProvider,
                                (Interface, Interface),
                                ILayoutProvider)

    def test_it(self):
        self._register()
        self._registerLayoutProvider()
        from karl.models.interfaces import ICatalogSearch
        from karl.content.interfaces import IForumsFolder
        testing.registerAdapter(DummySearchAdapter, (Interface),
                                ICatalogSearch)
        context = testing.DummyModel(title='abc')
        alsoProvides(context, IForumsFolder)
        from karl.models.interfaces import IIntranets
        intranets = testing.DummyModel(title='Intranets')
        directlyProvides(intranets, IIntranets)
        intranets['forums'] = context
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/show_forum.pt')
        self._callFUT(context, request)
        actions = renderer.actions
        self.assertEqual(actions[0][0], 'Add Forum Topic')


class TestAddForumFormController(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        
    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, *arg, **kw):
        from karl.content.views.forum import AddForumFormController
        return AddForumFormController(*arg, **kw)

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
        self.assertEqual(defaults['description'], '')
        self.assertEqual(defaults['security_state'], workflow.initial_state)
        
    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('title' in dict(fields))
        self.failUnless('description' in dict(fields))
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
        self.failUnless('page_title' in response)
        self.failUnless('api' in response)

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IForum
        def factory(title, desc, creator):
            return testing.DummyModel(
                title=title, description=desc, creator=creator)
        registerContentFactory(factory, IForum)
        converted = {
            'title':'title',
            'description':'desc',
            'security_state':'public'}

        context = testing.DummyModel()
        request = testing.DummyRequest()
        workflow = self._registerDummyWorkflow()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/title/')
        self.assertEqual(context['title'].title, 'title')
        self.assertEqual(context['title'].description, 'desc')
        self.assertEqual(context['title'].creator, None)
        self.assertEqual(workflow.initialized, True)

class TestAddForumTopicFormController(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        
    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, *arg, **kw):
        from karl.content.views.forum import AddForumTopicFormController
        return AddForumTopicFormController(*arg, **kw)

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        return request

    def _makeContext(self):
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        return context

    def _registerDummyWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_form_defaults(self):
        workflow = self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], '')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['text'], '')
        self.assertEqual(defaults['attachments'], [])
        self.assertEqual(defaults['security_state'], workflow.initial_state)
        
    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('attachments.*' in widgets)

    def test___call__(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('page_title' in response)
        self.failUnless('api' in response)
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self): 
        from karl.testing import DummyUpload
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IForumTopic
        from karl.content.interfaces import ICommunityFile

        def factory(title, text, creator):
            topic = testing.DummyModel(
                title=title, text=text, creator=creator)
            topic['comments'] = testing.DummyModel()
            topic['attachments'] = testing.DummyModel()
            return topic
        registerContentFactory(factory, IForumTopic)
        registerContentFactory(DummyFile, ICommunityFile)

        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename=r"C:\My Documents\Ha Ha\test2.txt")

        converted = {
            'title':'title',
            'text':'abc',
            'tags': 'thetesttag',
            'security_state':'public',
            'attachments':[attachment1, attachment2],
            }

        context = self._makeContext()
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        workflow = self._registerDummyWorkflow()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/title/')
        self.assertEqual(context['title'].title, 'title')
        self.assertEqual(context['title'].text, 'abc')
        self.assertEqual(context['title'].creator, None)
        self.assertEqual(workflow.initialized, True)
        self.assertEqual(len(context['title']['attachments']), 2)

class ShowForumTopicViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import show_forum_topic_view
        return show_forum_topic_view(context, request)

    def _register(self):
        d1 = 'Wednesday, January 28, 2009 08:32 AM'
        def dummy(date, flavor):
            return d1
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        testing.registerAdapter(DummyLayoutProvider,
                                (Interface, Interface),
                                ILayoutProvider)

    def test_no_security_policy(self):
        self._register()
        self._registerLayoutProvider()
        import datetime
        _NOW = datetime.datetime.now()
        context = testing.DummyModel()
        context.title = 'title'
        context['comments'] = testing.DummyModel()
        comment = testing.DummyModel()
        comment.creator = 'dummy'
        comment.created = _NOW
        comment.text = 'sometext'
        context['comments']['1'] = comment
        context['attachments'] = testing.DummyModel()
        from karl.models.interfaces import ISite
        from karl.content.interfaces import IForum
        directlyProvides(context, ISite)
        alsoProvides(context, IForum)
        context['profiles'] = profiles = testing.DummyModel()
        profiles['dummy'] = DummyProfile(title='Dummy Profile')
        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        renderer = testing.registerDummyRenderer(
            'templates/show_forum_topic.pt')
        self._callFUT(context, request)
        self.assertEqual(len(renderer.comments), 1)
        c0 = renderer.comments[0]
        self.assertEqual(c0['text'], 'sometext')

        self.assertEqual(renderer.comments[0]['date'],
                         'Wednesday, January 28, 2009 08:32 AM')
        self.assertEqual(c0['author_name'], 'Dummy Profile')
        self.assertEqual(renderer.comments[0]['edit_url'],
                         'http://example.com/comments/1/edit.html')


    def test_with_security_policy(self):
        self._register()
        self._registerLayoutProvider()
        import datetime
        _NOW = datetime.datetime.now()
        context = testing.DummyModel(title='title')
        from karl.content.interfaces import IForum
        alsoProvides(context, IForum)
        context['profiles'] = profiles = testing.DummyModel()
        profiles['dummy'] = DummyProfile()
        context['comments'] = testing.DummyModel()
        comment = testing.DummyModel(text='sometext')
        comment.creator = 'dummy'
        comment.created = _NOW
        context['comments']['1'] = comment
        context['attachments'] = testing.DummyModel()
        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        self._register()
        testing.registerDummySecurityPolicy(permissive=False)

        renderer = testing.registerDummyRenderer(
            'templates/show_forum_topic.pt')
        self._callFUT(context, request)

        self.assertEqual(renderer.comments[0]['edit_url'], None)

    def test_comment_ordering(self):
        self._register()
        self._registerLayoutProvider()
        import datetime
        _NOW = datetime.datetime.now()
        _BEFORE = _NOW - datetime.timedelta(hours=1)

        context = testing.DummyModel()
        context.title = 'title'
        context['comments'] = testing.DummyModel()

        comment = testing.DummyModel()
        comment.creator = 'dummy'
        comment.created = _NOW
        comment.text = 'My dog has fleas.'
        context['comments']['1'] = comment

        comment2 = testing.DummyModel()
        comment2.creator = 'dummy'
        comment2.created = _BEFORE
        comment2.text = "My cat's breath smells like cat food."
        context['comments']['2'] = comment2

        context['attachments'] = testing.DummyModel()
        from karl.models.interfaces import ISite
        from karl.content.interfaces import IForum
        directlyProvides(context, ISite)
        alsoProvides(context, IForum)
        context['profiles'] = profiles = testing.DummyModel()
        profiles['dummy'] = DummyProfile(title='Dummy Profile')
        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        renderer = testing.registerDummyRenderer(
            'templates/show_forum_topic.pt')
        self._callFUT(context, request)

        self.assertEqual(len(renderer.comments), 2)
        self.assertEqual(renderer.comments[0]['text'],
                         "My cat's breath smells like cat food.")
        self.assertEqual(renderer.comments[1]['text'],
                         'My dog has fleas.')


class TestEditForumFormController(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        
    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, *arg, **kw):
        from karl.content.views.forum import EditForumFormController
        return EditForumFormController(*arg, **kw)

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
        context.title = 'title'
        context.description = 'description'
        context.security_state = 'public'
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'title')
        self.assertEqual(defaults['description'], 'description')
        self.assertEqual(defaults['security_state'], 'public')
        
    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('title' in dict(fields))
        self.failUnless('description' in dict(fields))
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
        context.title = 'title'
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.assertEqual(response['page_title'], 'Edit title')
        self.failUnless('api' in response)

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        converted = {
            'title':'newtitle',
            'description':'newdescription',
            }
        context = testing.DummyModel(
            title='oldtitle', description='olddescription')
        context.catalog = DummyCatalog()
        from karl.models.interfaces import IObjectModifiedEvent
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Forum+Edited')
        self.assertEqual(context.title, 'newtitle')
        self.assertEqual(context.description, 'newdescription')
        self.assertEqual(context.modified_by, 'testeditor')

class EditForumTopicFormController(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, *arg, **kw):
        from karl.content.views.forum import EditForumTopicFormController
        return EditForumTopicFormController(*arg, **kw)

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        return request

    def _makeContext(self):
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        return context

    def _registerDummyWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def test_form_defaults(self):
        self._registerDummyWorkflow()
        context = self._makeContext()
        context.title = 'title'
        context.text = 'text'
        context.security_state = 'public'
        context['attachments'] = testing.DummyModel()
        context['attachments']['a'] = DummyFile(__name__='1',
                                                mimetype='text/plain')
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'title')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['text'], 'text')
        self.assertEqual(len(defaults['attachments']),1)
        self.assertEqual(defaults['security_state'], 'public')
        
    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        from karl.models.interfaces import ITagQuery
        from zope.interface import Interface
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('attachments.*' in widgets)

    def test___call__(self):
        context = self._makeContext()
        context.title = 'title'
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless(response['page_title'], 'Edit title')
        self.failUnless('api' in response)
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from karl.testing import DummyUpload
        context = testing.DummyModel(
            title='oldtitle',
            text='oldtext',
            )

        upload = DummyUpload(filename='test.txt')

        converted = {
            'title':'newtitle',
            'text':'newtext',
            'tags':[],
            'security_state':'public',
            'attachments':[DummyUpload()],
            }
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        def factory(**args):
            res = testing.DummyModel(**args)
            res.size = 10
            return res
        registerContentFactory(factory, ICommunityFile)
        context['attachments'] = testing.DummyModel()
        context.catalog = DummyCatalog()
        context.sessions = DummySessions()
        from karl.models.interfaces import IObjectModifiedEvent
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Forum+Topic+Edited')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.title, 'newtitle')
        self.assertEqual(context.text, 'newtext')
        self.assertEqual(len(context['attachments']), 1)
        self.assertEqual(context['attachments'].keys(), ['test.txt'])
        self.assertEqual(
            context['attachments']['test.txt'].mimetype, 'text/plain')
        
    

class dictall(dict):
    def getall(self, name):
        result = self.get(name)
        if result is None:
            return []
        return [result]

class DummySearchAdapter:
    def __init__(self, context):
        self.context = context

    def __call__(self, **kw):
        return 0, [], None

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

    def initialize(self, context):
        self.initialized = True

class DummySessions(dict):
    def get(self, name, default=None):
        if name not in self:
            self[name] = {}
        return self[name]

class DummyFile:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.size = 0

