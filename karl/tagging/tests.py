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

from pyramid import testing

import karl.testing

_marker = object()


class TagAddedTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.tagging import TagAddedEvent
        return TagAddedEvent

    def _makeOne(self, item=13, user='phred', name='test', community=_marker):
        klass = self._getTargetClass()
        if community is _marker:
            tag = testing.DummyModel(item=item, user=user, name=name,
                                     community=None)
        else:
            tag = testing.DummyModel(item=item, user=user, name=name,
                                     community=community)
        return klass(tag)

    def test_class_conforms_to_ITagAddedEvent(self):
        from zope.interface.verify import verifyClass
        from karl.tagging.interfaces import ITagAddedEvent
        verifyClass(ITagAddedEvent, self._getTargetClass())

    def test_object_conforms_to_ITagAddedEvent(self):
        from zope.interface.verify import verifyObject
        from karl.tagging.interfaces import ITagAddedEvent
        verifyObject(ITagAddedEvent, self._makeOne())


class TagRemovedTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.tagging import TagRemovedEvent
        return TagRemovedEvent

    def _makeOne(self, item=13, user='phred', name='test', community=_marker):
        klass = self._getTargetClass()
        if community is _marker:
            tag = testing.DummyModel(item=item, user=user, name=name,
                                     community=None)
        else:
            tag = testing.DummyModel(item=item, user=user, name=name,
                                     community=community)
        return klass(tag)

    def test_class_conforms_to_ITagRemovedEvent(self):
        from zope.interface.verify import verifyClass
        from karl.tagging.interfaces import ITagRemovedEvent
        verifyClass(ITagRemovedEvent, self._getTargetClass())

    def test_object_conforms_to_ITagRemovedEvent(self):
        from zope.interface.verify import verifyObject
        from karl.tagging.interfaces import ITagRemovedEvent
        verifyObject(ITagRemovedEvent, self._makeOne())


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

    def test___repr___wo_community(self):
        tag = self._makeOne()
        self.assertEqual(repr(tag),
                         "<Tag u'test' for 13 by u'phred', community None>")

    def test___repr___w_community(self):
        tag = self._makeOne(community='community')
        self.assertEqual(repr(tag),
                         "<Tag u'test' for 13 by u'phred', "
                         "community u'community'>")


