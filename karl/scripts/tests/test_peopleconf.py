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


class Test_load_peopleconf(unittest.TestCase):

    _tempdir = None

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()
        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _getTempDir(self):
        if self._tempdir is None:
            import tempfile
            self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    @property
    def xml_filename(self):
        import os
        return os.path.join(self._getTempDir(), 'peopleconf.xml')

    @property
    def config_filename(self):
        import os
        return os.path.join(self._getTempDir(), 'karl.ini')

    def _makeXML(self, xml):
        f = open(self.xml_filename, 'w')
        f.write(xml)
        f.flush()
        f.close()

    def _callFUT(self, root=None, filename=None, force_reindex=False):
        from karl.scripts.peopleconf import load

        args = []
        def _func(root, tree, force_reindex):
            args.append((root, tree, force_reindex))

        if root is None:
            from pyramid.testing import DummyModel
            root = DummyModel()

        if filename is None:
            filename = self.xml_filename

        argv = [None]
        if force_reindex:
            argv.append('--force-reindex')
        argv.append(filename)
        load(argv, peopleconf=_func, root=root)

        self.assertEqual(len(args), 1)
        return args[0]

    def test_force_reindex_w_existing(self):
        from pyramid.testing import DummyModel
        from karl.models.peopledirectory import PeopleDirectory
        self._makeXML(_EMPTY_XML_TEMPLATE)
        root = DummyModel()
        original_peopledir = root['people'] = PeopleDirectory()
        pdir, tree, force_reindex = self._callFUT(root, force_reindex=True)
        self.failUnless(pdir is original_peopledir)
        self.assertEqual(force_reindex, True)

    def test_force_reindex_no_existing(self):
        from pyramid.testing import DummyModel
        from karl.models.peopledirectory import PeopleDirectory
        self._makeXML(_EMPTY_XML_TEMPLATE)
        root = DummyModel()
        pdir, tree, force_reindex = self._callFUT(root, force_reindex=True)
        self.failUnless(isinstance(pdir, PeopleDirectory))
        self.assertEqual(force_reindex, True)

_EMPTY_XML_TEMPLATE = """\
<?xml version="1.0"?>
<peopledirectory/>
"""
