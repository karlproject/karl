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
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.security import Allow
from pyramid.security import DENY_ALL
from pyramid.url import resource_url

from karl.utils import find_chatter
from karl.utils import find_profiles
from karl.utils import find_users
from karl.utilities.image import thumb_url
from karl.views.api import TemplateAPI
from karl.views.communities import get_community_groups
from karl.views.utils import get_static_url


TIMEAGO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
CHATTER_THUMB_SIZE = (48, 48)


def get_context_tools(request, selected='posts'):
    chatter = find_chatter(request.context)
    chatter_url = resource_url(chatter, request)
    return [{'url': chatter_url,
             'title': 'Posts',
             'selected': selected=='posts' and 'selected',
            },
            {'url': '%sfollowing.html' % chatter_url,
             'title': 'Following',
             'selected': selected=='following' and 'selected',
            },
            {'url': '%sfollowers.html' % chatter_url,
             'title': 'Followers',
             'selected': selected=='followers' and 'selected',
            },
            {'url': '%stag.html' % chatter_url,
             'title': 'Topics',
             'selected': selected=='topics' and 'selected',
            },
            {'url': '%sdirect.html' % chatter_url,
             'title': 'Messages',
             'selected': selected=='messages' and 'selected',
            }]

def quip_info(request, *quips):
    result = []
    chatter = find_chatter(request.context)
    profiles = find_profiles(request.context)
    chatter_url = resource_url(chatter, request)
    for quip in quips:
        creator = quip.creator
        reposter = None
        if quip.repost is not None:
            creator = quip.repost
            reposter = quip.creator
        reply =  None
        if quip.reply in chatter:
            original = chatter[quip.reply]
            reply = original.creator
        profile = profiles.get(creator)
        photo = profile and profile.get('photo') or None
        if photo is not None:
            photo_url = thumb_url(photo, request, CHATTER_THUMB_SIZE)
        else:
            photo_url = get_static_url(request) + "/images/defaultUser.gif"
        timeago = str(quip.created.strftime(TIMEAGO_FORMAT))
        info = {'text': quip.text,
                'html': quip.html or quip.text,
                'creator': creator,
                'creator_url': '%screators.html?creators=%s' % (chatter_url,
                    quip.creator),
                'creator_image_url': photo_url,
                'reposter': reposter,
                'reply': reply,
                'timeago': timeago,
                'names': list(quip.names),
                'communities': list(quip.communities),
                'tags': list(quip.tags),
                'url': resource_url(quip, request),
                'private': bool(getattr(quip, '__acl__', ())),
                'quip_id': quip.__name__,
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

def _do_slice(iterable, request, check=True):
    orig = iterable #XXX
    start = request.GET.get('start', 0)
    count = request.GET.get('count', 20)
    since = request.GET.get('since')
    before = request.GET.get('before')
    def _check(x):
        return has_permission('view', x, request)
    if check:
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
    return {'recent': _do_slice(chatter.recent(), request),
           }


def all_chatter(context, request):
    """ HTML wrapper for 'all_chatter_json'.
    """
    layout = request.layout_manager.layout
    if layout is not None:
        layout.add_portlet('chatter.discover')
    info = all_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'All Chatter')
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    info['context_tools'] = get_context_tools(request, selected='discover')
    info['page_title'] = 'Chatter: Discover'
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
    layout = request.layout_manager.layout
    if layout is not None:
        layout.add_portlet('chatter.user_info')
        layout.add_portlet('chatter.show_only')
    info = followed_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'Posts')
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    info['context_tools'] = get_context_tools(request)
    info['page_title'] = 'Chatter: Posts'
    info['pushdown'] = False
    info['inline'] = False
    return info


