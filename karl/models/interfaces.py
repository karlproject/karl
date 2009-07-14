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

from zope.component.interfaces import IObjectEvent

from repoze.folder.interfaces import IFolder
from repoze.lemonade.interfaces import IContent

class ICommunityContent(IContent):
    """ Base interface for content which is within a community.
    """
    sendalert = Attribute(u'Should community members be notified on creation?.')
    creator = Attribute(u'Creating userid')
    title = Attribute(u'Title of content')

class IGroupSearchFactory(Interface):
    def __call__(context, request, term):
        """ return an object implementing IGroupSearch or None if
        no IGroupSearch can be found """

class IGroupSearch(Interface):
    def __call__():
        """ Return num, docids, resolver for a full search """

    def get_batch():
        """ Return a single batch of results (based on request information) """

# Interfaces for the LiveSearch grouping
class IPeople(Interface):
    """Grouping for LiveSearch and other purposes"""
    taggedValue('name', 'People')

class IPosts(Interface):
    """Grouping for LiveSearch and other purposes"""
    taggedValue('name', 'Posts')

class IPages(Interface):
    """Grouping for LiveSearch and other purposes"""
    taggedValue('name', 'Pages')

class IFiles(Interface):
    """Grouping for LiveSearch and other purposes"""
    taggedValue('name', 'Files')

class IOthers(Interface):
    """Grouping for LiveSearch and other purposes"""
    taggedValue('name', 'Others')

# --- end LiveSearch grouping

class ISite(IFolder):
    """ Karl site """
    taggedValue('name', 'Site')

    def update_indexes():
        """Add and remove catalog indexes to match a fixed schema"""

class ICommunities(IFolder):
    """ Communities folder """
    taggedValue('name', 'Communities')

class ICommentsFolder(IFolder):
    """ A container for comments """
    taggedValue('name', 'Comments Folder')

class IComment(IFolder, ICommunityContent, IPosts):
    """ A container holding a comment and any attachments """
    taggedValue('name', 'Comment')
    taggedValue('search_option', True)

class IAttachmentsFolder(IFolder):
    """ A container for attachments (implemented as File objects) """
    taggedValue('name', 'Attachments Folder')

class IMembers(IFolder):
    """ Easy access to community member data, and store invitations"""
    taggedValue('name', 'Members')

class IInvitation(Interface):
    """ Persistent object with information for joining KARL """
    taggedValue('name', 'Invitation')

    email = Attribute(u'Email address for the person being invited')
    message = Attribute(u'Personal message sent along with the invitation')

class IProfiles(IFolder):
    """ Profiles folder """
    taggedValue('name', 'Profiles')

    def getProfileByEmail(email):
        """ Return the profile which has the given email address.

        o Return None if no match is found.
        """

class IProfile(IFolder, IPeople):
    """ User profile """
    taggedValue('name', 'Profile')

    firstname = Attribute(u"User's first name.")
    lastname = Attribute(u"User's last name.")
    email = Attribute(u"User's email address.")

    # XXX The fields below (phone through biography) are OSI specific
    # and probably should be removed from here.  It's possible that
    # they don't need to be documented as interface attributes at all.
    phone = Attribute(u"User's phone number.")
    extension = Attribute(u"User's phone extension.")
    department = Attribute(u"User's department.")  # XXX redundant with categories?
    position = Attribute(u"User's position.")
    organization = Attribute(u"User's organization")  # XXX redundant with categories?
    location = Attribute(u"User's location.")
    country = Attribute(u"User's country.")
    website = Attribute(u"User's website url.")
    languages = Attribute(u"User's spoken languages.")
    office = Attribute(u"User's office.")  # XXX redundant with categories?
    room_no = Attribute(u"User's room number.")
    biography = Attribute(u"User's biography.")

    home_path = Attribute(u"Path to user's home model, possibly including "
                          u"view.  May be None.")
    categories = Attribute(
        u"A dictionary that maps category key to a list of "
        u"category value identifier strings. "
        u"Example: {'departments': ['finance']}. "
        u"Typical keys: 'entities', 'offices', 'departments', 'other'")

    password_reset_key = Attribute(
        u"Key for confirming password reset.  "
        u"Not for display or editing.")
    password_reset_time = Attribute(
        u"Datetime when password reset was requested.  "
        u"Not for display or editing.")

    def get_photo():
        """Gets this user's photo object, an instance of IImageFile.

        Photo is a full fledged model that is a child of the profile and is
        looked up according to a naming heuristic.

        """

    def get_alerts_preference(community_name):
        """Returns constant value representing user's alert preference for
        the given community.

        Possible values are:

        o IProfile.ALERT_IMMEDIATELY
        o IProfile.ALERT_DIGEST
        o IProfile.ALERT_NEVER

        """

    def set_alerts_preference(community_name, preference):
        """Sets user's alert preference for the given community.

        Possible values are:

        o IProfile.ALERT_IMMEDIATELY
        o IProfile.ALERT_DIGEST
        o IProfile.ALERT_NEVER

        """

