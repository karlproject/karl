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

import random

from BTrees import IOBTree
from BTrees import OOBTree
from persistent import Persistent
from zope.component import queryAdapter
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from repoze.bfg.traversal import find_model

from karl.utils import find_catalog
from karl.utils import find_community
from karl.tagging.interfaces import ITag
from karl.tagging.interfaces import ITagCommunityFinder
from karl.tagging.interfaces import ITaggingEngine
from karl.tagging.interfaces import ITaggingStatistics


class Tag(Persistent):
    """ Simple implementation of a tag.
    """
    implements(ITag)

    item = FieldProperty(ITag['item'])
    user = FieldProperty(ITag['user'])
    name = FieldProperty(ITag['name'])
    community = FieldProperty(ITag['community'])

    def __init__(self, item, user, name, community=None):
        self.item = item
        if not isinstance(user, unicode):
            user = unicode(user, 'utf-8')
        if not isinstance(name, unicode):
            name = unicode(name, 'utf-8')
        self.user = user
        self.name = name
        if community and not isinstance(community, unicode):
            community = unicode(community, 'utf-8')
        self.community = community

    def __cmp__(self, other):
        return cmp((self.item, self.user, self.name, self.community),
                   (other.item, other.user, other.name, other.community))

    def __hash__(self):
        return (hash(self.item) +
                hash(self.user) +
                hash(self.name) +
                hash(self.community))

    def __repr__(self):
        return '<%s %r for %i by %r, community %r>' %(
            self.__class__.__name__,
            self.name,
            self.item,
            self.user,
            self.community)

