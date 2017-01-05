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
import re

from BTrees.OOBTree import OOBTree
from persistent.mapping import PersistentMapping
from pyramid.location import lineage
from pyramid.interfaces import ILocation
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import principals_allowed_by_permission
from pyramid.traversal import resource_path
from pyramid.threadlocal import get_current_registry
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
from zope.interface import implements
from zope.interface import providedBy
from zope.interface.declarations import Declaration
from zope.component import getUtilitiesFor
from zope.component import queryAdapter
from zope.event import notify

from karl.content.interfaces import ICalendarCategory
from karl.content.interfaces import ICalendarLayer
from karl.content.interfaces import IPhoto
from karl.content.models.adapters import FlexibleTextIndexData
from karl.models.catalog import CachingCatalog
from karl.models.catalog import GranularIndex
from karl.models.interfaces import ICommunities
from karl.models.interfaces import IIndexFactory
from karl.models.interfaces import IPeopleDirectory
from karl.models.interfaces import IProfile
from karl.models.interfaces import IProfiles
from karl.models.interfaces import ISite
from karl.models.interfaces import ITextIndexData
from karl.models.interfaces import IUserAdded
from karl.models.interfaces import IUserAddedGroup
from karl.models.interfaces import IUserRemoved
from karl.models.interfaces import IUserRemovedGroup
from karl.models.interfaces import IVirtualData
from karl.tagging import Tags
from karl.tagging.index import TagIndex
from karl.utilities.groupsearch import WeightedQuery
from karl.utils import coarse_datetime_repr
from karl.utils import find_catalog
from karl.utils import find_tags
from karl.utils import find_users

try:
    from repozitory.archive import Archive
except ImportError:
    Archive = None


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

def get_containment(object, defaults):
    ifaces = set()
    for ancestor in lineage(object):
        ifaces.update(get_interfaces(ancestor, ()))
    return ifaces

def get_path(object, default):
    return resource_path(object)

def _get_texts(object, default):
    if IPhoto.providedBy(object):
        return default

    adapter = queryAdapter(object, ITextIndexData)
    if adapter is None:
        if (not IContent.providedBy(object) or
            ICalendarLayer.providedBy(object) or
            ICalendarCategory.providedBy(object)):
            return default
        adapter = FlexibleTextIndexData(object)
    texts = adapter()
    if not texts:
        return default
    return texts

def get_textrepr(object, default):
    """ Used for standard repoze.catalog text index. """
    texts = _get_texts(object, default)
    if texts is default:
        return default
    if isinstance(texts, basestring):
        return texts
    if len(texts) == 1:
        return texts[0]
    parts = [texts[0]] * 10
    parts.extend(texts[1:])
    return ' '.join(parts)

try:
    from repoze.pgtextindex.interfaces import IWeightedText
except ImportError: #pragma NO COVERAGE
    WeightedText = None
else: #pragma NO COVERAGE
    class WeightedText(unicode):
        implements(IWeightedText)

def get_object_tags(obj):
    path = resource_path(obj)
    catalog = find_catalog(obj)
    docid = catalog.document_map.docid_for_address(path)
    tags = find_tags(obj)
    return [tag.name for tag in tags.getTagObjects(items=(docid,))]

def is_created_by_staff(obj):
    creator = getattr(obj, 'creator', None)
    if not creator:
        return False
    users = find_users(obj)
    return users.member_of_group(creator, 'group.KarlStaff')

_surrogates = re.compile(u'[\uD800-\uDFFF]')

def get_weighted_textrepr(obj, default):
    """ Used for repoze.pgtextindex. """
    texts = _get_texts(obj, default)
    if texts is default:
        return default

    if isinstance(texts, basestring):
        texts = (texts,)

    # At least one version of 'pdftotext' has given us invalid Unicode by
    # including lone characters in one of the "surrogate" character ranges.
    # These characters must normally appear in pairs in order to be valid
    # Unicode.  While zope.index.text has no problem with this, PostgreSQL
    # chokes horribly on this text.  To get around this issue we just elide
    # any characters in one of the surrogate ranges.
    texts = [_surrogates.sub('', text) for text in texts]

    if WeightedText is None:
        # Old version of repoze.pgtextindex.
        return texts

    # Give the last text the D (default) weight.
    weighted = WeightedText(texts[-1])

    # Weight C indexes the rest of the texts.
    weighted.C = '\n'.join(texts[:-1])

    # Weight B indexes the tags (voice of the people).
    tags = get_object_tags(obj)
    if tags:
        weighted.B = ' '.join(tags)

    # Weight A indexes the keywords (voice of the organization).
    keywords = getattr(obj, 'search_keywords', None)
    if keywords:
        weighted.A = ' '.join(keywords)

    # Determine the coefficient.
    weight = getattr(obj, 'search_weight', 0)
    weighted.coefficient = WeightedQuery.weight_factor ** weight
    if is_created_by_staff(obj):
        weighted.coefficient *= 25.0

    # Index a marker if one is provided by the object's interfaces.
    weighted.marker = []
    for iface in get_interfaces(obj, ()):
        marker = iface.queryTaggedValue('marker')
        if marker:
            weighted.marker.append(marker)
            break

    # Add the Intranet marker to object if it is in a predefined path
    path = resource_path(obj)
    registry = get_current_registry()
    for intranet in registry.settings.get('intranet_search_paths', ()):
        if path.startswith(intranet):
            weighted.marker.append('Intranet')
            break

    return weighted

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

