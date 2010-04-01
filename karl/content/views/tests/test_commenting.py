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

from zope.interface import implements
from zope.interface import Interface
from zope.interface import alsoProvides
from repoze.bfg.testing import cleanUp

from repoze.bfg import testing
from repoze.bfg.testing import registerAdapter

from karl.content.interfaces import IBlogEntry
from karl.models.interfaces import IComment

from karl.testing import DummyLayoutProvider

class AddCommentViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Register mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        testing.registerUtility(self.mailer, IMailDelivery)

        # Register BlogCommentAlert adapter
        from karl.models.interfaces import IProfile
        from karl.models.interfaces import IComment
        from karl.content.views.adapters import BlogCommentAlert
        from karl.utilities.interfaces import IAlert
        from repoze.bfg.interfaces import IRequest
        testing.registerAdapter(BlogCommentAlert,
                                (IComment, IProfile, IRequest),
                                IAlert)

        # Create dummy site skel
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        community = DummyCommunity()
        site = community.__parent__.__parent__

        profiles = testing.DummyModel()
        site["profiles"] = profiles
        profiles["a"] = DummyProfile()
        profiles["b"] = DummyProfile()
        profiles["c"] = DummyProfile()

        community.member_names = set(["b", "c",])
        community.moderator_names = set(["a",])

        blog = testing.DummyModel()
        community["blog"] = blog

        blogentry = blog["foo"] = DummyBlogEntry()

        self.context = blogentry["comments"]

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.commenting import add_comment_view
        return add_comment_view(context, request)

    def test_notsubmitted(self):
        from formencode import Invalid
        request = testing.DummyRequest()
        self.assertRaises(Invalid, self._callFUT, self.context, request)
        self.assertEqual(0, len(self.mailer))

    def test_submitted_invalid(self):
        from formencode import Invalid
        request = testing.DummyRequest(
            params={
                'form.submitted': '1',
                }
            )
        request.method = 'POST'
        self.assertRaises(Invalid, self._callFUT, self.context, request)
        self.assertEqual(0, len(self.mailer))

    def test_submitted_valid(self):
        self._registerSecurityWorkflow()
        testing.registerDummyRenderer("templates/email_blog_comment_alert.pt")

        request = testing.DummyRequest(
            params={
                'form.submitted': '1',
                'add_comment': '<p>Some Text</p>',
                'security_state': 'public',
                'sendalert': '1',
                }
            )
        request.method = 'POST'
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyComment,
                                (Interface, ),
                                IContentFactory)
        response = self._callFUT(self.context, request)
        msg = 'http://example.com/communities/community/blog/foo/?status_message=Comment%20added'
        self.assertEqual(response.location, msg)
        self.assertEqual(3, len(self.mailer))
        self.assertEqual(self.context['99'].title, 'Re: Dummy Blog Entry')

    def test_submitted_valid_w_attachments(self):
        self._registerSecurityWorkflow()

        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename=r"C:\My Documents\I Test\test2.txt")
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('form.submitted', '1'),
                ('add_comment', '<p>Some Text</p>'),
                ('attachment', attachment1),
                ('attachment', attachment2),
                ('security_state', 'public'),
                ('sendalert', '1'),
            ])
        )

        testing.registerDummyRenderer("templates/email_blog_comment_alert.pt")

        request.method = 'POST'
        from repoze.lemonade.interfaces import IContentFactory
        from karl.models.interfaces import IComment
        testing.registerAdapter(lambda *arg: DummyComment,
                                (IComment, ),
                                IContentFactory)

        testing.registerAdapter(lambda *arg: testing.DummyModel,
                                (Interface, ),
                                IContentFactory)

        context = self.context
        response = self._callFUT(context, request)
        self.failUnless(context['99'])

        msg = 'http://example.com/communities/community/blog/foo/?status_message=Comment%20added'
        self.assertEqual(response.location, msg)
        self.assertEqual(3, len(self.mailer))

        comment = context['99']
        self.failUnless(comment['test1.txt'])
        self.assertEqual(comment['test1.txt'].filename, "test1.txt")
        self.failUnless(comment['test2.txt'])
        self.assertEqual(comment['test2.txt'].filename, "test2.txt")

    def test_with_get(self):
        from formencode import Invalid
        request = testing.DummyRequest()
        self.assertRaises(Invalid, self._callFUT, self.context, request)

class EditCommentViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.commenting import edit_comment_view
        return edit_comment_view(context, request)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def test_notsubmitted(self):
        self._registerLayoutProvider()
        self._registerSecurityWorkflow()

        context = testing.DummyModel(title='thetitle', text='thetext')
        context.__name__ = 'thecomment'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/edit_comment.pt')
        response =self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fieldvalues['add_comment'], 'thetext')

    def test_submitted_invalid(self):
        self._registerLayoutProvider()
        self._registerSecurityWorkflow()

        context = testing.DummyModel(title='thetitle', text='thetext')
        context.__name__ = 'thecomment'
        context.text = 'text'
        request = testing.DummyRequest(
            params={
                'form.submitted': '1',
                'sharing': False,
                }
            )
        renderer = testing.registerDummyRenderer('templates/edit_comment.pt')
        response =self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        self._registerSecurityWorkflow()

        blog_entry = DummyBlogEntry()
        context = blog_entry.comments
        context.__name__ = 'thecomment'
        context.text = 'yup'
        request = testing.DummyRequest(
            params={
                'form.submitted': '1',
                'add_comment': 'Some Text',
                'security_state': 'public',
                }
            )
        L = testing.registerEventListener((Interface, Interface))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertEqual(context.text, 'Some Text')
        self.assertEqual(len(L), 4)
        self.assertEqual(response.location,
                         'http://example.com/thecomment/')
        self.assertEqual(context.modified_by, 'testeditor')

class ShowCommentViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.commenting import show_comment_view
        return show_comment_view(context, request)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider
        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def test_it(self):
        self._registerLayoutProvider()

        context = testing.DummyModel(title='the title')

        request = testing.DummyRequest()
        def dummy_byline_info(context, request):
            return context
        from karl.content.views.interfaces import IBylineInfo
        from karl.content.interfaces import IBlogEntry
        alsoProvides(context, IBlogEntry)
        testing.registerAdapter(dummy_byline_info, (Interface, Interface),
                                IBylineInfo)
        renderer = testing.registerDummyRenderer('templates/show_comment.pt')
        response =self._callFUT(context, request)
        self.assertEqual(renderer.byline_info, context)


class RedirectCommentsTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.commenting import redirect_comments_view
        return redirect_comments_view(context, request)

    def test_redirect(self):
        context = testing.DummyModel()
        context.title = 'The comment'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

class DummyCommentsFolder(testing.DummyModel):

    @property
    def next_id(self):
        return u'99'


class DummyBlogEntry(testing.DummyModel):
    implements(IBlogEntry)

    title = "Dummy Blog Entry"
    __name__ = "DummyName"
    docid = 0

    def __init__(self, *arg, **kw):
        testing.DummyModel.__init__(self, *arg, **kw)
        self.comments = self["comments"] = DummyCommentsFolder()
        self["attachments"] = testing.DummyModel()
        self.arg = arg
        self.kw = kw

class DummyComment(testing.DummyModel):
    implements(IComment)

    text = "This is a test."
    title = "This is a comment."
    creator = u'a'

    def __init__(self, title, text, description, creator):
        testing.DummyModel.__init__(self,
            title=title,
            text=text,
            description=description,
            )

    def get_attachments(self):
        return self
