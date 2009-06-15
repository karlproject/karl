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

class TestMimeInfo(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, mimetype):
        from karl.utilities.mime import mime_info
        return mime_info(mimetype)

    def test_obtained_from_lookup(self):
        result = self._callFUT('application/pdf')
        self.assertEqual(result['small_icon_name'], 'pdf_small.gif')
        self.assertEqual(result['large_icon_name'], 'pdf_big.gif')
        self.assertEqual(result['title'], 'PDF')

    def test_obtained_from_mimetype_name(self):
        result = self._callFUT('non/existent')
        self.assertEqual(result['small_icon_name'], 'mime.png')
        self.assertEqual(result['large_icon_name'], 'mime.png')
        self.assertEqual(result['title'], 'Existent')
        
    def test_bad_mimetype_name(self):
        result = self._callFUT('nonexistent')
        self.assertEqual(result['small_icon_name'], 'mime.png')
        self.assertEqual(result['large_icon_name'], 'mime.png')
        self.assertEqual(result['title'], 'Generic File')
        
    def test_images_exist(self):
        from karl.utilities.mime import _LOOKUP as types
        from karl import views
        import os
        
        path = os.path.join(views.__path__[0], 'static', 'images')
        for t in types.values():
            small_icon = os.path.join(path, t['small_icon_name'])
            self.failUnless(os.path.isfile(small_icon), small_icon)
            
            large_icon = os.path.join(path, t['large_icon_name'])
            self.failUnless(os.path.isfile(large_icon), large_icon)
            
        
