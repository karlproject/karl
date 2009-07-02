from __future__ import with_statement

import os
import sys

from zope.component import queryUtility
from repoze.bfg.interfaces import ISettings
from repoze.sendmail.delivery import QueuedMailDelivery

from karl.utilities.mailer import FakeMailDelivery

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
        return FakeMailDelivery(suppress_mail)
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
        return OsiMailDelivery(queue_path)

class OsiMailDelivery(QueuedMailDelivery):
    white_list = None
    
    def __init__(self, queue_path):
        super(OsiMailDelivery, self).__init__(queue_path)

        settings = queryUtility(ISettings)
        white_list = getattr(settings, "mail_white_list", None)
        if white_list:
            with open(white_list) as f:
                self.white_list = set([
                    unicode(line.strip()) for line in f.readlines()
                ])
                
    def send(self, fromaddr, toaddrs, message):
        if self.white_list is not None:
            toaddrs = self._filter_white_list(toaddrs)

        if toaddrs:
            super(OsiMailDelivery, self).send(fromaddr, toaddrs, message)
            
    def _filter_white_list(self, toaddrs):
        white_list = self.white_list
        return [addr for addr in toaddrs if addr in white_list]
    
