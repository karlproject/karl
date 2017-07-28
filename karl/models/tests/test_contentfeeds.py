import unittest

from karl.testing import registerUtility

class SiteEventsTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.contentfeeds import SiteEvents
        return SiteEvents

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_ISiteEvents(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ISiteEvents
        verifyClass(ISiteEvents, self._getTargetClass())

    def test_instance_conforms_to_ISiteEvents(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ISiteEvents
        verifyObject(ISiteEvents, self._makeOne())

    def test___iter___empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack), [])

    def test_checked_empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack.checked(['phred'], None)), [])

    def test_checked_creator_empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack.checked(['phred'], 'wilma')), [])

    def test_checked_no_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bar')
        self.assertEqual(list(stack.checked(['phred'], None)), [])

    def test_checked_allowed_no_created(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred'])
        self.assertEqual(list(stack.checked(['phred'], 'wilma')), [])

    def test_checked_allowed_non_empty(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred', 'bharney'])
        stack.push(foo='baz', allowed=['bharney'])
        stack.push(foo='bam', allowed=['phred'])

        found = [dict(x) for g, i, x in stack.checked(['phred'], None)]

        self.assertEqual(found[0],
                         {'foo': 'bam', 'allowed': ['phred']})
        self.assertEqual(found[1],
                         {'foo': 'bar', 'allowed': ['phred', 'bharney']})

    def test_checked_allowed_created_non_empty(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred', 'bharney'], userid='phred',
                   content_type='Community')
        stack.push(foo='baz', allowed=['bharney'])
        stack.push(foo='bam', allowed=['phred', 'bharney'],
                   content_creator='phred', content_type='Blog Entry')
        stack.push(foo='bat', allowed=['phred', 'bharney'],
                   content_creator='bharney', content_type='Blog Entry')
        stack.push(foo='bah', allowed=['phred'])

        found = [dict(x) for g, i, x in stack.checked(['phred'], 'phred')]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'bam', 'allowed': ['phred', 'bharney'],
                          'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(found[1],
                         {'foo': 'bar', 'allowed': ['phred', 'bharney'],
                          'userid': 'phred',
                          'content_type': 'Community'})

    def test_newer_empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack.newer(0, 0)), [])

    def test_newer_miss_gen_index(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux')
        self.assertEqual(list(stack.newer(0, 0)), [])

    def test_newer_miss_no_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        stack.push(foo='bam', baz='qux')
        self.assertEqual(list(stack.newer(0, 0, ['phred'])), [])

    def test_newer_miss_not_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        stack.push(foo='bam', baz='qux', allowed=['bharney'])
        self.assertEqual(list(stack.newer(0, 0, ['phred'])), [])

    def test_newer_miss_allowed_not_creator(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        stack.push(foo='bam', baz='qux', allowed=['phred'],
                   content_type='Blog Entry', userid='bharney')
        self.assertEqual(list(stack.newer(0, 0, ['phred'], 'phred')), [])

    def test_newer_miss_allowed_creator_community(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        stack.push(foo='bam', baz='qux', allowed=['phred'],
                   content_type='Community', userid='phred')

        found = [dict(x) for g, i, x in stack.newer(0, 0, ['phred'], 'phred')]

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0],
                         {'foo': 'bam',
                          'baz': 'qux',
                          'content_type': 'Community',
                          'userid': 'phred',
                          'allowed': ['phred'],
                         })

    def test_newer_hit(self):
        stack = self._makeOne()
        stack.push(foo='bar')
        stack.push(foo='baz')
        stack.push(foo='qux')

        found = [dict(x) for g, i, x in stack.newer(0, 0)]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'qux'})
        self.assertEqual(found[1],
                         {'foo': 'baz'})

    def test_newer_creator_hit(self):
        stack = self._makeOne()
        stack.push(foo='bar')
        stack.push(foo='baz', userid='phred', content_type='Blog Entry')
        stack.push(foo='qux', content_creator='phred',
                   content_type='Blog Entry')

        found = [dict(x) for g, i, x in stack.newer(0, 0, created_by='phred')]

        self.assertEqual(found[0],
                         {'foo': 'qux', 'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(found[1],
                         {'foo': 'baz', 'userid': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(len(found), 2)

    def test_newer_creator_hit_with_community(self):
        stack = self._makeOne()
        stack.push(foo='bar')
        stack.push(foo='baz', userid='phred', content_type='Community')
        stack.push(foo='qux', content_creator='phred',
                   content_type='Blog Entry')

        found = [dict(x) for g, i, x in stack.newer(0, 0, created_by='phred')]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'qux', 'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(found[1],
                         {'foo': 'baz', 'userid': 'phred',
                          'content_type': 'Community'})

    def test_newer_hit_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred'])
        stack.push(foo='baz', allowed=['bharney'])
        stack.push(foo='qux', allowed=['phred'])

        found = [dict(x)
                    for g, i, x in stack.newer(0, 0, ['phred', 'bharney'])]

        self.assertEqual(found[0],
                         {'foo': 'qux', 'allowed': ['phred']})
        self.assertEqual(found[1],
                         {'foo': 'baz', 'allowed': ['bharney']})

    def test_newer_hit_allowed_creator(self):
        stack = self._makeOne()
        stack.push(foo='baz', allowed=['bharney'], userid='bharney',
                   content_type='Blog Entry')
        stack.push(foo='bar', allowed=['phred'], userid='phred',
                   content_type='Blog Entry')
        stack.push(foo='qux', allowed=['phred'], content_creator='phred',
                   content_type='Blog Entry')

        found = [dict(x)
                    for g, i, x in stack.newer(0, 0, ['phred', 'bharney'],
                                               'phred')]

        self.assertEqual(found[0],
                         {'foo': 'qux', 'allowed': ['phred'],
                          'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(found[1],
                         {'foo': 'bar', 'allowed': ['phred'],
                          'userid': 'phred', 'content_type': 'Blog Entry'})
        self.assertEqual(len(found), 2)

    def test_newer_hit_allowed_creator_with_community(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred'], userid='phred',
                   content_type='Community')
        stack.push(foo='baz', allowed=['bharney'], userid='bharney',
                   content_type='Blog Entry')
        stack.push(foo='qux', allowed=['phred'], content_creator='phred',
                   content_type='Blog Entry')

        found = [dict(x)
                    for g, i, x in stack.newer(0, 0, ['phred', 'bharney'],
                                               'phred')]

        self.assertEqual(found[0],
                         {'foo': 'qux', 'allowed': ['phred'],
                          'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(len(found), 1)

    def test_older_empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack.older(0, 0)), [])

    def test_older_miss_gen_index(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux')
        self.assertEqual(list(stack.older(0, 0)), [])

    def test_older_miss_no_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bam', baz='qux')
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        self.assertEqual(list(stack.older(0, 1, ['phred'])), [])

    def test_older_miss_not_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bam', baz='qux', allowed=['bharney'])
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        self.assertEqual(list(stack.older(0, 1, ['phred'])), [])

    def test_older_miss_allowed_not_creator(self):
        stack = self._makeOne()
        stack.push(foo='bar', baz='qux', allowed=['phred'])
        stack.push(foo='bam', baz='qux', allowed=['phred'],
                   content_type='Blog Entry', userid='bharney')
        self.assertEqual(list(stack.older(0, 1, ['phred'], 'phred')), [])

    def test_older_miss_allowed_creator_community(self):
        stack = self._makeOne()
        stack.push(foo='bam', baz='qux', allowed=['phred'],
                   content_type='Community', userid='phred')
        stack.push(foo='bar', baz='qux', allowed=['phred'])

        found = [dict(x) for g, i, x in stack.older(0, 1, ['phred'], 'phred')]

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0],
                         {'foo': 'bam',
                          'baz': 'qux',
                          'content_type': 'Community',
                          'userid': 'phred',
                          'allowed': ['phred'],
                         })

    def test_older_hit(self):
        stack = self._makeOne()
        stack.push(foo='bar')
        stack.push(foo='baz')
        stack.push(foo='qux')

        found = [dict(x) for g, i, x in stack.older(0, 2)]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'baz'})
        self.assertEqual(found[1],
                         {'foo': 'bar'})

    def test_older_creator_hit(self):
        stack = self._makeOne()
        stack.push(foo='baz', userid='phred', content_type='Blog Entry')
        stack.push(foo='qux', content_creator='phred',
                   content_type='Blog Entry')
        stack.push(foo='bar')

        found = [dict(x) for g, i, x in stack.older(0, 2, created_by='phred')]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'qux', 'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(found[1],
                         {'foo': 'baz', 'userid': 'phred',
                          'content_type': 'Blog Entry'})

    def test_older_creator_hit_with_community(self):
        stack = self._makeOne()
        stack.push(foo='baz', userid='phred', content_type='Community')
        stack.push(foo='qux', content_creator='phred',
                   content_type='Blog Entry')
        stack.push(foo='bar')

        found = [dict(x) for g, i, x in stack.older(0, 2, created_by='phred')]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'qux', 'content_creator': 'phred',
                          'content_type': 'Blog Entry'})
        self.assertEqual(found[1],
                         {'foo': 'baz', 'userid': 'phred',
                          'content_type': 'Community'})

    def test_older_hit_allowed(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred'])
        stack.push(foo='baz', allowed=['bharney'])
        stack.push(foo='qux', allowed=['phred'])

        found = [dict(x)
                    for g, i, x in stack.older(0, 2, ['phred', 'bharney'])]

        self.assertEqual(len(found), 2)
        self.assertEqual(found[0],
                         {'foo': 'baz', 'allowed': ['bharney']})
        self.assertEqual(found[1],
                         {'foo': 'bar', 'allowed': ['phred']})

    def test_older_hit_allowed_creator(self):
        stack = self._makeOne()
        stack.push(foo='baz', allowed=['bharney'], userid='bharney',
                   content_type='Blog Entry')
        stack.push(foo='bar', allowed=['phred'], userid='phred',
                   content_type='Blog Entry')
        stack.push(foo='qux', allowed=['phred'], content_creator='phred',
                   content_type='Blog Entry')

        found = [dict(x)
                    for g, i, x in stack.older(0, 2, ['phred', 'bharney'],
                                               'phred')]

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0],
                         {'foo': 'bar', 'allowed': ['phred'],
                          'userid': 'phred', 'content_type': 'Blog Entry'})

    def test_older_hit_allowed_creator_with_community(self):
        stack = self._makeOne()
        stack.push(foo='bar', allowed=['phred'], userid='phred',
                   content_type='Community')
        stack.push(foo='baz', allowed=['bharney'], userid='bharney',
                   content_type='Blog Entry')
        stack.push(foo='qux', allowed=['phred'], content_creator='phred',
                   content_type='Blog Entry')

        found = [dict(x)
                    for g, i, x in stack.older(0, 2, ['phred', 'bharney'],
                                               'phred')]

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0],
                         {'foo': 'bar', 'allowed': ['phred'],
                          'userid': 'phred',
                          'content_type': 'Community'})

    def test_push_one(self):
        stack = self._makeOne()
        stack.push(foo='bar')

        found = [dict(x) for g, i, x in stack]

        self.assertEqual(found[0], {'foo': 'bar'})

    def test_push_many(self):
        stack = self._makeOne()
        stack.push(foo='bar')
        stack.push(foo='baz')
        stack.push(foo='qux')

        found = [dict(x) for g, i, x in stack]

        self.assertEqual(found[0], {'foo': 'qux'})
        self.assertEqual(found[1], {'foo': 'baz'})
        self.assertEqual(found[2], {'foo': 'bar'})


