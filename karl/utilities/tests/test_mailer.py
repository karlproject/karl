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
        

class DummySettings:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
            

class FakeOS:
    def __init__(self, **environ):
        self.environ = environ
        
    
