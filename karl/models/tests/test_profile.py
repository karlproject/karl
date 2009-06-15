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

class ProfileTests(unittest.TestCase):
    def _getTargetClass(self):
        from karl.models.profile import Profile
        return Profile

    def _makeOne(self, **kw):
        return self._getTargetClass()(**kw)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IProfile
        verifyClass(IProfile, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IProfile
        verifyObject(IProfile, self._makeOne())

    def test_ctor(self):
        inst = self._makeOne(firstname='fred')
        self.assertEqual(inst.firstname, 'fred')

    def test_creator_is___name__(self):
        from repoze.bfg.testing import DummyModel
        profiles = DummyModel()
        inst = profiles['flinty'] = self._makeOne(firstname='fred',
                                                  lastname='flintstone ')

        self.assertEqual(inst.creator, 'flinty')

    def test_title(self):
        inst = self._makeOne(firstname='fred', lastname='flintstone ')
        self.assertEqual(inst.title, 'fred flintstone')

    def test_folderish(self):
        from repoze.folder import Folder
        from repoze.folder.interfaces import IFolder
        cls = self._getTargetClass()
        self.failUnless(IFolder.implementedBy(cls))
        o = self._makeOne()
        self.failUnless(IFolder.providedBy(o))
        self.failUnless(isinstance(o, Folder))
        self.failUnless(hasattr(o, "data"))
        
    def test_alert_prefs(self):
        from karl.models.interfaces import IProfile
        inst = self._makeOne()
        self.assertEqual(IProfile.ALERT_IMMEDIATELY, 
                         inst.get_alerts_preference("foo"))
        inst.set_alerts_preference("foo", IProfile.ALERT_DIGEST)
        self.assertEqual(IProfile.ALERT_DIGEST, 
                         inst.get_alerts_preference("foo"))
        inst.set_alerts_preference("foo", IProfile.ALERT_NEVER)
        self.assertEqual(IProfile.ALERT_NEVER, 
                         inst.get_alerts_preference("foo"))
        
        self.assertRaises(ValueError, inst.set_alerts_preference, "foo", 13)
        
    def test_verify_alert_prefs_persistent(self):
        from persistent.mapping import PersistentMapping
        inst = self._makeOne()
        self.failUnless(isinstance(inst._alert_prefs, PersistentMapping))
        
    def test_pending_alerts(self):
        inst = self._makeOne()
        self.assertEqual(0, len(inst._pending_alerts))
        inst._pending_alerts.append( "FOO" )
        self.assertEqual(1, len(inst._pending_alerts))
        self.assertEqual("FOO", inst._pending_alerts.pop(0))
        self.assertEqual(0, len(inst._pending_alerts))

    def test_pending_alerts_persistent(self):
        from persistent.list import PersistentList
        inst = self._makeOne()
        self.failUnless(isinstance(inst._pending_alerts, PersistentList))
    
class ProfilesFolderTests(unittest.TestCase):
    def _getTargetClass(self):
        from karl.models.profile import ProfilesFolder
        return ProfilesFolder

    def _makeOne(self, **kw):
        return self._getTargetClass()(**kw)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IProfiles
        verifyClass(IProfiles, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IProfiles
        verifyObject(IProfiles, self._makeOne())

    def test___init___defaults(self):
        pf = self._makeOne()
        self.assertEqual(len(pf.email_to_name), 0)
        self.assertEqual(pf.email_to_name.get('nonesuch'), None)

    def test_getProfileByEmail_miss(self):
        pf = self._makeOne()
        self.assertEqual(pf.getProfileByEmail('nonesuch@example.com'), None)

    def test_getProfileByEmail_hit(self):
        from repoze.bfg.testing import DummyModel
        pf = self._makeOne()
        profile = pf['extant'] = DummyModel()
        pf.email_to_name['extant@example.com'] = 'extant'
        self.failUnless(pf.getProfileByEmail('extant@example.com') is profile)
        
    def test_getProfileByEmail_mixedcase(self):
        from repoze.bfg.testing import DummyModel
        pf = self._makeOne()
        profile = pf['extant'] = DummyModel()
        pf.email_to_name['eXtant@example.com'] = 'extant'
        self.failUnless(pf.getProfileByEmail('Extant@example.com') is profile)
