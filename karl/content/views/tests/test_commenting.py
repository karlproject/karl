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

from datetime import datetime
import unittest

from zope.interface import implements
from zope.interface import Interface
from zope.interface import alsoProvides
from pyramid.testing import cleanUp

from pyramid import testing

from karl.content.interfaces import IBlogEntry
from karl.models.interfaces import IComment

from karl.testing import DummyFile
from karl.testing import DummySessions
from karl.testing import registerLayoutProvider

class AddCommentFormControllerTests(unittest.TestCase):
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
        from pyramid.interfaces import IRequest
        testing.registerAdapter(BlogCommentAlert,
                                (IComment, IProfile, IRequest),
                                IAlert)

        # Register IShowSendAlert adapter
        self.show_sendalert = True
        from karl.content.views.interfaces import IShowSendalert
        class DummyShowSendalert(object):
            def __init__(myself, context, request):
                myself.show_sendalert = self.show_sendalert

        testing.registerAdapter(DummyShowSendalert, (Interface, Interface),
                                IShowSendalert)

        # Create dummy site skel
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        community = DummyCommunity()
        site = community.__parent__.__parent__
        site.sessions = DummySessions()
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

        # Create dummy request
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.commenting import AddCommentFormController
        return AddCommentFormController(context, request)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def test_form_defaults(self):
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        self.failUnless('sendalert' in defaults and defaults['sendalert'])

    def test_form_defaults_wo_sendalert(self):
        self.show_sendalert = False
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults, {})

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('add_comment' in fields)
        self.failUnless('attachments' in fields)
        self.failUnless('sendalert' in fields)

    def test_form_fields_wo_sendalert(self):
        self.show_sendalert = False
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('add_comment' in fields)
        self.failUnless('attachments' in fields)
        self.failIf('sendalert' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('add_comment' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)
        self.failUnless('sendalert' in widgets)

    def test_form_widgets_wo_sendalert(self):
        self.show_sendalert = False
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('add_comment' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)
        self.failIf('sendalert' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo/#addcomment')

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo/')

    def test_handle_submit(self):
        from karl.models.interfaces import IComment
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyComment, IComment)
        registerContentFactory(DummyFile, ICommunityFile)

        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename=r"C:\My Documents\Ha Ha\test2.txt")
        converted = {'add_comment': u'This is my comment',
                     'attachments': [attachment1, attachment2],
                     'sendalert': False}
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)
        location = ('http://example.com/communities/community/blog/foo/'
                    '?status_message=Comment%20added')
        self.assertEqual(response.location, location)
        self.failUnless(u'99' in context)
        comment = context[u'99']
        self.assertEqual(comment.title, 'Re: Dummy Blog Entry')
        self.assertEqual(comment.text, u'This is my comment')
        self.assertEqual(len(comment), 2)
        self.failUnless('test1.txt' in comment)
        self.failUnless('test2.txt' in comment)

        # try again w/ a workflow, and w/ sendalert == True
        del context[u'99']
        workflow = self._registerSecurityWorkflow()
        blogentry = context.__parent__
        blogentry.creator = 'b'
        blogentry.created = datetime.now()
        blogentry.text = u'Blog entry text'
        converted = {'add_comment': u'This is my OTHER comment',
                     'attachments': [],
                     'sendalert': True,
                     'security_state': 'public'}
        testing.registerDummyRenderer(
            'karl.content.views:templates/email_blog_comment_alert.pt')
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, location)
        self.failUnless(u'99' in context)
        comment = context[u'99']
        self.assertEqual(len(comment), 0)
        mailer = self.mailer
        self.assertEqual(len(mailer), 3)
        recipients = [mail.mto[0] for mail in mailer]
        self.failUnless('a@x.org' in recipients)
        self.failUnless('b@x.org' in recipients)
        self.failUnless('c@x.org' in recipients)
        self.failUnless(comment in workflow.initialized)
        self.assertEqual(len(workflow.transitioned), 1)
        transition = workflow.transitioned[0]
        self.failUnless(transition['content'] is comment)
        self.assertEqual(transition['to_state'], 'public')


class EditCommentFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Create dummy site skel
        from karl.testing import DummyCommunity
        community = DummyCommunity()
        site = community.__parent__.__parent__
        site.sessions = DummySessions()
        blog = testing.DummyModel()
        community["blog"] = blog
        blogentry = blog["foo"] = DummyBlogEntry()
        container = blogentry["comments"]
        comment = container["99"] = DummyComment('Re: foo', 'text',
                                                 'description',
                                                 'creator')
        self.context = comment

        # Create dummy request
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.commenting import EditCommentFormController
        return EditCommentFormController(context, request)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('add_comment' in fields)
        self.failUnless('attachments' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('add_comment' in widgets)
        self.failUnless('attachments' in widgets)
        self.failUnless('attachments.*' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit Re: foo')
        self.failUnless('actions' in response)
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location,
                         'http://example.com/communities/community/blog/foo/')

    def test_handle_submit(self):
        from karl.models.interfaces import IComment
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyComment, IComment)
        registerContentFactory(DummyFile, ICommunityFile)

        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename="test1.txt")
        attachment2 = DummyUpload(filename=r"C:\My Documents\Ha Ha\test2.txt")
        converted = {'add_comment': u'This is my comment',
                     'attachments': [attachment1, attachment2],
                     'sendalert': False}
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)
        location = ('http://example.com/communities/community/blog/foo/'
                    'comments/99/')
        self.assertEqual(response.location, location)
        self.assertEqual(context.title, 'Re: foo')
        self.assertEqual(context.text, u'This is my comment')
        self.assertEqual(len(context), 2)
        self.failUnless('test1.txt' in context)
        self.failUnless('test2.txt' in context)

        # try again w/ a workflow, and delete an attachment
        blogentry = context.__parent__
        workflow = self._registerSecurityWorkflow()
        blogentry.text = u'Blog entry text'
        attachment1 = DummyUpload(None, None)
        attachment1.file = None
        attachment1.metadata = {}
        attachment2 = DummyUpload(None, None)
        attachment2.file = None
        attachment2.metadata = {'default': 'test2.txt',
                                'remove': True,
                                'name': ''}
        converted = {'add_comment': u'This is my OTHER comment',
                     'attachments': [attachment1, attachment2],
                     'security_state': 'public'}
        response = controller.handle_submit(converted)
        self.assertEqual(response.location, location)
        self.assertEqual(len(context), 1)
        self.failUnless('test1.txt' in context)
        self.failIf('test2.txt' in context)
        self.assertEqual(len(workflow.transitioned), 1)
        transition = workflow.transitioned[0]
        self.failUnless(transition['content'] is context)
        self.assertEqual(transition['to_state'], 'public')

class ShowCommentViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.commenting import show_comment_view
        return show_comment_view(context, request)

    def test_it(self):
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

    def test_redirect_with_status_message(self):
        context = testing.DummyModel()
        context.title = 'The comment'
        request = testing.DummyRequest({'status_message':'The status'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=The status')

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
