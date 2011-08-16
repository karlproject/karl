import unittest
from pyramid import testing


class TestMailDeliveryFactory(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, os=None):
        if os is None:
            import os
        from karl.utilities.mailer import mail_delivery_factory
        return mail_delivery_factory(os=os)

    def test_with_settings_and_suppress_mail(self):
        from pyramid.interfaces import ISettings
        from karl.utilities.mailer import FakeMailDelivery
        settings = DummySettings()
        testing.registerUtility(settings, ISettings)
        os = FakeOS(SUPPRESS_MAIL='1')
        delivery = self._callFUT(os)
        self.assertEqual(delivery.__class__, FakeMailDelivery)

    def test_mail_queue_path_unspecified(self):
        import os
        import sys
        from pyramid.interfaces import ISettings
        settings = DummySettings()
        testing.registerUtility(settings, ISettings)
        delivery = self._callFUT()
        exe = sys.executable
        sandbox = os.path.dirname(os.path.dirname(os.path.abspath(exe)))
        queue_path = os.path.join(os.path.join(sandbox, "var"), "mail_queue")
        self.assertEqual(delivery.queuePath, queue_path)

    def test_mail_queue_path_specified(self):
        from pyramid.interfaces import ISettings
        settings = DummySettings(mail_queue_path='/var/tmp')
        testing.registerUtility(settings, ISettings)
        delivery = self._callFUT()
        self.assertEqual(delivery.queuePath, '/var/tmp')

    def test_with_white_list(self):
        from tempfile import NamedTemporaryFile
        from pyramid.interfaces import ISettings
        from karl.utilities.mailer import WhiteListMailDelivery
        settings = DummySettings()
        f = NamedTemporaryFile()
        settings.mail_white_list = f.name
        testing.registerUtility(settings, ISettings)
        delivery = self._callFUT()
        self.assertEqual(delivery.__class__, WhiteListMailDelivery)

class TestWhiteListMailDelivery(unittest.TestCase):
    tmp_file = None

    def setUp(self):
        testing.setUp()
        self.white_list = None

    def tearDown(self):
        testing.tearDown()

        if self.tmp_file is not None:
            self.tmp_file.close()

    def _getTargetClass(self):
        from karl.utilities.mailer import WhiteListMailDelivery
        return WhiteListMailDelivery

    def _makeOne(self, sender=None):
        if sender is None:
            sender = DummyMailDelivery()
        return self._getTargetClass()(sender), sender

    def _set_whitelist(self, white_list):
        import tempfile
        from pyramid.testing import registerUtility
        from pyramid.interfaces import ISettings
        tmp = self.tmp_file = tempfile.NamedTemporaryFile()
        settings = DummySettings(mail_white_list=tmp.name)
        registerUtility(settings, ISettings)

        for email in white_list:
            print >>tmp, email
        tmp.flush()

    def test_queuePath(self):
        BEFORE = '/var/spool/before'
        AFTER = '/var/spool/after'
        delivery, sender = self._makeOne()
        sender.queuePath = BEFORE
        self.assertEqual(delivery.queuePath, BEFORE)
        delivery.queuePath = AFTER
        self.assertEqual(sender.queuePath, AFTER)

    def test_no_whitelist(self):
        delivery, sender = self._makeOne()

        delivery.send(["b", "c"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(["b", "c"], sender.calls[0]["toaddrs"])

    def test_one_recipient(self):
        self._set_whitelist(["b"])
        delivery, sender = self._makeOne()

        delivery.send(["b", "c"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(["b",], sender.calls[0]["toaddrs"])

    def test_no_recipients(self):
        self._set_whitelist(["d"])
        delivery, sender = self._makeOne()

        delivery.send(["b", "c"], "message")
        self.assertEqual(0, len(sender.calls))

    def test_all_recipients(self):
        self._set_whitelist(["b", "c"])
        delivery, sender = self._makeOne()

        delivery.send(["b", "c"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(["b", "c"], sender.calls[0]["toaddrs"])

    def test_case_insensitive(self):
        self._set_whitelist(["B@EXAMPLE.COM", 'c@example.com'])
        delivery, sender = self._makeOne()

        delivery.send(["b@example.com", "C@EXAMPLE.COM"], "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(
            ["b@example.com", "C@EXAMPLE.COM"], sender.calls[0]["toaddrs"])

    def test_address_normalization(self):
        self._set_whitelist(["B@EXAMPLE.COM", 'c@example.com'])
        delivery, sender = self._makeOne()

        delivery.send(["Fred <b@example.com>", "Bill <C@EXAMPLE.COM>"],
                      "message")
        self.assertEqual(1, len(sender.calls))
        self.assertEqual(
            ["Fred <b@example.com>", "Bill <C@EXAMPLE.COM>"],
            sender.calls[0]["toaddrs"])


class DummyMailDelivery(object):

    def __init__(self):
        self.calls = []

    def send(self, toaddrs, message):
        self.calls.append(dict(
            toaddrs=toaddrs,
            message=message,
        ))

class DummySettings:
    envelope_from_addr = 'karl@example.org'
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

class FakeOS:
    def __init__(self, **environ):
        self.environ = environ

