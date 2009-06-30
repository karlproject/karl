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
        from karl.scripts.mailin import MailinRunner
        return MailinRunner

    def _makeOne(self, args=(), maildir_root=None):
        if maildir_root is None:
            maildir_root = self.maildir_root
        argv = ['testing'] + list(args) + [maildir_root]
        mailin = self._getTargetClass()(argv, testing=True)
        return mailin

    def test___init___defaults(self):
        import os
        mailin = self._makeOne()
        self.assertEqual(mailin.name, 'testing')
        self.assertEqual(mailin.dry_run, False)
        self.assertEqual(mailin.verbosity, 1)
        self.assertEqual(mailin.pq_file,
                         os.path.join(self.maildir_root, 'pending.db'))
        self.assertEqual(mailin.maildir_root, self.maildir_root)
        self.assertEqual(mailin.config, None)
        self.assertEqual(mailin.log_file, 'log/mailin.log')
        self.assertEqual(mailin.default_tool, None)
        self.assertEqual(mailin.exited, None)
        self.assertEqual(mailin.printed, [])

    def test___init___config(self):
        mailin = self._makeOne(['-C', '/my/karl.ini'])
        self.assertEqual(mailin.config, '/my/karl.ini')
        mailin = self._makeOne(['--config', '/my/karl2.ini'])
        self.assertEqual(mailin.config, '/my/karl2.ini')

    def test___init___quiet(self):
        mailin = self._makeOne(['-q'])
        self.assertEqual(mailin.verbosity, 0)
        mailin = self._makeOne(['--quiet'])
        self.assertEqual(mailin.verbosity, 0)

    def test___init___verbose(self):
        mailin = self._makeOne(['-v'])
        self.assertEqual(mailin.verbosity, 2)
        mailin = self._makeOne(['--verbose'])
        self.assertEqual(mailin.verbosity, 2)

    def test___init___very_verbose(self):
        mailin = self._makeOne(['-vvv'])
        self.assertEqual(mailin.verbosity, 4)
        mailin = self._makeOne(['--verbose', '--verbose'])
        self.assertEqual(mailin.verbosity, 3)

    def test___init___dry_run(self):
        mailin = self._makeOne(['-n'])
        self.assertEqual(mailin.dry_run, True)
        mailin = self._makeOne(['--dry-run'])
        self.assertEqual(mailin.dry_run, True)

    def test___init___pending_queue(self):
        mailin = self._makeOne(['-p', 'foo'])
        self.assertEqual(mailin.pq_file, 'foo')
        mailin = self._makeOne(['--pending-queue=foo'])
        self.assertEqual(mailin.pq_file, 'foo')

    def test___init___log_file(self):
        mailin = self._makeOne(['-l', 'foo'])
        self.assertEqual(mailin.log_file, 'foo')
        mailin = self._makeOne(['--log-file=foo'])
        self.assertEqual(mailin.log_file, 'foo')

    def test___init___default_tool(self):
        mailin = self._makeOne(['-t', 'foo'])
        self.assertEqual(mailin.default_tool, 'foo')
        mailin = self._makeOne(['--default-tool=foo'])
        self.assertEqual(mailin.default_tool, 'foo')

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
        mailin.root = DummyModel()
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
        mailin.root = DummyModel()
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
