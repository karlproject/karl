from zope.component import queryUtility
from repoze.bfg.interfaces import ISettings
from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import Everyone
from repoze.mailin.monitor.models import MailInMonitor

def KarlMailInMonitor():
    settings = queryUtility(ISettings)
    pending_db_path = settings.pending_db_path
    maildir_path = settings.maildir_path

    class Factory(MailInMonitor):
        """
        Provide our own model for the root of the mail in monitor graph.  This way
        we provide an acl for security and our own mechanism for getting at config
        parameters.
        """
        __acl__ = [
            (Allow, 'group.KarlAdmin', ('view', 'manage')),
            (Deny, Everyone, ('view', 'manage'))
        ]

        def __init__(self, environ):
            """ Factory for bfg router.
            """
            # override MailInMonitor.__init__
            self.pending_db_path = pending_db_path
            self.maildir_path = maildir_path

    return Factory