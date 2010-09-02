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

class InvitationTests(unittest.TestCase):
    def _getTargetClass(self):
        from karl.models.members import Invitation
        return Invitation

    def _makeOne(self, email=u'x@y.org', message='Hi there, handsome.'):
        return self._getTargetClass()(email, message)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IInvitation
        verifyClass(IInvitation, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IInvitation
        verifyObject(IInvitation, self._makeOne())

    def test___init___defaults(self):
        invitation = self._makeOne()
        self.assertEqual(invitation.email, u'x@y.org')
        self.assertEqual(invitation.message, u'Hi there, handsome.')
        
    def test__init__(self):
        invitation = self._makeOne(email='z@x.gov', message='Ciao bello')
        self.assertEqual(invitation.email, u'z@x.gov')
        self.assertEqual(invitation.message, u'Ciao bello')
        
    def test_content_factory(self):
        from repoze.lemonade.testing import registerContentFactory
        from repoze.lemonade.content import create_content
        from karl.models.interfaces import IInvitation
        class DummyInvitation:
            def __init__(self, email):
                self.email = email
        registerContentFactory(DummyInvitation, IInvitation)
        invitation = create_content(IInvitation, u'q@r.p')
        self.failUnless(invitation.__class__ is DummyInvitation)
        self.assertEqual(invitation.email, u'q@r.p')