class _EventSubscriberTestsBase:

    _old_now = None

    def setUp(self):
        from pyramid.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from pyramid.testing import cleanUp
        cleanUp()

        if self._old_now is not None:
            self._setNow(self._old_now)

    def _setNow(self, callable):
        from karl.models import contentfeeds
        contentfeeds._NOW, self._old_now = callable, contentfeeds._NOW

    def _makeSite(self):
        from zope.interface import directlyProvides
        from pyramid.security import DENY_ALL
        from repoze.lemonade.content import create_content
        from repoze.lemonade.testing import registerContentFactory
        from karl.testing import DummyModel
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IProfile
        registerContentFactory(DummyModel, ICommunity)
        registerContentFactory(DummyModel, IProfile)
        site = DummyModel() # no events
        site.catalog = DummyCatalog()
        site.events = DummyEvents()
        site.tags = DummyTags()
        site['communities'] = DummyModel()
        c = create_content(ICommunity,
                           title="Testing",
                           description='blah blah blah' * 256,
                          )
        directlyProvides(c, ICommunity)
        site['communities']['testing'] = c
        c.docid = 123
        c.__acl__ = [('Allow', 'group:KarlAdmin', ('view',)),
                     ('Allow',
                        'group.community:testing:moderators', ('view',)),
                     ('Allow', 'group.community:testing:members', ('view',)),
                     DENY_ALL,
                    ]
        site['profiles'] = DummyModel()
        p = create_content(IProfile,
                           title="J. Phred Bloggs")
        directlyProvides(p, IProfile)
        p.creator = p.modified_by = 'phred'
        site['profiles']['phred'] = p
        p.docid = 456
        return site, c, p

    def _makeContent(self, community, name, **kw):
        from zope.interface import Interface
        from zope.interface import taggedValue
        from zope.interface import directlyProvides
        from repoze.lemonade.content import create_content
        from repoze.lemonade.testing import registerContentFactory
        from karl.testing import DummyModel
        base = kw.pop('base_interface', Interface)
        class IDummy(base):
            name = taggedValue('name', 'Dummy')
        registerContentFactory(DummyModel, IDummy)
        dummy = community[name] = create_content(IDummy, **kw)
        dummy.docid = 789
        directlyProvides(dummy, IDummy)
        return dummy # __acl__ is missing to imply acquired.


