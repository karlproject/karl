# Copyright (C) 2008-2009 Open Society Institute
# Thomas Moroz: tmoroz@sorosny.org
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

from zope.component import getUtility

from pyramid.security import effective_principals
from pyramid.traversal import model_path
from pyramid.url import model_url
from pyramid.renderers import render_to_response

from karl.content.interfaces import IForum
from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICatalogSearch
from karl.views.api import TemplateAPI
from karl.utilities.interfaces import IKarlDates
from karl.utils import find_profiles

from karl.content.views.forum import number_of_comments
from karl.content.views.forum import latest_object
from karl.content.views.forum import ShowForumsView


class OsiShowForumsView(ShowForumsView):
    _admin_actions = [
        ('Add Forum', 'add_forum.html'),
        ('All Forums', 'all_forums.html'),
    ]


def show_forums_view(context, request):
    return OsiShowForumsView(context, request)()


def all_forums_view(context, request):
    page_title = "Message Boards"
    api = TemplateAPI(context, request, page_title)

    # Don't use the forums folder as the starting point, use its
    # parent (the community) to allow recursion
    context_path = model_path(context.__parent__)

    searcher = ICatalogSearch(context)
    total, docids, resolver = searcher(
        interfaces=[ICommunity],
        path={'query': context_path, 'include_path': True},
        allowed={'query': effective_principals(request),
                 'operator': 'or'},
        sort_index='title',
    )

    community_data = []

    for docid in docids:
        community = resolver(docid)
        if community is not None:
            forum_data = get_forum_data(community, request)
            if forum_data:
                community_data.append({'title': community.title,
                                       'forum_data': forum_data})

    return render_to_response(
        'templates/all_forums.pt',
        {'api': api,
         'community_data': community_data},
        request=request
    )


def get_forum_data(community, request):
    karldates = getUtility(IKarlDates)
    searcher = ICatalogSearch(community)
    total, docids, resolver = searcher(
        interfaces=[IForum],
        path={'query': model_path(community), 'depth': 2},
        allowed={'query': effective_principals(request),
                 'operator': 'or'},
        sort_index='title',
    )

    if not total:
        return None

    forum_data = []

    profiles = find_profiles(community)
    profiles_href = model_url(profiles, request)

    for docid in docids:
        forum = resolver(docid)
        if forum is not None:
            D = {}
            D['title'] = forum.title
            D['url'] = model_url(forum, request)
            D['number_of_topics'] = len(forum)
            D['number_of_comments'] = number_of_comments(forum, request)

            latest = latest_object(forum, request)

            _NOW = datetime.datetime.now()

            if latest:
                D['latest_activity_url'] = model_url(latest, request)
                D['latest_activity_link'] = getattr(latest, 'title', None)
                creator = getattr(latest, 'creator', None)
                D['latest_activity_byhref'] = profiles_href + creator
                profile = profiles[creator]
                D['latest_activity_byname'] = profile.title
                modified = getattr(latest, 'modified_date', _NOW)
                modified_str = karldates(modified, 'longform')
                D['latest_activity_at'] = modified_str
            else:
                D['latest_activity_url'] = None
                D['latest_activity_link'] = None
                D['latest_activity_by'] = None
                D['latest_activity_at'] = None

            forum_data.append(D)

    return forum_data

