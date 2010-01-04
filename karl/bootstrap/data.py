from zope.component import queryUtility
from zope.interface import implements

from repoze.bfg.security import Allow
from repoze.bfg.security import Authenticated

from karl.bootstrap.interfaces import IInitialData
from karl.bootstrap.interfaces import IInitialOfficeData

from karl.security.policy import ADMINISTRATOR_PERMS
from karl.security.policy import GUEST_PERMS
from karl.security.policy import MEMBER_PERMS
from karl.security.policy import MODERATOR_PERMS

_marker = object()

class DefaultInitialData(object):
    implements(IInitialData)

    moderator_principals = ['group.KarlModerator']
    member_principals = ['group.KarlStaff']
    guest_principals = []
    community_tools = ('blog', 'wiki', 'calendar', 'files')
    intranet_tools = ('forums', 'intranets', 'files')
    admin_user = 'admin'
    admin_groups = ('group.KarlStaff', 'group.KarlAdmin')

    folder_markers = [
        ('network-news', 'Network News', 'network_news', 'files'),
        ('network-events', 'Network Events', 'network_events', 'files'),
    ]

    site_acl = [
        (Allow, Authenticated, GUEST_PERMS),
        (Allow, 'group.KarlStaff', MEMBER_PERMS),
        (Allow, 'group.KarlModerator', MODERATOR_PERMS),
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
    ]

    profiles_acl = [
        (Allow, 'group.KarlUserAdmin', ADMINISTRATOR_PERMS),
        ]

    staff_acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS+MODERATOR_PERMS),
        (Allow, 'group.KarlModerator', MODERATOR_PERMS),
        (Allow, 'group.KarlStaff', GUEST_PERMS)
        ]

    users_and_groups = [
        ('admin', 'Ad','Min','admin@example.com',
         ('group.KarlAdmin', 'group.KarlUserAdmin', 'group.KarlStaff')),
    ]

    _office_data = _marker
    @property
    def office_data(self):
        if self._office_data is _marker:
            self._office_data = queryUtility(
                IInitialOfficeData, default=None)
        return self._office_data


