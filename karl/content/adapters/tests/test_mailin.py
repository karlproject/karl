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

class MailinBase:
    """ Derived testcase classes must supply '_getTargetClass'.
    """
    def _cleanUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def _registerFactory(self, iface, factory=None):
        from repoze.lemonade.testing import registerContentFactory
        if factory is None:
            from pyramid.testing import DummyModel as factory
        registerContentFactory(factory, iface)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security')
        return workflow

    def _registerContextURL(self):
        # Technically this turns it into a kind of integration test, since
        # we end up also testing the OfflineContextURL, but in this case
        # I think testing this minor integration point is not a performance
        # hit and is somewhat useful.
        from karl.adapters.url import OfflineContextURL
        from pyramid.interfaces import IContextURL
        from pyramid.testing import registerAdapter
        from zope.interface import Interface
        registerAdapter(OfflineContextURL, (Interface, Interface), IContextURL)

    def _registerAlerts(self):
        from karl.utilities.interfaces import IAlerts
        from pyramid.testing import registerUtility
        alerts = DummyAlerts()
        registerUtility(alerts, IAlerts)
        return alerts

    def _registerSettings(self):
        from karl.testing import registerSettings
        registerSettings()

    def test_class_conforms_to_IMailinHandler(self):
        from zope.interface.verify import verifyClass
        from karl.adapters.interfaces import IMailinHandler
        verifyClass(IMailinHandler, self._getTargetClass())

    def test_instance_conforms_to_IMailinHandler(self):
        from zope.interface.verify import verifyObject
        from pyramid.testing import DummyModel
        from karl.adapters.interfaces import IMailinHandler
        verifyObject(IMailinHandler, self._makeOne(DummyModel()))

class BlogEntryMailinHandlerTests(unittest.TestCase, MailinBase):

    def setUp(self):
        self._cleanUp()

    def tearDown(self):
        self._cleanUp()

    def _getTargetClass(self):
        from karl.content.adapters.mailin import BlogEntryMailinHandler
        return BlogEntryMailinHandler

    def test_handle_no_email_attachments(self):
        from pyramid.testing import DummyModel
        from karl.models.interfaces import IComment
        import datetime
        self._registerFactory(IComment, DummyModel)
        self._registerContextURL()
        self._registerSettings()
        alerts = self._registerAlerts()
        workflow = self._registerSecurityWorkflow()
        context = _makeBlogEntryClass()('foo', 'foo', 'foo', 'foo')
        comments = context['comments'] = DummyModel()
        comments.next_id = '1'
        adapter = self._makeOne(context)
        message = object() # ignored
        info = {'subject': 'SUBJECT', 'author': 'phreddy',
                'date': datetime.datetime(2010, 5, 12, 2, 42)}

        adapter.handle(message, info, 'TEXT', [])

        self.assertEqual(len(comments), 1)
        comment_id, comment = comments.items()[0]
        self.assertEqual(comment_id, '1')
        self.assertEqual(comment.title, 'SUBJECT')
        self.assertEqual(comment.creator, 'phreddy')
        self.assertEqual(comment.text, 'TEXT')
        self.assertEqual(comment.description, 'TEXT')
        self.assertEqual(comment.created,
                         datetime.datetime(2010, 5, 12, 2, 42))
        self.failIf('attachments' in comment)

        self.assertEqual(len(alerts.emissions), 1)
        self.failUnless(workflow.initialized)

    def test_handle_w_email_attachments(self):
        import datetime
        from pyramid.testing import DummyModel
        from karl.models.interfaces import IComment
        from karl.content.interfaces import ICommunityFile
        self._registerFactory(IComment, DummyModel)
        self._registerFactory(ICommunityFile)
        self._registerSettings()
        self._registerContextURL()
        alerts = self._registerAlerts()
        workflow = self._registerSecurityWorkflow()
        context = _makeBlogEntryClass()('foo', 'foo', 'foo', 'foo')
        comments = context['comments'] = DummyModel()
        comments.next_id = '1'
        adapter = self._makeOne(context)
        message = object() # ignored
        info = {'subject': 'SUBJECT', 'author': 'phreddy',
                'date': datetime.datetime(2010, 5, 12, 2, 42)}
        attachments = [('file1.png', 'image/png', 'IMAGE1'),
                       ('file1.png', 'image/png', 'IMAGE2'),
                      ]

        adapter.handle(message, info, 'TEXT', attachments)

        self.assertEqual(len(comments), 1)
        comment_id, comment = comments.items()[0]
        self.assertEqual(comment_id, '1')
        self.assertEqual(comment.title, 'SUBJECT')
        self.assertEqual(comment.creator, 'phreddy')
        self.assertEqual(comment.text, 'TEXT')

        attachments = comment
        self.assertEqual(len(attachments), 2)
        file1 = attachments['file1.png']
        self.assertEqual(file1.title, 'file1.png')
        self.assertEqual(file1.filename, 'file1.png')
        self.assertEqual(file1.mimetype, 'image/png')
        self.assertEqual(file1.stream.read(), 'IMAGE1')
        file2 = attachments['file1-1.png']
        self.assertEqual(file2.title, 'file1.png')
        self.assertEqual(file2.filename, 'file1.png')
        self.assertEqual(file2.mimetype, 'image/png')
        self.assertEqual(file2.stream.read(), 'IMAGE2')

        self.assertEqual(len(alerts.emissions), 1)
        self.failUnless(workflow.initialized)

    def test_handle_w_alert(self):
        import datetime
        from pyramid.testing import DummyModel
        from karl.models.interfaces import IComment
        self._registerFactory(IComment, DummyModel)
        self._registerContextURL()
        self._registerSettings()
        alerts = self._registerAlerts()
        workflow = self._registerSecurityWorkflow()
        context = _makeBlogEntryClass()('foo', 'foo', 'foo', 'foo')
        comments = context['comments'] = DummyModel()
        comments.next_id = '1'
        adapter = self._makeOne(context)
        message = object() # ignored
        info = {'subject': 'SUBJECT', 'author': 'phreddy',
                'date': datetime.datetime(2010, 5, 12, 2, 42)}

        adapter.handle(message, info, 'TEXT', [])

        self.assertEqual(len(comments), 1)
        comment_id, comment = comments.items()[0]
        self.assertEqual(comment_id, '1')
        self.assertEqual(comment.title, 'SUBJECT')
        self.assertEqual(comment.creator, 'phreddy')
        self.assertEqual(comment.text, 'TEXT')
        self.failIf('attachments' in comment)

        self.assertEqual(len(alerts.emissions), 1)
        self.assertEqual(alerts.emissions,
            [(comment, 'http://offline.example.com/app/comments/1')])
        self.failUnless(workflow.initialized)

