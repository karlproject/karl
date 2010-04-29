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
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from webob.exc import HTTPFound
from zope.component import getMultiAdapter

from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import ICommunity
from karl.views.api import TemplateAPI
from karl.utils import get_setting
from karl.views.batch import get_catalog_batch_grid


# The name of the cookie that makes the communites view sticky.
# Possible cookie values are 'mine', 'active', 'all'.
# In case of no value or unknown value, 'mine' is considered
# as default.
_VIEW_COOKIE = 'karl.communities_view'
_VIEWS = [
    ('mine',
     'Mine',
     'Communities where I am a member',
     'my_communities.html',
    ),
    ('active',
     'Active',
     'Communities with activity within the last 30 days',
     'active_communities.html',
    ),
    ('all',
     'All',
     'All communities',
     'all_communities.html',
    ),
]
_VIEW_URL_LOOKUP = dict([(x[0], x[3])
                                            for x in _VIEWS])


def show_communities_view(context, request):
    # XXX:  make default unconditionally 'mine' once the "new" UI rolls out.
    default = 'demo' in request.GET and 'mine' or 'all'
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
                                 test=lambda x: True,
                                ):
    # Grab the data for the two listings, main communities and portlet
    communities_path = model_path(context)

    query = dict(
        sort_index='title',
        interfaces=[ICommunity],
        path={'query': communities_path, 'depth': 1},
        allowed={'query': effective_principals(request), 'operator': 'or'},
        )

    titlestartswith = request.params.get('titlestartswith')
    if titlestartswith:
        query['titlestartswith'] = (titlestartswith, titlestartswith)

    batch_info = get_catalog_batch_grid(context, request, **query)

    communities = []
    for community in batch_info['entries']:
        adapted = getMultiAdapter((community, request), ICommunityInfo)
        if test(adapted):
            communities.append(adapted)

    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)

    view_cookie = request.cookies.get(_VIEW_COOKIE)
    classes = []
    for name, title, description, urlname in _VIEWS:
        classes.append({'name': name,
                        'title': title,
                        'description': description,
                        'urlname': urlname,
                        'current': name == view_cookie,
                       })

    actions = []
    if has_permission('create', context, request):
        actions.append(('Add Community', 'add_community.html'))

    system_name = get_setting(context, 'system_name', 'KARL')
    page_title = '%s%s Communities' % (prefix, system_name)

    return {'communities': communities,
            'batch_info': batch_info,
            'letters': letter_info,
            'subview_classes': classes,
            'actions': actions,
            'api': TemplateAPI(context, request, page_title),
           }


def show_all_communities_view(context, request):
    _set_cookie_via_request(request, 'all')

    return _show_communities_view_helper(context, request)


def show_active_communities_view(context, request):
    _set_cookie_via_request(request, 'active')

    today = datetime.datetime.today()
    thirty_days_ago = today - datetime.timedelta(30)

    def _thirty(adapted):
        return (adapted.context.content_modified is not None and
                adapted.context.content_modified >= thirty_days_ago)

    return _show_communities_view_helper(context, request,
                                         prefix='Active ', test=_thirty)


def show_my_communities_view(context, request):
    _set_cookie_via_request(request, 'mine')

    def _mine(adapted):
        return adapted.member

    return _show_communities_view_helper(context, request,
                                         prefix='My ', test=_mine)


def get_my_communities(communities_folder, request):
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
    my_communities = []
    for community in communities:
        adapted = getMultiAdapter((community, request), ICommunityInfo)
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

