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

from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface import Interface

from pyramid import testing

from karl.utilities.interfaces import IAlert

from karl.testing import DummyCommunity
from karl.testing import DummyProfile

class TestAlerts(unittest.TestCase):
    def setUp(self):
        self.config = testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _get_instance(self):
        from karl.utilities.alerts import Alerts
        return Alerts()

    def test_emit(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from pyramid.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        self.config.registry.registerUtility(mailer, IMailDelivery)

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
        self.config.registry.registerAdapter(DummyEmailAlertAdapter,
                                             (IDummy, IProfile, IRequest),
                                             IAlert)

        self._get_instance().emit(context, request)
        self.assertEqual(3, len(mailer))

    def test_respect_alert_prefs(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from pyramid.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        self.config.registry.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["b"] = DummyProfile()
        profiles["b"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DAILY_DIGEST)
        profiles["c"] = DummyProfile()
        profiles["c"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_NEVER)
        profiles["d"] = DummyProfile()
        profiles["d"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_WEEKLY_DIGEST)
        profiles["e"] = DummyProfile()
        profiles["e"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_BIWEEKLY_DIGEST)

        community.member_names = set(("a","c",))
        community.moderator_names = set(("b",))

        request = testing.DummyRequest()
        self.config.registry.registerAdapter(DummyEmailAlertAdapter,
                                             (IDummy, IProfile, IRequest),
                                             IAlert)

        self._get_instance().emit(context, request)
        self.assertEqual(1, len(mailer))
        self.assertEqual(1, len(profiles["b"]._pending_alerts))

    def test_daily_digest(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from pyramid.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        self.config.registry.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["a"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DAILY_DIGEST)
        profiles["b"] = DummyProfile()
        profiles["b"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DAILY_DIGEST)

        community.member_names = set(("a",))
        community.moderator_names = set(("b",))

        request = testing.DummyRequest()
        self.config.registry.registerAdapter(DummyEmailAlertAdapter,
                                             (IDummy, IProfile, IRequest),
                                             IAlert)

        tool = self._get_instance()
        tool.emit(context, request)
        community.moderator_names = set()
        tool.emit(context, request)

        self.assertEqual(0, len(mailer))
        self.assertEqual(2, len(profiles["a"]._pending_alerts))
        self.assertEqual(1, len(profiles["b"]._pending_alerts))

        self.config.testing_add_renderer('karl.utilities:email_digest.pt')

        tool.send_digests(site, 'daily')

        self.assertEqual(0, len(profiles["a"]._pending_alerts))
        self.assertEqual(0, len(profiles["b"]._pending_alerts))

        self.assertEqual(2, len(mailer))
        mtos = [x.mto for x in mailer]
        self.assertTrue(['a@x.org',] in mtos)
        self.assertTrue(['b@x.org',] in mtos)

    def test_weekly_digests(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from pyramid.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        self.config.registry.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["a"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DAILY_DIGEST)
        profiles["b"] = DummyProfile()
        profiles["b"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_WEEKLY_DIGEST)
        profiles["c"] = DummyProfile()
        profiles["c"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_BIWEEKLY_DIGEST)

        community.member_names = set(("a", "b", "c"))
        community.moderator_names = set()

        request = testing.DummyRequest()
        self.config.registry.registerAdapter(DummyEmailAlertAdapter,
                                             (IDummy, IProfile, IRequest),
                                             IAlert)

        tool = self._get_instance()
        tool.emit(context, request)
        tool.emit(context, request)

        self.assertEqual(0, len(mailer))
        self.assertEqual(2, len(profiles["a"]._pending_alerts))
        self.assertEqual(2, len(profiles["b"]._pending_alerts))
        self.assertEqual(2, len(profiles["c"]._pending_alerts))

        self.config.testing_add_renderer('karl.utilities:email_digest.pt')

        tool.send_digests(site, "weekly")

        self.assertEqual(0, len(profiles["a"]._pending_alerts))
        self.assertEqual(0, len(profiles["b"]._pending_alerts))
        self.assertEqual(2, len(profiles["c"]._pending_alerts))

        self.assertEqual(2, len(mailer))
        mtos = [x.mto for x in mailer]
        self.assertTrue(['a@x.org',] in mtos)
        self.assertTrue(['b@x.org',] in mtos)

    def test_biweekly_digests(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from pyramid.interfaces import IRequest
        from karl.models.interfaces import IProfile
        from karl.testing import DummyMailer

        mailer = DummyMailer()
        self.config.registry.registerUtility(mailer, IMailDelivery)

        community = DummyCommunity()
        community["foo"] = context = testing.DummyModel()
        directlyProvides(context, IDummy)

        site = community.__parent__.__parent__
        site["profiles"] = profiles = testing.DummyModel()
        profiles["a"] = DummyProfile()
        profiles["a"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_DAILY_DIGEST)
        profiles["b"] = DummyProfile()
        profiles["b"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_WEEKLY_DIGEST)
        profiles["c"] = DummyProfile()
        profiles["c"].set_alerts_preference(community.__name__,
                                            IProfile.ALERT_BIWEEKLY_DIGEST)

        community.member_names = set(("a", "b", "c"))
        community.moderator_names = set()

        request = testing.DummyRequest()
        self.config.registry.registerAdapter(DummyEmailAlertAdapter,
                                             (IDummy, IProfile, IRequest),
                                             IAlert)

        tool = self._get_instance()
        tool.emit(context, request)
        tool.emit(context, request)

        self.assertEqual(0, len(mailer))
        self.assertEqual(2, len(profiles["a"]._pending_alerts))
        self.assertEqual(2, len(profiles["b"]._pending_alerts))
        self.assertEqual(2, len(profiles["c"]._pending_alerts))

        self.config.testing_add_renderer('karl.utilities:email_digest.pt')

        tool.send_digests(site, "biweekly")

        self.assertEqual(3, len(mailer))
        self.assertEqual(0, len(profiles["a"]._pending_alerts))
        self.assertEqual(0, len(profiles["b"]._pending_alerts))
        self.assertEqual(0, len(profiles["c"]._pending_alerts))

        mtos = [x.mto for x in mailer]
        self.assertTrue(['a@x.org',] in mtos)
        self.assertTrue(['b@x.org',] in mtos)
        self.assertTrue(['c@x.org',] in mtos)

class DummyEmailAlertAdapter(object):
    implements(IAlert)

    mfrom = "test@example.org"
    mto = ["a@x.org",]

    def __init__(self, context, profile, request):
        from repoze.postoffice.message import Message
        message = Message()
        message["From"] = "Karl <test@example.org>"
        message["To"] = "Andy Ex <a@x.org>"
        message["Subject"] = "Testing"
        message.set_payload("Test email", "UTF-8")
        self.message = message

class IDummy(Interface):
    pass
