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

class AttachmentsFolderTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.attachments import AttachmentsFolder
        return AttachmentsFolder

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IAttachmentsFolder(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IAttachmentsFolder
        verifyClass(IAttachmentsFolder, self._getTargetClass())

    def test_instance_conforms_to_IAttachmentsFolder(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IAttachmentsFolder
        verifyObject(IAttachmentsFolder, self._makeOne())

    def test_next_id_nomembers(self):
        attachments = self._makeOne()
        self.assertEqual(attachments.next_id, '1')
        
    def test_next_id_wthmembers(self):
        attachments = self._makeOne()
        attachments['1'] = testing.DummyModel()
        self.assertEqual(attachments.next_id, '2')
