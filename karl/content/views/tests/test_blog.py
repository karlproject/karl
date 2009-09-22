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

from zope.interface import implements


class ShowBlogViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

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
        from webob import MultiDict
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
        cleanUp()

    def tearDown(self):
        cleanUp()

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

class AddBlogEntryViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

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

        self.blog = testing.DummyModel()
        self.community["blog"] = self.blog

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.blog import add_blogentry_view
        return add_blogentry_view(context, request)

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def test_notsubmitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        self._register()
        renderer = testing.registerDummyRenderer('templates/add_blogentry.pt')
        response = self._callFUT(context, request)
        self.assertEqual(0, len(self.mailer))
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        context = testing.DummyModel()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1'})
                    )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/add_blogentry.pt')
        self._callFUT(context, request)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)
        self.assertEqual(0, len(self.mailer))

    def test_submitted_invalid_notitle(self):
        context = testing.DummyModel()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1',
                    #'title': '',
                    'text': 'text',
                    'sendalert': True})
                    )
        self._register()
        renderer = testing.registerDummyRenderer('templates/add_blogentry.pt')
        self._callFUT(context, request)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)
        self.assertEqual(0, len(self.mailer))

    def test_submitted_alreadyexists(self):
        from webob import MultiDict
        from karl.testing import DummyCatalog
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory

        self._register()
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        renderer = testing.registerDummyRenderer('templates/add_blogentry.pt')

        context = self.blog
        foo = testing.DummyModel()
        context['foo'] = foo
        self.site.system_email_domain = 'example.com'
        tags = DummyTags()
        self.site.tags = tags
        self.site.catalog = DummyCatalog()
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('sendalert', 'true'),
                    ('security_state', 'public'),
                    ])
            )

        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo-1/')

        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo-2/')

        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo-3/')

    def test_submitted_valid(self):
        from karl.testing import registerSettings
        registerSettings()

        context = self.blog
        self.site.system_email_domain = 'example.com'
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('sendalert', 'true'),
                    ('security_state', 'public'),
                    ])
            )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/add_blogentry.pt')
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo/')
        self.assertEqual(3, len(self.mailer))
        for x in self.mailer:
            self.assertEqual(x.mfrom, 'community@karl3.example.com')
        recipients = reduce(lambda x,y: x+y, [x.mto for x in self.mailer])
        recipients.sort()
        self.assertEqual(["a@x.org", "b@x.org", "c@x.org",], recipients)

    def test_submitted_valid_no_alert(self):
        context = self.blog
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('sendalert', 'false'),
                    ('security_state', 'public'),
                    ])
            )
        self._register()
        renderer = testing.registerDummyRenderer('templates/add_blogentry.pt')
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo/')
        self.failUnless(context['foo'])
        self.assertEqual(0, len(self.mailer))

    def test_submitted_valid_attachments(self):
        context = self.blog
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename=r"C:\My Documents\Ha Ha\test2.txt")
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                    ('form.submitted', '1'),
                    ('title', 'foo'),
                    ('text', 'text'),
                    ('tags', 'tag1'),
                    ('tags', 'tag2'),
                    ('attachment', attachment1),
                    ('attachment', attachment2),
                    ('sendalert', 'true'),
                    ('security_state', 'public'),
                    ])
            )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/add_blogentry.pt')
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(DummyFile, ICommunityFile)
        response = self._callFUT(context, request)

        blogentry_url = "http://example.com/communities/community/blog/foo/"
        self.assertEqual(response.location, blogentry_url)
        self.failUnless(context['foo'])
        self.assertEqual(3, len(self.mailer))
        recipients = reduce(lambda x,y: x+y, [x.mto for x in self.mailer])
        recipients.sort()
        self.assertEqual(["a@x.org", "b@x.org", "c@x.org",], recipients)

        attachments_url = "%sattachments" % blogentry_url
        self.failUnless(context['foo']['attachments']['test1.txt'])
        self.failUnless(context['foo']['attachments']['test2.txt'])

        from base64 import decodestring
        header, body = self.mailer[0].msg.split('\n\n', 1)
        body = decodestring(body)
        self.failUnless("%s/test1.txt" % attachments_url in body)
        self.failUnless("%s/test2.txt" % attachments_url in body)

        attachment1 = context['foo']['attachments']['test1.txt']
        self.assertEqual(attachment1.filename, "test1.txt")

        attachment2 = context['foo']['attachments']['test2.txt']
        self.assertEqual(attachment2.filename, "test2.txt")

class EditBlogEntryViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from repoze.bfg import testing
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _callFUT(self, context, request):
        from karl.content.views.blog import edit_blogentry_view
        return edit_blogentry_view(context, request)

    def test_notsubmitted(self):
        context = DummyBlogEntry()
        context.__name__ ='ablogentry'
        context.title = 'atitle'
        context.text = 'sometext'
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_blogentry.pt')
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        context = DummyBlogEntry()
        context.__name__ ='ablogentry'
        context.title = 'atitle'
        context.text = 'sometext'
        from webob import MultiDict
        from karl.testing import DummyCatalog
        context.catalog = DummyCatalog()
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted': '1',
                    'sendalert': '1',
            })
            )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_blogentry.pt')
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        self._register()
        context = DummyBlogEntry()
        context.__name__ ='ablogentry'
        from karl.testing import DummyCatalog
        context.catalog = DummyCatalog()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1',
                    'title':'foo',
                    'text':'text',
                    'sendalert': 'true',
                    'security_state': 'public',
                    'tags': 'thetesttag',
                    }))
        renderer = testing.registerDummyRenderer(
            'templates/edit_blogentry.pt')
        from karl.content.interfaces import IBlogEntry
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyBlogEntry, IBlogEntry)
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
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
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, api):
        from karl.content.views.blog import BlogSidebar
        b = BlogSidebar(context, request)
        return b(api)

    def test_render(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        api = object()
        renderer = testing.registerDummyRenderer('templates/blog_sidebar.pt')
        html = self._callFUT(context, request, api)
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
        html = self._callFUT(context, request, api)
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
