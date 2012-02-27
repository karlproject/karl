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
from karl.utils import find_profiles
from karl.utilities.image import thumb_url
from karl.views.api import TemplateAPI
from karl.views.utils import get_static_url


TIMEAGO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
CHATTER_THUMB_SIZE = (48, 48)


def get_context_tools(request):
    return [{'url': '#',
             'title': 'Posts',
             'selected': 'selected',
            },
            {'url': '#',
             'title': 'Following',
             'selected': False,
            },
            {'url': '#',
             'title': 'Topics',
             'selected': False,
            },
            {'url': '#',
             'title': 'Messages',
             'selected': False,
            },
            {'url': '#',
             'title': 'Discover',
             'selected': False,
            }]

def quip_info(request, *quips):
    result = []
    profiles = find_profiles(request.context)
    profile_url = resource_url(profiles, request)
    for quip in quips:
        profile = profiles.get(quip.creator)
        photo = profile.get('photo')
        if photo is not None:
            photo_url = thumb_url(photo, request, CHATTER_THUMB_SIZE)
        else:
            photo_url = get_static_url(request) + "/images/defaultUser.gif"
        timeago = str(quip.created.strftime(TIMEAGO_FORMAT))
        info = {'text': quip.text,
                'creator': quip.creator,
                'creator_url': '%s/%s' % (profile_url, quip.creator),
                'creator_image_url': photo_url,
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
    """ Return *all* recent chatter.

    Query string may include:

    - 'start':  the item index at which to begin including items.
    - 'count':  the maximun number of items to return.
    - 'before':  a string timestamp (in timeago format);  include items
                 which are older than the indicated time.
    - 'since':  a string timestamp (in timeago format);  include items
                which are newer than the indicated time.  Note that we
                return the *last* 'count' items newer than the supplied
                value.
    """
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    return {'recent': _do_slice(chatter.recent(), request),
           }


def all_chatter(context, request):
    """ HTML wrapper for 'all_chatter_json'.
    """
    info = followed_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'All Chatter')
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    info['context_tools'] = get_context_tools(request)
    return info


def followed_chatter_json(context, request):
    """ Return recent chatter by the current user, or by users followed by her.

    Query string may include:

    - 'start':  the item index at which to begin including items.
    - 'count':  the maximun number of items to return.
    - 'before':  a string timestamp (in timeago format);  include items
                 which are older than the indicated time.
    - 'since':  a string timestamp (in timeago format);  include items
                which are newer than the indicated time.  Note that we
                return the *last* 'count' items newer than the supplied
                value.
    """
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    return {'recent': _do_slice(chatter.recentFollowed(userid), request),
           }


def followed_chatter(context, request):
    """ HTML wrapper for 'followed_chatter_json'.
    """
    info = followed_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'Recent Chatter')
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    info['context_tools'] = get_context_tools(request)
    return info


def creators_chatter_json(context, request):
    """ Return recent chatter by any of the named users.

    Query string must include:

    - 'creators':  a sequence of userid's (may be a comma-separated string).

    Query string may include:

    - 'start':  the item index at which to begin including items.
    - 'count':  the maximun number of items to return.
    - 'before':  a string timestamp (in timeago format);  include items
                 which are older than the indicated time.
    - 'since':  a string timestamp (in timeago format);  include items
                which are newer than the indicated time.  Note that we
                return the *last* 'count' items newer than the supplied
                value.
    """
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
    """ HTML wrapper for 'creators_chatter_json'.
    """
    try:
        info = creators_chatter_json(context, request)
    except KeyError:
        return HTTPFound(location=resource_url(context, request))
    info['api'] = TemplateAPI(context, request, 'Chatter: %s' %
                        ', '.join(['@%s' % x for x in info['creators']]))
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    info['context_tools'] = get_context_tools(request)
    return info


def names_chatter_json(context, request):
    """ Return recent chatter mentioning any of the named users.

    Query string must include:

    - 'names':  a sequence of userid's (may be a comma-separated string).

    Query string may include:

    - 'start':  the item index at which to begin including items.
    - 'count':  the maximun number of items to return.
    - 'before':  a string timestamp (in timeago format);  include items
                 which are older than the indicated time.
    - 'since':  a string timestamp (in timeago format);  include items
                which are newer than the indicated time.  Note that we
                return the *last* 'count' items newer than the supplied
                value.
    """
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
    """ HTML wrapper for 'names_chatter_json'.
    """
    try:
        info = names_chatter_json(context, request)
    except KeyError:
        return HTTPFound(location=resource_url(context, request))
    info['api'] = TemplateAPI(context, request, 'Chatter: %s' %
                        ', '.join(['@%s' % x for x in info['names']]))
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    info['context_tools'] = get_context_tools(request)
    return info


def tag_chatter_json(context, request):
    """ Return recent chatter mentioning a given tag.

    Query string must include:

    - 'tag':  a tag name.

    Query string may include:

    - 'start':  the item index at which to begin including items.
    - 'count':  the maximun number of items to return.
    - 'before':  a string timestamp (in timeago format);  include items
                 which are older than the indicated time.
    - 'since':  a string timestamp (in timeago format);  include items
                which are newer than the indicated time.  Note that we
                return the *last* 'count' items newer than the supplied
                value.
    """
    tag = request.GET['tag']
    chatter = find_chatter(context)
    return {'recent': _do_slice(chatter.recentWithTag(tag), request),
            'tag': tag,
           }


def tag_chatter(context, request):
    """ HTML wrapper for 'tag_chatter_json'.
    """
    try:
        info = tag_chatter_json(context, request)
    except KeyError:
        return HTTPFound(location=resource_url(context, request))
    info['api'] = TemplateAPI(context, request, 'Chatter: #%s' % info['tag'])
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    info['context_tools'] = get_context_tools(request)
    return info


def community_chatter_json(context, request):
    """ Return recent chatter mentioning a given community.

    Query string must include:

    - 'community':  a community name.

    Query string may include:

    - 'start':  the item index at which to begin including items.
    - 'count':  the maximun number of items to return.
    - 'before':  a string timestamp (in timeago format);  include items
                 which are older than the indicated time.
    - 'since':  a string timestamp (in timeago format);  include items
                which are newer than the indicated time.  Note that we
                return the *last* 'count' items newer than the supplied
                value.
    """
    community = context.__name__
    chatter = find_chatter(context)
    return {'community': community,
            'recent': _do_slice(
                            chatter.recentWithCommunity(community), request),
           }


def community_chatter(context, request):
    """ HTML wrapper for 'community_chatter_json'.
    """
    info = community_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request,
                              'Chatter: &%s' % info['community'])
    info['chatter_form_url'] = resource_url(find_chatter(context), request,
                                            'add_chatter.html')
    return info


def update_followed(context, request):
    """ View / update the list of users followed by the current user.

    If posted, the form data must include the following:

    - 'followed': a newline-separated list of userids.
    """
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
    """ Add a new quip to the chatterbox.

    The form data must include the following:

    - 'text': the text of the quip (XXX 140 character max)

    The form data may include the following:

    - 'private':  if non-empty, the quip will have an ACL which allows
                  viewing only by the creator, any names mentioned in the
                  text (via '@name'), or members of any communities mentioned
                  in the text (via '&community').
    """
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