class BlogMailinHandlerTests(unittest.TestCase, MailinBase):

    _old__NOW = None

    def setUp(self):
        self._cleanUp()

    def tearDown(self):
        self._cleanUp()

        if self._old__NOW is not None:
            self._set_NOW(self._old__NOW)

    def _set_NOW(self, value):
        from karl.content.adapters import mailin
        self._old__NOW = mailin._NOW = value

    def _getTargetClass(self):
        from karl.content.adapters.mailin import BlogMailinHandler
        return BlogMailinHandler

    def test_handle_no_email_attachments(self):
        import datetime
        from pyramid.testing import DummyModel
        from karl.content.interfaces import IBlogEntry
        self._set_NOW(datetime.datetime(2009, 01, 28, 10, 00, 00))
        self._registerFactory(IBlogEntry, _makeBlogEntryClass())
        self._registerContextURL()
        self._registerSettings()
        alerts = self._registerAlerts()
        workflow = self._registerSecurityWorkflow()
        context = DummyModel()
        adapter = self._makeOne(context)
        message = object() # ignored
        info = {'subject': 'SUBJECT', 'author': 'phreddy',
                'date': datetime.datetime(2010, 5, 12, 2, 42)}

        adapter.handle(message, info, 'TEXT', [])

        self.assertEqual(len(context), 1)
        entry_id, entry = context.items()[0]
        self.assertEqual(entry_id, 'subject')
        self.assertEqual(entry.title, 'SUBJECT')
        self.assertEqual(entry.creator, 'phreddy')
        self.assertEqual(entry.text, 'TEXT')
        self.assertEqual(entry.description, 'TEXT')
        self.assertEqual(entry.created, datetime.datetime(2010, 5, 12, 2, 42))
        self.failIf(len(entry['attachments']))

        self.assertEqual(len(alerts.emissions), 1)
        self.assertEqual(alerts.emissions,
            [(entry, 'http://offline.example.com/app/subject')])
        self.failUnless(workflow.initialized)

    def test_handle_with_email_attachments_no_entry_attachments(self):
        import datetime
        from pyramid.testing import DummyModel
        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import ICommunityFile
        self._set_NOW(datetime.datetime(2009, 01, 28, 10, 00, 00))
        self._registerFactory(IBlogEntry, _makeBlogEntryClass(False))
        self._registerFactory(ICommunityFile)
        self._registerContextURL()
        self._registerSettings()
        alerts = self._registerAlerts()
        workflow = self._registerSecurityWorkflow()
        context = DummyModel()
        adapter = self._makeOne(context)
        message = object() # ignored
        info = {'subject': 'SUBJECT', 'author': 'phreddy',
                'date': datetime.datetime(2010, 5, 12, 2, 42)}
        attachments = [('file1.bin', 'application/octet-stream', 'DATA'),
                       ('file2.png', 'image/png', 'IMAGE'),
                      ]

        adapter.handle(message, info, 'TEXT', attachments)

        self.assertEqual(len(context), 1)
        entry_id, entry = context.items()[0]
        self.assertEqual(entry_id, 'subject')
        self.assertEqual(entry.title, 'SUBJECT')
        self.assertEqual(entry.creator, 'phreddy')
        self.assertEqual(entry.text, 'TEXT')

        attachments = entry['attachments']
        self.assertEqual(len(attachments), 2)
        file1 = attachments['file1.bin']
        self.assertEqual(file1.title, 'file1.bin')
        self.assertEqual(file1.filename, 'file1.bin')
        self.assertEqual(file1.mimetype, 'application/octet-stream')
        self.assertEqual(file1.stream.read(), 'DATA')
        file2 = attachments['file2.png']
        self.assertEqual(file2.title, 'file2.png')
        self.assertEqual(file2.filename, 'file2.png')
        self.assertEqual(file2.mimetype, 'image/png')
        self.assertEqual(file2.stream.read(), 'IMAGE')

        self.assertEqual(len(alerts.emissions), 1)
        self.assertEqual(alerts.emissions,
            [(entry, 'http://offline.example.com/app/subject')])
        self.failUnless(workflow.initialized)

    def test_handle_with_email_attachments_w_entry_attachments(self):
        import datetime
        from pyramid.testing import DummyModel
        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import ICommunityFile
        self._set_NOW(datetime.datetime(2009, 01, 28, 10, 00, 00))
        self._registerFactory(IBlogEntry, _makeBlogEntryClass())
        self._registerFactory(ICommunityFile)
        self._registerContextURL()
        self._registerSettings()
        alerts = self._registerAlerts()
        workflow = self._registerSecurityWorkflow()
        context = DummyModel()
        adapter = self._makeOne(context)
        message = object() # ignored
        info = {'subject': 'SUBJECT', 'author': 'phreddy',
                'date': datetime.datetime(2010, 5, 12, 2, 42)}
        attachments = [('file1.bin', 'application/octet-stream', 'DATA'),
                       ('file2.png', 'image/png', 'IMAGE'),
                      ]

        adapter.handle(message, info, 'TEXT', attachments)

        self.assertEqual(len(context), 1)
        entry_id, entry = context.items()[0]
        self.assertEqual(entry_id, 'subject')
        self.assertEqual(entry.title, 'SUBJECT')
        self.assertEqual(entry.creator, 'phreddy')
        self.assertEqual(entry.text, 'TEXT')

        attachments = entry['attachments']
        self.assertEqual(len(attachments), 2)
        file1 = attachments['file1.bin']
        self.assertEqual(file1.title, 'file1.bin')
        self.assertEqual(file1.filename, 'file1.bin')
        self.assertEqual(file1.mimetype, 'application/octet-stream')
        self.assertEqual(file1.stream.read(), 'DATA')
        file2 = attachments['file2.png']
        self.assertEqual(file2.title, 'file2.png')
        self.assertEqual(file2.filename, 'file2.png')
        self.assertEqual(file2.mimetype, 'image/png')
        self.assertEqual(file2.stream.read(), 'IMAGE')

        self.assertEqual(len(alerts.emissions), 1)
        self.assertEqual(alerts.emissions,
            [(entry, 'http://offline.example.com/app/subject')])
        self.failUnless(workflow.initialized)


def _makeBlogEntryClass(init_attachments=True):
    from zope.interface import implements
    from pyramid.testing import DummyModel
    from karl.models.interfaces import ICommunityContent

    class DummyBlogEntry(DummyModel):
        implements(ICommunityContent)

        # Impose same signature in constructor as real model
        def __init__(self, title, text, description, creator):
            DummyModel.__init__(self,
                                title=title,
                                text=text,
                                description=description,
                                creator=creator)
            if init_attachments:
                self['attachments'] = DummyModel()
    return DummyBlogEntry

class DummyAlerts(object):
    def __init__(self):
        self.emissions = []

    def emit(self, context, request):
        from pyramid.url import model_url
        url = model_url(context, request)
        self.emissions.append((context, url))

class DummySettings:
    envelope_from_addr = 'karl@example.org'
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