class Test_user_joined_community(_EventSubscriberTestsBase,
                                 unittest.TestCase):

    def _callFUT(self, event):
        from karl.models.contentfeeds import user_joined_community
        return user_joined_community(event)

    def _makeEvent(self, add_interface=True, **kw):
        from zope.interface import classImplements
        from karl.models.interfaces import IUserAddedGroup
        class DummyEvent:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        if add_interface:
            classImplements(DummyEvent, IUserAddedGroup)
        return DummyEvent(**kw)

    def test_not_IUserAddedGroup(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(add_interface=False)

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_non_community_group(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(site=site,
                                id='phred',
                                login='phred@example.com',
                                groups=set(['a', 'b']),
                                old_groups=set(['a']))

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_w_nonesuch_community_group(self):
        from pyramid.interfaces import IAuthorizationPolicy
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        event = self._makeEvent(site=site,
                                id='phred',
                                login='phred@example.com',
                                groups=set(
                                    ['a',
                                     'group.community:nonesuch:members',
                                    ]),
                                old_groups=set(['a']))

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_w_community_group(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        event = self._makeEvent(site=site,
                                id='phred',
                                login='phred@example.com',
                                groups=set(
                                    ['a',
                                     'group.community:testing:members',
                                     'group.community:testing:moderators',
                                    ]),
                                old_groups=set(['a']))

        self._callFUT(event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'joined_left')
        self.assertEqual(info['operation'], 'joined')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Community')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['title'], community.title)
        self.assertEqual(info['description'], community.description)
        self.assertEqual(info['short_description'],
                         '%s...' % community.description[:256])
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((123,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])


class Test_user_left_community(_EventSubscriberTestsBase,
                               unittest.TestCase):

    def _callFUT(self, event):
        from karl.models.contentfeeds import user_left_community
        return user_left_community(event)

    def _makeEvent(self, add_interface=True, **kw):
        from zope.interface import classImplements
        from karl.models.interfaces import IUserRemovedGroup
        class DummyEvent:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        if add_interface:
            classImplements(DummyEvent, IUserRemovedGroup)
        return DummyEvent(**kw)

    def test_not_IUserRemovedGroup(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(add_interface=False)

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_non_community_group(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(site=site,
                                id='phred',
                                login='phred@example.com',
                                groups=set(['a']),
                                old_groups=set(['a', 'b']),
                               )

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_w_nonesuch_community_group(self):
        from pyramid.interfaces import IAuthorizationPolicy
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        event = self._makeEvent(site=site,
                                id='phred',
                                login='phred@example.com',
                                groups=set(['a']),
                                old_groups=set(
                                    ['a',
                                     'group.community:nonesuch:members',
                                    ]),
                               )

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_w_community_group(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        event = self._makeEvent(site=site,
                                id='phred',
                                login='phred@example.com',
                                groups=set(['a']),
                                old_groups=set(
                                    ['a',
                                     'group.community:testing:members',
                                     'group.community:testing:moderators',
                                    ]),
                               )

        self._callFUT(event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'joined_left')
        self.assertEqual(info['operation'], 'left')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Community')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['title'], community.title)
        self.assertEqual(info['description'], community.description)
        self.assertEqual(info['short_description'],
                         '%s...' % community.description[:256])
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((123,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])


class Test_user_added_content(_EventSubscriberTestsBase,
                              unittest.TestCase):

    def _callFUT(self, context, event):
        from karl.models.contentfeeds import user_added_content
        return user_added_content(context, event)

    def _makeEvent(self, add_interface=True, **kw):
        from zope.interface import classImplements
        from repoze.folder.interfaces import IObjectAddedEvent
        class DummyEvent:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        if add_interface:
            classImplements(DummyEvent, IObjectAddedEvent)
        return DummyEvent(**kw)

    def test_not_IObjectAddedEvent(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(add_interface=False)

        self._callFUT(object(), event)

        self.failIf(site.events._pushed)

    def test_added_community(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        community.creator = 'phred'
        event = self._makeEvent(object=community)

        self._callFUT(community, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_community')
        self.assertEqual(info['operation'], 'added')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Community')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/communities/testing')
        self.assertEqual(info['title'], community.title)
        self.assertEqual(info['description'], community.description)
        self.assertEqual(info['short_description'],
                         '%s...' % community.description[:256])
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((123,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_added_profile(self):
        from datetime import datetime
        from pyramid.interfaces import IAuthorizationPolicy
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        event = self._makeEvent(object=profile)

        self._callFUT(profile, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_profile')
        self.assertEqual(info['operation'], 'added')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'J. Phred Bloggs')
        self.assertEqual(info['context_url'], '/profiles/phred')
        self.assertEqual(info['content_type'], 'Person')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/profiles/phred')
        self.assertEqual(info['title'], 'J. Phred Bloggs')
        self.assertEqual(info['description'], '')
        self.assertEqual(info['short_description'], '')
        self.assertEqual(info['comment_count'], 0)
        self.assertEqual(info['author'], 'J. Phred Bloggs')
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((456,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_added_content_inside_profile(self):
        from datetime import datetime
        from pyramid.interfaces import IAuthorizationPolicy
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        content = self._makeContent(profile, 'photo',
                                    creator = 'phred',
                                    modified_by = 'phred',
                                    title='Phred @ Beach',
                                    description = 'DESC')
        event = self._makeEvent(object=content)

        self._callFUT(content, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_other')
        self.assertEqual(info['operation'], 'added')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'J. Phred Bloggs')
        self.assertEqual(info['context_url'], '/profiles/phred')
        self.assertEqual(info['content_type'], 'Dummy')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/profiles/phred/photo')
        self.assertEqual(info['title'], 'Phred @ Beach')
        self.assertEqual(info['description'], 'DESC')
        self.assertEqual(info['short_description'], 'DESC')
        self.assertEqual(info['comment_count'], 0)
        self.assertEqual(info['author'], 'J. Phred Bloggs')
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((789,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    @unittest.expectedFailure
    def test_added_non_community_non_comment(self):
        from datetime import datetime
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.testing import DummyModel
        from karl.models.interfaces import IPosts
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        content = self._makeContent(community, 'content',
                                    creator = 'phred',
                                    title='TITLE',
                                    description = 'DESC',
                                    base_interface = IPosts,
                                   )
        comments = content['comments'] = DummyModel()
        comments['one'] = DummyModel()
        comments['two'] = DummyModel()
        event = self._makeEvent(object=content)

        self._callFUT(content, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_other')
        self.assertEqual(info['operation'], 'added')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Dummy')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/communities/testing/content')
        self.assertEqual(info['title'], 'TITLE')
        self.assertEqual(info['description'], 'DESC')
        self.assertEqual(info['short_description'], 'DESC')
        self.assertEqual(info['comment_count'], len(comments))
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((789,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    @unittest.expectedFailure
    def test_added_comment(self):
        from datetime import datetime
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.testing import DummyModel
        from karl.models.interfaces import IPosts
        from karl.models.interfaces import IComment
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        content = self._makeContent(community, 'content',
                                    creator = 'bharney',
                                    title='TITLE',
                                    description = 'DESC',
                                    base_interface = IPosts,
                                   )
        comment = self._makeContent(community, 'comment',
                                    creator = 'phred',
                                    title='TITLE',
                                    description = 'DESC',
                                    base_interface = IComment,
                                   )
        comments = content['comments'] = DummyModel()
        comments['one'] = comment
        event = self._makeEvent(object=comment)

        self._callFUT(comment, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_other')
        self.assertEqual(info['operation'], 'added')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Dummy')
        self.assertEqual(info['content_creator'], 'bharney')
        self.assertEqual(info['url'],
                         '/communities/testing/content/comments/one')
        self.assertEqual(info['title'], 'TITLE')
        self.assertEqual(info['description'], 'DESC')
        self.assertEqual(info['short_description'], 'DESC')
        self.assertEqual(info['comment_count'], 0)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((789,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])


class Test_user_modified_content(_EventSubscriberTestsBase,
                                 unittest.TestCase):

    def _callFUT(self, context, event):
        from karl.models.contentfeeds import user_modified_content
        return user_modified_content(context, event)

    def _makeEvent(self, add_interface=True, **kw):
        from zope.interface import classImplements
        from karl.models.interfaces import IObjectModifiedEvent
        class DummyEvent:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        if add_interface:
            classImplements(DummyEvent, IObjectModifiedEvent)
        return DummyEvent(**kw)

    def test_not_IObjectModifiedEvent(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(add_interface=False)

        self._callFUT(object(), event)

        self.failIf(site.events._pushed)

    def test_modified_community(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        community.modified_by = 'phred'
        event = self._makeEvent(object=community)

        self._callFUT(community, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_community')
        self.assertEqual(info['operation'], 'edited')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Community')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/communities/testing')
        self.assertEqual(info['title'], community.title)
        self.assertEqual(info['description'], community.description)
        self.assertEqual(info['short_description'],
                         '%s...' % community.description[:256])
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((123,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_modified_profile(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        event = self._makeEvent(object=profile)

        self._callFUT(profile, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_profile')
        self.assertEqual(info['operation'], 'edited')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'J. Phred Bloggs')
        self.assertEqual(info['context_url'], '/profiles/phred')
        self.assertEqual(info['content_type'], 'Person')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/profiles/phred')
        self.assertEqual(info['title'], 'J. Phred Bloggs')
        self.assertEqual(info['description'], '')
        self.assertEqual(info['short_description'], '')
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], 'J. Phred Bloggs')
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((456,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_modified_content_inside_profile(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        content = self._makeContent(profile, 'photo',
                                    creator = 'phred',
                                    modified_by = 'phred',
                                    title='Phred @ Beach',
                                    description = 'DESC')
        event = self._makeEvent(object=content)

        self._callFUT(content, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_other')
        self.assertEqual(info['operation'], 'edited')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'J. Phred Bloggs')
        self.assertEqual(info['context_url'], '/profiles/phred')
        self.assertEqual(info['content_type'], 'Dummy')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/profiles/phred/photo')
        self.assertEqual(info['title'], 'Phred @ Beach')
        self.assertEqual(info['description'], 'DESC')
        self.assertEqual(info['short_description'], 'DESC')
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], 'J. Phred Bloggs')
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((789,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_modified_non_community(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        content = self._makeContent(community, 'content',
                                    modified_by = 'phred',
                                    title='TITLE',
                                    description = 'DESC')
        event = self._makeEvent(object=content)

        self._callFUT(content, event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'added_edited_other')
        self.assertEqual(info['operation'], 'edited')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Dummy')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/communities/testing/content')
        self.assertEqual(info['title'], 'TITLE')
        self.assertEqual(info['description'], 'DESC')
        self.assertEqual(info['short_description'], 'DESC')
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((789,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])


class Test_user_tagged_content(_EventSubscriberTestsBase,
                                 unittest.TestCase):

    def _callFUT(self, event):
        from karl.models.contentfeeds import user_tagged_content
        return user_tagged_content(event)

    def _makeEvent(self, add_interface=True, **kw):
        from zope.interface import classImplements
        from karl.tagging.interfaces import ITagAddedEvent
        class DummyEvent:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        if add_interface:
            classImplements(DummyEvent, ITagAddedEvent)
        return DummyEvent(**kw)

    def test_not_ITagAddedEvent(self):
        site, community, profile = self._makeSite()
        event = self._makeEvent(add_interface=False)

        self._callFUT(event)

        self.failIf(site.events._pushed)

    def test_tagged_community(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.testing import DummyRequest
        from pyramid.threadlocal import manager
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        site.catalog.document_map._map[community.docid
                                      ] = '/communities/testing'
        # WAAA:  set up thread-locals
        manager.push({'request': DummyRequest(context=community),
                      'registry': manager.get()['registry']})
        event = self._makeEvent(item=community.docid,
                                user=profile.__name__,
                                name='youreit',
                               )

        self._callFUT(event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'tagged_community')
        self.assertEqual(info['operation'], 'tagged')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Community')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/communities/testing')
        self.assertEqual(info['title'], community.title)
        self.assertEqual(info['description'], community.description)
        self.assertEqual(info['short_description'],
                         '%s...' % community.description[:256])
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tagname'], 'youreit')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((123,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_tagged_profile(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.testing import DummyRequest
        from pyramid.threadlocal import manager
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        site.catalog.document_map._map[profile.docid] = '/profiles/phred'
        # WAAA:  set up thread-locals
        manager.push({'request': DummyRequest(context=profile),
                      'registry': manager.get()['registry']})
        event = self._makeEvent(item=profile.docid,
                                user=profile.__name__,
                                name='youreit',
                               )

        self._callFUT(event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'tagged_profile')
        self.assertEqual(info['operation'], 'tagged')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'J. Phred Bloggs')
        self.assertEqual(info['context_url'], '/profiles/phred')
        self.assertEqual(info['content_type'], 'Person')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/profiles/phred')
        self.assertEqual(info['title'], 'J. Phred Bloggs')
        self.assertEqual(info['description'], '')
        self.assertEqual(info['short_description'], '')
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], 'J. Phred Bloggs')
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tagname'], 'youreit')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((456,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

    def test_tagged_non_community(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.testing import DummyRequest
        from pyramid.threadlocal import manager
        from datetime import datetime
        NOW = datetime(2010, 7, 13, 12, 47, 12)
        self._setNow(lambda: NOW)
        registerUtility(DummyACLPolicy(), IAuthorizationPolicy)
        site, community, profile = self._makeSite()
        content = self._makeContent(community, 'content',
                                    modified_by = 'phred',
                                    title='TITLE',
                                    description = 'DESC',
                                    docid=31415)
        site.catalog.document_map._map[content.docid
                                      ] = '/communities/testing/content'
        # WAAA:  set up thread-locals
        manager.push({'request': DummyRequest(context=content),
                      'registry': manager.get()['registry']})
        event = self._makeEvent(item=content.docid,
                                user=profile.__name__,
                                name='youreit',
                               )

        self._callFUT(event)

        self.assertEqual(len(site.events._pushed), 1)
        info = site.events._pushed[0]
        self.assertEqual(info['timestamp'], NOW)
        self.assertEqual(info['flavor'], 'tagged_other')
        self.assertEqual(info['operation'], 'tagged')
        self.assertEqual(info['userid'], 'phred')
        self.assertEqual(info['context_name'], 'Testing')
        self.assertEqual(info['context_url'], '/communities/testing')
        self.assertEqual(info['content_type'], 'Dummy')
        self.assertEqual(info['content_creator'], 'phred')
        self.assertEqual(info['url'], '/communities/testing/content')
        self.assertEqual(info['title'], 'TITLE')
        self.assertEqual(info['description'], 'DESC')
        self.assertEqual(info['short_description'], 'DESC')
        self.assertEqual(info['comment_count'], False)
        self.assertEqual(info['author'], profile.title)
        self.assertEqual(info['profile_url'], '/profiles/phred')
        self.assertEqual(info['thumbnail'],
                         '/profiles/phred/profile_thumbnail')
        self.assertEqual(info['tagname'], 'youreit')
        self.assertEqual(info['tags'],
                         ['australia', 'africa', 'north_america'])
        self.assertEqual(site.tags._called_with, ((789,), None, None))
        self.assertEqual(sorted(info['allowed']),
                         ['group.KarlAdmin',
                          'group.community:testing:members',
                          'group.community:testing:moderators',
                         ])

class DummyACLPolicy:

    def __init__(self, community_name='testing'):
        self._community_name = community_name

    def principals_allowed_by_permission(self, context, permission):
        return ['group.KarlAdmin',
                'group.community:%s:members' % self._community_name,
                'group.community:%s:moderators' % self._community_name,
               ]


class DummyEvents:
    def __init__(self):
        self._pushed = []

    def push(self, **kw):
        self._pushed.append(kw)


class DummyDocumentMap:
    def __init__(self):
        self._map = {}

    def address_for_docid(self, docid):
        return self._map.get(docid)


class DummyCatalog:
    def __init__(self):
        self.document_map = DummyDocumentMap()


class DummyTags:
    _called_with = None

    def getCloud(self, items=None, users=None, community=None):
        self._called_with = items, users, community
        return set([('north_america', 3),
                    ('africa', 5),
                    ('europe', 1),
                    ('australia', 7),
                   ])