def get_content_modified_date(object, default):
    return _get_date_or_datetime(object, 'content_modified', default)

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

def get_modified_by(object, default):
    userid = getattr(object, 'modified_by', None)
    if userid is None:
        return default
    return userid

def get_email(object, default):
    email = getattr(object, 'email', None)
    if email is None:
        return default
    return email.lower()

def get_allowed_to_view(object, default):
    principals = principals_allowed_by_permission(object, 'view')
    if not principals:
        # An empty value tells the catalog to match anything, whereas when
        # there are no principals with permission to view we want for there
        # to be no matches.
        principals = ['NO ONE no way NO HOW',]
    return principals

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

class RepozitoryEngineParams(object):
    @property
    def db_string(self):
        return get_current_registry().settings['repozitory_db_string']

    @property
    def kwargs(self):
        return {}


Uninitialized = object()


class Site(Folder):
    implements(ISite, ILocation)
    __name__ = ''
    __parent__ = None
    __acl__ = [(Allow, Authenticated, 'view')]
    title = 'Site'
    list_aliases = None
    _repo = Uninitialized
    _login_tries = Uninitialized

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
        self.list_aliases = OOBTree()

    @property
    def repo(self):
        if get_current_registry().settings.get('repozitory_db_string') is None:
            return None

        # Create self._repo on demand.
        repo = self._repo
        if repo is Uninitialized:
            self._repo = repo = Archive(RepozitoryEngineParams())
        return repo

    @property
    def login_tries(self):
        tries = self._login_tries
        if tries is Uninitialized:
            self._login_tries = tries = PersistentMapping()
        return tries

    def update_indexes(self):
        """ Ensure that we have indexes matching what the application needs.

        This function is called when the site is first created, and again
        whenever the ``reindex_catalog`` script is run.

        Extensions can arrange to get their own indexes added by registering
        named utilities for the
        :interface:`karl.models.interfaces.IIndexFactory` interface:  each
        such interface will be called to create a new (or overwritten) index.
        """
        indexes = {
            'name': CatalogFieldIndex(get_name),
            'title': CatalogFieldIndex(get_title), # used as sort index
            'titlestartswith': CatalogFieldIndex(get_title_firstletter),
            'interfaces': CatalogKeywordIndex(get_interfaces),
            'containment': CatalogKeywordIndex(get_containment),
            'texts': CatalogTextIndex(get_textrepr),
            'path': CatalogPathIndex2(get_path, attr_discriminator=get_acl),
            'allowed':CatalogKeywordIndex(get_allowed_to_view),
            'creation_date': GranularIndex(get_creation_date),
            'modified_date': GranularIndex(get_modified_date),
            'content_modified': GranularIndex(get_content_modified_date),
            'start_date': GranularIndex(get_start_date),
            'end_date': GranularIndex(get_end_date),
            'publication_date': GranularIndex(get_publication_date),
            'mimetype': CatalogFieldIndex(get_mimetype),
            'creator': CatalogFieldIndex(get_creator),
            'modified_by': CatalogFieldIndex(get_modified_by),
            'email': CatalogFieldIndex(get_email),
            'tags': TagIndex(self),
            'lastfirst': CatalogFieldIndex(get_lastfirst),
            'member_name': CatalogTextIndex(get_member_name),
            'virtual':CatalogFieldIndex(get_virtual),
        }

        for name, utility in getUtilitiesFor(IIndexFactory):
            indexes[name] = utility()

        catalog = self.catalog

        # add indexes
        for name, index in indexes.iteritems():
            if name not in catalog:
                catalog[name] = index

        # remove indexes
        for name in catalog.keys():
            if name not in indexes:
                del catalog[name]