def messages_json(context, request):
    """ Return messages for the current user.

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
    return {'messages': _do_slice(chatter.recentPrivate(userid),
                                  request, False),
           }


def messages(context, request):
    """ HTML wrapper for 'followed_chatter_json'.
    """
    layout = request.layout_manager.layout
    info = messages_json(context, request)
    info['api'] = TemplateAPI(context, request, 'Messages')
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    info['context_tools'] = get_context_tools(request, selected='messages')
    info['page_title'] = 'Chatter: Messages'
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
    creators = _quippers_from_users(context, request, creators)
    creator_list = [x['userid'] for x in creators]
    chatter = find_chatter(context)
    return {'recent': _do_slice(chatter.recentWithCreators(*creator_list), request),
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
                        ', '.join(['@%s' % x['userid'] for x in info['creators']]))
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    info['context_tools'] = get_context_tools(request)
    info['page_title'] = 'Chatter: %s' % ', '.join(['@%s' % x['userid']
                         for x in info['creators']])
    layout = request.layout_manager.layout
    if layout is not None:
        layout.add_portlet('chatter.follow_info', info['creators'])
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
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    info['context_tools'] = get_context_tools(request)
    info['page_title'] = 'Chatter: %s' % ', '.join(['@%s' % x
                         for x in info['names']])
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
    chatter = find_chatter(context)
    tag_list = chatter.recentTags()
    try:
        info = tag_chatter_json(context, request)
    except KeyError:
        info = {'recent':[], 'tag':''}
    info['api'] = TemplateAPI(context, request, 'Chatter: #%s' % info['tag'])
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    info['context_tools'] = get_context_tools(request, selected='topics')
    info['page_title'] = 'Chatter: Topics'
    layout = request.layout_manager.layout
    if layout is not None:
        layout.add_portlet('chatter.quip_tags', tag_list)
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
                            chatter.recentWithCommunities(community), request),
           }


def community_chatter(context, request):
    """ HTML wrapper for 'community_chatter_json'.
    """
    info = community_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request,
                              'Chatter: &%s' % info['community'])
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    return info


def my_communities_chatter_json(context, request):
    """ Return recent chatter mentioning current user's communities.

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
    principals = effective_principals(request)
    communities = [x[0] for x in get_community_groups(principals)]
    chatter = find_chatter(context)
    return {'communities': communities,
            'recent': _do_slice(
                      chatter.recentWithCommunities(*communities), request),
           }


def my_communities_chatter(context, request):
    """ HTML wrapper for 'my_communities_chatter_json'.
    """
    info = community_chatter_json(context, request)
    info['api'] = TemplateAPI(context, request, 'Chatter: My Communities')
    chatter_url = resource_url(find_chatter(context), request)
    info['chatter_url'] = chatter_url
    info['chatter_form_url'] = '%sadd_chatter.html' % chatter_url
    return info


def discover_community_members_json(context, request):
    """ Return users who share a community with the given user.

    Query string may include:

    - 'userid':  the user whose communities we enumerate (defaults to the
                 current user).
    """
    users = find_users(context)
    userid = request.GET.get('userid', None)
    if userid is None:
        userid = authenticated_userid(request)
        principals = effective_principals(request)
        communities = [x[0] for x in get_community_groups(principals)]
    else:
        info = users.get(userid)
        communities = [x[0] for x in get_community_groups(info['groups'])]
    c_groups = [(x, _quippers_from_users(context, request,
         users.users_in_group('group.community:%s:members' % x)))
         for x in communities]
    return {'userid': userid,
            'members': dict(c_groups),
           }


def discover_people(context, request):
    """ View the list of users that share communities with the current user.
    """
    chatter = find_chatter(context)
    share_with = discover_community_members_json(context, request)
    return {'api':  TemplateAPI(context, request,
                                'Share communities with: %s' % share_with['userid']),
            'members': share_with,
            'context_tools': get_context_tools(request, selected='discover'),
            'chatter_url': request.resource_url(chatter),
           }


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


def add_followed(context, request):
    """ Add an user to the list of users followed by the current user.

    The form data must include the following:

    - 'add': a new userid to add to the list.
    """
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    add = request.GET.get('add')
    if add is not None:
        following = list(chatter.listFollowed(userid))
        if add not in following:
            following.append(add)
            chatter.setFollowed(userid, following)
    location = "%sfollowing.html" % resource_url(context, request)
    return HTTPFound(location=location)


