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

class PageTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.page import Page
        return Page

    def _makeOne(self, title=u'title', text=u'text', description=u'text',
            creator=u'admin'):
        return self._getTargetClass()(title, text, description, creator)

    def test_class_conforms_to_IPage(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IPage
        verifyClass(IPage, self._getTargetClass())

    def test_instance_conforms_to_IPage(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IPage
        verifyObject(IPage, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.text, u'text')
        self.assertEqual(instance.description, u'text')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')

        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IAttachmentsFolder
        verifyObject(IAttachmentsFolder, instance['attachments'])

    def test_instance_construct_with_none(self):
        instance = self._makeOne(text=u'<div>x</div>')
        self.assertEqual(instance.text, u'<div>x</div>')


class DummyContent:
    pass
