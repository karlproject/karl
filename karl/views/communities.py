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

from repoze.bfg.security import has_permission
from repoze.bfg.security import effective_principals
from repoze.bfg.security import authenticated_userid
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from webob.exc import HTTPFound
from zope.component import getMultiAdapter
from zope.index.text.parsetree import ParseError

from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import ICommunity
from karl.views.api import TemplateAPI
from karl.utils import coarse_datetime_repr
from karl.utils import find_communities
from karl.utils import find_profiles
from karl.utils import get_setting
from karl.views.batch import get_catalog_batch_grid


_TODAY = None
def _today():
    return _TODAY or datetime.datetime.today()

# The name of the cookie that makes the communites view sticky.
# Possible cookie values are 'mine', 'active', 'all'.
# In case of no value or unknown value, 'mine' is considered
# as default.
_VIEW_COOKIE = 'karl.communities_view'
_VIEWS = [
    ('all',
     'All',
     'All communities',
     'all_communities.html',
    ),
    ('active',
     'Active',
     'Communities with activity within the last six months',
     'active_communities.html',
    ),
]
_VIEW_URL_LOOKUP = dict([(x[0], x[3]) for x in _VIEWS])


def show_communities_view(context, request):
    default = 'all'
    which = request.cookies.get(_VIEW_COOKIE, default)
    urlname = _VIEW_URL_LOOKUP[which]
    target = model_url(context, request, urlname)
    response = HTTPFound(location=target)
    return response


def _set_cookie_via_request(request, value):
    header = ('Set-Cookie', '%s=%s; Path=/' %
                    (_VIEW_COOKIE, value))
    request.cookies[_VIEW_COOKIE] = value
    request.response_headerlist = [header]


def _show_communities_view_helper(context,
                                  request,
                                  prefix='',
                                  **kw
                                 ):
    # Grab the data for the two listings, main communities and portlet
    communities_path = model_path(context)

    query = dict(
        sort_index='title',
        interfaces=[ICommunity],
        path={'query': communities_path, 'depth': 1},
        allowed={'query': effective_principals(request), 'operator': 'or'},
        **kw
        )

    qualifiers = []
    titlestartswith = request.params.get('titlestartswith')
    if titlestartswith:
        query['titlestartswith'] = (titlestartswith, titlestartswith)
        qualifiers.append("Communities that begin with '%s'" % titlestartswith)

    body = request.params.get('body')
    if body:
        query['texts'] = body
        qualifiers.append('Search for "%s"' % body)

    error = None
    try:
        batch_info = get_catalog_batch_grid(context, request, **query)
    except ParseError, e:
        batch_info = { 'entries': [], 'batching_required': False }
        error = 'Error: %s' % e

    communities = []
    for community in batch_info['entries']:
        adapted = getMultiAdapter((community, request), ICommunityInfo)
        communities.append(adapted)

    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)

    view_cookie = request.cookies.get(_VIEW_COOKIE)
    classes = []
    for name, title, description, urlname in _VIEWS:
        classes.append({'name': name,
                        'title': title,
                        'description': description,
                        'href': urlname,
                        'selected': name == view_cookie,
                       })

    actions = []
    if has_permission('create', context, request):
        actions.append(('Add Community', 'add_community.html'))

    system_name = get_setting(context, 'system_name', 'KARL')
    page_title = '%s%s Communities' % (prefix, system_name)

    my_communities = get_my_communities(context, request)

    preferred_communities = get_preferred_communities(context, request)

    return {'communities': communities,
            'batch_info': batch_info,
            'letters': letter_info,
            'community_tabs': classes,
            'actions': actions,
            'my_communities': my_communities, 
            'preferred_communities': preferred_communities,
            'api': TemplateAPI(context, request, page_title),
            'profile': None,
            'qualifiers': qualifiers,
            'error': error,
           }


def show_all_communities_view(context, request):
    _set_cookie_via_request(request, 'all')

    return _show_communities_view_helper(context, request)


def show_active_communities_view(context, request):
    _set_cookie_via_request(request, 'active')

    six_months_ago = _today() - datetime.timedelta(days=180)
    content_modified = (coarse_datetime_repr(six_months_ago), None)

    return _show_communities_view_helper(context,
                                         request, prefix='Active ',
                                         content_modified=content_modified,
                                        )


