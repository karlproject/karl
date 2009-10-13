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

class MailinRunnerTests(unittest.TestCase):

    def setUp(self):
        self._makeMaildir()
        cleanUp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.maildir_root)
        cleanUp()

    def _makeMaildir(self, root=None):
        import os
        if root is None:
            import tempfile
            root = tempfile.mkdtemp()
        self.maildir_root = root
        os.mkdir(os.path.join(root, 'Maildir'))
        os.mkdir(os.path.join(root, 'Maildir', 'new'))
        os.mkdir(os.path.join(root, 'Maildir', 'cur'))
        os.mkdir(os.path.join(root, 'Maildir', 'tmp'))

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

class DummyOptions:
    dry_run = False
    verbosity = 1
    pq_file = None
    log_file = None
    default_tool = None
    text_scrubber = None

class DummyHandler:
    contet = handle_args = None
    def handle(self, message, info, text, attachments):
        self.handle_args = (message, info, text, attachments)

class DummyDocumentMap:
    def __init__(self):
        self._map = {}

    def address_for_docid(self, docid):
        return self._map[docid]

class DummyCatalog:
    def __init__(self):
        self.document_map = DummyDocumentMap()

class DummyMessage:
    to = None
    from_ = None
    subject = None
    payload = None
    content_type = None
    filename = None
    getpayload_kw = None
    boundary = None

    def _munge(self, name):
        name = name.lower()
        if name == 'from':
            name = 'from_'
        if '-' in name:
            name = '_'.join(name.split('-'))
        return name

    def get_all(self, name, failobj=None):
        name = self._munge(name)
        return getattr(self, name, failobj)

    def __getitem__(self, key):
        key = self._munge(key)
        value = getattr(self, key, self)
        if value is self:
            raise KeyError(key)
        return value

    def get(self, key, failobj=None):
        try:
            return self[key]
        except KeyError:
            return failobj

    def get_payload(self, i=None, decode=False):
        if self.getpayload_kw is None:
            self.getpayload_kw = []
        self.getpayload_kw.append((i, decode))
        if i is None:
            return self.payload
        return self.payload[i]

    def get_filename(self):
        return self.filename

    def get_content_type(self):
        return self.content_type

    def is_multipart(self):
        return isinstance(self.payload, tuple)

    def get_boundary(self):
        return self.boundary

    def walk(self):
        if self.is_multipart:
            for part in self.payload:
                yield part
        raise StopIteration


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
        from karlsample.utilities.mailin import text_scrubber
        self.assertRaises(Exception, text_scrubber, "TEXT", "text/html")

    def test_no_mimetype(self, text=test_message):
        from karlsample.utilities.mailin import text_scrubber
        from karlsample.utilities.mailin import REPLY_SEPARATOR
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(text))

    def test_good_mimetype(self):
        from karlsample.utilities.mailin import text_scrubber
        from karlsample.utilities.mailin import REPLY_SEPARATOR
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
