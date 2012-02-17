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
"""Chatter views
"""
import itertools

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.url import resource_url

from karl.utils import find_chatter
from karl.views.api import TemplateAPI


def recent_chatter(context, request):
    api = TemplateAPI(context, request, 'Recent Chatter')
    chatter = find_chatter(context)
    def qurl(quip):
        return resource_url(quip, request)
    return {'api': api,
            'recent': itertools.islice(chatter.recent(), 20),
            'qurl': qurl,
           }


def tag_chatter(context, request):
    if not request.subpath:
        return HTTPFound(location=resource_url(context, request))
    tag = request.subpath[0]
    chatter = find_chatter(context)
    api = TemplateAPI(context, request, 'Chatter: #%s' % tag)
    def qurl(quip):
        return resource_url(quip, request)
    return {'api': api,
            'recent': itertools.islice(chatter.recentWithTag(tag), 20),
            'qurl': qurl,
           }


def community_chatter(context, request):
    community = context.__name__
    chatter = find_chatter(context)
    api = TemplateAPI(context, request, 'Chatter: &%s' % community)
    def qurl(quip):
        return resource_url(quip, request)
    return {'api': api,
            'recent': itertools.islice(
                        chatter.recentWithCommunity(community), 20),
            'qurl': qurl,
           }


def add_chatter(context, request):
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    chatter.addQuip(request.POST['text'], userid)
    location = resource_url(context, request)
    return HTTPFound(location=location)
