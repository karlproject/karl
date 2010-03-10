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

from repoze.bfg import testing

from zope.interface import implements


class ShowBlogViewTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.blog import show_blog_view
        return show_blog_view(context, request)

    def test_it(self):
        context = testing.DummyModel()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        from karl.testing import DummyProfile
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')
        directlyProvides(context, ISite)
        context.catalog = {'creation_date': DummyCreationDateIndex()}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['dummy'] = DummyProfile(title='Dummy Creator')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'year': 2009, 'month': 4}))
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)
        from datetime import datetime
        entry = testing.DummyModel(
            creator='dummy', title='Dummy Entry',
            description='Some words',
            created=datetime(2009, 4, 15))
        from zope.interface import directlyProvides
        from karl.content.interfaces import IBlogEntry
        directlyProvides(entry, IBlogEntry)
        entry['comments'] = testing.DummyModel()
        entry['comments']['1'] = DummyComment()
        context['e1'] = entry
        renderer = testing.registerDummyRenderer('templates/show_blog.pt')
        def dummy_byline_info(context, request):
            return context
        from zope.interface import Interface
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        self._callFUT(context, request)
        self.assertEqual(len(renderer.entries), 1)
        self.assertEqual(renderer.entries[0]['title'], 'Dummy Entry')
        self.assertEqual(renderer.entries[0]['creator_href'],
                         'http://example.com/e1/')
        self.assertEqual(renderer.entries[0]['href'],
                         'http://example.com/e1/')
        self.assertEqual(renderer.entries[0]['creator_title'],
                         'Dummy Creator')

class ShowBlogEntryViewTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.utilities.interfaces import IKarlDates
        from karl.models.interfaces import ITagQuery
        testing.registerUtility(dummy, IKarlDates)
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _callFUT(self, context, request):
        from karl.content.views.blog import show_blogentry_view
        return show_blogentry_view(context, request)

    def test_no_security_policy(self):
        context = DummyBlogEntry()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        from karl.testing import DummyProfile
        directlyProvides(context, ISite)
        from karl.content.interfaces import IBlog
        from zope.interface import alsoProvides

        alsoProvides(context, IBlog)
        context['profiles'] = profiles = testing.DummyModel()
        profiles['dummy'] = DummyProfile(title='Dummy Profile')
        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from zope.interface import Interface
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        self._register()
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)
        renderer = testing.registerDummyRenderer('templates/show_blogentry.pt')
        self._callFUT(context, request)
        self.assertEqual(len(renderer.comments), 1)
        c0 = renderer.comments[0]
        self.assertEqual(c0['text'], 'sometext')

        self.assertEqual(d1, renderer.comments[0]['date'])
        self.assertEqual(c0['author_name'], 'Dummy Profile')
        self.assertEqual(renderer.comments[0]['edit_url'],
                         'http://example.com/blogentry/comments/1/edit.html')


    def test_with_security_policy(self):
        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import IBlog
        from zope.interface import alsoProvides
        context = DummyBlogEntry()
        alsoProvides(context, IBlog)
        alsoProvides(context, IBlogEntry)
        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from zope.interface import Interface
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        self._register()
        testing.registerDummySecurityPolicy(permissive=False)

        renderer = testing.registerDummyRenderer('templates/show_blogentry.pt')
        self._callFUT(context, request)

        self.assertEqual(renderer.comments[0]['edit_url'], None)

    def test_comment_ordering(self):
        context = DummyBlogEntry()
        context['comments']['2'] = DummyComment(now=1233149510, text=u'before')
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        from karl.testing import DummyProfile
        directlyProvides(context, ISite)
        from karl.content.interfaces import IBlog
        from zope.interface import alsoProvides

        alsoProvides(context, IBlog)
        context['profiles'] = profiles = testing.DummyModel()
        profiles['dummy'] = DummyProfile(title='Dummy Profile')
        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from zope.interface import Interface
        from karl.content.views.interfaces import IBylineInfo
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        self._register()
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)
        renderer = testing.registerDummyRenderer('templates/show_blogentry.pt')
        self._callFUT(context, request)
        self.assertEqual(len(renderer.comments), 2)
        self.assertEqual('before', renderer.comments[0]['text'])
        self.assertEqual('sometext', renderer.comments[1]['text'])