class Tags(Persistent):
    implements(ITaggingEngine, ITaggingStatistics)

    _v_nextid = None

    def __init__(self, site):
        self.site = site # need a backref
        self._reset()

    # ITaggingStatistics attributes
    def __len__(self):
        return len(self._tagid_to_obj)

    @property
    def tagCount(self):
        return len(self._name_to_tagids)

    @property
    def itemCount(self):
        return len(self._item_to_tagids)

    @property
    def userCount(self):
        return len(self._user_to_tagids)

    # ITaggingEngine methods.
    def getTagsWithPrefix(self, prefix):
        """ See ITaggingEngine.
        """
        for key in self._name_to_tagids.keys(min=prefix):
            if key.startswith(prefix):
                yield key
            else:
                raise StopIteration

    def getTags(self, items=None, users=None, community=None):
        """ See ITaggingEngine.
        """
        if items is None and users is None and community is None:
            # shortcut
            return set(self._name_to_tagids.keys())

        result = self.getTagObjects(items, users, community=community)
        return set([tag.name for tag in result])

    def getTagObjects(self, items=None, users=None, tags=None, community=None):
        """ See ITaggingEngine.
        """
        ids = self._getTagIds(items, users, tags, community)
        return set([self._tagid_to_obj[id] for id in ids])

    def getCloud(self, items=None, users=None, community=None):
        """ See ITaggingEngine.
        """
        if isinstance(items, int):
            items = [items]
        if isinstance(users, basestring):
            users = [users]

        tags = self.getTagObjects(items=items, users=users,
                                  community=community)
        d = {}
        for tag in tags:
            if d.has_key(tag.name):
                d[tag.name] += 1
            else:
                d[tag.name] = 1
        return set(d.items())

    def getItems(self, tags=None, users=None, community=None):
        """ See ITaggingEngine.
        """
        uids = self._getTagIds(items=None, users=users, tags=tags,
                               community=community)
        res = set()
        for uid in uids:
            o = self._tagid_to_obj.get(uid)
            if o is not None:
                res.add(o.item)
        return res

    def getUsers(self, tags=None, items=None, community=None):
        """ See ITaggingEngine.
        """
        ids = self._getTagIds(items=items, users=None, tags=tags,
                              community=community)
        return set([self._tagid_to_obj[id].user for id in ids])

    def getRelatedTags(self, tag, degree=1, community=None, user=None):
        """ See ITaggingEngine.
        """
        result = set()
        degree_counter = 1
        previous_degree_tags = set([tag])
        degree_tags = set()
        while degree_counter <= degree:
            for cur_name in previous_degree_tags:
                tagids = self._name_to_tagids.get(cur_name, ())
                for tagid in tagids:
                    tag_obj = self._tagid_to_obj[tagid]
                    if community and tag_obj.community != community:
                        continue
                    if user and tag_obj.user != user:
                        continue
                    degree_tags.update(self.getTags(
                                                items=(tag_obj.item,),
                                                users=(tag_obj.user,),
                                                community=community,
                                                ))
            # After all the related tags of this degree were found, update the
            # result set and clean up the variables for the next round.
            result.update(degree_tags)
            previous_degree_tags = degree_tags
            degree_tags = set()
            degree_counter += 1
        # Make sure the original is not included
        if tag in result:
            result.remove(tag)
        return result

    def getRelatedItems(self, item, community=None, user=None):
        """ See ITaggingEngine.
        """
        if user is None:
            tags = self.getTags([item], community=community)
            items = self.getItems(tags, community=community)
        else:
            tags = self.getTags([item], community=community, users=(user,))
            items = self.getItems(tags, community=community, users=(user,))
        if item in items:
            items.remove(item)
        result = []
        for otherItem in items:
            otherTags = self.getTags([otherItem], community=community)
            result.append((otherItem, len(tags.intersection(otherTags))))
        return sorted(result, key=lambda i: i[1], reverse=True)

    def getRelatedUsers(self, user, community=None):
        """ See ITaggingEngine.
        """
        tags = self.getTags(users=[user], community=community)
        users = self.getUsers(tags, community=community)
        if user in users:
            users.remove(user)
        result = []
        for otherUser in users:
            otherTags = self.getTags(users=[otherUser], community=community)
            result.append((otherUser, len(tags.intersection(otherTags))))
        return sorted(result, key=lambda i: i[1], reverse=True)

    def getFrequency(self, tags=None, community=None, user=None):
        """ See ITaggingEngine.
        """
        if user is not None:
            users = [user]
        else:
            users = None
        if tags is None:
            tags = self.getTags(users=users, community=community)
        result = {}
        for tag in tags:
            objects = self.getTagObjects(tags=[tag], users=users,
                                         community=community, )
            result[tag] = len(objects)
        return sorted(result.items(), key=lambda x: x[1])

    def update(self, item, user, tags):
        """ See ITaggingEngine.
        """
        c_finder = queryAdapter(self, ITagCommunityFinder)
        community = c_finder and c_finder(item) or None
        tags_item = set(self._item_to_tagids.get(item, ()))
        tags_user = set(self._user_to_tagids.get(user, ()))
        tags_tags = set()
        for t in tags:
            tags_tags.update(self._name_to_tagids.get(t, ()))
        old_tag_ids = tags_item.intersection(tags_user)
        # any tags of the same user/item that are not in tags
        old_tag_ids = old_tag_ids.difference(tags_tags)

        old_tags = set([self._tagid_to_obj[id]
                        for id in old_tag_ids])

        new_tags = set([Tag(item, user, tagName, community)
                            for tagName in tags])

        add_tags = new_tags.difference(old_tags)

        add_tag_ids = []
        for tagObj in add_tags:
            id = self._add(tagObj)
            add_tag_ids.append(id)
            ids = self._user_to_tagids.get(user)
            if ids is None:
                self._user_to_tagids[user] = IOBTree.IOSet((id,))
            else:
                ids.insert(id)

            ids = self._item_to_tagids.get(item)
            if ids is None:
                self._item_to_tagids[item] = IOBTree.IOSet((id,))
            else:
                ids.insert(id)

            ids = self._name_to_tagids.get(tagObj.name)
            if ids is None:
                self._name_to_tagids[tagObj.name] = IOBTree.IOSet((id,))
            else:
                ids.insert(id)
        del_tag_ids = old_tag_ids.difference(add_tag_ids)
        self._delTags(del_tag_ids)

    def delete(self, item=None, user=None, tag=None):
        if item is None and user is None and tag is None:
            raise ValueError('Must specify at least one criterion')
        tags = None
        if item is not None:
            tags = set(self._item_to_tagids.get(item, ()))
        if user is not None:
            user_tags = set(self._user_to_tagids.get(user, ()))
            if tags is not None:
                tags = tags.intersection(user_tags)
            else:
                tags = user_tags
        if tag is not None:
            name_tags = set(self._name_to_tagids.get(tag, ()))
            if tags is not None:
                tags = tags.intersection(name_tags)
            else:
                tags = name_tags
        self._delTags(tags)
        return len(tags)

    def rename(self, old, new):
        """ See ITaggingEngine.
        """
        if old == new:
            return 0
        if not isinstance(new, unicode):
            new = new.decode('utf-8')
        tagIds = set(self._name_to_tagids.get(old, ()))
        for tagId in tagIds:
            tagObj = self._tagid_to_obj[tagId]
            tagObj.name = new
        newTagIds = IOBTree.IOSet(self._name_to_tagids.get(new, ()))
        newTagIds.update(tagIds)
        self._name_to_tagids[new] = newTagIds
        if tagIds:
            del self._name_to_tagids[old]
        return len(tagIds)

    def normalize(self, normalizer=None):
        """ See ITaggingEngine.
        """
        if normalizer is None:
            normalizer = lambda x: x.lower()
        names = list(self._name_to_tagids.keys())
        count = 0
        for name in names:
            newName = normalizer(name)
            if newName != name:
                count += self.rename(name, newName)
        return count

    def _reset(self):
        # Map tagid to tag object
        self._tagid_to_obj = IOBTree.IOBTree()
        # Indexes
        self._user_to_tagids = OOBTree.OOBTree()
        self._item_to_tagids = IOBTree.IOBTree()
        self._name_to_tagids = OOBTree.OOBTree()

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randrange(0, 2**31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self._tagid_to_obj:
                return uid
            #self._v_nextid = None

    def _add(self, tagObj):
        uid = self._generateId()
        self._tagid_to_obj[uid] = tagObj
        return uid

    def _getTagIds(self, items=None, users=None, tags=None, community=None):
        if items is None and users is None and tags is None:
            # get them all
            result = set()
            for v in self._item_to_tagids.values():
                result.update(v)
        else:
            result = None
            for seq, bt in ((items, self._item_to_tagids),
                            (users, self._user_to_tagids),
                            (tags, self._name_to_tagids)):
                res = set()
                if seq is not None:
                    for item in seq:
                        res.update(bt.get(item, set()))
                    if result is not None:
                        result = result.intersection(res)
                    else:
                        result = res
        if community is None:
            return result
        return set([x for x in result
                        if self._tagid_to_obj[x].community == community])

    def _delTags(self, del_tag_ids):
        """deletes tags in iterable"""
        for id in del_tag_ids:
            tagObj = self._tagid_to_obj[id]
            self._user_to_tagids[tagObj.user].remove(id)
            if not len(self._user_to_tagids[tagObj.user]):
                del self._user_to_tagids[tagObj.user]

            self._item_to_tagids[tagObj.item].remove(id)
            if not len(self._item_to_tagids[tagObj.item]):
                del self._item_to_tagids[tagObj.item]

            self._name_to_tagids[tagObj.name].remove(id)
            if not len(self._name_to_tagids[tagObj.name]):
                del self._name_to_tagids[tagObj.name]
            del self._tagid_to_obj[id]


class TagCommunityFinder(object):
    implements(ITagCommunityFinder)

    def __init__(self, context):
        self.context = context

    def __call__(self, docid):
        site = self.context.site
        catalog = find_catalog(site)
        if catalog is None:
            raise ValueError('No catalog')
        path = catalog.document_map.address_for_docid(docid)
        if path is None:
            raise KeyError(docid)
        doc = find_model(site, path)
        community = find_community(doc)
        return community and community.__name__ or None
