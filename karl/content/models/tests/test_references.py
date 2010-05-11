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


class OrderingTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.references import Ordering
        return Ordering

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IOrdering(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IOrdering
        verifyClass(IOrdering, self._getTargetClass())

    def test_instance_conforms_to_IOrdering(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IOrdering
        verifyObject(IOrdering, self._makeOne())

    def test_empty(self):
        ordering = self._makeOne()
        self.assertEqual(ordering.items(), [])

    def test_sync(self):
        ordering = self._makeOne()

        ordering.sync(['s1', 's2'])
        self.assertEqual(ordering.items(), [u's1', u's2'])

        ordering.sync(['s2'])
        self.assertEqual(ordering.items(), [u's2'])

        ordering.sync(['s3', 's2', 's4'])
        self.assertEqual(ordering.items(), [u's2', u's3', u's4'])

    def test_add_empty(self):
        ordering = self._makeOne()
        ordering.add(u's3')
        self.assertEqual(ordering.items(), [u's3'])

    def test_add_nonempty(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2'])
        ordering.add(u's3')
        self.assertEqual(ordering.items(), [u's1', u's2', u's3'])

    def test_remove(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2', 's3', 's4'])
        ordering.remove(u's3')
        self.assertEqual(ordering.items(), [u's1', u's2', u's4'])

    def test_moveUp_middle(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2', 's3', 's4'])
        ordering.moveUp('s3')
        self.assertEqual(ordering.items(), [u's1', u's3', u's2', u's4'])

    def test_moveUp_top(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2', 's3', 's4'])
        ordering.moveUp('s1')
        self.assertEqual(ordering.items(), [u's2', u's3', u's4', u's1'])

    def test_moveDown_middle(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2', 's3', 's4'])
        ordering.moveDown ('s1')
        self.assertEqual(ordering.items(), [u's2', u's1', u's3', u's4'])

    def test_moveDown_end(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2', 's3', 's4'])
        ordering.moveDown ('s4')
        self.assertEqual(ordering.items(), [u's4', u's1', u's2', u's3'])

    def test_previous_next(self):
        ordering = self._makeOne()
        ordering.sync(['s1', 's2', 's3', 's4'])
        self.assertEqual(ordering.previous_name(u's2'), u's1')
        self.assertEqual(ordering.previous_name(u's1'), None)
        self.assertEqual(ordering.next_name(u's3'), u's4')
        self.assertEqual(ordering.next_name(u's4'), None)


class ReferenceSectionTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.references import ReferenceSection
        return ReferenceSection

    def _makeOne(self, title=u'', description=u'', creator=u'admin'):
        return self._getTargetClass()(title, description, creator)

    def test_class_conforms_to_IReferenceSection(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IReferenceSection
        verifyClass(IReferenceSection, self._getTargetClass())

    def test_instance_conforms_to_IReferenceSection(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IReferenceSection
        verifyObject(IReferenceSection, self._makeOne())

    def test_instance_has_valid_construction(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IOrdering
        instance = self._makeOne()
        self.assertEqual(instance.title, u'')
        self.assertEqual(instance.description, u'')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        verifyObject(IOrdering, instance.ordering)


class ReferenceManualTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.references import ReferenceManual
        return ReferenceManual

    def _makeOne(self, title=u'', description=u'', creator=u'admin'):
        return self._getTargetClass()(title, description, creator)

    def test_class_conforms_to_IReferenceManual(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IReferenceManual
        verifyClass(IReferenceManual, self._getTargetClass())

    def test_instance_conforms_to_IReferenceManual(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IReferenceManual
        verifyObject(IReferenceManual, self._makeOne())

    def test_instance_has_valid_construction(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IOrdering
        instance = self._makeOne()
        self.assertEqual(instance.title, u'')
        self.assertEqual(instance.description, u'')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        verifyObject(IOrdering, instance.ordering)