class TagsTests(unittest.TestCase):

    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
        karl.testing.registerAdapter(_factory, Interface, ITagCommunityFinder)

    def _registerEventsListener(self):
        events = karl.testing.registerEventListener()
        del events[:]
        return events

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

    def test_getTagObjects_bad_key(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        objects = engine.getTagObjects(items=(13,None,15))
        self.assertEqual(len(objects), 4)

    def test_getCloud_w_items_as_int(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'bharney', ('foo',))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        cloud = dict(engine.getCloud(items=13))
        self.assertEqual(len(cloud), 2)
        self.assertEqual(cloud['foo'], 2)
        self.assertEqual(cloud['bar'], 1)

    def test_getCloud_w_users_as_string(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        cloud = dict(engine.getCloud(users='bharney'))
        self.assertEqual(len(cloud), 1)
        self.assertEqual(cloud['foo'], 1)

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

    def test_getCloud_no_community_after_rename(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        engine.rename('foo', 'goo')
        cloud = dict(engine.getCloud())
        self.assertEqual(len(cloud), 3)
        self.assertEqual(cloud['goo'], 2)
        self.assertEqual(cloud['bar'], 2)
        self.assertEqual(cloud['baz'], 1)

    def test_getCloud_no_community_after_delete(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        engine.delete(13, tag='bar')
        cloud = dict(engine.getCloud())
        self.assertEqual(len(cloud), 3)
        self.assertEqual(cloud['foo'], 2)
        self.assertEqual(cloud['bar'], 1)
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

    def test_getCloud_w_community_match_after_delete(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        engine.delete(13, tag='bar')
        cloud = dict(engine.getCloud(community='community'))
        self.assertEqual(len(cloud), 3)
        self.assertEqual(cloud['foo'], 2)
        self.assertEqual(cloud['bar'], 1)
        self.assertEqual(cloud['baz'], 1)

    def test_getCloud_w_community_match_after_delete_all(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(14, 'bharney', ('foo',))
        engine.update(15, 'phred', ('bar', 'baz'))
        engine.delete(15, tag='baz')
        cloud = dict(engine.getCloud(community='community'))
        self.assertEqual(len(cloud), 2)
        self.assertEqual(cloud['foo'], 2)
        self.assertEqual(cloud['bar'], 2)

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

    def test_getRelatedUsers_wo_community(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedUsers(user='phred')
        self.assertEqual(len(related), 2)
        self.assertEqual(related[0], ('wylma', 1))
        self.assertEqual(related[1], ('bharney', 1))

    def test_getRelatedUsers_w_valid_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedUsers(user='phred', community='community')
        self.assertEqual(len(related), 2)
        self.assertEqual(related[0], ('wylma', 1))
        self.assertEqual(related[1], ('bharney', 1))

    def test_getRelatedUsers_w_invalid_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        related = engine.getRelatedUsers(user='phred', community='nonesuch')
        self.assertEqual(len(related), 0)

    def test_getFrequency_defaults(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        freq = engine.getFrequency()
        self.assertEqual(len(freq), 4)
        self.failUnless(('foo', 1) in freq)
        self.failUnless(('bar', 4) in freq)
        self.failUnless(('baz', 1) in freq)
        self.failUnless(('qux', 1) in freq)

    def test_getFrequency_w_tags(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        freq = engine.getFrequency(tags=['bar', 'foo', 'nonesuch'])
        self.assertEqual(len(freq), 3)
        self.failUnless(('foo', 1) in freq)
        self.failUnless(('bar', 4) in freq)
        self.failUnless(('nonesuch', 0) in freq)

    def test_getFrequency_w_user(self):
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        freq = engine.getFrequency(user='phred')
        self.assertEqual(len(freq), 3)
        self.failUnless(('foo', 1) in freq)
        self.failUnless(('bar', 2) in freq)
        self.failUnless(('baz', 1) in freq)

    def test_getFrequency_w_valid_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        freq = engine.getFrequency(community='community')
        self.assertEqual(len(freq), 4)
        self.failUnless(('foo', 1) in freq)
        self.failUnless(('bar', 4) in freq)
        self.failUnless(('baz', 1) in freq)
        self.failUnless(('qux', 1) in freq)

    def test_getFrequency_w_invalid_community(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        engine.update(13, 'phred', ('foo', 'bar'))
        engine.update(13, 'wylma', ('bar',))
        engine.update(14, 'bharney', ('qux', 'bar'))
        engine.update(15, 'phred', ('bar', 'baz'))
        freq = engine.getFrequency(community='nonesuch')
        self.assertEqual(len(freq), 0)

    def test_update_one(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        TAGS = ('bedrock', 'dinosaur')
        events = self._registerEventsListener()
        engine = self._makeOne()

        engine.update(13, 'phred', TAGS)

        self.assertEqual(len(events), 2)
        self.assertTrue(TagAddedEvent(
                            Tag(13, 'phred', TAGS[1], None)) in events)
        self.assertTrue(TagAddedEvent(
                            Tag(13, 'phred', TAGS[0], None)) in events)

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
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        TAGS = ('bedrock', 'dinosaur')
        self._registerCommunityFinder()
        events = self._registerEventsListener()

        engine = self._makeOne()

        engine.update(13, 'phred', TAGS)

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0],
                         TagAddedEvent(Tag(13, 'phred', TAGS[0], 'community')))
        self.assertEqual(events[1],
                         TagAddedEvent(Tag(13, 'phred', TAGS[1], 'community')))
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

    def test_update_dupe_plus_remove(self):
        from karl.tagging import Tag
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()

        engine.update(13, 'phred', ('bedrock', 'dinosaur'))
        events = self._registerEventsListener()

        engine.update(13, 'phred', ('bedrock',))

        # No event for the duplicated tag.
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0],
                         TagRemovedEvent(Tag(13, 'phred', 'dinosaur')))

        tagObjs = list(engine.getTagObjects())
        self.assertEqual(len(tagObjs), 1)
        tuples = [(x.user, x.item, x.name) for x in tagObjs]
        self.failUnless(('phred', 13, 'bedrock') in tuples)
        self.failIf(('phred', 13, 'dinosaur') in tuples)

    def test_update_dupe_plus_add(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        engine = self._makeOne()

        engine.update(13, 'phred', ('bedrock',))
        events = self._registerEventsListener()

        engine.update(13, 'phred', ('bedrock', 'dinosaur'))

        # No event for the duplicated tag.
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0],
                         TagAddedEvent(Tag(13, 'phred', 'dinosaur')))

        tagObjs = list(engine.getTagObjects())
        self.assertEqual(len(tagObjs), 2)
        tuples = [(x.user, x.item, x.name) for x in tagObjs]
        self.failUnless(('phred', 13, 'bedrock') in tuples)
        self.failUnless(('phred', 13, 'dinosaur') in tuples)

    def test_delete_all_criteria_None_raises_ValueError(self):
        events = self._registerEventsListener()
        engine = self._makeOne()
        self.assertRaises(ValueError, engine.delete, None, None, None)
        self.assertEqual(len(events), 0)

    def _populate(self, engine):
        engine.update(13, 'phred', ('bedrock', 'dinosaur'))
        engine.update(42, 'bharney', ('bedrock', 'neighbor'))
        engine.update(13, 'bharney', ('bedrock',))

    def test_delete_w_item(self):
        from karl.tagging import Tag
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.delete(item=42)

        self.assertEqual(count, 2)

        self.assertEqual(len(events), 2)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'neighbor'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)

        self.failIf(42 in engine.getItems())
        self.failUnless(13 in engine.getItems())

        tags = engine.getTags(items=(13,))
        self.assertEqual(len(tags), 2)
        self.failUnless('bedrock' in tags)
        self.failUnless('dinosaur' in tags)

        tagObjs = engine.getTagObjects(items=(13,))
        self.assertEqual(len(tagObjs), 3)

    def test_delete_w_user(self):
        from karl.tagging import Tag
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.delete(user='bharney')

        self.assertEqual(len(events), 3)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'neighbor'))
                            in events)

        self.failIf('bharney' in engine.getUsers())
        self.failUnless('phred' in engine.getUsers())

        tags = engine.getTags(users=('phred',))
        self.assertEqual(len(tags), 2)
        self.failUnless('bedrock' in tags)
        self.failUnless('dinosaur' in tags)

        tagObjs = engine.getTagObjects(users=('phred',))
        self.assertEqual(len(tagObjs), 2)

    def test_delete_w_tag(self):
        from karl.tagging import Tag
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.delete(tag='bedrock')

        self.assertEqual(count, 3)

        self.assertEqual(len(events), 3)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'phred', 'bedrock'))
                            in events)

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
        from karl.tagging import Tag
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.delete(item=42, user='bharney')

        self.assertEqual(count, 2)

        self.assertEqual(len(events), 2)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'neighbor'))
                            in events)

        self.failUnless('bedrock' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failIf('neighbor' in engine.getTags())

        self.failUnless('phred' in engine.getUsers())
        self.failUnless('bharney' in engine.getUsers())

        self.failUnless(13 in engine.getItems())
        self.failIf(42 in engine.getItems())

    def test_delete_w_item_and_user_and_tag(self):
        from karl.tagging import Tag
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.delete(item=42, user='bharney', tag='bedrock')

        self.assertEqual(count, 1)

        self.assertEqual(len(events), 1)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)

        self.failUnless('bedrock' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failUnless('neighbor' in engine.getTags())

        self.failUnless('phred' in engine.getUsers())
        self.failUnless('bharney' in engine.getUsers())

        self.failUnless(13 in engine.getItems())
        self.failUnless(42 in engine.getItems())

    def test_delete_all(self):
        self._registerCommunityFinder()
        engine = self._makeOne()
        self._populate(engine)

        count = engine.delete(item=42)
        count += engine.delete(item=13)

        self.assertEqual(count, 5)

        self.failIf(42 in engine.getItems())
        self.failIf(13 in engine.getItems())

    def test_delete_nonesuch(self):
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.delete(item=57)

        self.assertEqual(count, 0)
        self.assertEqual(len(events), 0)

    def test_rename_same(self):
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()
        self.assertEqual(engine.rename('bedrock', 'bedrock'), 0)
        self.assertEqual(len(events), 0)

    def test_rename_nonesuch(self):
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()
        self.assertEqual(engine.rename('nonesuch', 'bedrock'), 0)
        self.assertEqual(len(events), 0)

    def test_rename_actual(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.rename('bedrock', 'Bedrock')
        self.assertEqual(count, 3)

        self.assertEqual(len(events), 6)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'phred', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'bharney', 'Bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'bharney', 'Bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'phred', 'Bedrock'))
                            in events)

        self.failIf('bedrock' in engine.getTags())
        self.failUnless('Bedrock' in engine.getTags())

    def test_reassign_to_new_user(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        engine.reassign('bharney', 'phony')

        self.assertEqual(len(events), 6)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'neighbor'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'phony', 'neighbor'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'phony', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'phony', 'bedrock'))
                            in events)

        self.assertTrue('neighbor' in engine.getTags())
        self.assertTrue('phred' in engine.getUsers())
        self.assertTrue('phony' in engine.getUsers())
        self.assertFalse('bharney' in engine.getUsers())

    def test_reassign_to_existing_user(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        engine.reassign('bharney', 'phred')

        self.assertEqual(len(events), 6)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'neighbor'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'phred', 'neighbor'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'phred', 'bedrock'))
                            in events)
        # Note that we emit an event, even though phred already had this
        # tag, because the implementation would get too gnarly if we tried
        # to filter it out.
        self.failUnless(TagAddedEvent(Tag(13, 'phred', 'bedrock'))
                            in events)

        self.assertTrue('neighbor' in engine.getTags())
        self.assertTrue('phred' in engine.getUsers())
        self.assertFalse('phony' in engine.getUsers())
        self.assertFalse('bharney' in engine.getUsers())

    def test_normalize_default(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        engine.update(13, 'phred', ('BEDROCK', 'DINOSAUR'))
        engine.update(42, 'bharney', ('BEDROCK', 'NEIGHBOR'))
        engine.update(13, 'bharney', ('BEDROCK',))
        events = self._registerEventsListener()

        count = engine.normalize()
        self.assertEqual(count, 5)

        self.assertEqual(len(events), 10)
        self.failUnless(TagRemovedEvent(Tag(13, 'phred', 'BEDROCK'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'phred', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'phred', 'DINOSAUR'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'phred', 'dinosaur'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'BEDROCK'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'NEIGHBOR'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'BEDROCK'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)

        self.failUnless('bedrock' in engine.getTags())
        self.failIf('BEDROCK' in engine.getTags())
        self.failUnless('neighbor' in engine.getTags())
        self.failIf('NEIGHBOR' in engine.getTags())
        self.failUnless('dinosaur' in engine.getTags())
        self.failIf('DINOSAUR' in engine.getTags())

    def test_normalize_callable(self):
        from karl.tagging import Tag
        from karl.tagging import TagAddedEvent
        from karl.tagging import TagRemovedEvent
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()

        count = engine.normalize(lambda x: '-'.join(x))
        self.assertEqual(count, 5)

        self.assertEqual(len(events), 10)
        self.failUnless(TagRemovedEvent(Tag(13, 'phred', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'phred', 'b-e-d-r-o-c-k'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'phred', 'dinosaur'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'phred', 'd-i-n-o-s-a-u-r'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'bharney', 'b-e-d-r-o-c-k'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(42, 'bharney', 'neighbor'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(42, 'bharney', 'n-e-i-g-h-b-o-r'))
                            in events)
        self.failUnless(TagRemovedEvent(Tag(13, 'bharney', 'bedrock'))
                            in events)
        self.failUnless(TagAddedEvent(Tag(13, 'bharney', 'b-e-d-r-o-c-k'))
                            in events)

        self.failIf('bedrock' in engine.getTags())
        self.failUnless('b-e-d-r-o-c-k' in engine.getTags())
        self.failIf('neighbor' in engine.getTags())
        self.failUnless('n-e-i-g-h-b-o-r' in engine.getTags())
        self.failIf('dinosaur' in engine.getTags())
        self.failUnless('d-i-n-o-s-a-u-r' in engine.getTags())

    def test_getTagsWithPrefix_hit(self):
        engine = self._makeOne()
        self._populate(engine)
        events = self._registerEventsListener()
        engine.update(13, 'bharney', ('bedrock', 'bambam', 'dinosaur'))

        found = list(engine.getTagsWithPrefix('b'))
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0], 'bambam')
        self.assertEqual(found[1], 'bedrock')

class TagCommunityFinderTests(unittest.TestCase):

    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
        karl.testing.registerModels({'/commune/doc': doc})
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
        karl.testing.registerModels({'/profiles/user1': user1})
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

    def test_index_doc(self):
        index = self._makeOne()
        before = index.__dict__.copy()
        site_before = index.site.__dict__.copy()
        index.index_doc(1, object())
        self.assertEqual(index.__dict__, before)
        self.assertEqual(index.site.__dict__, site_before)

    def test_unindex_doc(self):
        index = self._makeOne()
        before = index.__dict__.copy()
        site_before = index.site.__dict__.copy()
        index.unindex_doc(1)
        self.assertEqual(index.__dict__, before)
        self.assertEqual(index.site.__dict__, site_before)

    def test_reindex_doc(self):
        index = self._makeOne()
        before = index.__dict__.copy()
        site_before = index.site.__dict__.copy()
        index.reindex_doc(1, object())
        self.assertEqual(index.__dict__, before)
        self.assertEqual(index.site.__dict__, site_before)

    def test_clear(self):
        index = self._makeOne()
        before = index.__dict__.copy()
        site_before = index.site.__dict__.copy()
        index.clear()
        self.assertEqual(index.__dict__, before)
        self.assertEqual(index.site.__dict__, site_before)

    def test_apply_intersect_wo_docids(self):
        index = self._makeOne()
        res = index.apply_intersect({'query': ['a', 'b'], 'operator':'or'},
                                    docids=None)
        self.assertEquals(set(res), set([1, 2, 3]))

    def test_apply_intersect_w_docids(self):
        index = self._makeOne()
        res = index.apply_intersect({'query': ['a', 'b'], 'operator':'or'},
                                    docids=index.family.IF.Set([1, 2]))
        self.assertEquals(set(res), set([1, 2]))

    def test_apply_bare_query(self):
        index = self._makeOne()
        res = index.apply(['a', 'b'])
        self.assertEquals(set(res), set([2]))

    def test_apply_default(self):
        index = self._makeOne()
        res = index.apply(dict(query=['a', 'b']))
        self.assertEquals(set(res), set([2]))

    def test_apply_or(self):
        index = self._makeOne()
        res = index.apply(dict(query=['a', 'b'], operator='or'))
        self.assertEquals(set(res), set([1, 2, 3]))

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