class AddBlogEntryFormControllerTests(unittest.TestCase):
    def setUp(self):
        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        testing.registerUtility(self.mailer, IMailDelivery)

        # Register BlogEntryAlert adapter
        from karl.models.interfaces import IProfile
        from karl.content.interfaces import IBlogEntry
        from karl.content.views.adapters import BlogEntryAlert
        from karl.utilities.interfaces import IAlert
        from repoze.bfg.interfaces import IRequest
        testing.registerAdapter(BlogEntryAlert,
                                (IBlogEntry, IProfile, IRequest),
                                IAlert)

        testing.registerDummySecurityPolicy("a")

        # Create dummy site skel
        from karl.testing import DummyCommunity
        self.community = DummyCommunity()
        self.site = self.community.__parent__.__parent__

        self.profiles = testing.DummyModel()
        self.site["profiles"] = self.profiles
        from karl.testing import DummyProfile
        self.profiles["a"] = DummyProfile()
        self.profiles["b"] = DummyProfile()
        self.profiles["c"] = DummyProfile()
        for profile in self.profiles.values():
            profile["alerts"] = testing.DummyModel()

        self.community.member_names = set(["b", "c",])
        self.community.moderator_names = set(["a",])

        self.blog = self._makeContext()
        self.community["blog"] = self.blog

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, *arg, **kw):
        from karl.content.views.blog import AddBlogEntryFormController
        return AddBlogEntryFormController(*arg, **kw)

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

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

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
        self.assertEqual(defaults['sendalert'], True)
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
        self.failUnless('api' in response)

    def test_handle_cancel(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from karl.testing import registerSettings
        registerSettings()

        context = self.blog
        self.site.system_email_domain = 'example.com'
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        self.site.sessions = DummySessions()
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename=r"C:\My Documents\Ha Ha\test2.txt")
        converted = {
            'title':'foo',
            'text':'text',
            'tags':['tag1', 'tag2'],
            'sendalert':True,
            'security_state':'public',
            'attachments':[attachment1, attachment2],
            }
        self._register()
        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        registerContentFactory(DummyFile, ICommunityFile)
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo/')
        self.assertEqual(3, len(self.mailer))
        for x in self.mailer:
            self.assertEqual(x.mfrom, 'community@karl3.example.com')
        recipients = reduce(lambda x,y: x+y, [x.mto for x in self.mailer])
        recipients.sort()
        self.assertEqual(["a@x.org", "b@x.org", "c@x.org",], recipients)

        blogentry_url = "http://example.com/communities/community/blog/foo/"

        attachments_url = "%sattachments" % blogentry_url
        self.failUnless(context['foo']['attachments']['test1.txt'])
        self.failUnless(context['foo']['attachments']['test2.txt'])

        from base64 import decodestring
        body = self.mailer[0].msg.get_payload(decode=True)
        self.failUnless("%s/test1.txt" % attachments_url in body)
        self.failUnless("%s/test2.txt" % attachments_url in body)

        attachment1 = context['foo']['attachments']['test1.txt']
        self.assertEqual(attachment1.filename, "test1.txt")

        attachment2 = context['foo']['attachments']['test2.txt']
        self.assertEqual(attachment2.filename, "test2.txt")

class EditBlogEntryFormControllerTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        return request

    def _makeContext(self):
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        return context

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _makeOne(self, *arg, **kw):
        from karl.content.views.blog import EditBlogEntryFormController
        return EditBlogEntryFormController(*arg, **kw)

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
        context.text = 'abc'
        context['attachments'] = testing.DummyModel()
        context['attachments']['a'] = DummyFile(__name__='1',
                                                mimetype='text/plain')
        context.security_state = 'private'
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'title')
        self.assertEqual(defaults['tags'], [])
        self.assertEqual(defaults['text'], 'abc')
        self.assertEqual(len(defaults['attachments']), 1)
        self.assertEqual(defaults['security_state'], 'private')

    def test_form_fields(self):
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless('tags' in dict(fields))
        self.failUnless('security_state' in dict(fields))

    def test_form_widgets(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        self._registerDummyWorkflow()
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets({'security_state':True})
        self.failUnless('security_state' in widgets)
        self.failUnless('attachments.*' in widgets)

    def test___call__(self):
        context = self._makeContext()
        context.title = 'thing'
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit thing')

    def test_handle_cancel(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        from schemaish.type import File as SchemaFile
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        from karl.testing import DummyCatalog
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        self._registerDummyWorkflow()
        context = DummyBlogEntry()
        context.sessions = DummySessions()
        context.__name__ ='ablogentry'
        context.catalog = DummyCatalog()
        context['attachments'] = testing.DummyModel()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        converted = {'title':'foo',
                     'text':'text',
                     'security_state':'public',
                     'tags':'thetesttag',
                     'attachments':[SchemaFile(None, None, None)],
                     }
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, 'http://example.com/ablogentry/')
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, 'foo')
        self.assertEqual(context.text, 'text')
        self.assertEqual(context.modified_by, 'testeditor')

class MonthRangeTests(unittest.TestCase):
    def test_coarse_month_range(self):
        from karl.content.views.blog import coarse_month_range
        self.assertEqual(coarse_month_range(2009, 4), (12385440, 12411359))
        self.assertEqual(coarse_month_range(2008, 1), (11991456, 12018239))


class BlogSidebarTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request, api):
        from karl.content.views.blog import BlogSidebar
        b = BlogSidebar(context, request)
        return b(api)

    def test_render(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        api = object()
        renderer = testing.registerDummyRenderer('templates/blog_sidebar.pt')
        self._callFUT(context, request, api)
        self.assertEquals(renderer.api, api)
        self.assertEquals(len(renderer.activity_list), 0)
        self.assertEquals(renderer.blog_url, 'http://example.com/')

    def test_render_with_content(self):
        context = testing.DummyModel()
        from datetime import datetime
        from zope.interface import directlyProvides
        from karl.content.interfaces import IBlogEntry
        e1 = testing.DummyModel(created=datetime(2009, 1, 2))
        directlyProvides(e1, IBlogEntry)
        e2 = testing.DummyModel(created=datetime(2009, 1, 10))
        directlyProvides(e2, IBlogEntry)
        context['e1'] = e1
        context['e2'] = e2
        request = testing.DummyRequest()
        api = object()
        renderer = testing.registerDummyRenderer('templates/blog_sidebar.pt')
        self._callFUT(context, request, api)
        self.assertEquals(renderer.api, api)
        self.assertEquals(len(renderer.activity_list), 1)
        self.assertEquals(renderer.activity_list[0].year, 2009)
        self.assertEquals(renderer.activity_list[0].month_name, 'January')
        self.assertEquals(renderer.activity_list[0].count, 2)
        self.assertEquals(renderer.blog_url, 'http://example.com/')

    def test_render_ten(self):
        context = testing.DummyModel()
        from datetime import datetime
        from zope.interface import directlyProvides
        from karl.content.interfaces import IBlogEntry
        for month in range(1, 11):
            for day in (4, 7):
                e = testing.DummyModel(created=datetime(2008, month, day))
                directlyProvides(e, IBlogEntry)
                context['e%d-%d' % (month, day)] = e
        request = testing.DummyRequest()
        api = object()
        renderer = testing.registerDummyRenderer('templates/blog_sidebar.pt')
        self._callFUT(context, request, api)
        self.assertEquals(len(renderer.activity_list), 10)

class Test_upload_attachments(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from karl.content.views.blog import upload_attachments
        return upload_attachments(*arg, **kw)

    def test_with_filename(self):
        from karl.content.interfaces import ICommunityFile
        from StringIO import StringIO
        attachments = [ DummyFile(filename='abc', mimetype='text/plain',
                                  file=StringIO('abc')) ]
        folder = testing.DummyModel()
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyFile, ICommunityFile)
        request = testing.DummyRequest()
        self._callFUT(attachments, folder, 'chris', request)
        self.failUnless('abc' in folder)

    def test_with_filename_too_big(self):
        from karl.testing import registerSettings
        from karl.content.interfaces import ICommunityFile
        from StringIO import StringIO
        registerSettings(upload_limit=1)
        attachments = [ DummyFile(filename='abc', mimetype='text/plain',
                                  file=StringIO('abc')) ]
        folder = testing.DummyModel()
        from repoze.lemonade.testing import registerContentFactory
        class BigDummyFile(object):
            def __init__(self, **kw):
                self.__dict__.update(kw)
                self.size = 10000
        registerContentFactory(BigDummyFile, ICommunityFile)
        request = testing.DummyRequest()
        self.assertRaises(ValueError,
                          self._callFUT, attachments, folder, 'chris', request)

    def test_without_filename_remove(self):
        from karl.content.interfaces import ICommunityFile
        attachment = DummyFile(filename=None, metadata={'remove':True,
                                                        'default':'a'})
        attachments = [ attachment ]
        folder = testing.DummyModel()
        folder['a'] = testing.DummyModel()
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyFile, ICommunityFile)
        request = testing.DummyRequest()
        self._callFUT(attachments, folder, 'chris', request)
        self.failIf('a' in folder)

class DummyComment(testing.DummyModel):
    creator = u'dummy'

    def __init__(self, now=1233149520.9288571, text=u'sometext'):
        testing.DummyModel.__init__(self)
        self.text = text
        from datetime import datetime
        self.created = datetime.fromtimestamp(now)

class DummyRoot(testing.DummyModel):
    def __init__(self):
        from karl.testing import DummyProfile
        testing.DummyModel.__init__(self)
        self['profiles'] = testing.DummyModel()
        self['profiles'][u'dummy'] = DummyProfile()

from karl.content.interfaces import IBlogEntry

class DummyBlogEntry(testing.DummyModel):
    implements(IBlogEntry)

    title = 'The blog entry'
    docid = 0
    def __init__(self, title='', text='', description='',
                creator=u'a'):
        testing.DummyModel.__init__(self)
        self.title = title
        self.text = text
        self.description = description
        self.creator = creator
        self['comments'] = testing.DummyModel()
        self['comments']['1'] = DummyComment()
        self.__parent__ = DummyRoot()
        self.__name__ = 'blogentry'
        self['attachments'] = testing.DummyModel()
        from datetime import datetime
        self.created = datetime.now()

d1 = 'Wednesday, January 28, 2009 08:32 AM'
def dummy(date, flavor):
    return d1

class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyTagQuery(DummyAdapter):
    tagswithcounts = []
    docid = 'ABCDEF01'

class DummyTags:
    def update(self, *args, **kw):
        self._called_with = (args, kw)

class DummyFile:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.size = 0

class DummyCreationDateIndex:
    def discriminator(self, obj, default):
        return obj.created


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

class DummySessions(dict):
    def get(self, name, default=None):
        if name not in self:
            self[name] = {}
        return self[name]

