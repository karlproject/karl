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
from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface import Interface

from repoze.bfg import testing

from karl.utilities.interfaces import IAlert

from karl.testing import DummyCommunity
from karl.testing import DummyProfile

class TestAlerts(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _get_instance(self):
        from karl.utilities.alerts import Alerts
        return Alerts()

    def test_emit(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.bfg.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["b"] = DummyProfile()
        profiles["c"] = DummyProfile()

        community.member_names = set(("a","c",))
        community.moderator_names = set(("b",))

        request = testing.DummyRequest()
        testing.registerAdapter(DummyEmailAlertAdapter,
                                (IDummy, IProfile, IRequest), IAlert)

        self._get_instance().emit(context, request)
        self.assertEqual(3, len(mailer))

    def test_respect_alert_prefs(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.bfg.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["b"] = DummyProfile()
        profiles["b"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DIGEST)
        profiles["c"] = DummyProfile()
        profiles["c"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_NEVER)

        community.member_names = set(("a","c",))
        community.moderator_names = set(("b",))

        request = testing.DummyRequest()
        testing.registerAdapter(DummyEmailAlertAdapter,
                                (IDummy, IProfile, IRequest), IAlert)

        self._get_instance().emit(context, request)
        self.assertEqual(1, len(mailer))
        self.assertEqual(1, len(profiles["b"]._pending_alerts))

    def test_digest(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.bfg.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["a"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DIGEST)
        profiles["b"] = DummyProfile()
        profiles["b"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DIGEST)

        community.member_names = set(("a",))
        community.moderator_names = set(("b",))

        request = testing.DummyRequest()
        testing.registerAdapter(DummyEmailAlertAdapter,
                                (IDummy, IProfile, IRequest), IAlert)

        tool = self._get_instance()
        tool.emit(context, request)
        community.moderator_names = set()
        tool.emit(context, request)

        self.assertEqual(0, len(mailer))
        self.assertEqual(2, len(profiles["a"]._pending_alerts))
        self.assertEqual(1, len(profiles["b"]._pending_alerts))

        tool.send_digests(site)

        self.assertEqual(2, len(mailer))
        self.assertEqual(0, len(profiles["a"]._pending_alerts))
        self.assertEqual(0, len(profiles["b"]._pending_alerts))

        self.assertEqual(['a@x.org',], mailer[0].mto)
        self.assertEqual(['b@x.org',], mailer[1].mto)

class DummyEmailAlertAdapter(object):
    implements(IAlert)

    mfrom = "test@example.org"
    mto = ["a@x.org",]

    def __init__(self, context, profile, request):
        from email.message import Message
        message = Message()
        message["From"] = "Karl <test@example.org>"
        message["To"] = "Andy Ex <a@x.org>"
        message["Subject"] = "Testing"
        message.set_payload("Test email")
        self.message = message

class IDummy(Interface):
    pass
