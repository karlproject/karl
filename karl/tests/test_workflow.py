import unittest
from repoze.bfg import testing

class TestIntranetsContainment(unittest.TestCase):
    def _callFUT(self, ob):
        from karl.workflow import intranets_containment
        return intranets_containment(ob)

    def test_true(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IIntranets
        ob = testing.DummyModel()
        directlyProvides(ob, IIntranets)
        self.assertEqual(self._callFUT(ob), True)

    def test_false(self):
        ob = testing.DummyModel()
        self.assertEqual(self._callFUT(ob), False)

class TestPrivateCommunityContainment(unittest.TestCase):
    def _callFUT(self, ob):
        from karl.workflow import private_community_containment
        return private_community_containment(ob)

    def test_true(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        ob = testing.DummyModel()
        directlyProvides(ob, ICommunity)
        ob.security_state = 'private'
        self.assertEqual(self._callFUT(ob), True)

    def test_false(self):
        ob = testing.DummyModel()
        self.assertEqual(self._callFUT(ob), False)

    def test_false_in_intranet(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IIntranets
        from karl.models.interfaces import ICommunity
        ob = testing.DummyModel()
        ob.security_state = 'private'
        directlyProvides(ob, (IIntranets, ICommunity))
        self.assertEqual(self._callFUT(ob), False)

class TestPublicCommunityContainment(unittest.TestCase):
    def _callFUT(self, ob):
        from karl.workflow import public_community_containment
        return public_community_containment(ob)

    def test_true(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        ob = testing.DummyModel()
        directlyProvides(ob, ICommunity)
        ob.security_state = 'public'
        self.assertEqual(self._callFUT(ob), True)

    def test_false(self):
        ob = testing.DummyModel()
        self.assertEqual(self._callFUT(ob), False)

    def test_false_in_intranet(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IIntranets
        from karl.models.interfaces import ICommunity
        ob = testing.DummyModel()
        ob.security_state = 'public'
        directlyProvides(ob, (IIntranets, ICommunity))
        self.assertEqual(self._callFUT(ob), False)

class Test_content_to_inherits(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import content_to_inherits
        return content_to_inherits(ob, transition)

    def test_it_no_acl(self):
        ob = testing.DummyModel()
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        self._callFUT(ob, None)
        # doesn't blow up
        self.failIf(hasattr(ob, '__acl__'))
        # reindexes even if it's in the correct state
        self.assertEqual(index.indexed, {1234:ob})

    def test_it_has_acl(self):
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        self._callFUT(ob, None)
        self.failIf(hasattr(ob, '__acl__'))
        self.assertEqual(index.indexed, {1234: ob})

class Test_content_to_private(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import content_to_private
        return content_to_private(ob, transition)

    def test_it(self):
        from karl.models.interfaces import ICommunity
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        from zope.interface import directlyProvides
        directlyProvides(ob, ICommunity)
        ob.moderators_group_name = 'moderators'
        ob.members_group_name = 'members'
        self._callFUT(ob, None)
        from repoze.bfg.security import Allow
        from karl.security.policy import MODERATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import NO_INHERIT
        from karl.security.policy import ADMINISTRATOR_PERMS
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1], (Allow, 'moderators', MODERATOR_PERMS))
        self.assertEqual(ob.__acl__[2], (Allow, 'members', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[3], NO_INHERIT)
        self.assertEqual(index.indexed, {1234: ob})

class Test_to_profile(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import to_profile
        return to_profile(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import GUEST_PERMS
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import NO_INHERIT
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.creator = 'creator'
        ob.users = DummyUsers(**{'creator':
                                 {'groups':['group.community:foo:members']}})
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'creator', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[1],
                         (Allow, 'group.KarlUserAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[2],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[3],
                         (Allow, 'group.KarlStaff', GUEST_PERMS))
        self.assertEqual(ob.__acl__[4],
                         (Allow, 'group.community:foo:members', GUEST_PERMS))
        self.assertEqual(ob.__acl__[5], NO_INHERIT)
        self.assertEqual(index.indexed, {1234: ob})


class Test_comment_to_inherits(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import comment_to_inherits
        return comment_to_inherits(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.creator = 'creator'
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1],
                         (Allow, 'creator', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[2],
                         (Deny, Everyone, ('edit', 'delete')))
        self.assertEqual(index.indexed, {1234: ob})

class Test_forum_topic_to_inherits(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import forum_topic_to_inherits
        return forum_topic_to_inherits(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.creator = 'creator'
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1],
                         (Allow, 'creator', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[2],
                         (Deny, Everyone, ('edit', 'delete')))
        self.assertEqual(index.indexed, {1234: ob})

class Test_forum_to_inherits(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import forum_to_inherits
        return forum_to_inherits(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from karl.models.interfaces import ICommunity
        from karl.security.policy import CREATE
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.creator = 'creator'
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlStaff', (CREATE,)))
        self.assertEqual(index.indexed, {1234: ob})

class Test_intranet_content_to_inherits(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import intranet_content_to_inherits
        return intranet_content_to_inherits(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.creator = 'creator'
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1],
                         (Allow, 'creator', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[2],
                         (Deny, Everyone, ('edit', 'delete')))
        self.assertEqual(index.indexed, {1234: ob})

class Test_community_to_private(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import community_to_private
        return community_to_private(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import MODERATOR_PERMS
        from karl.security.policy import NO_INHERIT
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        ob.moderators_group_name = 'moderators'
        ob.members_group_name = 'members'
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1], (Allow, 'moderators', MODERATOR_PERMS))
        self.assertEqual(ob.__acl__[2], (Allow, 'members', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[3], NO_INHERIT)
        self.assertEqual(index.indexed, {1234: ob})

class Test_community_to_public(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import community_to_public
        return community_to_public(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import GUEST_PERMS
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import MODERATOR_PERMS
        from karl.security.policy import NO_INHERIT
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        ob.moderators_group_name = 'moderators'
        ob.members_group_name = 'members'
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1], (Allow, 'moderators', MODERATOR_PERMS))
        self.assertEqual(ob.__acl__[2], (Allow, 'members', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[3], (Allow, 'group.KarlStaff',
                                         GUEST_PERMS))
        self.assertEqual(ob.__acl__[4], NO_INHERIT)
        self.assertEqual(index.indexed, {1234: ob})

class Test_community_to_intranet(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import community_to_intranet
        return community_to_intranet(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import MODERATOR_PERMS
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        directlyProvides(ob, ICommunity)
        ob.moderators_group_name = 'moderators'
        ob.members_group_name = 'members'
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1], (Allow, 'moderators', MODERATOR_PERMS))
        self.assertEqual(ob.__acl__[2], (Allow, 'members', MEMBER_PERMS))
        self.assertEqual(index.indexed, {1234: ob})


class Test_blogentry_to_inherits(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import blogentry_to_inherits
        return blogentry_to_inherits(ob, transition)

    def test_it_has_no_acl(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import ADMINISTRATOR_PERMS
        ob = testing.DummyModel()
        ob.docid = 1234
        ob.creator = 'dummyUser'
        index = DummyIndex()
        ob.catalog = {'path': index}
        self._callFUT(ob, None)
        acl = ob.__acl__
        self.assertEqual(len(acl), 3)
        self.assertEqual(acl[0], (Allow, 'group.KarlAdmin',ADMINISTRATOR_PERMS))
        self.assertEqual(acl[1], (Allow, 'dummyUser', MEMBER_PERMS))
        self.assertEqual(acl[2], (Deny, Everyone, ('edit', 'delete')))

        self.assertEqual(index.indexed, {1234: ob})

    def test_it_has_acl(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import ADMINISTRATOR_PERMS
        ob = testing.DummyModel()
        ob.docid = 1234
        ob.creator = 'dummyUser'
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        self._callFUT(ob, None)

        acl = ob.__acl__
        self.assertEqual(len(acl), 3)
        self.assertEqual(acl[0], (Allow, 'group.KarlAdmin',ADMINISTRATOR_PERMS))
        self.assertEqual(acl[1], (Allow, 'dummyUser', MEMBER_PERMS))
        self.assertEqual(acl[2], (Deny, Everyone, ('edit', 'delete')))

        self.assertEqual(index.indexed, {1234: ob})

class Test_blogentry_to_private(unittest.TestCase):
    def _callFUT(self, ob, transition):
        from karl.workflow import blogentry_to_private
        return blogentry_to_private(ob, transition)

    def test_it(self):
        from zope.interface import directlyProvides
        from repoze.bfg.security import Allow
        from karl.models.interfaces import ICommunity
        from karl.security.policy import ADMINISTRATOR_PERMS
        from karl.security.policy import GUEST_PERMS
        from karl.security.policy import MODERATOR_PERMS
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import NO_INHERIT
        comm = testing.DummyModel()
        directlyProvides(comm, ICommunity)
        ob = testing.DummyModel()
        ob.__acl__ = []
        index = DummyIndex()
        ob.catalog = {'path': index}
        ob.docid = 1234
        ob.creator = 'b'
        directlyProvides(ob, ICommunity)
        ob.moderators_group_name = 'moderators'
        ob.members_group_name = 'members'
        self._callFUT(ob, None)
        self.assertEqual(ob.__acl__[0],
                         (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        self.assertEqual(ob.__acl__[1], (Allow, 'b', MEMBER_PERMS))
        self.assertEqual(ob.__acl__[2], (Allow, 'moderators', MODERATOR_PERMS))
        self.assertEqual(ob.__acl__[3], (Allow, 'members', GUEST_PERMS))
        self.assertEqual(ob.__acl__[4], NO_INHERIT)
        self.assertEqual(index.indexed, {1234: ob})


class TestReindex(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from karl.workflow import _reindex
        return _reindex(*arg, **kw)

    def test_with_allowed_index_present(self):
        from repoze.folder.interfaces import IFolder
        from zope.interface import directlyProvides
        root = testing.DummyModel()
        root.catalog = {}
        root.docid = 0
        path = root.catalog['path'] = DummyIndex()
        allowed = root.catalog['allowed'] = DummyIndex()
        one = testing.DummyModel()
        one.docid = 1
        two = testing.DummyModel()
        two.docid = 2
        directlyProvides(root, IFolder)
        root['one'] = one
        root['two'] = two
        self._callFUT(root)
        self.failUnless(path.indexed.keys(), [0])
        self.assertEqual(sorted(allowed.indexed.keys()), [0,1,2])

    def test_with_allowed_index_missing(self):
        from repoze.folder.interfaces import IFolder
        from zope.interface import directlyProvides
        root = testing.DummyModel()
        root.catalog = {}
        root.docid = 0
        path = root.catalog['path'] = DummyIndex()
        one = testing.DummyModel()
        one.docid = 1
        two = testing.DummyModel()
        two.docid = 2
        directlyProvides(root, IFolder)
        root['one'] = one
        root['two'] = two
        self._callFUT(root)
        self.failUnless(path.indexed.keys(), [0])

class Test_reset_profile(unittest.TestCase):
    def tearDown(self):
        testing.cleanUp()

    def setUp(self):
        testing.cleanUp()

    def _registerWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        return registerDummyWorkflow('security')

    def _callFUT(self, event):
        from karl.workflow import reset_profile
        reset_profile(event)

    def _makeSite(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        from zope.interface import directlyProvides
        registerContentFactory(None, IProfile)
        site = testing.DummyModel()
        site['profiles'] = testing.DummyModel()
        site.users = DummyUsers(
            userid={'groups': ['group.community:foo:members',
                               'group.another']})
        profile = site['profiles']['userid'] = testing.DummyModel()
        directlyProvides(profile, IProfile)
        profile.__acl__ = ['1']
        profile.creator = 'userid'
        profile.docid = 1234
        return site, profile

    def test_uninteresting_event(self):
        workflow = self._registerWorkflow()
        self._callFUT(object())
        self.failIf(workflow.resetted)

    def test_added_group_event(self):
        from zope.interface import implements
        from karl.models.interfaces import IUserAddedGroup
        workflow = self._registerWorkflow()
        class AddedGroup:
            implements(IUserAddedGroup)
            id = 'userid'
            login = 'userid'
            groups = ()

        event = AddedGroup()
        site, profile = self._makeSite()
        event.site = site
        self._callFUT(event)
        self.assertEqual(workflow.resetted, [profile])

    def test_removed_group_event(self):
        from zope.interface import implements
        from karl.models.interfaces import IUserRemovedGroup
        workflow = self._registerWorkflow()
        class RemovedGroup:
            implements(IUserRemovedGroup)
            id = 'userid'
            login = 'userid'
            groups = ()

        event = RemovedGroup()
        site, profile = self._makeSite()
        event.site = site
        self._callFUT(event)
        self.assertEqual(workflow.resetted, [profile])

class DummyContent:
    pass

class DummyCatalog:
    def reindex_doc(self, docid, obj): # pragma: no cover
        assert 0, "don't go here"

class DummyIndex:
    def __init__(self):
        self.indexed = {}
    def reindex_doc(self, docid, obj):
        self.indexed[docid] = obj

class DummyUsers:
    def __init__(self, **mapping):
        self.mapping = mapping

    def get_by_id(self, id):
        return self.mapping[id]

