from __future__ import with_statement

import os
import unittest
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

class TestMailDeliveryFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, os=os):
        from karl.utilities.mailer import mail_delivery_factory
        return mail_delivery_factory(os=os)

    def test_no_settings(self):
        from karl.utilities.mailer import FakeMailDelivery
        delivery = self._callFUT()
        self.assertEqual(delivery.__class__, FakeMailDelivery)

    def test_with_settings_and_suppress_mail(self):
        from repoze.bfg.interfaces import ISettings 
        from karl.utilities.mailer import FakeMailDelivery
        settings = DummySettings()
        testing.registerUtility(settings, ISettings)
        os = FakeOS(SUPPRESS_MAIL='1')
        delivery = self._callFUT(os)
        self.assertEqual(delivery.__class__, FakeMailDelivery)

    def test_mail_queue_path_unspecified(self):
        import sys
        from repoze.bfg.interfaces import ISettings 
        settings = DummySettings()
        testing.registerUtility(settings, ISettings)
        delivery = self._callFUT()
        exe = sys.executable
        sandbox = os.path.dirname(os.path.dirname(os.path.abspath(exe)))
        queue_path = os.path.join(os.path.join(sandbox, "var"), "mail_queue")
        self.assertEqual(delivery.queuePath, queue_path)

    def test_mail_queue_path_specified(self):
        from repoze.bfg.interfaces import ISettings
        settings = DummySettings(mail_queue_path='/var/tmp')
        testing.registerUtility(settings, ISettings)
        delivery = self._callFUT()
        self.assertEqual(delivery.queuePath, '/var/tmp')


class TestWhiteListMailDelivery(unittest.TestCase):
    tmp_name = '/tmp/white_list.txt'

    def _set_whitelist(self, white_list):
        from repoze.bfg.testing import registerUtility
        from repoze.bfg.interfaces import ISettings
        settings = DummySettings(mail_white_list=self.tmp_name)
        registerUtility(settings, ISettings)

        with open(self.tmp_name, "w") as f:
            for email in white_list:
                print >>f, email

    def setUp(self):
        cleanUp()
        self.white_list = None

    def tearDown(self):
        cleanUp()

        import os
        if os.path.exists(self.tmp_name):
            os.remove(self.tmp_name)

    def test_no_whitelist(self):
        from karl.utilities.mailer import WhiteListMailDelivery
        sender = DummyMailDelivery()
        delivery = WhiteListMailDelivery(sender)

        delivery.send("a", ["b", "c"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(["b", "c"], sender.calls[0]["toaddrs"])

    def test_one_recipient(self):
        from karl.utilities.mailer import WhiteListMailDelivery
        sender = DummyMailDelivery()
        self._set_whitelist(["b"])

        delivery = WhiteListMailDelivery(sender)
        delivery.send("a", ["b", "c"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(["b",], sender.calls[0]["toaddrs"])

    def test_no_recipients(self):
        from karl.utilities.mailer import WhiteListMailDelivery
        sender = DummyMailDelivery()
        self._set_whitelist(["d"])

        delivery = WhiteListMailDelivery(sender)
        delivery.send("a", ["b", "c"], "message")
        self.assertEqual(0, len(sender.calls))

    def test_all_recipients(self):
        from karl.utilities.mailer import WhiteListMailDelivery
        sender = DummyMailDelivery()
        self._set_whitelist(["b", "c"])

        delivery = WhiteListMailDelivery(sender)
        delivery.send("a", ["b", "c"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(["b", "c"], sender.calls[0]["toaddrs"])

class DummyMailDelivery(object):
    def __init__(self):
        self.calls = []

    def send(self, fromaddr, toaddrs, message):
        self.calls.append(dict(
            fromaddr=fromaddr,
            toaddrs=toaddrs,
            message=message,
        ))

class DummySettings:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

class FakeOS:
    def __init__(self, **environ):
        self.environ = environ