IProfile.ALERT_IMMEDIATELY = 0
IProfile.ALERT_DIGEST = 1
IProfile.ALERT_NEVER = 2

class IFile(Interface):
    """ A model object which provides a file-like interface analogous to
    static resource.
    """
    stream = Attribute(u'A read-only stream for getting file contents.')
    mimetype = Attribute(u'Mime type of file')
    size = Attribute(u'Size in bytes of file')

class IImageFile(IFile):
    """ An image file.
    """
    extension = Attribute(u'File extension based on mime type')

class ICommunity(IFolder, IContent, IOthers):
    """ Community folder """
    taggedValue('name', 'Community')

    description = Attribute(u'Description -- plain text summary')
    text = Attribute(u'Text -- includes wiki markup.')
    content_modified = Attribute(
        u'datetime: last modification to any subcontent ')

class ICreatedModified(Interface):
    """ Interface indicating content that has its created and modified
    attributes managed by an event subscriber (this implies all IContent
    content at the moment). """
    modified = Attribute(u'Datetime indicating modification')
    created = Attribute(u'Datetime indicating creation')

class IToolFactory(Interface):
    """ A utility interface """
    interfaces = Attribute(
        'Sequence of interface objects that inform ``is_current``. '
        'The context must be one of these for the tool factory to be '
        'considered "current" by the UI')

    name = Attribute('The tool factory name')

    def add(context, request):
        """ Perform the work required to add a tool """

    def remove(context, request):
        """ Perform the work required to remove a tool """

    def is_present(context, request):
        """ Return true if the tool is present in the context """

    def is_current(context, request):
        """ Returns true if the tool is the ``current`` tool """

    def tab_url(context, request):
        """ Returns the tab URL for the tool """

class ITextIndexData(Interface):
    """ An adapter which returns a string representing data useable
    for text indexing"""
    def __call__():
        """ Return text data """

# XXX Arguably, this is display logic and belongs in views.
class IGridEntryInfo(Interface):
    """Adapt resources for display in a grid listing"""

    title = Attribute("")
    url = Attribute("")
    type = Attribute("")
    modified = Attribute("")
    created = Attribute("")
    creator_title = Attribute("")
    creator_url = Attribute("")

class ICommunityInfo(Interface):
    """ An adapter for obtaining information about a single community """
    name = Attribute('The name of the community')
    title = Attribute('The title of the community')
    description = Attribute('The description of the community')
    url = Attribute("Community URL")
    number_of_members = Attribute("Number of members in the community")
    last_activity_date = Attribute("Date content was last modified")

class ICatalogSearch(Interface):
    """Centralize policies about searching"""

class ITagQuery(Interface):
    """Centralize policies about listing tag information"""

    tagusers = Attribute("List the taguser information on a resource")

class IObjectWillBeModifiedEvent(IObjectEvent):
    """ An event type sent before an object is modified  """
    object = Attribute('The object that will be modified')

class IObjectModifiedEvent(IObjectEvent):
    """ An event type sent after an object is modified """
    object = Attribute('The object which was modified')

class ILetterManager(Interface):
    """ Adapter to manage community and profile letter box info """

class ICatalogSearchCache(Interface):
    """ Utility which provides a cache for catalog searches """
    generation = Attribute('The current cache generation number')
    def clear():
        """ Clears the cache """
    def get(key, default=None):
        """ Return the value for ``key`` or ``None`` if no value """
    def __setitem__(key, val):
        """ Set the key to val """

class ICatalogQueryEvent(Interface):
    """Notification that a catalog was queried"""
    catalog = Attribute('The catalog that was queried')
    query = Attribute('Keyword parameters passed in the query')
    duration = Attribute('How long the query took, in seconds')
    result = Attribute('The result of the query: (result_count, [docid])')

