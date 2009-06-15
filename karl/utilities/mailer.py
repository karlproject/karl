import os
import sys

from zope.interface import implements
from zope.component import queryUtility
from repoze.bfg.interfaces import ISettings
from repoze.sendmail.delivery import QueuedMailDelivery
from repoze.sendmail.interfaces import IMailDelivery

def boolean(s):
    s = s.lower()
    return s.startswith('y') or s.startswith('1') or s.startswith('t')

def mail_delivery_factory(os=os): # accepts 'os' for unit test purposes
    """Factory method for creating an instance of repoze.sendmail.IDelivery
    for use by this application.
    """
    settings = queryUtility(ISettings)
    
    # If settings utility not present, we are probably testing and should
    # suppress sending mail.  Can also be set explicitly in environment 
    # variable
    suppress_mail = boolean(os.environ.get('SUPPRESS_MAIL', ''))

    if settings is None or suppress_mail:
        return FakeMailDelivery()
    else:
        queue_path = getattr(settings, "mail_queue_path", None)
        if queue_path is None:
            # Default to var/mail_queue
            # we assume that the console script lives in the 'bin' dir of a
            # sandbox or buildout, and that the mail_queue directory lives in 
            # the 'var' directory of the sandbox or buildout
            exe = sys.executable
            sandbox = os.path.dirname(os.path.dirname(os.path.abspath(exe)))
            queue_path = os.path.join(
                os.path.join(sandbox, "var"), "mail_queue"
            )
        queue_path = os.path.abspath(os.path.normpath(
            os.path.expanduser(queue_path)))
        return QueuedMailDelivery(queue_path)

class FakeMailDelivery:
    implements(IMailDelivery)

    def __init__(self, quiet=False):
        self.quiet = quiet
        
    def send(self, mfrom, mto, msg):
        if not self.quiet:
            print 'From:', mfrom
            print 'To:', mto
            print 'Message:', msg

# Make an instance available as registerable component
# (If for some reason we find config data isn't set yet or we think it might
# change during run time, register the factory instead.)
#mailer = mail_delivery_factory()