def get_my_communities(communities_folder, request, ignore_preferred=False):
    # sorted by title
    principals = effective_principals(request)
    communities = {}

    for name, role in get_community_groups(principals):
        if name in communities:
            continue
        try:
            community = communities_folder[name]
        except KeyError:
            continue
        communities[name] = (community.title, community)

    communities = communities.values()
    communities.sort()
    communities = [ x[1] for x in communities ]
    preferred = get_preferred_communities(communities_folder, request)
    # if preferred list is empty show all instead of nothing
    if preferred == []:
        ignore_preferred = True
    my_communities = []
    for community in communities:
        adapted = getMultiAdapter((community, request), ICommunityInfo)
        if not ignore_preferred and preferred is not None \
            and adapted.title in preferred:
            my_communities.append(adapted)
        if preferred is None or ignore_preferred:
            my_communities.append(adapted)
    return my_communities


COMMUNITY_NAME_REGEX = re.compile(
    r'^group.community:(?P<name>\S+):(?P<role>\S+)$'
    )


def get_community_groups(principals):
    groups = []
    for principal in principals:
        match = COMMUNITY_NAME_REGEX.match(principal)
        if match:
            name, role = match.groups()
            groups.append((name, role))
    return groups

def set_preferred_communities(context, request, communities):
    profiles = find_profiles(context)
    userid = authenticated_userid(request)
    profile = profiles[userid]
    profile.preferred_communities = communities

def get_preferred_communities(context, request):
    profiles = find_profiles(context)
    userid = authenticated_userid(request)
    profile = profiles[userid]
    # old profiles will not have this attribute, so to be safe use getattr
    preferred_communities = getattr(profile, 'preferred_communities', None)
    return preferred_communities

def jquery_set_preferred_view(context, request):
    request.response_headerlist = [('Cache-Control',
        'max-age=0, no-cache, no-store, private, must-revalidate')]
    communities_folder = find_communities(context)
    communities = request.params.getall('preferred[]')
    set_preferred_communities(communities_folder, request, communities)
    updated_communities = get_my_communities(communities_folder, request)
    return { 'my_communities': updated_communities,
             'preferred': communities,
             'show_all': False,
             'profile': None,
             'status_message': 'Set preferred communities.'}

def jquery_clear_preferred_view(context, request):
    request.response_headerlist = [('Cache-Control',
        'max-age=0, no-cache, no-store, private, must-revalidate')]
    communities_folder = find_communities(context)
    set_preferred_communities(communities_folder, request, None)
    updated_communities = get_my_communities(communities_folder, request)
    return { 'my_communities': updated_communities,
             'preferred': None,
             'show_all': False,
             'profile': None,
             'status_message': 'Cleared preferred communities.'}

def jquery_list_preferred_view(context, request):
    request.response_headerlist = [('Cache-Control',
        'max-age=0, no-cache, no-store, private, must-revalidate')]
    communities_folder = find_communities(context)
    communities = get_my_communities(communities_folder, request)
    preferred = get_preferred_communities(communities_folder, request)
    return { 'my_communities': communities,
             'preferred': preferred,
             'show_all': False,
             'profile': None,
             'status_message': None}

def jquery_edit_preferred_view(context, request):
    request.response_headerlist = [('Cache-Control',
        'max-age=0, no-cache, no-store, private, must-revalidate')]
    communities_folder = find_communities(context)
    communities = get_my_communities(communities_folder,
                                     request,
                                     ignore_preferred=True)
    preferred = get_preferred_communities(communities_folder, request)
    return { 'my_communities': communities,
             'preferred': preferred }

def jquery_list_my_communities_view(context, request):
    request.response_headerlist = [('Cache-Control',
        'max-age=0, no-cache, no-store, private, must-revalidate')]
    communities_folder = find_communities(context)
    communities = get_my_communities(communities_folder,
                                     request,
                                     ignore_preferred=True)
    preferred = get_preferred_communities(communities_folder, request)
    return { 'my_communities': communities,
             'preferred': preferred,
             'show_all': True,
             'profile': None,
             'status_message': None}

