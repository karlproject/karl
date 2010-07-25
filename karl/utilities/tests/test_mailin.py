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

class MailinRunnerTests(unittest.TestCase):

    def setUp(self):
        self.maildir_root = self._makeMaildir()
        testing.cleanUp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.maildir_root)
        testing.cleanUp()

    def _makeMaildir(self):
        import os
        import tempfile
        root = tempfile.mkdtemp()
        os.mkdir(os.path.join(root, 'Maildir'))
        os.mkdir(os.path.join(root, 'Maildir', 'new'))
        os.mkdir(os.path.join(root, 'Maildir', 'cur'))
        os.mkdir(os.path.join(root, 'Maildir', 'tmp'))
        return root

    def _getTargetClass(self):
        from karl.utilities.mailin import MailinRunner
        return MailinRunner

    def _makeOne(self, root=None, maildir_root=None, options=None):
        if root is None:
            from repoze.bfg import testing
            root = testing.DummyModel()
        if maildir_root is None:
            maildir_root = self.maildir_root
        if options is None:
            options = DummyOptions
        mailin = self._getTargetClass()(
            root, maildir_root, options, testing=True)
        return mailin

    def test_exit(self):
        mailin = self._makeOne()
        mailin.exit(23)
        self.assertEqual(mailin.exited, 23)

    def test_print_no_message(self):
        mailin = self._makeOne()
        mailin.print_()
        self.assertEqual(mailin.printed, [''])

    def test_print_w_message(self):
        mailin = self._makeOne()
        mailin.print_('foobar')
        self.assertEqual(mailin.printed, ['foobar'])

    def test_section_defaults(self):
        mailin = self._makeOne()
        mailin.section('foobar')
        divider = '-' * 65
        self.assertEqual(mailin.printed, [divider, 'foobar', divider])

    def test_section_w_sep(self):
        mailin = self._makeOne()
        mailin.section('foobar', '#')
        divider = '#' * 65
        self.assertEqual(mailin.printed, [divider, 'foobar', divider])

    def test_section_w_verbosity(self):
        mailin = self._makeOne()
        mailin.section('foobar', verbosity=2)
        self.assertEqual(mailin.printed, [])

    def test_processMessage_reply_no_attachments(self):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.testing import registerModels
        from karl.adapters.interfaces import IMailinHandler
        INFO = {'community': 'testing',
                'tool': 'random',
                'in_reply_to': '7FFFFFFF', # token for docid 0
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        handler = DummyHandler()
        def _handlerFactory(context):
            handler.context = context
            return handler
        registerAdapter(_handlerFactory, DummyModel, IMailinHandler)
        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        comments = entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        registerModels({'/communities/testing/random/entry': entry})
        message = DummyMessage()
        text = 'This entry stinks!'
        attachments = ()

        mailin.processMessage(message, INFO, text, attachments)

        self.assertEqual(handler.context, entry)
        self.assertEqual(handler.handle_args,
                         (message, INFO, text, attachments))

    def test_processMessage_reply_w_attachment(self):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.testing import registerModels
        from karl.adapters.interfaces import IMailinHandler
        INFO = {'community': 'testing',
                'tool': 'random',
                'in_reply_to': '7FFFFFFF', # token for docid 0
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        handler = DummyHandler()
        def _handlerFactory(context):
            handler.context = context
            return handler
        registerAdapter(_handlerFactory, DummyModel, IMailinHandler)
        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        comments = entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        registerModels({'/communities/testing/random/entry': entry})
        message = DummyMessage()
        text = 'This entry stinks!'
        attachments = [('foo.txt', 'text/plain', 'My attachment')]

        mailin.processMessage(message, INFO, text, attachments)

        self.assertEqual(handler.context, entry)
        self.assertEqual(handler.handle_args,
                         (message, INFO, text, attachments))

class MailinRunner2Tests(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from karl.utilities.mailin import MailinRunner2
        return MailinRunner2

    def _makeOne(self, root=None):
        if root is None:
            from repoze.bfg import testing
            root = testing.DummyModel()
        mailin = self._getTargetClass()(
            root, 'zodb://test', '/postoffice', 'queue',
            dummy_queue_factory_factory(self.queue),
        )
        return mailin

    def _set_up_queue(self, messages):
        self.queue = DummyQueue(messages)

        from repoze.bfg.testing import DummyModel
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.adapters.interfaces import IMailinDispatcher
        from karl.adapters.interfaces import IMailinHandler
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.testing import registerUtility

        self.handlers = []
        def handler_factory(context):
            handler = DummyHandler(context)
            self.handlers.append(handler)
            return handler
        registerAdapter(handler_factory, DummyModel, IMailinHandler)
        registerAdapter(DummyDispatcher, DummyModel, IMailinDispatcher)

        self.mailer = DummyMailer()
        registerUtility(self.mailer, IMailDelivery)

    def test_one_message_reply_no_attachments(self):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerModels
        info = {'community': 'testing',
                'tool': 'random',
                'in_reply_to': '7FFFFFFF', # token for docid 0
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        comments = entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        registerModels({'/communities/testing/random/entry': entry})

        mailin()
        mailin.close()

        self.assertEqual(len(self.handlers), 1)
        handler = self.handlers[0]
        self.assertEqual(handler.context, entry)
        self.assertEqual(handler.handle_args,
                         (message, info, text, attachments))
        self.assertEqual(len(self.mailer), 0)

    def test_process_message_reply_w_attachment(self):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerModels
        info = {'community': 'testing',
                'tool': 'random',
                'in_reply_to': '7FFFFFFF', # token for docid 0
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        comments = entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        registerModels({'/communities/testing/random/entry': entry})

        mailin()

        self.assertEqual(len(self.handlers), 1)
        handler = self.handlers[0]
        self.assertEqual(handler.context, entry)
        self.assertEqual(handler.handle_args,
                         (message, info, text, attachments))
        self.assertEqual(len(self.mailer), 0)

    def test_bounce_message(self):
        info = {'community': 'testing',
                'tool': 'random',
                'in_reply_to': '7FFFFFFF', # token for docid 0
                'author': 'phreddy',
                'subject': 'Feedback',
                'error': 'Not witty enough',
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        self._makeOne()()
        self.assertEqual(self.queue.bounced, [
            (message, None, 'Not witty enough', None)])
        self.assertEqual(len(self.mailer), 1)

    def test_bounce_message_throttled(self):
        testing.registerDummyRenderer(
            'karl.utilities:templates/bounce_email_throttled.pt')
        message = DummyMessage(None, 'Message body.', ())
        message['X-Postoffice-Rejected'] = 'Throttled'
        message['From'] = 'Clarence'
        self._set_up_queue([message,])

        mailin = self._makeOne()
        mailin()

        self.assertEqual(len(self.queue.bounced), 1)
        bounced = self.queue.bounced[0]
        self.assertEqual(bounced[0], message)
        self.assertEqual(bounced[1], None)
        self.assertEqual(bounced[2], None)
        self.assertEqual(bounced[3]['To'], 'Clarence')
        self.assertEqual(len(self.mailer), 1)

    def test_quarantine_message(self):
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerModels
        info = {'community': 'testing',
                'tool': 'random',
                'in_reply_to': '7FFFFFFF', # token for docid 0
                'author': 'phreddy',
                'subject': 'Feedback',
                'exception': 'Not witty enough',
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        comments = entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        registerModels({'/communities/testing/random/entry': entry})

        mailin()
        q_message, error = self.queue.quarantined[0]
        self.assertEqual(q_message, message)
        self.failUnless('Not witty enough' in error)
        self.assertEqual(len(self.mailer), 1)

class DummyOptions:
    dry_run = False
    verbosity = 1
    pq_file = None
    log_file = None
    default_tool = None
    text_scrubber = None

class DummyHandler:
    handle_args = None

    def __init__(self, context=None):
        self.context = context

    def handle(self, message, info, text, attachments):
        self.handle_args = (message, info, text, attachments)
        if 'exception' in info:
            raise Exception(info['exception'])

class DummyDocumentMap:
    def __init__(self):
        self._map = {}

    def address_for_docid(self, docid):
        return self._map[docid]

class DummyCatalog:
    def __init__(self):
        self.document_map = DummyDocumentMap()

class DummyMessage(dict):
    def __init__(self, info=None, text=None, attachments=None):
        self.info = info
        self.text = text
        self.attachments = attachments
        self['Message-Id'] = '123456789'

def dummy_queue_factory_factory(queue):
    def factory(uri, name, path):
        assert uri == 'zodb://test', uri
        assert name == 'queue', name
        assert path == '/postoffice', path
        return queue, lambda: None
    return factory

class DummyQueue(list):
    def __init__(self, messages):
        super(DummyQueue, self).__init__(messages)
        self.bounced = []
        self.quarantined = []

    def pop_next(self):
        return self.pop(0)

    def quarantine(self, message, error, send, message_from):
        self.quarantined.append((message, error))
        send(message_from, ['foo@example.com'], "You're in quarantine!")

    def bounce(self, message, send, from_addr, error=None,
               bounce_message=None):
        self.bounced.append((message, from_addr, error, bounce_message))
        send(from_addr, ['foo@example.com'], message)


class DummyDispatcher(object):
    def __init__(self, context):
        self.context = context

    def crackHeaders(self, message):
        return message.info

    def crackPayload(self, message):
        return message.text, message.attachments

class DummyMailer(list):
    def send(self, from_addr, to_addrs, message):
        self.append((from_addr, to_addrs, message))

test_message = """A message for *you*.

You are nice.
--- Reply ABOVE THIS LINE to post a comment ---
A quote of some sort.
"""

test_message_gmail = """A message for *you*.

You are nice.

On Tue, Mar 24, 2009 at 5:56 PM, Chris chris@example.org wrote:

> --- Reply ABOVE THIS LINE to post a comment ---
> A quote of some sort.
"""

test_message_outlook = """A message for *you*.

You are nice.

________________________________

From: KARL [mailto:staff-8-test@carlos.agendaless.com]
Sent: Wednesday, March 25, 2009 10:12 AM
To: Test User
Subject: [Staff 8 Test] Email Alert Test

--- Reply ABOVE THIS LINE to post a comment ---

A quote of some sort.
"""

test_message_outlook_express = """A message for *you*.

You are nice.

  ----- Original Message -----
  From: KARL
  To: Test User
  Sent: Tuesday, March 24, 2009 5:00 PM
  Subject: [Staff 8 Test] Email Alert Test


  A quote of some sort.
  """

test_message_thunderbird = """A message for *you*.

You are nice.

KARL wrote:
> --- Reply ABOVE THIS LINE to post a comment ---
> A quote of some sort.
"""

class TestMailinTextScrubber(unittest.TestCase):
    def test_bad_mimetype(self):
        from karl.utilities.mailin import text_scrubber
        self.assertRaises(Exception, text_scrubber, "TEXT", "text/html")

    def test_no_mimetype(self, text=test_message):
        from karl.utilities.mailin import text_scrubber
        from karl.utilities.mailin import REPLY_SEPARATOR
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(text))

    def test_good_mimetype(self):
        from karl.utilities.mailin import text_scrubber
        from karl.utilities.mailin import REPLY_SEPARATOR
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(test_message,
                                                 mimetype="text/plain"))

    def test_gmail(self):
        self.test_no_mimetype(test_message_gmail)

    def test_outlook(self):
        self.test_no_mimetype(test_message_outlook)

    def test_outlook_express(self):
        self.test_no_mimetype(test_message_outlook_express)

    def test_thunderbird(self):
        self.test_no_mimetype(test_message_thunderbird)

class DummySend(object):
    def __init__(self):
        self.calls = []

    def __call__(self, fromaddr, toaddrs, message):
        self.calls.append(dict(
            fromaddr=fromaddr,
            toaddrs=toaddrs,
            message=message,
        ))

class DummySettings:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
