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

import datetime

from zope.interface import implements
from zope.interface import providedBy
from zope.interface.declarations import Declaration
from zope.component import queryAdapter
from zope.event import notify

from persistent.mapping import PersistentMapping

from repoze.bfg.interfaces import ILocation
from repoze.bfg.security import Allow
from repoze.bfg.security import Authenticated
from repoze.bfg.security import principals_allowed_by_permission
from repoze.bfg.traversal import model_path
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
from repoze.catalog.indexes.path2 import CatalogPathIndex2
from repoze.catalog.document import DocumentMap
from repoze.folder import Folder
from repoze.lemonade.content import create_content
from repoze.lemonade.content import IContent
from repoze.session.manager import SessionDataManager
from repoze.who.plugins.zodb.users import Users

from karl.content.interfaces import ICalendarCategory
from karl.content.interfaces import ICalendarLayer
from karl.models.catalog import CachingCatalog
from karl.models.interfaces import ICommunities
from karl.models.interfaces import ISite
from karl.models.interfaces import IPeopleDirectory
from karl.models.interfaces import IProfile
from karl.models.interfaces import IProfiles
from karl.models.interfaces import ITextIndexData
from karl.models.interfaces import IVirtualData
from karl.models.interfaces import IUserAdded
from karl.models.interfaces import IUserAddedGroup
from karl.models.interfaces import IUserRemoved
from karl.models.interfaces import IUserRemovedGroup
from karl.tagging import Tags
from karl.tagging.index import TagIndex
from karl.utils import coarse_datetime_repr

class UserEvent(object):
    def __init__(self, site, id, login, groups, old_groups=None):
        self.site = site
        self.id = id
        self.login = login
        self.groups = groups
        self.old_groups = old_groups

class UserAddedEvent(UserEvent):
    implements(IUserAdded)

class UserRemovedEvent(UserEvent):
    implements(IUserRemoved)

class UserAddedGroupEvent(UserEvent):
    implements(IUserAddedGroup)

class UserRemovedGroupEvent(UserEvent):
    implements(IUserRemovedGroup)

class KARLUsers(Users):

    def __init__(self, site):
        super(KARLUsers, self).__init__()
        self.site = site

    def add(self, id, login, password, groups=None, encrypted=False):
        super(KARLUsers, self).add(id, login, password, groups,
                                   encrypted=encrypted)
        notify(UserAddedEvent(self.site, id, login, groups))

    def remove(self, id):
        info = self.byid[id] # XXX should be self.data
        super(KARLUsers, self).remove(id)
        notify(UserRemovedEvent(self.site, id, info['login'], info['groups']))

    def add_group(self, id, group):
        info = self.byid[id] # XXX should be self.data
        before = set(info['groups'])
        super(KARLUsers, self).add_group(id, group)
        after = set(info['groups'])
        if before != after:
            notify(UserAddedGroupEvent(self.site, id, info['login'],
                                       after, before))

    def remove_group(self, id, group):
        info = self.byid[id] # should be self.data
        before = set(info['groups'])
        super(KARLUsers, self).remove_group(id, group)
        after = set(info['groups'])
        if before != after:
            notify(UserRemovedGroupEvent(self.site, id, info['login'],
                                         after, before))


def get_acl(object, default):
    return getattr(object, '__acl__', default)

def get_title(object, default):
    title = getattr(object, 'title', '')
    if isinstance(title, basestring):
        # lowercase for alphabetic sorting
        title = title.lower()
    return title

def get_name(object, default):
    return getattr(object, '__name__', default)

def get_title_firstletter(object, default):
    title = get_title(object, default)
    if title:
        try:
            title = title[0]
        except TypeError:
            return default
        try:
            return title.upper()
        except AttributeError:
            return default
    return default

def get_interfaces(object, default):
    # we unwind all derived and immediate interfaces using spec.flattened()
    # (providedBy would just give us the immediate interfaces)
    provided_by = list(providedBy(object))
    spec = Declaration(provided_by)
    ifaces = list(spec.flattened())
    return ifaces

def get_path(object, default):
    return model_path(object)

