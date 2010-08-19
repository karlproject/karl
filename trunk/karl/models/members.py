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

"""A folder that manages community membership.

A community will have a sub-item of `members` that can be traversed
to.  It will then have views registered against it for the various
screens, and methods that provide easy access to data stored outside
of the folder (e.g. current members.) It will also contain some
persistent content, such as invitations.
"""

from zope.interface import implements
from repoze.folder import Folder

from karl.models.interfaces import IMembers
from karl.models.interfaces import IInvitation
from persistent import Persistent

class Invitation(Persistent):
    implements(IInvitation)

    def __init__(self, email, message):
        Persistent.__init__(self)
        self.email = unicode(email)
        self.message = unicode(message)

class Members(Folder):
    implements(IMembers)

