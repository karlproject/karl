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

class CommunityTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.models.community import Community
        return Community

    def _makeOne(self, title=u'title', 
                 description=u'description', text=u'text', 
                 creator=u'admin'):
        tc = self._getTargetClass()
        return tc(title, description, text, creator)

    def test_class_conforms_to_ICommunity(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ICommunity
        verifyClass(ICommunity, self._getTargetClass())

    def test_instance_conforms_to_ICommunity(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ICommunity
        verifyObject(ICommunity, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.description, u'description')
        self.assertEqual(instance.text, u'text')
        self.assertEqual(instance.creator, u'admin')
        self.assert_('members' in instance.keys())

    def test_instance_construct_with_none(self):
        instance = self._makeOne(text=None)
        self.assertEqual(instance.text, u'')

    def test_member_names(self):
        instance = self._makeOne()
        instance.users = DummyUsers(['a', 'b'])
        names = instance.member_names
        self.assertEqual(sorted(list(names)), ['a', 'b'])

    def test_moderator_names(self):
        instance = self._makeOne()
        instance.users = DummyUsers(['a', 'b'])
        names = instance.moderator_names
        self.assertEqual(sorted(list(names)), ['a', 'b'])

    def test_number_of_members(self):
        instance = self._makeOne()
        instance.users = DummyUsers(['a', 'b'])
        num = instance.number_of_members
        self.assertEqual(num, 2)

    def test_members_group_name(self):
        instance = self._makeOne()
        instance.__name__ = 'foo'
        self.assertEqual(instance.members_group_name,
                         'group.community:foo:members')

    def test_moderators_group_name(self):
        instance = self._makeOne()
        instance.__name__ = 'foo'
        self.assertEqual(instance.moderators_group_name,
                         'group.community:foo:moderators')

    
class DummyUsers:
    def __init__(self, groups):
        self.groups = groups
        
    def users_in_group(self, group_name):
        return self.groups
    