class IUserAdded(Interface):
    """ Event interface for having a new user added to the system.
    """
    site = Attribute('The site object')
    id = Attribute('The unique identifier for the user')
    login = Attribute('The name under which the user logs in.')
    groups = Attribute('The initial set of groups to which the user belongs.')

class IUserRemoved(Interface):
    """ Event interface for having a user removed from the system.
    """
    site = Attribute('The site object')
    id = Attribute('The unique identifier for the user')
    login = Attribute('The name under which the user logs in.')
    groups = Attribute('The set of groups to which the user belongs.')

class IUserAddedGroup(Interface):
    """ Event interface for when a user has just added a new group.
    """
    site = Attribute('The site object')
    id = Attribute('The unique identifier for the user')
    login = Attribute('The name under which the user logs in.')
    groups = Attribute('The set of groups to which the user now belongs.')
    old_groups = Attribute('The set of groups to which the user '
                           'formerly belonged.')

class IUserRemovedGroup(Interface):
    """ Event interface for when a user has just removed a group.
    """
    site = Attribute('The site object')
    id = Attribute('The unique identifier for the user')
    login = Attribute('The name under which the user logs in.')
    groups = Attribute('The set of groups to which the user now belongs.')
    old_groups = Attribute('The set of groups to which the user '
                           'formerly belonged.')

class IFeedsContainer(IFolder):
    """ Container for fetched feeds """
    taggedValue('name', 'Feeds')

class IFeed(IContent):
    taggedValue('name', 'Feed')

    title = Attribute('Title')
    subtitle = Attribute('Subtitle')
    link = Attribute('Link to source HTML page')

    etag = Attribute('Etag (bandwidth optimization)')
    feed_modified = Attribute('Last-modified date (bandwidth optimization)')

    entries = Attribute('List of contained IFeedEntry objects')

    old_uri = Attribute('Old feed URI (set if the feed moves or disappears)')
    new_uri = Attribute('New feed URI (set if the feed moves or disappears)')

    def update(parser):
        """Change the content to match a FeedParser result.
        """

class IFeedEntry(Interface):
    taggedValue('name', 'Feed Entry')

    title = Attribute('Title')
    summary = Attribute('Summary')
    link = Attribute('Link to source HTML page')
    id = Attribute('Globally unique entry identifier')
    content_html = Attribute('The content as a sanitized HTML string')
    published = Attribute('Publication date as a datetime')
    updated = Attribute('Last update as a datetime')

    def update(parser_entry):
        """Change the content to match a FeedParser entry.
        """

class IIntranets(ICommunity):
    """ Mark the top of the intranet hierarchy e.g. /osi """
    taggedValue('name', 'Intranets')
    feature = Attribute('HTML for the feature portlet')

class IIntranet(IFolder):
    """ Mark an intranet community to attach views """
    taggedValue('name', 'Intranet')

class IAttachmentPolicy(Interface):
    """Policy controlling attachments"""

    def support():
        """Return true if the given object should support attachments"""

class IPeopleDirectory(IFolder):
    """Searchable directory of profiles.

    Contains IPeopleSection objects.
    """
    title = Attribute("Directory title")
    categories = Attribute("Mapping of category ID to PeopleCategory")
    catalog = Attribute("Catalog of profiles")
    order = Attribute("Sequence of section IDs to display as tabs")

class IPeopleSection(IFolder):
    """Section of the people directory.

    Contains IPeopleReport objects.
    """
    title = Attribute("Section title")
    tab_title = Attribute("Title to put on the section tab")
    columns = Attribute("Sequence of IPeopleReportGroups")

    def set_columns(columns):
        """Set the sequence of IPeopleReportGroups for this section"""

class IPeopleReportGroup(Interface):
    """A group of reports displayed in a section"""
    title = Attribute("Report group title")
    reports = Attribute("Sequence of IPeopleReports and IPeopleReportGroups")

    def set_reports(reports):
        """Set the sequence of IPeopleReports and IPeopleReportGroups"""

class IPeopleReport(Interface):
    """A report about people"""
    title = Attribute("Report title")
    link_title = Attribute("Title to use for the link to the report")
    css_class = Attribute("CSS class of the link to the report")
    filters = Attribute("Reduces the content of the report.  "
        "Maps category ID to a list of values.")
    columns = Attribute("IDs of columns to display in the report.")

    def set_filter(catid, values):
        """Add a profile category value filter to this report."""

    def set_columns(columns):
        """Set the IDs of columns to display"""
