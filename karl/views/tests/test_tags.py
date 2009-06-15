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
from karl import testing as karltesting

class AddTagsTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, values):
        from karl.views.tags import add_tags
        return add_tags(context, request, values)
    
    def test_w_no_values(self):
        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags()
        request = testing.DummyRequest()

        self._callFUT(context, request, None)

        self.assertEqual(tags.getTags_called_with, None)
        self.assertEqual(tags.updated, None)
    
    def test_w_string(self):
        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags()
        request = testing.DummyRequest()

        self._callFUT(context, request, 'foo')

        self.assertEqual(tags.getTags_called_with,
                         (('docid',), ('userid',), None))
        self.assertEqual(tags.updated, ('docid', 'userid', ['foo']))
    
    def test_no_existing_values(self):
        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags()
        request = testing.DummyRequest()

        self._callFUT(context, request, ('foo', 'bar'))

        self.assertEqual(tags.getTags_called_with,
                         (('docid',), ('userid',), None))
        self.assertEqual(tags.updated,
                         ('docid', 'userid', ['foo', 'bar']))
    
    def test_w_existing_values(self):
        testing.registerDummySecurityPolicy('userid')
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags(tags=('baz',))
        request = testing.DummyRequest()

        self._callFUT(context, request, ('foo', 'bar'))

        self.assertEqual(tags.getTags_called_with,
                         (('docid',), ('userid',), None))
        self.assertEqual(tags.updated,
                         ('docid', 'userid', ['baz', 'foo', 'bar']))

class SetTagsTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, values):
        from karl.views.tags import set_tags
        return set_tags(context, request, values)

    def test_w_normal_values(self):
        testing.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags()
        self._callFUT(context, request, ['a', 'b'])
        self.assertEqual(tags.getTags_called_with, None)
        self.assertEqual(tags.updated, ('docid', 'userid', ['a', 'b']))

    def test_w_None(self):
        testing.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags()
        self._callFUT(context, request, None)
        self.assertEqual(tags.getTags_called_with, None)
        self.assertEqual(tags.updated, ('docid', 'userid', ()))


class ShowTagViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import showtag_view
        return showtag_view(context, request)

    def test_without_tag(self):
        context = testing.DummyModel()
        context.tags = DummyTags()
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, None)
        self.assertEqual(len(renderer.entries), 0)
        self.assertEqual(len(renderer.related), 0)

    def test_with_tag(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        context = testing.DummyModel()
        context.title = 'title'
        testing.registerModels({'/foo': context})
        directlyProvides(context, IDummyBlogEntry)
        registerContentFactory(testing.DummyModel, IDummyBlogEntry)
        tags = context.tags = DummyTags()
        def _getRelated(tag, degree=1, community=None, user=None):
            assert tag == 'tag1'
            assert degree == 1
            assert community is None
            assert user is None
            return ['tag2', 'tag3']
        tags.getRelatedTags = _getRelated
        context.catalog = karltesting.DummyCatalog({1:'/foo'})
        request = testing.DummyRequest()
        request.subpath = [u'tag1']
        renderer = testing.registerDummyRenderer('templates/showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, u'tag1')
        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['description'], '')
        self.assertEqual(entry['title'], 'title')
        self.assertEqual(entry['href'], 'http://example.com/')
        self.assertEqual(entry['tagusers_count'], '1 person')
        self.assertEqual(entry['type'], 'Blog Entry')
        self.assertEqual(entry['tagusers_href'],
                         'http://example.com/tagusers.html?tag=tag1&docid=1')
        self.assertEqual(len(renderer.related), 2)
        self.assertEqual(renderer.related[0], 'tag2')
        self.assertEqual(renderer.related[1], 'tag3')

    def test_with_tag_multiple_users(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        context = testing.DummyModel()
        context.title = 'title'
        testing.registerModels({'/foo': context})
        directlyProvides(context, IDummyBlogEntry)
        registerContentFactory(testing.DummyModel, IDummyBlogEntry)
        tags = context.tags = DummyTags(users=('dummy', 'dummy2'))
        def _getRelated(tag, degree=1, community=None, user=None):
            assert tag == 'tag1'
            assert degree == 1
            assert community is None
            assert user is None
            return []
        tags.getRelatedTags = _getRelated
        context.catalog = karltesting.DummyCatalog({1:'/foo'})
        request = testing.DummyRequest()
        request.subpath = [u'tag1']
        renderer = testing.registerDummyRenderer('templates/showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, u'tag1')
        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['description'], '')
        self.assertEqual(entry['title'], 'title')
        self.assertEqual(entry['href'], 'http://example.com/')
        self.assertEqual(entry['tagusers_count'], '2 people')
        self.assertEqual(entry['type'], 'Blog Entry')
        self.assertEqual(entry['tagusers_href'],
                         'http://example.com/tagusers.html?tag=tag1&docid=1')
        self.assertEqual(len(renderer.related), 0)

    def test_with_jumptag(self):
        # This is when the tagcloud or taglisting "jumps" to a tag
        # page using the input box.
        context = testing.DummyModel()
        context.tags = DummyTags()
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        request.params = {'jumptag': 'tag2'}
        request.view_name = 'showtag'
        renderer = testing.registerDummyRenderer('templates/showtag.pt')

        response = self._callFUT(context, request)

        self.assertEqual(response.location, 'http://example.com/showtag/tag2')


class CommunityShowTagViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import community_showtag_view
        return community_showtag_view(context, request)

    def test_without_tag(self):
        root = testing.DummyModel()
        root.tags = DummyTags()
        root.catalog = DummyCatalog()
        context = root['community'] = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                                'templates/community_showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, None)
        self.assertEqual(len(renderer.entries), 0)
        self.assertEqual(len(renderer.related), 0)
        self.assertEqual(renderer.crumbs, 'KARL / Communities / community')

    def test_with_tag(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import ICommunity
        root = testing.DummyModel()
        tags = root.tags = DummyTags()
        def _getRelated(tag, degree=1, community=None, user=None):
            assert tag == 'tag1'
            assert degree == 1
            assert community == 'community'
            assert user is None
            return ['tag2', 'tag3']
        tags.getRelatedTags = _getRelated
        root.catalog = karltesting.DummyCatalog({1:'/community'})
        context = root['community'] = testing.DummyModel()
        context.title = 'title'
        testing.registerModels({'/community': context})
        directlyProvides(context, ICommunity)
        registerContentFactory(testing.DummyModel, ICommunity)
        request = testing.DummyRequest()
        request.subpath = [u'tag1']
        renderer = testing.registerDummyRenderer(
                                'templates/community_showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, u'tag1')
        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['description'], '')
        self.assertEqual(entry['title'], 'title')
        self.assertEqual(entry['href'], 'http://example.com/community/')
        self.assertEqual(entry['tagusers_count'], '1 person')
        self.assertEqual(entry['type'], 'Community')
        self.assertEqual(entry['tagusers_href'],
                         'http://example.com/community/'
                         'tagusers.html?tag=tag1&docid=1')
        self.assertEqual(len(renderer.related), 2)
        self.assertEqual(renderer.related[0], 'tag2')
        self.assertEqual(renderer.related[1], 'tag3')

    def test_with_tag_multiple_users(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import ICommunity
        root = testing.DummyModel()
        tags = root.tags = DummyTags()
        def _getUsers(tags=None, items=None, community=None):
            assert list(tags) == ['tag1']
            assert list(items) == [1]
            assert community == 'community'
            return ('dummy', 'dummy2')
        tags.getUsers = _getUsers
        def _getRelated(tag, degree=1, community=None, user=None):
            assert tag == 'tag1'
            assert degree == 1
            assert community == 'community'
            assert user is None
            return []
        tags.getRelatedTags = _getRelated
        root.catalog = karltesting.DummyCatalog({1:'/community'})
        context = root['community'] = testing.DummyModel()
        context.title = 'title'
        testing.registerModels({'/community': context})
        directlyProvides(context, ICommunity)
        registerContentFactory(testing.DummyModel, ICommunity)
        request = testing.DummyRequest()
        request.subpath = [u'tag1']
        renderer = testing.registerDummyRenderer(
                                'templates/community_showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, u'tag1')
        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['description'], '')
        self.assertEqual(entry['title'], 'title')
        self.assertEqual(entry['href'], 'http://example.com/community/')
        self.assertEqual(entry['tagusers_count'], '2 people')
        self.assertEqual(entry['type'], 'Community')
        self.assertEqual(entry['tagusers_href'],
                         'http://example.com/community/'
                         'tagusers.html?tag=tag1&docid=1')
        self.assertEqual(len(renderer.related), 0)

    def test_with_jumptag(self):
        # This is when the tagcloud or taglisting "jumps" to a tag
        # page using the input box.
        root = testing.DummyModel()
        root.tags = DummyTags()
        root.catalog = DummyCatalog()
        context = root['community'] = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {'jumptag': 'tag2'}
        request.view_name = 'showtag'
        renderer = testing.registerDummyRenderer(
                                'templates/community_showtag.pt')

        response = self._callFUT(context, request)

        self.assertEqual(response.location,
                         'http://example.com/community/showtag/tag2')

class ProfileShowTagViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import profile_showtag_view
        return profile_showtag_view(context, request)

    def test_without_tag(self):
        root = testing.DummyModel()
        root.tags = DummyTags()
        root.catalog = DummyCatalog()
        profiles = root['profiles'] = testing.DummyModel()
        context = profiles['phred'] = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                                'templates/profile_showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, None)
        self.assertEqual(len(renderer.entries), 0)
        self.assertEqual(len(renderer.related), 0)
        self.assertEqual(renderer.crumbs, 'KARL / Profiles / phred')

    def test_with_tag(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        root = testing.DummyModel()
        tags = root.tags = DummyTags()
        def _getRelated(tag, degree=1, community=None, user=None):
            assert tag == 'tag1'
            assert degree == 1
            assert community is None
            assert user == 'phred'
            return ['tag2', 'tag3']
        tags.getRelatedTags = _getRelated
        root.catalog = karltesting.DummyCatalog({1:'/profiles/phred'})
        profiles = root['profiles'] = testing.DummyModel()
        context = profiles['phred'] = testing.DummyModel()
        context.title = 'title'
        testing.registerModels({'/profiles/phred': context})
        directlyProvides(context, IProfile)
        registerContentFactory(testing.DummyModel, IProfile)
        request = testing.DummyRequest()
        request.subpath = [u'tag1']
        renderer = testing.registerDummyRenderer(
                                'templates/profile_showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(tags.getItems_called_with,
                        (('tag1',), ('phred',), None))
        self.assertEqual(renderer.tag, u'tag1')
        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['description'], '')
        self.assertEqual(entry['title'], 'title')
        self.assertEqual(entry['href'], 'http://example.com/profiles/phred/')
        self.assertEqual(entry['tagusers_count'], '1 person')
        self.assertEqual(entry['type'], 'Profile')
        self.assertEqual(entry['tagusers_href'],
                         'http://example.com/profiles/phred/'
                         'tagusers.html?tag=tag1&docid=1')
        self.assertEqual(len(renderer.related), 2)
        self.assertEqual(renderer.related[0], 'tag2')
        self.assertEqual(renderer.related[1], 'tag3')

    def test_with_tag_multiple_users(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        root = testing.DummyModel()
        tags = root.tags = DummyTags()
        def _getUsers(tags=None, items=None, community=None):
            assert list(tags) == ['tag1']
            assert list(items) == [1]
            assert community is None
            return ('dummy', 'dummy2')
        tags.getUsers = _getUsers
        def _getRelated(tag, degree=1, community=None, user=None):
            assert tag == 'tag1'
            assert degree == 1
            assert community is None
            assert user == 'phred'
            return []
        tags.getRelatedTags = _getRelated
        root.catalog = karltesting.DummyCatalog({1:'/profiles/phred'})
        profiles = root['profiles'] = testing.DummyModel()
        context = profiles['phred'] = testing.DummyModel()
        context.title = 'title'
        testing.registerModels({'/profiles/phred': context})
        directlyProvides(context, IProfile)
        registerContentFactory(testing.DummyModel, IProfile)
        request = testing.DummyRequest()
        request.subpath = [u'tag1']
        renderer = testing.registerDummyRenderer(
                                'templates/profile_showtag.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, u'tag1')
        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['description'], '')
        self.assertEqual(entry['title'], 'title')
        self.assertEqual(entry['href'], 'http://example.com/profiles/phred/')
        self.assertEqual(entry['tagusers_count'], '2 people')
        self.assertEqual(entry['type'], 'Profile')
        self.assertEqual(entry['tagusers_href'],
                         'http://example.com/profiles/phred/'
                         'tagusers.html?tag=tag1&docid=1')
        self.assertEqual(len(renderer.related), 0)

    def test_with_jumptag(self):
        # This is when the tagcloud or taglisting "jumps" to a tag
        # page using the input box.
        root = testing.DummyModel()
        root.tags = DummyTags()
        root.catalog = DummyCatalog()
        profiles = root['profiles'] = testing.DummyModel()
        context = profiles['phred'] = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {'jumptag': 'tag2'}
        request.view_name = 'showtag'
        renderer = testing.registerDummyRenderer(
                                'templates/profile_showtag.pt')

        response = self._callFUT(context, request)

        self.assertEqual(response.location,
                         'http://example.com/profiles/phred/showtag/tag2')


class TagCloudViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import tag_cloud_view
        return tag_cloud_view(context, request)

    def test_wo_tags_tool(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/tagcloud.pt')
        context.catalog = DummyCatalog()

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_empty(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/tagcloud.pt')
        tags = context.tags = DummyTags()
        tags.getCloud = lambda: []
        context.catalog = DummyCatalog()

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_one_tag(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/tagcloud.pt')
        tags = context.tags = DummyTags()
        tags.getCloud = lambda: [('foo', 1)]
        context.catalog = DummyCatalog()

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['name'], 'foo')
        self.assertEqual(entry['count'], 1)
        self.assertEqual(entry['weight'], 7)
        self.assertEqual(entry['class'], 'tagweight7')

    def test_w_tags_sorted_by_name(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/tagcloud.pt')
        tags = context.tags = DummyTags()
        tags.getCloud = lambda: [('tag_%03d' % x, x)
                                    for x in range(10)]
        context.catalog = DummyCatalog()

        self._callFUT(context, request)

        self.assertEqual(renderer.entries[0]['name'], 'tag_000')
        self.assertEqual(renderer.entries[-1]['name'], 'tag_009')

    def test_w_tags_exceeding_limit(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        renderer = testing.registerDummyRenderer('templates/tagcloud.pt')
        tags = context.tags = DummyTags()
        tags.getCloud = lambda: [('tag_%03d' % x, x)
                                    for x in range(120)]
        context.catalog = DummyCatalog()

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 100)
        names = [x['name'] for x in renderer.entries]
        for i in range(20):
            self.failIf('tag_%03d' % i in names)
        for i in range(20, 120):
            self.failUnless('tag_%03d' % i in names)

    # XXX need tests for the tag weight computation with multiple tags.


class CommunityTagCloudViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import community_tag_cloud_view
        return community_tag_cloud_view(context, request)

    def test_wo_tags_tool(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                        'templates/community_tagcloud.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)
        self.assertEqual(renderer.crumbs, 'KARL / Communities / community')

    def test_w_tags_tool_empty(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        tags = context.tags = DummyTags()
        def _getCloud(items=None, users=None, community=None):
            assert items is None
            assert users is None
            assert community == 'community'
            return []
        tags.getCloud = _getCloud
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                        'templates/community_tagcloud.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_one_tag(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        tags = context.tags = DummyTags()
        def _getCloud(items=None, users=None, community=None):
            assert items is None
            assert users is None
            assert community == 'community'
            return [('foo', 1)]
        tags.getCloud = _getCloud
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                        'templates/community_tagcloud.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 1)
        entry = renderer.entries[0]
        self.assertEqual(entry['name'], 'foo')
        self.assertEqual(entry['count'], 1)
        self.assertEqual(entry['weight'], 7)
        self.assertEqual(entry['class'], 'tagweight7')

    def test_w_tags_sorted_by_name(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        tags = context.tags = DummyTags()
        def _getCloud(items=None, users=None, community=None):
            assert items is None
            assert users is None
            assert community == 'community'
            return [('tag_%03d' % x, x) for x in range(10)]
        tags.getCloud = _getCloud
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                        'templates/community_tagcloud.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.entries[0]['name'], 'tag_000')
        self.assertEqual(renderer.entries[-1]['name'], 'tag_009')

    def test_w_tags_exceeding_limit(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        tags = context.tags = DummyTags()
        def _getCloud(items=None, users=None, community=None):
            assert items is None
            assert users is None
            assert community == 'community'
            return [('tag_%03d' % x, x) for x in range(120)]
        tags.getCloud = _getCloud
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                        'templates/community_tagcloud.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 100)
        names = [x['name'] for x in renderer.entries]
        for i in range(20):
            self.failIf('tag_%03d' % i in names)
        for i in range(20, 120):
            self.failUnless('tag_%03d' % i in names)

    # XXX need tests for the tag weight computation with multiple tags.


class TagListingViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import tag_listing_view
        return tag_listing_view(context, request)

    def test_wo_tags_tool(self):
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_empty(self):
        context = testing.DummyModel()
        tags = context.tags = DummyTags()
        tags.getFrequency = lambda: []
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_nonempty(self):
        TAGS = [('foo', 2), ('bar', 1), ('baz', 3),]
        context = testing.DummyModel()
        tags = context.tags = DummyTags()
        tags.getFrequency = lambda: TAGS
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), len(TAGS))
        self.assertEqual(renderer.entries[0], {'name': 'bar', 'count': 1})
        self.assertEqual(renderer.entries[1], {'name': 'baz', 'count': 3})
        self.assertEqual(renderer.entries[2], {'name': 'foo', 'count': 2})

class CommunityTagListingViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import community_tag_listing_view
        return community_tag_listing_view(context, request)

    def test_wo_tags_tool(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                            'templates/community_taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)
        self.assertEqual(renderer.crumbs, 'KARL / Communities / community')

    def test_w_tags_tool_empty(self):
        context = testing.DummyModel()
        context.__name__ = 'community'
        tags = context.tags = DummyTags()
        def _getFrequency(tags=None, community=None):
            assert tags is None
            assert community == 'community'
            return []
        tags.getFrequency = _getFrequency
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                            'templates/community_taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_nonempty(self):
        TAGS = [('foo', 3), ('bar', 2), ('baz', 1)]
        context = testing.DummyModel()
        context.__name__ = 'community'
        tags = context.tags = DummyTags()
        def _getFrequency(tags=None, community=None):
            assert tags is None
            assert community == 'community'
            return TAGS
        tags.getFrequency = _getFrequency
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                            'templates/community_taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), len(TAGS))
        self.assertEqual(renderer.entries[0], {'name': 'bar', 'count': 2})
        self.assertEqual(renderer.entries[1], {'name': 'baz', 'count': 1})
        self.assertEqual(renderer.entries[2], {'name': 'foo', 'count': 3})

class ProfileTagListingViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import profile_tag_listing_view
        return profile_tag_listing_view(context, request)

    def test_wo_tags_tool(self):
        context = testing.DummyModel()
        context.__name__ = 'phred'
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                            'templates/profile_taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)
        self.assertEqual(renderer.crumbs, 'KARL / Profiles / phred')

    def test_w_tags_tool_empty(self):
        context = testing.DummyModel()
        context.__name__ = 'phred'
        tags = context.tags = DummyTags()
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['phred']
            assert community is None
            return []
        tags.getTags = _getTags
        def _getFrequency(tags=None, community=None, user=None):
            assert tags == []
            assert community is None
            assert user == 'phred'
            return []
        tags.getFrequency = _getFrequency
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                            'templates/profile_taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), 0)

    def test_w_tags_tool_nonempty(self):
        TAGS = [('foo', 3), ('bar', 2), ('baz', 1)]
        context = testing.DummyModel()
        context.__name__ = 'phred'
        tags = context.tags = DummyTags()
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['phred']
            assert community is None
            return [x[0] for x in TAGS]
        tags.getTags = _getTags
        def _getFrequency(tags=None, community=None, user=None):
            assert tags == [x[0] for x in TAGS]
            assert community is None
            assert user == 'phred'
            return TAGS
        tags.getFrequency = _getFrequency
        context.catalog = DummyCatalog()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                            'templates/profile_taglisting.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.entries), len(TAGS))
        self.assertEqual(renderer.entries[0], {'name': 'bar', 'count': 2})
        self.assertEqual(renderer.entries[1], {'name': 'baz', 'count': 1})
        self.assertEqual(renderer.entries[2], {'name': 'foo', 'count': 3})

class TagUsersViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import tag_users_view
        return tag_users_view(context, request)

    def test_with_tag_missing(self):
        request = testing.DummyRequest()
        request.params = {'docid': '1'}
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '400 Bad Request')

    def test_with_docid_missing(self):
        request = testing.DummyRequest()
        request.params = {'tag': 'tag1'}
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '400 Bad Request')

    def test_with_both_params_no_tags_tool(self):
        root = testing.DummyModel()
        path = root['path'] = testing.DummyModel()
        to = path['to'] = testing.DummyModel()
        target = to['item'] = testing.DummyModel()
        target.title = 'Target'
        testing.registerModels({'/path/to/item': target})
        request = testing.DummyRequest()
        request.params = {'tag': 'tag1', 'docid': '1'}
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        renderer = testing.registerDummyRenderer('templates/tagusers.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, 'tag1')
        self.assertEqual(renderer.url, 'http://example.com/path/to/item/')
        self.assertEqual(renderer.title, 'Target')
        self.assertEqual(len(renderer.users), 0)

    def test_with_both_params_w_tags_tool(self):
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        tags = context.tags = DummyTags()
        tags.getUsers = lambda tags=None, items=None, community=None: ['phred']
        tags.getTags = lambda items=None, users=None, community=None: ['tag2']
        path = context['path'] = testing.DummyModel()
        to = path['to'] = testing.DummyModel()
        target = to['item'] = testing.DummyModel()
        target.title = 'Target'
        testing.registerModels({'/path/to/item': target})
        profiles = context['profiles'] = testing.DummyModel()
        p1 = profiles['phred'] = testing.DummyModel()
        p1.firstname, p1.lastname = 'J. Phred', 'Bloggs'
        request = testing.DummyRequest()
        request.params = {'tag': 'tag1', 'docid': '1'}
        renderer = testing.registerDummyRenderer('templates/tagusers.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.users), 1)
        self.assertEqual(renderer.users[0]['login'], 'phred')
        self.assertEqual(renderer.users[0]['fullname'], 'J. Phred Bloggs')
        self.assertEqual(renderer.users[0]['also'], ['tag2'])

class CommunityTagUsersViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import community_tag_users_view
        return community_tag_users_view(context, request)

    def test_with_tag_missing(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {'docid': '1'}

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '400 Bad Request')

    def test_with_docid_missing(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {'tag': 'tag1'}

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '400 Bad Request')

    def test_with_both_params_no_tags_tool(self):
        root = testing.DummyModel()
        root.catalog = karltesting.DummyCatalog({1:'/community/target'})
        context = root['community'] = testing.DummyModel()
        target = context['target'] = testing.DummyModel()
        target.title = 'Target'
        testing.registerModels({'/community/target': target})
        request = testing.DummyRequest()
        request.params = {'tag': 'tag1', 'docid': '1'}
        renderer = testing.registerDummyRenderer(
                                'templates/community_tagusers.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.tag, 'tag1')
        self.assertEqual(renderer.url, 'http://example.com/community/target/')
        self.assertEqual(renderer.title, 'Target')
        self.assertEqual(len(renderer.users), 0)

    def test_with_both_params_w_tags_tool(self):
        root = testing.DummyModel()
        root.catalog = karltesting.DummyCatalog({1:'/community/target'})
        context = root['community'] = testing.DummyModel()
        target = context['target'] = testing.DummyModel()
        target.title = 'Target'
        testing.registerModels({'/community/target': target})
        tags = root.tags = DummyTags()
        def _getUsers(tags=None, items=None, community=None):
            assert list(tags) == ['tag1']
            assert list(items) == [1]
            assert community == 'community'
            return ['phred']
        tags.getUsers = _getUsers
        def _getTags(items=None, users=None, community=None):
            assert list(items) == [1]
            assert list(users) == ['phred']
            assert community == 'community'
            return ['tag2']
        tags.getTags = _getTags
        profiles = root['profiles'] = testing.DummyModel()
        p1 = profiles['phred'] = testing.DummyModel()
        p1.firstname, p1.lastname = 'J. Phred', 'Bloggs'
        request = testing.DummyRequest()
        request.params = {'tag': 'tag1', 'docid': '1'}
        renderer = testing.registerDummyRenderer(
                                'templates/community_tagusers.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.users), 1)
        self.assertEqual(renderer.users[0]['login'], 'phred')
        self.assertEqual(renderer.users[0]['fullname'], 'J. Phred Bloggs')
        self.assertEqual(renderer.users[0]['also'], ['tag2'])


class ManageTagsViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import manage_tags_view
        return manage_tags_view(context, request)

    def test_not_submitted(self):
        context = testing.DummyModel()
        context.__name__ = 'phred'
        tags = context.tags = DummyTags()
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['phred']
            assert community is None
            return ['tag1', 'tag2']
        tags.getTags = _getTags
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
                                'templates/profile_tagedit.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.tags), 2)
        self.assertEqual(renderer.tags[0], 'tag1')
        self.assertEqual(renderer.tags[1], 'tag2')

    def test_submitted_rename(self):
        context = testing.DummyModel()
        context.__name__ = 'phred'
        tags = context.tags = DummyTags()
        class DummyTag:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        def _getItems(tags=None, users=None, community=None):
            assert list(tags) == ['foo']
            assert list(users) == ['phred']
            assert community is None
            return [1, 2]
        tags.getItems = _getItems
        def _getTagObjects(items=None, users=None, tags=None, community=None):
            assert list(items) == [1, 2]
            assert list(users) == ['phred']
            assert tags is None
            assert community is None
            return [DummyTag(item=1, user='phred', name='foo'),
                    DummyTag(item=2, user='phred', name='foo'),
                    DummyTag(item=2, user='phred', name='baz'),
                   ]
        tags.getTagObjects = _getTagObjects
        _updated = []
        def _update(item, user, tags):
            _updated.append((item, user, tags))
        tags.update = _update
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['phred']
            assert community is None
            return ['bar', 'baz']
        tags.getTags = _getTags
        request = testing.DummyRequest()
        request.POST['form.rename'] = 'Rename tag'
        request.POST['old_tag'] = 'foo'
        request.POST['new_tag'] = 'bar'
        renderer = testing.registerDummyRenderer(
                                'templates/profile_tagedit.pt')

        self._callFUT(context, request)

        self.failUnless((1, 'phred', ['bar']) in _updated)
        self.failUnless((2, 'phred', ['bar', 'baz']) in _updated)

    def test_submitted_delete(self):
        context = testing.DummyModel()
        context.__name__ = 'phred'
        tags = context.tags = DummyTags()
        class DummyTag:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        def _getItems(tags=None, users=None, community=None):
            assert list(tags) == ['foo']
            assert list(users) == ['phred']
            assert community is None
            return [1, 2]
        tags.getItems = _getItems
        def _getTagObjects(items=None, users=None, tags=None, community=None):
            assert list(items) == [1, 2]
            assert list(users) == ['phred']
            assert tags is None
            assert community is None
            return [DummyTag(item=1, user='phred', name='foo'),
                    DummyTag(item=2, user='phred', name='foo'),
                    DummyTag(item=2, user='phred', name='baz'),
                   ]
        tags.getTagObjects = _getTagObjects
        _deleted = []
        def _delete(item=None, user=None, tag=None):
            _deleted.append((item, user, tag))
        tags.delete = _delete
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['phred']
            assert community is None
            return ['bar', 'baz']
        tags.getTags = _getTags
        request = testing.DummyRequest()
        request.POST['form.delete'] = 'Remove tag'
        request.POST['old_tag'] = 'foo'
        renderer = testing.registerDummyRenderer(
                                'templates/profile_tagedit.pt')

        self._callFUT(context, request)

        self.failUnless((1, 'phred', 'foo') in _deleted)
        self.failUnless((2, 'phred', 'foo') in _deleted)


class AjaxViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self.context = context = testing.DummyModel()
        context.tags = DummyTags()
        context.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()

    def _callAdd(self, context, request):
        from karl.views.tags import jquery_tag_add_view
        return jquery_tag_add_view(context, request)

    def _callDel(self, context, request):
        from karl.views.tags import jquery_tag_del_view
        return jquery_tag_del_view(context, request)

    def test_add(self):
        request = testing.DummyRequest()
        request.params = {'val': 'tag1'}
        response = self._callAdd(self.context, request)
        # We just check that the server returned OK
        # which means an empty dict.
        self.assertEqual(response.content_type, 'application/x-json')
        self.assertEqual(response.body, '{}')

    def test_add_space_fails(self):
        request = testing.DummyRequest()
        request.params = {'val': 'tag 1'}
        response = self._callAdd(self.context, request)
        # We just check that the server returned the error.
        self.assertEqual(response.content_type, 'application/x-json')
        self.assertEqual(response.body,  '{"error": "Adding tag failed, '
                                         'it contains illegal characters."}')

    def test_add_unicode_fails(self):
        request = testing.DummyRequest()
        request.params = {'val': u'tag\xe1'.encode('utf')}
        response = self._callAdd(self.context, request)
        # We just check that the server returned the error.
        self.assertEqual(response.content_type, 'application/x-json')
        self.assertEqual(response.body,  '{"error": "Adding tag failed, '
                                         'it contains illegal characters."}')

    def test_del(self):
        request = testing.DummyRequest()
        request.params = {'val': 'tag1'}
        # We delete a nonexistent tag, nevertheless the
        # server replies OK even in this case.
        response = self._callDel(self.context, request)
        # We just check that the server returned OK
        # which means an empty dict.
        self.assertEqual(response.content_type, 'application/x-json')
        self.assertEqual(response.body, '{}')

    def test_add_existing(self):
        request = testing.DummyRequest()
        request.params = {'val': 'tag1'}
        response = self._callAdd(self.context, request)
        self.assertEqual(response.content_type, 'application/x-json')
        self.assertEqual(response.body, '{}')
        #
        # Now, do it again.
        # Although the tag already exists, it just says ok.
        response = self._callAdd(self.context, request)
        self.assertEqual(response.content_type, 'application/x-json')
        self.assertEqual(response.body, '{}')


class TestJQueryTagSearchView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.tags import jquery_tag_search_view
        return jquery_tag_search_view(context, request)

    def test_it(self):
        from karl.models.interfaces import ITagQuery
        from zope.interface import Interface
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        request = testing.DummyRequest(params={'val':'ignored'})
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.headerlist[0],
                         ('Content-Type', 'application/x-json'))
        self.assertEqual(response.app_iter[0],
                         '[{"text": "foo"}, {"text": "bar"}]')


class DummyTagQuery:
    def __init__(self, context, request):
        pass
    def tags_with_prefix(self, val):
        return ['foo', 'bar']

class DummyDocumentMap:
    def docid_for_address(self, path):
        return 'docid'
    def address_for_docid(self, docid):
        return '/path/to/item'

class DummyCatalog:
    document_map = DummyDocumentMap()

class DummyTags:
    getTags_called_with = getItems_called_with = getUsers_called_with = None
    updated = deleted = None

    def __init__(self, tags=(), items=(1,), users=('dummy',)):
        self.items = items
        self.users = users
        self.tags = tags

    def getTags(self, items=None, users=None, community=None):
        self.getTags_called_with = (items, users, community)
        return self.tags

    def getItems(self, tags=None, users=None, community=None):
        self.getItems_called_with = (tags, users, community)
        return self.items

    def getUsers(self, tags=None, items=None, community=None):
        self.getUsers_called_with = (tags, items, community)
        return self.users

    def update(self, item, user, tags):
        self.updated = (item, user, tags)

    def delete(self, item=None, user=None, tag=None):
        self.deleted = (item, user, tag)


from karl.models.interfaces import ICommunityContent
from zope.interface import taggedValue
class IDummyBlogEntry(ICommunityContent):
    taggedValue('name', 'Blog Entry')