def remove_followed(context, request):
    """ Remove an user from the list of users followed by the current user.

    The form data must include the following:

    - 'remove': a userid to remove from the list.
    """
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    remove = request.GET.get('remove')
    if remove is not None:
        following = list(chatter.listFollowed(userid))
        if remove in following:
            following.remove(remove)
            chatter.setFollowed(userid, following)
    location = "%sfollowing.html" % resource_url(context, request)
    return HTTPFound(location=location)


def following_json(context, request):
    """ View the list of users whom a given user is following.

    Query string may include:

    - 'userid':  the user for whom to enumerate followed users.  If not passed,
                 defaults to the current user.
    """
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    profiles = find_profiles(context)
    userid = request.GET.get('userid')
    if userid is None:
        userid = authenticated_userid(request)
    user_list = chatter.listFollowed(userid)
    following = _quippers_from_users(context, request, user_list)
    return {'members': following,
            'userid': userid,
           }


def followed_by_json(context, request):
    """ View the list of users who follow a given user.

    Query string may include:

    - 'userid':  the user for whom to enumerate followers.  If not passed,
                 defaults to the current user.
    """
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    profiles = find_profiles(context)
    userid = request.GET.get('userid')
    if userid is None:
        userid = authenticated_userid(request)
    user_list = chatter.listFollowing(userid)
    followed_by = _quippers_from_users(context, request, user_list)
    return {'followed_by': followed_by,
            'userid': userid,
           }

def following(context, request):
    """ View the list of users followed by the current user.
    """
    layout = request.layout_manager.layout
    if layout is not None:
        layout.add_portlet('chatter.user_info')
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    layout = request.layout_manager.layout
    following = following_json(context, request)
    return {'api':  TemplateAPI(context, request,
                                'Followed by: %s' % following['userid']),
            'members': following,
            'context_tools': get_context_tools(request, selected='following'),
            'chatter_url': chatter_url,
            'page_title': 'Chatter: Following'
           }


def followed_by(context, request):
    """ View the list of users following the current user.
    """
    layout = request.layout_manager.layout
    if layout is not None:
        layout.add_portlet('chatter.user_info')
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    layout = request.layout_manager.layout
    followed_by = followed_by_json(context, request)
    return {'api':  TemplateAPI(context, request,
                                'Following: %s' % followed_by['userid']),
            'followed_by': followed_by,
            'context_tools': get_context_tools(request, selected='followers'),
            'chatter_url': chatter_url,
           }


def quip_view(context, request):
    """ View a single quip
    """
    return {'quip': quip_info(request, *[context])[0],
            'context_tools': get_context_tools(request, selected='posts'),
            'page_title': 'Chatter: Quip',
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

    - 'repost':   a karl user id. If non-empty, this quip will be marked as a
                  repost. When displayed, the quip will show the profile
                  picture of the original author.

    - 'reply':    a string with a quip id. If non-empty, this post will be
                  marked as a reply to the referenced quip.
    """
    chatter = find_chatter(context)
    userid = authenticated_userid(request)
    repost = request.POST.get('repost')
    reply = request.POST.get('reply')
    name = chatter.addQuip(request.POST['text'],
                           userid,
                           repost=repost,
                           reply=reply)
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

def _quippers_from_users(context, request, user_list):
    userid = authenticated_userid(request)
    chatter = find_chatter(context)
    chatter_url = resource_url(chatter, request)
    profiles = find_profiles(context)
    following = []
    for quipper in user_list:
        info = {}
        profile = profiles.get(quipper)
        photo = profile and profile.get('photo') or None
        if photo is not None:
            photo_url = thumb_url(photo, request, CHATTER_THUMB_SIZE)
        else:
            photo_url = get_static_url(request) + "/images/defaultUser.gif"
        info['image_url'] = photo_url
        info['userid'] = quipper
        info['fullname'] = profile.title
        info['url'] = '%screators.html?creators=%s' % (chatter_url, quipper)
        user_list = chatter.listFollowed(userid)
        info['followed'] = quipper in user_list
        following.append(info)
    return following
