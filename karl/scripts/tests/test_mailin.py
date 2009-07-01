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

class MailinScriptTests(unittest.TestCase):

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

    def _callFUT(self, args=[]):
        from karl.scripts.mailin import main
        from repoze.bfg import testing
        argv = ['mailin', self.maildir_root] + args
        res = []
        def mailin_factory(root, maildir_root, options):
            res[:] = [(root, maildir_root, options)]
            return lambda: None
        main(argv, factory=mailin_factory, root=testing.DummyModel())
        return res[0]

    def test_defaults(self):
        import os
        root, maildir_root, options = self._callFUT()
        self.assert_(root is not None)
        self.assertEqual(options.dry_run, False)
        self.assertEqual(options.verbosity, 1)
        self.assertEqual(options.pq_file,
                         os.path.join(self.maildir_root, 'pending.db'))
        self.assertEqual(maildir_root, self.maildir_root)
        self.assertEqual(options.config, None)
        self.assertEqual(options.log_file, 'log/mailin.log')
        self.assertEqual(options.default_tool, None)

    def test_config(self):
        root, maildir_root, options = self._callFUT(['-C', '/my/karl.ini'])
        self.assertEqual(options.config, '/my/karl.ini')
        root, maildir_root, options = self._callFUT(
            ['--config', '/my/karl2.ini'])
        self.assertEqual(options.config, '/my/karl2.ini')

    def test_quiet(self):
        root, maildir_root, options = self._callFUT(['-q'])
        self.assertEqual(options.verbosity, 0)
        root, maildir_root, options = self._callFUT(['--quiet'])
        self.assertEqual(options.verbosity, 0)

    def test_verbose(self):
        root, maildir_root, options = self._callFUT(['-v'])
        self.assertEqual(options.verbosity, 2)
        root, maildir_root, options = self._callFUT(['--verbose'])
        self.assertEqual(options.verbosity, 2)

    def test_very_verbose(self):
        root, maildir_root, options = self._callFUT(['-vvv'])
        self.assertEqual(options.verbosity, 4)
        root, maildir_root, options = self._callFUT(['--verbose', '--verbose'])
        self.assertEqual(options.verbosity, 3)

    def test_dry_run(self):
        root, maildir_root, options = self._callFUT(['-n'])
        self.assertEqual(options.dry_run, True)
        root, maildir_root, options = self._callFUT(['--dry-run'])
        self.assertEqual(options.dry_run, True)

    def test_pending_queue(self):
        root, maildir_root, options = self._callFUT(['-p', 'foo'])
        self.assertEqual(options.pq_file, 'foo')
        root, maildir_root, options = self._callFUT(['--pending-queue=foo'])
        self.assertEqual(options.pq_file, 'foo')

    def test_log_file(self):
        root, maildir_root, options = self._callFUT(['-l', 'foo'])
        self.assertEqual(options.log_file, 'foo')
        root, maildir_root, options = self._callFUT(['--log-file=foo'])
        self.assertEqual(options.log_file, 'foo')

    def test_default_tool(self):
        root, maildir_root, options = self._callFUT(['-t', 'foo'])
        self.assertEqual(options.default_tool, 'foo')
        root, maildir_root, options = self._callFUT(['--default-tool=foo'])
        self.assertEqual(options.default_tool, 'foo')

