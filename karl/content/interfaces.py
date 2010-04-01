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

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import taggedValue

from repoze.folder.interfaces import IFolder

from karl.models.interfaces import IPosts
from karl.models.interfaces import IOthers
from karl.models.interfaces import IPages
from karl.models.interfaces import IFiles
from karl.models.interfaces import ICommunityContent

# IIntranet and IIntranets are here only for b/w compat
from karl.models.interfaces import IIntranet
from karl.models.interfaces import IIntranets

class IBlog(IFolder):
    """A folder containing blog entries"""
    taggedValue('name', 'Blog')

    title = Attribute(u'Title needed for backlinks')

class IBlogEntry(ICommunityContent, IPosts):
    """A folder for a blog entry and its comments

    o The `comments` key returns a CommentsFolder
    o The `attachments` key returns an AttachmentsFolder

    """
    taggedValue('name', 'Blog Entry')
    taggedValue('search_option', True)

class ICalendar(IFolder):
    """A folder that holds a community's calendar events"""
    taggedValue('name', 'Calendar')

    title = Attribute(u'Title needed for backlinks')

class ICalendarEvent(ICommunityContent, IOthers):
    """A folder for a calendar event"""
    taggedValue('name', 'Event')
    taggedValue('search_option', True)

    title = Attribute(u'Event title')
    startDate = Attribute(u'DateTime object with value from form')
    endDate = Attribute(u'DateTime object with value from form')
    text = Attribute(u'Text description of event.')
    location = Attribute(u'Location of event.')
    attendees = Attribute(u'List of names of people attending event.')
    contact_name = Attribute(u'Name of person to contact about this event.')
    contact_email = Attribute(u'Email of person to contact about this event.')
    creator = Attribute(u'User id of user that created this event.')
    calendar_category = Attribute("Name of the associated calendar category")

class ICalendarLayer(Interface):
    taggedValue('default_name', '_default_layer_')
    title = Attribute(u'Layer title')
    color = Attribute(u'Layer color')
    paths = Attribute(u'Layer paths')

class ICalendarCategory(Interface):
    taggedValue('default_name', '_default_category_')
    title = Attribute(u'Calendar title')

class INewsItem(ICommunityContent, IFolder):
    """ A news item.
    """
    # These tagged values mean this content type should appear in the list of
    # types to search in the advanced search.
    taggedValue('name', 'News Item')
    taggedValue('search_option', True)

    title = Attribute(u'Title of news item.')
    text = Attribute(u'Body of news item.')
    publication_date = Attribute(u'Date item was (will be) published.')
    creator = Attribute(u'User id of user that created this news item.')
    caption = Attribute(u'Caption that appears under photo for this article.')

    def get_photo():
        """ Get photo, if any, for this news item.
        """

class IReferenceManual(IFolder, ICommunityContent, IPages):
    """A reference manual in a community"""
    taggedValue('name', 'Reference Manual')
    description = Attribute(u'Description')

class IReferenceSection(IFolder, ICommunityContent, IPages):
    """A section of a reference manual in a community"""
    taggedValue('name', 'Reference Section')
    description = Attribute(u'Description')

class IWiki(IFolder):
    """A folder containing wiki pages"""
    taggedValue('name', 'Wiki')

    title = Attribute(u'Title needed for backlinks')

class IWikiPage(IFolder, ICommunityContent, IPages):
    """A page using wiki markup
    """
    taggedValue('name', 'Wiki Page')
    taggedValue('search_option', True)
    text = Attribute(u'Text -- includes wiki markup.')

class IPage(ICommunityContent, IPages):
    """A page that isn't in a wiki
    """
    taggedValue('name', 'Page')
    title = Attribute(u'Title')
    text = Attribute(u'Text')

class ICommunityFolder(ICommunityContent, IFolder):
    """A folder in a community"""
    taggedValue('name', 'Folder')

class ICommunityRootFolder(IFolder):
    """The root folder under the Files tab in a community"""
    taggedValue('name', 'Files')

    title = Attribute(u'Title needed for backlinks')

class IIntranetRootFolder(IFolder):
    """The root folder under the Files tab in an intranet"""
    taggedValue('name', 'Files')

    title = Attribute(u'Title needed for backlinks')

class IIntranetFolder(ICommunityContent, IFolder):
    """ Marker for an IComunityFolder folder in an intranet"""
    taggedValue('name', 'Folder')

class INewsFolder(ICommunityContent, IFolder):
    """ Marker for a newsitem folder that needs special layout """
    taggedValue('name', 'Folder')

class IEventsFolder(ICommunityContent, IFolder):
    """ Marker for an events folder that needs special layout"""
    taggedValue('name', 'Folder')

class IReferencesFolder(ICommunityContent, IFolder):
    """ Marker for a folder containing only reference manuals """
    taggedValue('name', 'Folder')


class ICommunityFile(ICommunityContent, IFiles):
    """A file in a community"""
    taggedValue('name', 'File')
    taggedValue('search_option', True)

    blobfile = Attribute(u'Optional file attachment')
    mimetype = Attribute(u'Content type')
    filename = Attribute(u'Uploaded filename')
    size = Attribute(u'Size in bytes')

class IImage(Interface):
    """ An image. """

    image_size = Attribute(u'Tuple of (width, height) in pixels.')

    def thumbnail(size):
        """
        Returns resized image bound by size, which is a tuple of
        (width, height).
        """

    def image():
        """
        Returns instance of PIL.Image.
        """

class IForumsFolder(IFolder):
    """ A folder that contains forums """
    taggedValue('name', 'Forums')

class IForum(IFolder, IPosts):
    """ A forum in a community """
    taggedValue('name', 'Forum')

class IForumTopic(ICommunityContent, IPosts):
    """ A topic in a forum """
    taggedValue('name', 'Forum Topic')

    text = Attribute(u"Form post content.")

class IIntranetsTool(IFolder):
    """ Stash data for intranet communities and register views """
    taggedValue('name', 'Intranets Tool')

class IOrdering(Interface):
    """ Persistent ordering of content in a folder """

    def sync(entries):
        """ Find mistakes between the ordering and context """

    def moveUp(name):
        """ Move an item up in the ordering """

    def moveDown(name):
        """ Move an item down in the ordering """

    def add(name):
        """ Add an item at the end of the ordering """

    def remove(name):
        """ Remove an item from the ordering """

    def items():
        """ Return the internal list of names in the ordering as list"""

    def previous_name(current_name):
        """ Given a name, return the previous name or None """

    def next_name(current_name):
        """ Given a name, return the next name or None """
