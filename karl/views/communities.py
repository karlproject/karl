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

import re
from zope.component import getMultiAdapter

from repoze.bfg.security import has_permission
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path

from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch_grid
from karl.utils import get_setting

from repoze.bfg.chameleon_zpt import render_template_to_response

from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import ICommunity

def show_communities_view(context, request):
    system_name = get_setting(context, 'system_name', 'KARL')
    page_title = '%s Communities' % system_name
    actions = []

    if has_permission('create', context, request):
        actions.append(('Add Community', 'add_community.html'))
    api = TemplateAPI(context, request, page_title)

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
        communities.append(adapted)

    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)

    my_communities = get_my_communities(context, request)

    return render_template_to_response(
        'templates/communities.pt',
        api=api,
        actions=actions,
        communities=communities,
        my_communities=my_communities,
        batch_info=batch_info,
        letters=letter_info,
        )

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

community_name_regex = re.compile(
    r'^group.community:(?P<name>\S+):(?P<role>\S+)$'
    )

def get_community_groups(principals):
    groups = []
    for principal in principals:
        match = community_name_regex.match(principal)
        if match:
            name, role = match.groups()
            groups.append((name, role))
    return groups

