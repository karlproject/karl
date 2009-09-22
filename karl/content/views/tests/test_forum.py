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

from zope.testing.cleanup import cleanUp
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
        ad = testing.registerAdapter(DummyLayoutProvider,
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
        topics = renderer.topics
        self.assertEqual(actions[0][0], 'Add Forum Topic')

class AddForumView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import add_forum_view
        return add_forum_view(context, request)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def test_cancel(self):
        request = testing.DummyRequest(params={'form.cancel':'1'})
        context = testing.DummyModel()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_submitted_bad_values(self):
        request = testing.DummyRequest(params=dictall({'form.submitted':'1',
                                               'title':'',
                                               'tags':'',
                                               'description':'',}))

        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer(
            'templates/add_forum.pt')
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(str(renderer.fielderrors['description']),
                         'Please enter a value')
        self.assertEqual(str(renderer.fielderrors['title']),
                         'Please enter a value')

    def test_submitted_success(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IForum
        def factory(title, desc, creator):
            return testing.DummyModel(
                title=title, description=desc, creator=creator)
        registerContentFactory(factory, IForum)
        request = testing.DummyRequest(params=dictall({'form.submitted':'1',
                                               'title':'title',
                                               'tags':'',
                                               'description':'desc',}))

        context = testing.DummyModel()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/title/')
        self.assertEqual(context['title'].title, 'title')
        self.assertEqual(context['title'].description, 'desc')
        self.assertEqual(context['title'].creator, None)

class TestAddForumTopicView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import add_forum_topic_view
        return add_forum_topic_view(context, request)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider,
                                     (Interface, Interface),
                                     ILayoutProvider)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def test_cancel(self):
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict({'form.cancel':'1'})
        context = testing.DummyModel()
        self._registerLayoutProvider()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_submitted_bad_values(self):
        self._registerLayoutProvider()
        request = testing.DummyRequest(
            params=dictall({'form.submitted':'1',
                            'title':'',
                            'text':''}))

        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer(
            'templates/add_forumtopic.pt')
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(str(renderer.fielderrors['title']),
                         'Please enter a value')

    def test_submitted_success(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IForumTopic
        def factory(title, text, creator):
            topic = testing.DummyModel(
                title=title, text=text, creator=creator)
            topic['comments'] = testing.DummyModel()
            topic['attachments'] = testing.DummyModel()
            return topic
        registerContentFactory(factory, IForumTopic)
        request = testing.DummyRequest(params=dictall({
            'form.submitted':'1',
            'title':'title',
            'text':'abc',
            'tags': 'thetesttag',
            }))

        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/title/')
        self.assertEqual(context['title'].title, 'title')
        self.assertEqual(context['title'].text, 'abc')
        self.assertEqual(context['title'].creator, None)


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
        ad = testing.registerAdapter(DummyLayoutProvider,
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

class TestEditForumView(unittest.TestCase):
    template_fn = 'templates/edit_forum.pt'
    def setUp(self):
        cleanUp()
        from karl.testing import registerSecurityWorkflow
        registerSecurityWorkflow()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import edit_forum_view
        return edit_forum_view(context, request)

    def test_notsubmitted(self):
        renderer = testing.registerDummyRenderer(self.template_fn)
        request = testing.DummyRequest()
        context = testing.DummyModel(
            title = 'title',
            description = 'description',
            )
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        renderer = testing.registerDummyRenderer(self.template_fn)
        from webob import MultiDict

        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = testing.DummyModel(title='oldtitle')
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        renderer = testing.registerDummyRenderer(self.template_fn)
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title':'newtitle',
                    'description':'newdescription',
                    'tags': 'thetesttag',
                    })
            )
        context = testing.DummyModel(
            title='oldtitle', description='olddescription')
        context.catalog = DummyCatalog()
        from karl.models.interfaces import IObjectModifiedEvent
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Forum%20edited')
        self.assertEqual(context.title, 'newtitle')
        self.assertEqual(context.description, 'newdescription')
        self.assertEqual(context.modified_by, 'testeditor')



class TestEditForumTopicView(unittest.TestCase):
    template_fn = 'templates/edit_forumtopic.pt'
    def setUp(self):
        cleanUp()
        from karl.testing import registerSecurityWorkflow
        registerSecurityWorkflow()
        from karl.testing import registerTagbox
        registerTagbox()
        from karl.testing import registerLayoutProvider
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.forum import edit_forum_topic_view
        return edit_forum_topic_view(context, request)

    def test_notsubmitted(self):
        renderer = testing.registerDummyRenderer(self.template_fn)
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        context = testing.DummyModel(
            title = 'title',
            text = 'text',
            )
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        renderer = testing.registerDummyRenderer(self.template_fn)
        from webob import MultiDict

        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    })
            )
        context = testing.DummyModel(title='oldtitle')
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        context = testing.DummyModel(
            title='oldtitle',
            text='oldtext',
            )
        renderer = testing.registerDummyRenderer(self.template_fn)
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title':'newtitle',
                    'text':'newtext',
                    })
            )
        context['attachments'] = testing.DummyModel()
        context.catalog = DummyCatalog()
        from karl.models.interfaces import IObjectModifiedEvent
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Forum%20Topic%20edited')
        self.assertEqual(L[0], context)
        self.assertEqual(L[1].object, context)
        self.assertEqual(context.title, 'newtitle')
        self.assertEqual(context.text, 'newtext')
        self.assertEqual(len(context['attachments']), 0)
        self.assertEqual(context.modified_by, 'testeditor')

    def test_submitted_valid_with_attachments(self):
        context = testing.DummyModel(
            title='oldtitle',
            text='oldtext',
            )
        class DummyUpload:
            filename='test.txt'
            file='123'
            type='text/plain'
        renderer = testing.registerDummyRenderer(self.template_fn)
        from webob import MultiDict
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted':'1',
                    'title':'newtitle',
                    'text':'newtext',
                    'attachment0':DummyUpload(),
                    })
            )
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        def factory(**args):
            res = testing.DummyModel(**args)
            res.size = 10
            return res
        registerContentFactory(factory, ICommunityFile)
        context['attachments'] = testing.DummyModel()
        context.catalog = DummyCatalog()
        from karl.models.interfaces import IObjectModifiedEvent
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Forum%20Topic%20edited')
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
