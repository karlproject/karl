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



def quip_info(request, *quips):
    result = []
    for quip in quips:
        info = {'text': quip.text,
                'creator': quip.creator,
                'created': quip.created,
                'names': list(quip.names),
                'communities': list(quip.communities),
                'tags': list(quip.tags),
                'url': resource_url(quip, request),
               }
        result.append(info)
    return result

def _do_slice(iterable, request):
    start = request.GET.get('start', 0)
    count = request.GET.get('count', 20)
    return quip_info(request,
                     *[x for x in
                           itertools.islice(iterable, start, start + count)])

def recent_chatter_json(context, request):
    chatter = find_chatter(context)
    return {'recent': _do_slice(chatter.recent(), request),
           }


def recent_chatter(context, request):
    info = recent_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'Recent Chatter')
    return info


def creators_chatter_json(context, request):
    creators = request.GET['creators']
    if isinstance(creators, basestring):
        creators = [creators]
    else:
        creators = list(creators)
    chatter = find_chatter(context)
    return {'recent': _do_slice(chatter.recentWithCreators(*creators), request),
            'creators': creators,
           }


def creators_chatter(context, request):
    try:
        info = creators_chatter_json(context, request)
    except KeyError:
        return HTTPFound(location=resource_url(context, request))
    info['api'] = TemplateAPI(context, request, 'Chatter: %s' %
                        ', '.join(['@%s' % x for x in info['creators']]))
    return info


def names_chatter_json(context, request):
    names = request.GET['names']
    if isinstance(names, basestring):
        names = [names]
    else:
        names = list(names)
    chatter = find_chatter(context)
    return {'recent': _do_slice(chatter.recentWithNames(*names), request),
            'names': names,
           }


def names_chatter(context, request):
    try:
        info = names_chatter_json(context, request)
    except KeyError:
        return HTTPFound(location=resource_url(context, request))
    info['api'] = TemplateAPI(context, request, 'Chatter: %s' %
                        ', '.join(['@%s' % x for x in info['names']]))
    return info


def tag_chatter_json(context, request):
    tag = request.GET['tag']
    chatter = find_chatter(context)
    return {'recent': _do_slice(chatter.recentWithTag(tag), request),
            'tag': tag,
           }


def tag_chatter(context, request):
    try:
        info = tag_chatter_json(context, request)
    except KeyError:
        return HTTPFound(location=resource_url(context, request))
    info['api'] = TemplateAPI(context, request, 'Chatter: #%s' % info['tag'])
    return info


def community_chatter_json(context, request):
    community = context.__name__
    chatter = find_chatter(context)
    return {'community': community,
            'recent': _do_slice(
                            chatter.recentWithCommunity(community), request),
           }


def community_chatter(context, request):
    info = community_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request,
                              'Chatter: &%s' % info['community'])
    return info

def add_chatter(context, request):
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    chatter.addQuip(request.POST['text'], userid)
    location = resource_url(context, request)
    return HTTPFound(location=location)
