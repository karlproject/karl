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

from zope.interface import implements

from repoze.who.interfaces import IMetadataProvider

class HTGroupsMetadataProviderPlugin:
    implements(IMetadataProvider)
    
    def __init__(self, filename):
        self.filename = filename
        self.users = self._refresh()

    def _refresh(self):
        f = open(self.filename, 'r')
        users = {}
        for line in f:
            if not line.strip():
                continue
            groupname, usernames = line.split(':')
            groupname.strip()
            usernames.strip()
            usernames = usernames.split()
            for username in usernames:
                groups = users.setdefault(username, [])
                if groupname not in groups:
                    groups.append('group.' + groupname)
        return users

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        userid = identity['repoze.who.userid']
        groups = self.users.get(userid, [])
        identitygroups = identity.setdefault('groups', [])
        identitygroups.extend(groups)

