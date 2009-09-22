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

import calendar

from zope.component import queryAdapter
from zope.component import queryUtility

from repoze.bfg.interfaces import ISettings
from repoze.bfg.traversal import find_root
from repoze.bfg.traversal import find_interface
from repoze.lemonade.content import get_content_type

from karl.models.interfaces import ICommunity
from karl.models.interfaces import ISite
from karl.models.interfaces import IIntranets
from karl.models.interfaces import IIntranet
from karl.models.interfaces import IAttachmentPolicy

def find_site(context):
    site = find_interface(context, ISite)
    if site is None:
        # for unittesting convenience
        site = find_root(context)
    return site

def find_users(context):
    return getattr(find_site(context), 'users', None)

def find_catalog(context):
    return getattr(find_site(context), 'catalog', None)

def find_tags(context):
    return getattr(find_site(context), 'tags', None)

def find_profiles(context):
    return find_site(context).get('profiles')

def find_community(context):
    return find_interface(context, ICommunity)

def find_communities(context):
    return find_site(context).get('communities')

def find_intranet(context):
    # Find the ancestor that has IIntranet, e.g. /osi/someoffice
    return find_interface(context, IIntranet)

def find_intranets(context):
    # Find the community in the site with IIntranets
    site = find_site(context)
    for v in site.values():
        if IIntranets.providedBy(v):
            return v

    return []

def find_peopledirectory_catalog(context):
    site = find_site(context)
    people = site.get('people', None)
    if not people:
        return None
    return getattr(people, 'catalog', None)

def get_setting(context, setting_name, default=None):
    # Grab a setting from ISettings.  (context is ignored.)
    settings = queryUtility(ISettings)
    return getattr(settings, setting_name, default)

def get_content_type_name(resource):
    content_iface = get_content_type(resource)
    return content_iface.getTaggedValue('name')

def debugsearch(context, **kw):
    from karl.models.adapters import CatalogSearch
    searcher = CatalogSearch(context)
    kw['use_cache'] = False
    num, docids, resolver = searcher(**kw)
    L = []
    for docid in docids:
        L.append(resolver(docid))
    return num, L

def get_session(context, request):
    site = find_site(context)
    session = site.sessions.get(request.environ['repoze.browserid'])
    return session

_MAX_32BIT_INT = int((1<<31) - 1)

def docid_to_hex(docid):
    return '%08X' % (_MAX_32BIT_INT + docid)

def hex_to_docid(hex):
    return int('%s' % hex, 16) - _MAX_32BIT_INT

def coarse_datetime_repr(date):
    """Convert a datetime to an integer with 100 second granularity.

    The granularity reduces the number of index entries in the
    catalog.
    """
    timetime = calendar.timegm(date.timetuple())
    return int(timetime) // 100

def support_attachments(context):
    """Return true if the given object should support attachments"""
    adapter = queryAdapter(context, IAttachmentPolicy)
    if adapter:
        return adapter.support()
    else:
        # support attachments by default
        return True