def get_textrepr(object, default):
    adapter = queryAdapter(object, ITextIndexData)
    if adapter is not None:
        text = adapter()
        return text
    elif (IContent.providedBy(object) and
          not (ICalendarLayer.providedBy(object) or
               ICalendarCategory.providedBy(object))):
        fmt = "%s %s"
        tr = fmt % (
            getattr(object, 'title', ''),
            getattr(object, 'description', ''),
            )
        return tr
    return default

def _get_date_or_datetime(object, attr, default):
    d = getattr(object, attr, None)
    if (isinstance(d, datetime.datetime) or
        isinstance(d, datetime.date)):
        return coarse_datetime_repr(d)
    return default

def get_creation_date(object, default):
    return _get_date_or_datetime(object, 'created', default)

def get_modified_date(object, default):
    return _get_date_or_datetime(object, 'modified', default)

def get_start_date(object, default):
    # For monthly browsing of calendar events
    return _get_date_or_datetime(object, 'startDate', default)

def get_end_date(object, default):
    # For monthly browsing of calendar events
    return _get_date_or_datetime(object, 'endDate', default)

def get_publication_date(object, default):
    return _get_date_or_datetime(object, 'publication_date', default)

def get_mimetype(object, default):
    mimetype = getattr(object, 'mimetype', None)
    if mimetype is None:
        return default
    return mimetype

def get_creator(object, default):
    creator = getattr(object, 'creator', None)
    if creator is None:
        return default
    return creator

def get_email(object, default):
    email = getattr(object, 'email', None)
    if email is None:
        return default
    return email.lower()

def get_allowed_to_view(object, default):
    return principals_allowed_by_permission(object, 'view')

def get_lastfirst(object, default):
    if not IProfile.providedBy(object):
        return default
    return ('%s, %s' % (object.lastname, object.firstname)).lower()

def get_member_name(object, default):
    if not IProfile.providedBy(object):
        return default
    return ('%s %s' % (object.firstname, object.lastname)).lower()

def get_virtual(object, default):
    adapter = queryAdapter(object, IVirtualData)
    if adapter is not None:
        return adapter()
    return default

class Site(Folder):
    implements(ISite, ILocation)
    __name__ = None
    __parent__ = None
    __acl__ = [(Allow, Authenticated, 'view')]
    title = 'Site'

    def __init__(self):
        super(Site, self).__init__()
        self.catalog = CachingCatalog()
        self.update_indexes()
        self.catalog.document_map = DocumentMap()

        profiles = create_content(IProfiles)
        self['profiles'] = profiles
        communities = create_content(ICommunities)
        self['communities'] = communities
        people = create_content(IPeopleDirectory)
        self['people'] = people
        self.users = KARLUsers(self)
        self.tags = Tags(self)
        self.sessions = SessionDataManager(3600, 5)
        self.filestore = PersistentMapping()

    def update_indexes(self):
        indexes = {
            'name': CatalogFieldIndex(get_name),
            'title': CatalogFieldIndex(get_title), # used as sort index
            'titlestartswith': CatalogFieldIndex(get_title_firstletter),
            'interfaces': CatalogKeywordIndex(get_interfaces),
            'texts': CatalogTextIndex(get_textrepr),
            'path': CatalogPathIndex2(get_path, attr_discriminator=get_acl),
            'allowed':CatalogKeywordIndex(get_allowed_to_view),
            'creation_date': CatalogFieldIndex(get_creation_date),
            'modified_date': CatalogFieldIndex(get_modified_date),
            'start_date': CatalogFieldIndex(get_start_date),
            'end_date': CatalogFieldIndex(get_end_date),
            'publication_date': CatalogFieldIndex(get_publication_date),
            'mimetype': CatalogFieldIndex(get_mimetype),
            'creator': CatalogFieldIndex(get_creator),
            'email': CatalogFieldIndex(get_email),
            'tags': TagIndex(self),
            'lastfirst': CatalogFieldIndex(get_lastfirst),
            'member_name': CatalogTextIndex(get_member_name),
            'virtual':CatalogFieldIndex(get_virtual),
            }

        catalog = self.catalog

        # add indexes
        for name, index in indexes.iteritems():
            if name not in catalog:
                catalog[name] = index

        # remove indexes
        for name in catalog.keys():
            if name not in indexes:
                del catalog[name]
