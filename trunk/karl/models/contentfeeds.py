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

from datetime import datetime

_NOW = datetime.utcnow

from appendonly import AppendStack
from persistent import Persistent
from persistent.mapping import PersistentMapping
from repoze.bfg.security import principals_allowed_by_permission
from repoze.bfg.threadlocal import get_current_request
from repoze.bfg.traversal import find_model
from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IObjectAddedEvent
from repoze.lemonade.content import get_content_type
from zope.interface import implements

from karl.models.interfaces import IObjectModifiedEvent
from karl.models.interfaces import IPosts
from karl.models.interfaces import IComment
from karl.models.interfaces import ISiteEvents
from karl.models.interfaces import IUserAddedGroup
from karl.models.interfaces import IUserRemovedGroup
from karl.tagging.interfaces import ITagAddedEvent
from karl.utils import find_catalog
from karl.utils import find_community
from karl.utils import find_events
from karl.utils import find_site
from karl.utils import find_tags


class SiteEvents(Persistent):
    implements(ISiteEvents)

    def __init__(self):
        self._stack = AppendStack()

    def __iter__(self):
        """ See ISiteEvents.
        """
        for gen, index, mapping in self._stack:
            yield gen, index, mapping
        # TODO:  iterate archive?

    def checked(self, principals, created_by):
        """ See ISiteEvents.
        """
        if principals:
            principals = set(principals)
        for gen, index, mapping in self._stack:
            userid = mapping.get('userid', None)
            created = mapping.get('content_creator', userid)
            if created_by and created != created_by and userid != created_by:
                continue
            allowed = set(mapping.get('allowed', ()))
            if not principals or allowed & principals:
                yield gen, index, mapping
        # TODO:  iterate archive?

    def newer(self, latest_gen, latest_index, principals=None, created_by=None):
        """ See ISiteEvents.
        """
        iterable = self.checked(principals, created_by)
        for gen, index, mapping in iterable:
            if (gen, index) > (latest_gen, latest_index):
                yield gen, index, mapping
        # TODO:  iterate archive?

    def older(self, earliest_gen, earliest_index,
              principals=None, created_by=None):
        """ See ISiteEvents.
        """
        iterable = self.checked(principals, created_by)
        for gen, index, mapping in iterable:
            if (gen, index) < (earliest_gen, earliest_index):
                yield gen, index, mapping
        # TODO:  iterate archive?


    def push(self, **kw):
        """ See ISiteEvents.
        """
        self._stack.push(PersistentMapping(kw),
                        # TODO:  pruner=???
                        )

#
#   Event subscribers
#
MEMBER_PREFIX = 'group.community:'

def _getInfo(profile, content):
    community = find_community(content)
    if community is None:
        context_name = context_url = None
    else:
        context_name = community.title
        context_url = model_path(community)
    tagger = find_tags(content)
    if tagger is not None:
        cloud = list(tagger.getCloud(items=(content.docid,)))
        tag_counts = sorted(cloud, key=lambda x: x[1], reverse=True)[:3]
        tags = [x[0] for x in tag_counts]
    else:
        tags = ()
    content_type = get_content_type(content)
    desc = getattr(content, 'description', '')
    short = len(desc) > 80 and '%s...' % desc[:80] or desc
    if IPosts.providedBy(content):
        comment_count = len(content.get('comments', ()))
    else:
        comment_count = False
    content_creator = profile.__name__
    if IComment.providedBy(content):
        # my content filter needs to know if a comment was made inside my post
        content_creator = content.__parent__.__parent__.creator
    return {'content_type': content_type.getTaggedValue('name'),
            'userid': profile.__name__,
            'context_name': context_name,
            'context_url': context_url,
            'content_creator': content_creator,
            'url': model_path(content),
            'title': content.title,
            'description': desc,
            'short_description': short,
            'allowed':
                principals_allowed_by_permission(content, 'view'),
            'comment_count': comment_count,
            'tags': tags,                 #XXX
            'author': profile.title,
            'profile_url': '/profiles/%s' % profile.__name__,
            'thumbnail': '/profiles/%s/profile_thumbnail' % profile.__name__,
            'timestamp': _NOW(),
           }

def user_joined_community(event):
    if IUserAddedGroup.providedBy(event):
        delta = event.groups - event.old_groups
        joined = [x for x in delta if x.startswith(MEMBER_PREFIX)]
        events = find_events(event.site)
        if not events or not joined:
            return
        profile = event.site['profiles'][event.id]
        for group in joined:
            community_id, gtype = group[len(MEMBER_PREFIX):].split(':')
            if gtype == 'members':
                community = event.site['communities'].get(community_id)
                if community is None:
                    continue
                info = _getInfo(profile, community)
                info['flavor'] = 'joined_left'
                info['operation'] = 'joined'
                events.push(**info)


def user_left_community(event):
    if IUserRemovedGroup.providedBy(event):
        delta = event.old_groups - event.groups
        left = [x for x in delta if x.startswith(MEMBER_PREFIX)]
        events = find_events(event.site)
        if not events or not left:
            return
        profile = event.site['profiles'][event.id]
        for group in left:
            community_id, gtype = group[len(MEMBER_PREFIX):].split(':')
            if gtype == 'members':
                community = event.site['communities'].get(community_id)
                if community is None:
                    continue
                info = _getInfo(profile, community)
                info['flavor'] = 'joined_left'
                info['operation'] = 'left'
                events.push(**info)


def user_added_content(added, event):
    if IObjectAddedEvent.providedBy(event):
        events = find_events(added)
        if not events:
            return
        site = find_site(added)
        profile_id = getattr(added, 'creator', None)
        if profile_id in (None, 'None'):
            return
        profile = site['profiles'][profile_id]
        info = _getInfo(profile, added)
        if info is None:
            return
        if info['content_type'] == 'Community':
            info['flavor'] = 'added_edited_community'
        elif info['content_type'] == 'Profile':
            info['flavor'] = 'added_edited_profile'
        else:
            info['flavor'] = 'added_edited_other'
        info['operation'] = 'added'
        events.push(**info)


def user_modified_content(modified, event):
    if IObjectModifiedEvent.providedBy(event):
        events = find_events(modified)
        if not events:
            return
        site = find_site(modified)
        profile_id = getattr(modified, 'modified_by', None)
        if profile_id in (None, 'None'):
            return
        profile = site['profiles'][profile_id]
        info = _getInfo(profile, modified)
        if info is None:
            return
        if info['content_type'] == 'Community':
            info['flavor'] = 'added_edited_community'
        elif info['content_type'] == 'Profile':
            info['flavor'] = 'added_edited_profile'
        else:
            info['flavor'] = 'added_edited_other'
        info['operation'] = 'edited'
        events.push(**info)


def user_tagged_content(event):
    if ITagAddedEvent.providedBy(event):
        request = get_current_request()
        context = getattr(request, 'context', None)
        if context is None:
            return
        events = find_events(context)
        if not events:
            return
        site = find_site(context)
        catalog = find_catalog(context)
        path = catalog.document_map.address_for_docid(event.item)
        tagged = find_model(site, path)
        if tagged is None:
            return
        profile_id = event.user
        if profile_id in (None, 'None'):
            return
        profile = site['profiles'][profile_id]
        info = _getInfo(profile, tagged)
        if info is None:
            return
        if info['content_type'] == 'Community':
            info['flavor'] = 'tagged_community'
        elif info['content_type'] == 'Profile':
            info['flavor'] = 'tagged_profile'
        else:
            info['flavor'] = 'tagged_other'
        info['operation'] = 'tagged'
        info['tagname'] = event.name
        events.push(**info)
