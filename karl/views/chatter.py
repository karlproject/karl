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
import datetime
import itertools

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.security import Allow
from pyramid.security import DENY_ALL
from pyramid.url import resource_url

from karl.utils import find_chatter
from karl.views.api import TemplateAPI


TIMEAGO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def quip_info(request, *quips):
    result = []
    for quip in quips:
        timeago = str(quip.created.strftime(TIMEAGO_FORMAT))
        info = {'text': quip.text,
                'creator': quip.creator,
                'timeago': timeago,
                'names': list(quip.names),
                'communities': list(quip.communities),
                'tags': list(quip.tags),
                'url': resource_url(quip, request),
               }
        result.append(info)
    return result

def _lastn(iterable, count):
    buffer = []
    for item in iterable:
        buffer.append(item)
        while len(buffer) > count:
            buffer.pop(0)
    return buffer

def _do_slice(iterable, request):
    orig = iterable #XXX
    start = request.GET.get('start', 0)
    count = request.GET.get('count', 20)
    since = request.GET.get('since')
    before = request.GET.get('before')
    def _check(x):
        return has_permission('view', x, request)
    iterable = itertools.ifilter(_check, iterable)
    if since is not None:
        since_dt = datetime.datetime.strptime(since, TIMEAGO_FORMAT)
        iterable = itertools.takewhile(lambda x: x.created > since_dt, iterable)
        iterable = _lastn(iterable, count)
    elif before is not None:
        before_dt = datetime.datetime.strptime(before, TIMEAGO_FORMAT)
        iterable = itertools.dropwhile(lambda x: x.created >= before_dt,
                                       iterable)
        iterable = itertools.islice(iterable, count)
    else:
        iterable = itertools.islice(iterable, start, start + count)
    return quip_info(request, *list(iterable))


def all_chatter_json(context, request):
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    return {'recent': _do_slice(chatter.recent(), request),
           }


def all_chatter(context, request):
    info = followed_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'All Chatter')
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    return info


def followed_chatter_json(context, request):
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    return {'recent': _do_slice(chatter.recentFollowed(userid), request),
           }


def followed_chatter(context, request):
    info = followed_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'Recent Chatter')
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    return info


def creators_chatter_json(context, request):
    creators = request.GET['creators']
    if isinstance(creators, basestring):
        creators = creators.split(',')
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
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    return info


def names_chatter_json(context, request):
    names = request.GET['names']
    if isinstance(names, basestring):
        names = names.split(',')
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
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
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
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
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
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    return info


def update_followed(context, request):
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    followed = request.POST.get('followed')
    if followed is not None:
        followed = filter(None, followed.splitlines())
        chatter.setFollowed(userid, followed)
        location = resource_url(context, request)
        return HTTPFound(location=location)
    return {'api':  TemplateAPI(context, request, 'Followed by: %s' % userid),
            'followed': '\n'.join(chatter.listFollowed(userid)),
            'view_url': resource_url(context, request, request.view_name),
           }


def add_chatter(context, request):
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    name = chatter.addQuip(request.POST['text'], userid)
    if request.POST.get('private'):
        quip = chatter[name]
        acl = quip.__acl__ = [(Allow, 'view', userid)]
        for name in quip.names:
            acl.append((Allow, 'view', name))
        for community in quip.communities:
            group = 'group.community:%s:members' % community
            acl.append((Allow, 'view', group))
        acl.append(DENY_ALL)
    location = resource_url(context, request)
    return HTTPFound(location=location)
