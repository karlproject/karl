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

from karl.models.catalog import CachingCatalog
from karl.models.interfaces import IPeopleCategory
from karl.models.interfaces import IPeopleCategoryItem
from karl.models.interfaces import IPeopleDirectory
from karl.models.interfaces import IPeopleDirectorySchemaChanged
from karl.models.interfaces import IPeopleReport
from karl.models.interfaces import IPeopleReportGroup
from karl.models.interfaces import IPeopleSection
from karl.models.interfaces import IProfile
from karl.models.site import get_acl
from karl.models.site import get_allowed_to_view
from karl.models.site import get_lastfirst
from karl.models.site import get_path
from karl.models.site import get_textrepr
from karl.utils import find_profiles
from karl.utils import find_users
from persistent import Persistent
from persistent.mapping import PersistentMapping
from repoze.bfg.traversal import model_path
from repoze.catalog.document import DocumentMap
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
from repoze.catalog.indexes.path2 import CatalogPathIndex2
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.folder import Folder
from zope.interface import implements


def get_lastname_firstletter(obj, default):
    if not IProfile.providedBy(obj):
        return default
    return obj.lastname[:1].upper()


class ProfileCategoryGetter:
    """Gets category values from profiles, for indexing.

    Limited to a particular category key.
    """

    def __init__(self, catid):
        self.catid = catid

    def __call__(self, obj, default):
        if not IProfile.providedBy(obj):
            return default
        categories = getattr(obj, 'categories', None)
        if not categories:
            return default
        values = categories.get(self.catid)
        if not values:
            return default
        return values


def get_department(obj, default):
    res = getattr(obj, 'department', None)
    if res is None:
        return default
    return res.lower()

def get_email(obj, default):
    res = getattr(obj, 'email', None)
    if res is None:
        return default
    return res.lower()

def get_location(obj, default):
    res = getattr(obj, 'location', None)
    if res is None:
        return default
    return res.lower()

def get_organization(obj, default):
    res = getattr(obj, 'organization', None)
    if res is None:
        return default
    return res.lower()

def get_phone(obj, default):
    phone = getattr(obj, 'phone', None)
    if phone is None:
        return default
    ext = getattr(obj, 'extension', None)
    if ext:
        return '%s x %s' % (phone, ext)
    else:
        return phone

def get_position(obj, default):
    res = getattr(obj, 'position', None)
    if res is None:
        return default
    return res.lower()

def get_groups(obj, default):
    if not IProfile.providedBy(obj):
        return default
    users = find_users(obj)
    user = users.get_by_id(obj.__name__)
    if user:
        return user.get('groups', default)
    return default

def is_staff(obj, default):
    groups = get_groups(obj, default)
    if groups is default:
        return default
    if groups and 'group.KarlStaff' in groups:
        return True
    else:
        return False

class PeopleDirectory(Folder):
    implements(IPeopleDirectory)
    title = 'People'

    def __init__(self):
        super(PeopleDirectory, self).__init__()
        self.categories = PersistentMapping()  # {id: PeopleCategory}
        self.categories.__parent__ = self
        self.catalog = CachingCatalog()
        self.catalog.document_map = DocumentMap()
        self.update_indexes()
        self.order = ()  # order of sections

        # Set up a default configuration
        self['all'] = section = PeopleSection('All')
        section['all'] = report = PeopleReport('All')
        report.set_columns(['name', 'organization', 'location', 'email'])
        self.set_order(['all'])

    def set_order(self, order):
        self.order = tuple(order)

    def update_indexes(self):
        indexes = {
            'lastfirst': CatalogFieldIndex(get_lastfirst),
            'lastnamestartswith': CatalogFieldIndex(get_lastname_firstletter),
            'texts': CatalogTextIndex(get_textrepr),
            # path index is needed for profile deletion
            'path': CatalogPathIndex2(get_path, attr_discriminator=get_acl),
            'allowed': CatalogKeywordIndex(get_allowed_to_view),
            'is_staff': CatalogFieldIndex(is_staff),
            'groups': CatalogKeywordIndex(get_groups),

            # provide indexes for sorting reports
            'department': CatalogFieldIndex(get_department),
            'email': CatalogFieldIndex(get_email),
            'location': CatalogFieldIndex(get_location),
            'organization': CatalogFieldIndex(get_organization),
            'phone': CatalogFieldIndex(get_phone),
            'position': CatalogFieldIndex(get_position),
            }

        # provide indexes for filtering reports
        for catid in self.categories.keys():
            getter = ProfileCategoryGetter(catid)
            indexes['category_%s' % catid] = CatalogKeywordIndex(getter)

        catalog = self.catalog
        need_reindex = False

        # add indexes
        for name, index in indexes.items():
            if name not in catalog:
                catalog[name] = index
                need_reindex = True

        # remove indexes
        for name in catalog.keys():
            if name not in indexes:
                del catalog[name]

        return need_reindex


class PeopleCategory(PersistentMapping):
    implements(IPeopleCategory)

    def __init__(self, title):
        super(PeopleCategory, self).__init__()
        self.title = title

class PeopleCategoryItem(Persistent):
    implements(IPeopleCategoryItem)

    def __init__(self, title, description=u''):
        self.title = title
        self.description = description  # HTML blob

class PeopleSection(Folder):
    implements(IPeopleSection)

    def __init__(self, title, tab_title=None):
        super(PeopleSection, self).__init__()
        self.title = title
        if tab_title is None:
            tab_title = title
        self.tab_title = tab_title
        self.columns = ()  # a sequence of PeopleSectionColumns

    def set_columns(self, columns):
        self.columns = tuple(columns)

class PeopleReportGroup(Persistent):
    implements(IPeopleReportGroup)

    def __init__(self, title):
        self.title = title
        self.reports = ()  # a sequence of PeopleReports and PeopleReportGroups

    def set_reports(self, reports):
        self.reports = tuple(reports)

class PeopleSectionColumn(PeopleReportGroup):
    implements(IPeopleSection)

    def __init__(self):
        # a report group with an empty title
        super(PeopleSectionColumn, self).__init__('')

class PeopleReport(Persistent):
    implements(IPeopleReport)

    def __init__(self, title, link_title=None, css_class=''):
        self.title = title
        if link_title is None:
            link_title = title
        self.link_title = link_title
        self.css_class = css_class
        self.query = None  # a dictionary of catalog query params
        self.filters = PersistentMapping()  # {category ID -> [value]}
        self.columns = ()  # column IDs

    def set_query(self, query):
        self.query = query

    def set_filter(self, catid, values):
        self.filters[catid] = tuple(values)

    def set_columns(self, columns):
        self.columns = tuple(columns)

class PeopleDirectorySchemaChanged(object):
    implements(IPeopleDirectorySchemaChanged)

    def __init__(self, peopledir):
        self.peopledir = peopledir


def reindex_peopledirectory(peopledir):
    catalog = peopledir.catalog
    document_map = catalog.document_map
    profiles = find_profiles(peopledir)
    for obj in profiles.values():
        if IProfile.providedBy(obj):
            path = model_path(obj)
            docid = document_map.docid_for_address(path)
            if not docid:
                docid = document_map.add(path)
                catalog.index_doc(docid, obj)
            else:
                catalog.reindex_doc(docid, obj)

