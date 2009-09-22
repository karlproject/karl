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

""" An attachments facility that can be hung off resources"""

from zope.interface import implements
from repoze.folder import Folder

from karl.models.interfaces import IAttachmentsFolder

class AttachmentsFolder(Folder):
    implements(IAttachmentsFolder)
    title = u'Attachments Folder'

    #XXX next_id appears to be unused--attachment ids are filenames of
    #    uploaded files.
    @property
    def next_id(self):
        """Return a string with the next highest number key"""
        try:
            maxkey = self.data.maxKey()
        except ValueError:
            # no members
            return '1'
        return unicode(int(maxkey) + 1)
    
