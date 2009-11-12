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

class UpdateFeedsScriptTests(unittest.TestCase):

    def _callFUT(self, args=[]):
        from karl.scripts.update_feeds import main
        from repoze.bfg import testing
        argv = ['update_feeds'] + args
        res = []
        tx = DummyTransaction()
        def update_func(root, config, force):
            res[:] = [(root, config, force)]
        main(argv, root=testing.DummyModel(), update_func=update_func)
        return res[0]

    def test_defaults(self):
        root, config, force = self._callFUT()
        self.assert_(root is not None)
        self.assert_('etc' in config)
        self.assertEqual(force, False)

    def test_config(self):
        root, config, force = self._callFUT(['-C', '/my/karl.ini'])
        self.assertEqual(config, '/my/karl.ini')
        root, config, force = self._callFUT(
            ['--config', '/my/karl2.ini'])
        self.assertEqual(config, '/my/karl2.ini')

    def test_force(self):
        root, config, force = self._callFUT(['-f'])
        self.assertEqual(force, True)
        root, config, force = self._callFUT(['--force'])
        self.assertEqual(force, True)

class DummyTransaction(object):
    def commit(self):
        pass

    def abort(self):
        pass
