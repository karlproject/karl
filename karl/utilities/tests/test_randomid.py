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

class TestFriendlyRandomId(unittest.TestCase):
    def _callFUT(self, len):
        from karl.utilities.randomid import friendly_random_id
        return friendly_random_id(len)

    def test_it(self):
        s = self._callFUT(4)
        self.assertEqual(len(s), 4)
        s = self._callFUT(6)
        self.assertEqual(len(s), 6)
        

class TestUnfriendlyRandomId(unittest.TestCase):
    def _callFUT(self, len):
        from karl.utilities.randomid import unfriendly_random_id
        return unfriendly_random_id(len)

    def test_it(self):
        s = self._callFUT(4)
        self.assertEqual(len(s), 4)
        s = self._callFUT(6)
        self.assertEqual(len(s), 6)
    
