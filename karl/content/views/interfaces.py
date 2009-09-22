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

from zope.interface import Interface
from zope.interface import Attribute

class IFileInfo(Interface):
    """ An interface representing file info for display in views """
    name = Attribute('The name of the file in its container')
    title = Attribute('The title of the file or folder')
    modified = Attribute('A string representing the modification time/date '
                         'of the file or folder')
    url = Attribute('A url for the file or folder')
    mimeinfo = Attribute('Mime information for the file or folder '
        '(instance of karl.utilities.interfaces.IMimeInfo)')
    size = Attribute('File size with units such as MB')

class IBylineInfo(Interface):
    """ Grabe resource info for showing a byline in ZPT macro"""

    author_name = Attribute('The title of the profile for the creator')
    author_url = Attribute('The URL to the profile of the creator')
    posted_date = Attribute('A pretty representation of the posted date')

class IFolderCustomizer(Interface):
    """ Use adaptation to push policies on folder creation out of core"""

    markers = Attribute('Sequence of interfaces to mark the new folder')

class IShowSendalert(Interface):
    """ Policy for when to show-hide the sendalert choice """

    show_sendalert = Attribute('Boolean to determine visible')

class IShowIsPrivate(Interface):
    """ Policy for when to show-hide the is-private choice """

class INetworkNewsMarker(Interface):
    """ TTW assignable marker to customize a network news folder """

class INetworkEventsMarker(Interface):
    """ TTW assignable marker to customize a network events folder """
