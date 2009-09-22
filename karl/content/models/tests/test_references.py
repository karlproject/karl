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
        instance = self._makeOne()
        self.assertEqual(instance.title, u'')
        self.assertEqual(instance.description, u'')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')

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
        instance = self._makeOne()
        self.assertEqual(instance.title, u'')
        self.assertEqual(instance.description, u'')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        self.assert_(hasattr(instance, 'ordering'))
        ordering = instance.ordering
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IOrdering
        verifyObject(IOrdering, ordering)
        
    def test_ordering_sync(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        ordering = instance.ordering

        ordering.sync(instance.keys())
        self.assertEqual(ordering.items(), [u's1', u's2'])
        del instance['s1']
        ordering.sync(instance.keys())
        self.assertEqual(ordering.items(), [u's2'])
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ordering.sync(instance.keys())
        self.assertEqual(ordering.items(), [u's2', u's3', u's4'])

    def test_ordering_add(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        ordering = instance.ordering
        ordering.sync(instance.keys())

        ordering.add(u's3')
        self.assertEqual(ordering.items(), [u's1', u's2', u's3'])

    def test_ordering_remove(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ordering = instance.ordering
        ordering.sync(instance.keys())

        ordering.remove(u's3')
        self.assertEqual(ordering.items(), [u's1', u's2', u's4'])

    def test_ordering_moveUp_middle(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ordering = instance.ordering
        ordering.sync(instance.keys())

        ordering.moveUp('s3')
        self.assertEqual(ordering.items(), [u's1', u's3', u's2', u's4'])


    def test_ordering_moveUp_top(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ordering = instance.ordering
        ordering.sync(instance.keys())

        ordering.moveUp('s1')
        self.assertEqual(ordering.items(), [u's2', u's3', u's4', u's1'])

    def test_ordering_moveDown_middle(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ordering = instance.ordering
        ordering.sync(instance.keys())

        ordering.moveDown ('s1')
        self.assertEqual(ordering.items(), [u's2', u's1', u's3', u's4'])

    def test_ordering_moveDown_end(self):
        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ordering = instance.ordering
        ordering.sync(instance.keys())

        ordering.moveDown ('s4')
        self.assertEqual(ordering.items(), [u's4', u's1', u's2', u's3'])

    def test_ordering_previous_next(self):

        instance = self._makeOne()
        instance['s1'] = testing.DummyModel(title='Section 1')
        instance['s2'] = testing.DummyModel(title='Section 2')
        instance['s3'] = testing.DummyModel(title='Section 3')
        instance['s4'] = testing.DummyModel(title='Section 4')
        ord = instance.ordering
        ord.sync(instance.keys())

        self.assertEqual(ord.previous_name(u's2'), u's1')
        self.assertEqual(ord.previous_name(u's1'), None)
        self.assertEqual(ord.next_name(u's3'), u's4')
        self.assertEqual(ord.next_name(u's4'), None)

