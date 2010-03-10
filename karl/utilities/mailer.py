from __future__ import with_statement

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

    md = QueuedMailDelivery(queue_path)
    if getattr(settings, "mail_white_list", None):
        md = WhiteListMailDelivery(md)
    return md

class FakeMailDelivery:
    implements(IMailDelivery)

    def __init__(self, quiet=True):
        self.quiet = quiet

    def send(self, mfrom, mto, msg):
        if not self.quiet:
            print 'From:', mfrom
            print 'To:', mto
            print 'Message:', msg

class WhiteListMailDelivery(object):
    """Decorates an IMailDelivery with a recipient whitelist"""
    implements(IMailDelivery)

    def __init__(self, md):
        self.md = md
        settings = queryUtility(ISettings)
        white_list_fn = getattr(settings, "mail_white_list", None)
        if white_list_fn:
            with open(white_list_fn) as f:
                self.white_list = set(
                    unicode(line.strip()).lower() for line in f.readlines())
        else:
            self.white_list = None

    def _get_queuePath(self):
        return self.md.queuePath
    def _set_queuePath(self, value):
        self.md.queuePath = value
    queuePath = property(_get_queuePath, _set_queuePath)

    def send(self, fromaddr, toaddrs, message):
        if self.white_list is not None:
            toaddrs = [addr for addr in toaddrs
                if addr.lower() in self.white_list]
        if toaddrs:
            self.md.send(fromaddr, toaddrs, message)


# Make an instance available as registerable component
# (If for some reason we find config data isn't set yet or we think it might
# change during run time, register the factory instead.)
#mailer = mail_delivery_factory()
