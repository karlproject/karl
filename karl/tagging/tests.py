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

import unittest

from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

_marker = object()

class TagTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.tagging import Tag
        return Tag

    def _makeOne(self, item=13, user='phred', name='test', community=_marker):
        klass = self._getTargetClass()
        if community is _marker:
            return klass(item, user, name)
        else:
            return klass(item, user, name, community)

    def test_class_conforms_to_ITag(self):
        from zope.interface.verify import verifyClass
        from karl.tagging.interfaces import ITag
        verifyClass(ITag, self._getTargetClass())

    def test_object_conforms_to_ITag(self):
        from zope.interface.verify import verifyObject
        from karl.tagging.interfaces import ITag
        verifyObject(ITag, self._makeOne())

    def test_ctor_simple(self):
        tag = self._makeOne()

        self.assertEqual(tag.item, 13)
        self.failUnless(isinstance(tag.item, int))
        self.assertEqual(tag.user, 'phred')
        self.failUnless(isinstance(tag.user, unicode))
        self.assertEqual(tag.name, 'test')
        self.failUnless(isinstance(tag.name, unicode))
        self.assertEqual(tag.community, None)

    def test_ctor_w_community(self):
        tag = self._makeOne(community='community')

        self.assertEqual(tag.item, 13)
        self.failUnless(isinstance(tag.item, int))
        self.assertEqual(tag.user, 'phred')
        self.failUnless(isinstance(tag.user, unicode))
        self.assertEqual(tag.name, 'test')
        self.failUnless(isinstance(tag.name, unicode))
        self.assertEqual(tag.community, 'community')
        self.failUnless(isinstance(tag.community, unicode))

    def test_identity_within_a_set(self):
        target = set()

        tag1 = self._makeOne()
        target.add(tag1)

        tag2 = self._makeOne()
        target.add(tag2)

        self.assertEqual(len(target), 1)
        self.failUnless(tag1 in target)
        self.failUnless(tag2 in target)
        self.failUnless(list(target)[0] is tag1)

    def test_identity_within_a_set_w_matching_communities(self):
        target = set()

        tag1 = self._makeOne(community='community')
        target.add(tag1)

        tag2 = self._makeOne(community='community')
        target.add(tag2)

        self.assertEqual(len(target), 1)
        self.failUnless(tag1 in target)
        self.failUnless(tag2 in target)
        self.failUnless(list(target)[0] is tag1)

    def test_identity_within_a_set_w_different_communities(self):
        target = set()

        tag1 = self._makeOne()
        target.add(tag1)

        tag2 = self._makeOne(community='community')
        target.add(tag2)

        self.assertEqual(len(target), 2)
        self.failUnless(tag1 in target)
        self.failUnless(tag2 in target)


class TagsTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.tagging import Tags
        return Tags

    def _makeOne(self, site=None):
        if site is None:
            site = testing.DummyModel()
        klass = self._getTargetClass()
        return klass(site)

    def _registerCommunityFinder(self, name='community'):
        from zope.interface import Interface
        from karl.tagging.interfaces import ITagCommunityFinder
        def _factory(context):
            def _callable(item):
                return name
            return _callable
        testing.registerAdapter(_factory, Interface, ITagCommunityFinder)

    def test_class_conforms_to_ITaggingEngine(self):
        from zope.interface.verify import verifyClass
        from karl.tagging.interfaces import ITaggingEngine
        verifyClass(ITaggingEngine, self._getTargetClass())

    def test_object_conforms_to_ITaggingEngine(self):
        from zope.interface.verify import verifyClass
        from karl.tagging.interfaces import ITaggingEngine
        verifyClass(ITaggingEngine, self._getTargetClass())

    def test_class_conforms_to_ITaggingStatistics(self):
        from zope.interface.verify import verifyObject
        from karl.tagging.interfaces import ITaggingStatistics
        verifyObject(ITaggingStatistics, self._makeOne())

    def test_object_conforms_to_ITaggingStatistics(self):
        from zope.interface.verify import verifyObject
        from karl.tagging.interfaces import ITaggingStatistics
        verifyObject(ITaggingStatistics, self._makeOne())

    def test_empty(self):
        engine = self._makeOne()
        self.assertEqual(len(engine), 0)
        self.assertEqual(engine.tagCount, 0)
        self.assertEqual(engine.itemCount, 0)
        self.assertEqual(engine.userCount, 0)
        self.assertEqual(len(list(engine.getTagsWithPrefix('x'))), 0)
        self.assertEqual(len(engine.getTags()), 0)
        self.assertEqual(len(engine.getTagObjects()), 0)
        self.assertEqual(len(engine.getCloud()), 0)
        self.assertEqual(len(engine.getItems()), 0)
        self.assertEqual(len(engine.getUsers()), 0)
        self.assertEqual(len(engine.getRelatedTags('nonesuch')), 0)
        self.assertEqual(len(engine.getRelatedItems(42)), 0)
        self.assertEqual(len(engine.getRelatedUsers('nonesuch')), 0)
        self.assertEqual(len(engine.getFrequency()), 0)

    def test_getTags_no_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        self.assertEqual(sorted(engine.getTags()), ['bar', 'baz', 'foo'])

    def test_getTags_w_community_match(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        tags = sorted(engine.getTags(community='community'))
        self.assertEqual(tags, ['bar', 'baz', 'foo'])

    def test_getTags_w_community_nonesuch(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        self.assertEqual(sorted(engine.getTags(community='nonesuch')), [])

    def test_getTagObjects_no_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        objects = engine.getTagObjects()
        self.assertEqual(len(objects), 5)

    def test_getTagObjects_w_community_match(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        objects = engine.getTagObjects(community='community')
        self.assertEqual(len(objects), 5)

    def test_getTagObjects_w_community_nonesuch(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        objects = engine.getTagObjects(community='nonesuch')
        self.assertEqual(len(objects), 0)

    def test_getCloud_no_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        cloud = dict(engine.getCloud())
        self.assertEqual(len(cloud), 3)
        self.assertEqual(cloud['foo'], 2)
        self.assertEqual(cloud['bar'], 2)
        self.assertEqual(cloud['baz'], 1)

    def test_getCloud_w_community_match(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        cloud = dict(engine.getCloud(community='community'))
        self.assertEqual(len(cloud), 3)
        self.assertEqual(cloud['foo'], 2)
        self.assertEqual(cloud['bar'], 2)
        self.assertEqual(cloud['baz'], 1)

    def test_getCloud_w_community_nonesuch(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        cloud = dict(engine.getCloud(community='nonesuch'))
        self.assertEqual(len(cloud), 0)

    def test_getItems_no_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        items = engine.getItems()
        self.assertEqual(len(items), 3)
        self.failUnless(13 in items)
        self.failUnless(14 in items)
        self.failUnless(15 in items)

    def test_getItems_w_community_match(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        items = engine.getItems(community='community')
        self.assertEqual(len(items), 3)
        self.failUnless(13 in items)
        self.failUnless(14 in items)
        self.failUnless(15 in items)

    def test_getItems_w_community_nonesuch(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        items = engine.getItems(community='nonesuch')
        self.assertEqual(len(items), 0)

    def test_getUsers_no_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        users = engine.getUsers()
        self.assertEqual(len(users), 2)
        self.failUnless('phred' in users)
        self.failUnless('bharney' in users)

    def test_getUsers_w_community_match(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        users = engine.getUsers(community='community')
        self.assertEqual(len(users), 2)
        self.failUnless('phred' in users)
        self.failUnless('bharney' in users)

    def test_getUsers_w_community_nonesuch(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        users = engine.getUsers(community='nonesuch')
        self.assertEqual(len(users), 0)

    def test_getRelatedTags_defaults(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedTags('bar')
        self.assertEqual(len(related), 2)
        self.failUnless('foo' in related)
        self.failUnless('baz' in related)

    #def test_getRelatedTags_w_degree_gt_1(self): #TODO

    def test_getRelatedTags_w_matching_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedTags('bar', community='community')
        self.assertEqual(len(related), 2)

    def test_getRelatedTags_w_invalid_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedTags('bar', community='nonesuch')
        self.assertEqual(len(related), 0)

    def test_getRelatedTags_w_matching_user(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedTags('bar', user='phred')
        self.assertEqual(len(related), 2)

    def test_getRelatedTags_no_matching_user(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedTags('bar', user='bharney')
        self.assertEqual(len(related), 0)

    def test_getRelatedItems_defaults(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar', 'baz'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedItems(15)
        self.assertEqual(len(related), 2)
        self.assertEqual(related[0], (13, 2))
        self.assertEqual(related[1], (14, 1))

    def test_getRelatedItems_w_matching_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedItems(15, community='community')
        self.assertEqual(len(related), 2)

    def test_getRelatedItems_w_invalid_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedItems(15, community='nonesuch')
        self.assertEqual(len(related), 0)

    def test_getRelatedItems_w_matching_user(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedItems(15, user='phred')
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0], (13, 1))

    def test_getRelatedItems_no_matching_user(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedItems(15, user='bharney')
        self.assertEqual(len(related), 0)

    def test_update_one(self):
        TAGS = ('bedrock', 'dinosaur')
        engine = self._makeOne()

        engine.update(13, 'phred', TAGS)

        self.assertEqual(engine.tagCount, len(TAGS))
        self.assertEqual(engine.itemCount, 1)
        self.assertEqual(engine.userCount, 1)

        self.assertEqual(len(engine.getTags()), len(TAGS))
        for tag in TAGS:
            self.failUnless(tag in engine.getTags())

        self.assertEqual(len(engine.getTagObjects()), len(TAGS))
        for tagObj in engine.getTagObjects():
            self.assertEqual(tagObj.user, 'phred')
            self.assertEqual(tagObj.item, 13)
            self.failUnless(tagObj.name in TAGS)
            self.assertEqual(tagObj.community, None)

        self.assertEqual(len(engine.getCloud()), len(TAGS))
        for tag, freq in engine.getCloud():
            self.failUnless(tag in TAGS)
            self.assertEqual(freq, 1)

        self.assertEqual(len(engine.getItems()), 1)
        self.failUnless(13 in engine.getItems())

        self.assertEqual(len(engine.getUsers()), 1)
        self.failUnless('phred' in engine.getUsers())

        self.assertEqual(len(engine.getRelatedTags('bedrock')), 1)
        self.failUnless('dinosaur' in engine.getRelatedTags('bedrock'))

        self.assertEqual(len(engine.getRelatedTags('dinosaur')), 1)
        self.failUnless('bedrock' in engine.getRelatedTags('dinosaur'))

        self.assertEqual(len(engine.getRelatedItems(13)), 0)
        self.assertEqual(len(engine.getRelatedUsers('phred')), 0)

        self.assertEqual(len(engine.getFrequency()), len(TAGS))
        for tag in TAGS:
            self.assertEqual(len(engine.getFrequency((tag,))), 1)
            self.assertEqual(engine.getFrequency((tag,))[0][0], tag)
            self.assertEqual(engine.getFrequency((tag,))[0][1], 1)

    def test_update_one_with_community(self):
        self._registerCommunityFinder()

        TAGS = ('bedrock', 'dinosaur')
        engine = self._makeOne()

        engine.update(13, 'phred', TAGS)

        self.assertEqual(engine.tagCount, len(TAGS))
        self.assertEqual(engine.itemCount, 1)
        self.assertEqual(engine.userCount, 1)

        self.assertEqual(len(engine.getTags()), len(TAGS))
        for tag in TAGS:
            self.failUnless(tag in engine.getTags())

        self.assertEqual(len(engine.getTagObjects()), len(TAGS))
        for tagObj in engine.getTagObjects():
            self.assertEqual(tagObj.user, 'phred')
            self.assertEqual(tagObj.item, 13)
            self.failUnless(tagObj.name in TAGS)
            self.assertEqual(tagObj.community, 'community')

        self.assertEqual(len(engine.getCloud()), len(TAGS))
        for tag, freq in engine.getCloud():
            self.failUnless(tag in TAGS)
            self.assertEqual(freq, 1)

        self.assertEqual(len(engine.getItems()), 1)
        self.failUnless(13 in engine.getItems())

        self.assertEqual(len(engine.getUsers()), 1)
        self.failUnless('phred' in engine.getUsers())

        self.assertEqual(len(engine.getRelatedTags('bedrock')), 1)
        self.assertEqual(len(engine.getRelatedTags('bedrock',
                                                   community='community')), 1)
        self.failUnless('dinosaur' in engine.getRelatedTags('bedrock'))

        self.assertEqual(len(engine.getRelatedTags('dinosaur')), 1)
        self.failUnless('bedrock' in engine.getRelatedTags('dinosaur'))

        self.assertEqual(len(engine.getRelatedItems(13)), 0)
        self.assertEqual(len(engine.getRelatedUsers('phred')), 0)

        self.assertEqual(len(engine.getFrequency()), len(TAGS))
        for tag in TAGS:
            self.assertEqual(len(engine.getFrequency((tag,))), 1)
            self.assertEqual(engine.getFrequency((tag,))[0][0], tag)
            self.assertEqual(engine.getFrequency((tag,))[0][1], 1)

    def test_update_dupe_leaves_old_values_updates_timestamp(self):
        engine = self._makeOne()

        engine.update(13, 'phred', ('bedrock', 'dinosaur'))
        engine.update(13, 'phred', ('bedrock',))

        tagObjs = list(engine.getTagObjects())
        self.assertEqual(len(tagObjs), 1)
        self.assertEqual(tagObjs[0].user, 'phred')
        self.assertEqual(tagObjs[0].item, 13)
        self.assertEqual(tagObjs[0].name, 'bedrock')

    def test_delete_all_criteria_None_raises_ValueError(self):
        engine = self._makeOne()
        self.assertRaises(ValueError, engine.delete, None, None, None)

    def _populate(self, engine):
        engine.update(13, 'phred', ('bedrock', 'dinosaur'))
        engine.update(42, 'bharney', ('bedrock', 'neighbor'))
        engine.update(13, 'bharney', ('bedrock',))

    def test_delete_w_item(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(item=42)

        self.assertEqual(count, 2)

        self.failIf(42 in engine.getItems())
        self.failUnless(13 in engine.getItems())

        tags = engine.getTags(items=(13,))
        self.assertEqual(len(tags), 2)
        self.failUnless('bedrock' in tags)
        self.failUnless('dinosaur' in tags)

        tagObjs = engine.getTagObjects(items=(13,))
        self.assertEqual(len(tagObjs), 3)

    def test_delete_w_user(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(user='bharney')

        self.failIf('bharney' in engine.getUsers())
        self.failUnless('phred' in engine.getUsers())

        tags = engine.getTags(users=('phred',))
        self.assertEqual(len(tags), 2)
        self.failUnless('bedrock' in tags)
        self.failUnless('dinosaur' in tags)

        tagObjs = engine.getTagObjects(users=('phred',))
        self.assertEqual(len(tagObjs), 2)

    def test_delete_w_tag(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(tag='bedrock')

        self.assertEqual(count, 3)

        self.failIf('bedrock' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failUnless('neighbor' in engine.getTags())

        tags = engine.getTags(users=('phred',))
        self.assertEqual(len(tags), 1)
        self.failIf('bedrock' in tags)
        self.failUnless('dinosaur' in tags)

        tags = engine.getTags(users=('bharney',))
        self.assertEqual(len(tags), 1)
        self.failIf('bedrock' in tags)
        self.failUnless('neighbor' in tags)

    def test_delete_w_item_and_user(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(item=42, user='bharney')

        self.assertEqual(count, 2)

        self.failUnless('bedrock' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failIf('neighbor' in engine.getTags())

        self.failUnless('phred' in engine.getUsers())
        self.failUnless('bharney' in engine.getUsers())

        self.failUnless(13 in engine.getItems())
        self.failIf(42 in engine.getItems())

    def test_delete_w_item_and_user_and_tag(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(item=42, user='bharney', tag='bedrock')

        self.assertEqual(count, 1)

        self.failUnless('bedrock' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failUnless('neighbor' in engine.getTags())

        self.failUnless('phred' in engine.getUsers())
        self.failUnless('bharney' in engine.getUsers())

        self.failUnless(13 in engine.getItems())
        self.failUnless(42 in engine.getItems())

    def test_delete_nonesuch(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(item=57)

        self.assertEqual(count, 0)

    def test_rename_same(self):
        engine = self._makeOne()
        self._populate(engine)
        self.assertEqual(engine.rename('bedrock', 'bedrock'), 0)

    def test_rename_nonesuch(self):
        engine = self._makeOne()
        self._populate(engine)
        self.assertEqual(engine.rename('nonesuch', 'bedrock'), 0)

    def test_rename_actual(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.rename('bedrock', 'Bedrock')
        self.assertEqual(count, 3)

        self.failIf('bedrock' in engine.getTags())
        self.failUnless('Bedrock' in engine.getTags())

    def test_normalize_default(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('BEDROCK', 'DINOSAUR'))
        engine.update(42, 'bharney', ('BEDROCK', 'NEIGHBOR'))
        engine.update(13, 'bharney', ('BEDROCK',))

        count = engine.normalize()
        self.assertEqual(count, 5)

        self.failUnless('bedrock' in engine.getTags())
        self.failIf('BEDROCK' in engine.getTags())
        self.failUnless('neighbor' in engine.getTags())
        self.failIf('NEIGHBOR' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failIf('DINOSAUR' in engine.getTags())

    def test_normalize_callable(self):
        engine = self._makeOne()
        self._populate(engine)

        count = engine.normalize(lambda x: '-'.join(x))
        self.assertEqual(count, 5)

        self.failIf('bedrock' in engine.getTags())
        self.failUnless('b-e-d-r-o-c-k' in engine.getTags())
        self.failIf('neighbor' in engine.getTags())
        self.failUnless('n-e-i-g-h-b-o-r' in engine.getTags())
        self.failIf('dinosaur' in engine.getTags())
        self.failUnless('d-i-n-o-s-a-u-r' in engine.getTags())

    def test_getTagsWithPrefix_hit(self):
        engine = self._makeOne()
        self._populate(engine)
        engine.update(13, 'bharney', ('bedrock', 'bambam', 'dinosaur'))

        found = list(engine.getTagsWithPrefix('b'))
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0], 'bambam')
        self.assertEqual(found[1], 'bedrock')

class TagCommunityFinderTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.tagging import TagCommunityFinder
        return TagCommunityFinder

    def _makeOne(self, context=None):
        if context is None:
            context = testing.DummyModel()
        return self._getTargetClass()(context)

    def test_class_conforms_to_ITagCommunityFinder(self):
        from zope.interface.verify import verifyClass
        from karl.tagging.interfaces import ITagCommunityFinder
        verifyClass(ITagCommunityFinder, self._getTargetClass())

    def test_object_conforms_to_ITagCommunityFinder(self):
        from zope.interface.verify import verifyObject
        from karl.tagging.interfaces import ITagCommunityFinder
        verifyObject(ITagCommunityFinder, self._makeOne())

    def test___call___no_catalog_raises(self):
        context = testing.DummyModel()
        site = context.site = testing.DummyModel()
        adapter = self._makeOne(context)
        self.assertRaises(ValueError, adapter, 123)

    def test___call___w_catalog_bad_docid_raises(self):
        context = testing.DummyModel()
        site = context.site = testing.DummyModel()
        catalog = site.catalog = testing.DummyModel()
        catalog.document_map = DummyDocumentMap()
        adapter = self._makeOne(context)
        self.assertRaises(KeyError, adapter, 123)

    def test___call___w_catalog_good_docid(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        context = testing.DummyModel()
        site = context.site = testing.DummyModel()
        commune = site['commune'] = testing.DummyModel()
        directlyProvides(commune, ICommunity)
        doc = commune['doc'] = testing.DummyModel()
        testing.registerModels({'/commune/doc': doc})
        catalog = site.catalog = testing.DummyModel()
        catalog.document_map = DummyDocumentMap({123: '/commune/doc'})

        adapter = self._makeOne(context)

        self.assertEqual(adapter(123), 'commune')

    def test___call___w_catalog_good_docid_not_in_community(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        context = testing.DummyModel()
        site = context.site = testing.DummyModel()
        profiles = site['profiles'] = testing.DummyModel()
        user1 = profiles['user1'] = testing.DummyModel()
        testing.registerModels({'/profiles/user1': user1})
        catalog = site.catalog = testing.DummyModel()
        catalog.document_map = DummyDocumentMap({123: '/profiles/user1'})

        adapter = self._makeOne(context)

        self.assertEqual(adapter(123), None)


class TagIndexTests(unittest.TestCase):
    
    def _getTargetClass(self):
        from karl.tagging.index import TagIndex
        return TagIndex

    def _makeOne(self, context=None):
        if context is None:
            context = testing.DummyModel()
            context.tags = DummyTaggingEngine()
        return self._getTargetClass()(context)

    def test_class_conforms_to_ICatalogIndex(self):
        from zope.interface.verify import verifyClass
        from repoze.catalog.interfaces import ICatalogIndex
        verifyClass(ICatalogIndex, self._getTargetClass())

    def test_object_conforms_to_ICatalogIndex(self):
        from zope.interface.verify import verifyObject
        from repoze.catalog.interfaces import ICatalogIndex
        verifyObject(ICatalogIndex, self._makeOne())

    def test_apply_or(self):
        index = self._makeOne()
        res = index.apply(dict(query=['a', 'b'], operator='or'))
        self.assertEquals(set(res), set([1, 2, 3]))

    def test_apply_default(self):
        index = self._makeOne()
        res = index.apply(dict(query=['a', 'b']))
        self.assertEquals(set(res), set([2]))

    def test_apply_and(self):
        index = self._makeOne()
        res = index.apply(dict(query=['a', 'b'], operator='and'))
        self.assertEquals(set(res), set([2]))

    def test_apply_and_one(self):
        index = self._makeOne()
        res = index.apply(dict(query='a', operator='and'))
        self.assertEquals(set(res), set([1, 2]))

    def test_apply_and_none(self):
        index = self._makeOne()
        res = index.apply(dict(query=[], operator='and'))
        self.assertEquals(set(res), set())

    def test_apply_bad_operator(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.apply,
            dict(query=[], operator='foo'))


class DummyTaggingEngine:
    def getItems(self, tags, users=None, community=None):
        res = set()
        if 'a' in tags:
            res.add(1)
            res.add(2)
        if 'b' in tags:
            res.add(2)
            res.add(3)
        return res


class DummyDocumentMap:

    def __init__(self, map=None):
        if map is None:
            map = {}
        self._map = map

    def address_for_docid(self, docid):
        return self._map.get(docid)
