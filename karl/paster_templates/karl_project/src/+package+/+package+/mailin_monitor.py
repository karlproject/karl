from persistent import Persistent
from zope.component import queryUtility
from repoze.bfg.interfaces import ISettings
from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import Everyone
from repoze.mailin.monitor.models import MailInMonitor

class KarlMailInMonitor(Persistent, MailInMonitor):
    _pending_db_path = None
    _maildir_path = None
    __acl__ = [
        (Allow, 'group.KarlAdmin', ('view', 'manage')),
        (Deny, Everyone, ('view', 'manage'))
    ]

    def __init__(self):
        # override MailInMonitor.__init__
        pass

    @property
    def pending_db_path(self):
        if self._pending_db_path is None:
            settings = queryUtility(ISettings)
            self._pending_db_path = settings.pending_db_path
        return self._pending_db_path

    @property
    def maildir_path(self):
        if self._maildir_path is None:
            settings = queryUtility(ISettings)
            self._maildir_path = settings.maildir_path
        return self._maildir_path

