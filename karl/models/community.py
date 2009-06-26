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

from datetime import datetime
from zope.interface import implements
from repoze.folder import Folder

from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunities
from karl.models.members import Members

from karl.utils import find_users

class Community(Folder):
    implements(ICommunity)
    _members_group = 'group.community:%s:members'
    _moderators_group = 'group.community:%s:moderators'
    default_tool = '' # means default tab (overview)
    content_modified = None # will be set by subscriber

    def __init__(self, title, description, text=u'', creator=u''):

        super(Community, self).__init__()
        self.title = unicode(title)
        self.description = unicode(description)
        if text is None:
            self.text = u''
        else:
            self.text = unicode(text)            
        self.creator = creator
        self['members'] = members = Members()

    @property
    def members_group_name(self):
        return self._members_group % self.__name__

    @property
    def moderators_group_name(self):
        return self._moderators_group % self.__name__

    @property
    def number_of_members(self):
        return len(self.member_names)

    @property
    def member_names(self):
        name = self._members_group % self.__name__
        return self._get_group_names(name)

    @property
    def moderator_names(self):
        name = self._moderators_group % self.__name__
        return self._get_group_names(name)

    def _get_group_names(self, group):
        users = find_users(self)
        names = users.users_in_group(group)
        return set(names)
        

class CommunitiesFolder(Folder):
    implements(ICommunities)
    title = 'Communities'
    
    
