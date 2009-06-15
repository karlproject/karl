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

_HTGROUPS = """
one: a b c
two: c d e
three:
"""

class TestHTGroupsPlugin(unittest.TestCase):
    def _makeOne(self, filename):
        from karl.models.whoplugins import HTGroupsMetadataProviderPlugin
        return HTGroupsMetadataProviderPlugin(filename)

    def test_add_metadata(self):
        import tempfile
        t = tempfile.NamedTemporaryFile()
        t.write(_HTGROUPS)
        t.flush()
        filename = t.name
        plugin = self._makeOne(filename)
        identity = {'repoze.who.userid':'c'}
        environ = {}
        plugin.add_metadata(environ, identity)
        self.assertEqual(identity['groups'], ['group.one', 'group.two'])

        identity = {'repoze.who.userid':'a'}
        plugin.add_metadata(environ, identity)
        self.assertEqual(identity['groups'], ['group.one'])


    
    
    
    
