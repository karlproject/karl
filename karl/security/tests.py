import unittest

from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

class TestKARLSecurityPolicy(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.security.policy import KARLSecurityPolicy
        return KARLSecurityPolicy

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_class_implements_ISecurityPolicy(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ISecurityPolicy
        verifyClass(ISecurityPolicy, self._getTargetClass())

    def test_instance_implements_ISecurityPolicy(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ISecurityPolicy
        verifyObject(ISecurityPolicy, self._makeOne(lambda *arg: None))

    def test_permits(self):
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        from karl.security.policy import VIEW
        from karl.security.policy import MEMBER_PERMS
        from karl.security.policy import ALL
        from karl.security.policy import NO_INHERIT
        policy = self._makeOne(lambda *arg: [])
        root = testing.DummyModel()
        community = testing.DummyModel(__name__='community', __parent__=root)
        blog = testing.DummyModel(__name__='blog', __parent__=community)
        root.__acl__ = [
            (Allow, Authenticated, VIEW),
            ]
        community.__acl__ = [
            (Allow, 'fred', ALL),
            (Allow, 'wilma', VIEW),
            NO_INHERIT,
            ]
        blog.__acl__ = [
            (Allow, 'barney', MEMBER_PERMS),
            (Allow, 'wilma', VIEW),
            ]
        policy = self._makeOne(lambda request: request.principals)
        request = testing.DummyRequest()

        request.principals = ['wilma']
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'wilma', VIEW))
        result = policy.permits(blog, request, 'delete')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL))

        request.principals = ['fred']
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL))
        result = policy.permits(blog, request, 'doesntevenexistyet')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'fred', ALL))

        request.principals = ['barney']
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, blog)
        self.assertEqual(result.ace, (Allow, 'barney', MEMBER_PERMS))
        result = policy.permits(blog, request, 'administer')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL))
        
        request.principals = ['someguy']
        result = policy.permits(root, request, 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, (Allow, Authenticated, VIEW))
        result = policy.permits(blog, request, 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL))

        request.principals = []
        result = policy.permits(root, request, 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, None)

        request.principals = []
        context = testing.DummyModel()
        result = policy.permits(context, request, 'view')
        self.assertEqual(result, False)
        
    def test_principals_allowed_by_permission_direct(self):
        from repoze.bfg.security import Allow
        from karl.security.policy import NO_INHERIT
        context = testing.DummyModel()
        acl = [ (Allow, 'chrism', ('read', 'write')),
                NO_INHERIT,
                (Allow, 'other', 'read') ]
        context.__acl__ = acl
        policy = self._makeOne(lambda *arg: None)
        result = sorted(
            policy.principals_allowed_by_permission(context, 'read'))
        self.assertEqual(result, ['chrism'])

    def test_principals_allowed_by_permission(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from karl.security.policy import ALL
        from karl.security.policy import NO_INHERIT
        root = testing.DummyModel(__name__='', __parent__=None)
        community = testing.DummyModel(__name__='community', __parent__=root)
        blog = testing.DummyModel(__name__='blog', __parent__=community)
        root.__acl__ = [ (Allow, 'chrism', ('read', 'write')),
                         (Allow, 'other', ('read',)),
                         (Allow, 'jim', ALL)]
        community.__acl__ = [  (Deny, 'flooz', 'read'),
                               (Allow, 'flooz', 'read'),
                               (Allow, 'mork', 'read'),
                               (Deny, 'jim', 'read'),
                               (Allow, 'someguy', 'manage')]
        blog.__acl__ = [ (Allow, 'fred', 'read'),
                         NO_INHERIT]
        
        policy = self._makeOne(lambda *arg: None)
        result = sorted(policy.principals_allowed_by_permission(blog, 'read'))
        self.assertEqual(result, ['fred'])
        result = sorted(policy.principals_allowed_by_permission(community,
                                                                'read'))
        self.assertEqual(result, ['chrism', 'mork', 'other'])
        result = sorted(policy.principals_allowed_by_permission(community,
                                                                'read'))
        result = sorted(policy.principals_allowed_by_permission(root, 'read'))
        self.assertEqual(result, ['chrism', 'jim', 'other'])

    def test_principals_allowed_by_permission_no_acls(self):
        policy = self._makeOne(lambda *arg: None)
        context = testing.DummyModel()
        result = sorted(policy.principals_allowed_by_permission(context,'read'))
        self.assertEqual(result, [])

    def test_effective_principals(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.principals = ['fred']
        policy = self._makeOne(lambda request: request.principals)
        result = sorted(policy.effective_principals(request))
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
        self.assertEqual(result,
                         ['fred', Authenticated, Everyone])

    def test_no_effective_principals(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.principals = []
        policy = self._makeOne(lambda request: request.principals)
        result = sorted(policy.effective_principals(request))
        from repoze.bfg.security import Everyone
        self.assertEqual(result, [Everyone])

    def test_authenticated_userid(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.principals = ['fred']
        policy = self._makeOne(lambda request: request.principals)
        result = policy.authenticated_userid(request)
        self.assertEqual(result, 'fred')

    def test_no_authenticated_userid(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.principals = []
        policy = self._makeOne(lambda request: request.principals)
        result = policy.authenticated_userid(request)
        self.assertEqual(result, None)

class TestAllPermissionsList(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.security.policy import AllPermissionsList
        return AllPermissionsList

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        thing = self._makeOne()
        self.assertEqual(thing.__iter__(), ())
        self.failUnless('anything' in thing)

class TestGetWhoPrincipals(unittest.TestCase):
    def _callFUT(self, request):
        from karl.security.policy import get_who_principals
        return get_who_principals(request)

    def test_with_creds(self):
        request = testing.DummyRequest()
        request.environ = {'repoze.who.identity':
                           {'repoze.who.userid':'fred', 'groups':['a', 'b']}}
        result = self._callFUT(request)
        self.assertEqual(result, ['fred', 'a', 'b'])

    def test_no_creds(self):
        request = testing.DummyRequest()
        result = self._callFUT(request)
        self.assertEqual(result, [])

class TestRepozeWhoKARLSecurityPolicy(unittest.TestCase):
    def _callFUT(self):
        from karl.security.policy import RepozeWhoKARLSecurityPolicy
        return RepozeWhoKARLSecurityPolicy()

    def test_it(self):
        policy = self._callFUT()
        from karl.security.policy import get_who_principals
        self.assertEqual(policy.get_principals, get_who_principals)
        

class TestACLPathCache(unittest.TestCase):

    def _getTargetClass(self):
        from karl.security.cache import ACLPathCache
        return ACLPathCache

    def _makeOne(self):
        return self._getTargetClass()()

    def _makeACE(self, allow=True, principal='phreddy', permission='testing'):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        action = allow and Allow or Deny
        return (action, principal, permission)

    def _makeModel(self, name=None, parent=None, principals=('phreddy',)):
        from repoze.bfg.testing import DummyModel
        model = DummyModel()
        if parent is not None:
            parent[name] = model
        if principals:
            model.__acl__ = [self._makeACE(principal=x) for x in principals]
        return model

    def test_class_conforms_to_IACLPathCache(self):
        from zope.interface.verify import verifyClass
        from karl.security.cache import IACLPathCache
        verifyClass(IACLPathCache, self._getTargetClass())

    def test_instance_conforms_to_IACLPathCache(self):
        from zope.interface.verify import verifyObject
        from karl.security.cache import IACLPathCache
        verifyObject(IACLPathCache, self._makeOne())

    def test_ctor(self):
        cache = self._makeOne()
        self.assertEqual(len(cache._index), 0)

    def test_clear_default(self):
        cache = self._makeOne()
        root = self._makeModel()
        cache.index(root)
        self.assertEqual(len(cache._index), 1)
        cache.clear()
        self.assertEqual(len(cache._index), 0)

    def test_clear_nondefault(self):
        cache = self._makeOne()
        root = self._makeModel()
        cache.index(root)
        child = self._makeModel(name='child', parent=root, principals=('bob',))
        cache.index(child)
        self.assertEqual(len(cache._index), 2)
        cache.clear(child)
        self.assertEqual(len(cache._index), 1)
        self.assertEqual(cache._index.keys()[0], ())

    def test_clear_intermediate(self):
        cache = self._makeOne()
        root = self._makeModel()
        cache.index(root)
        child = self._makeModel('child', root, principals=('bob',))
        cache.index(child)
        grand = self._makeModel('grand', child, principals=('alice',))
        cache.index(grand)
        self.assertEqual(len(cache._index), 3)
        cache.clear(child)
        self.assertEqual(len(cache._index), 1)
        self.assertEqual(cache._index.keys()[0], ())

    def test_index_no_acl(self):
        cache = self._makeOne()
        root = self._makeModel()
        cache.index(root)
        child = self._makeModel('child', root, principals=())
        cache.index(child)
        self.assertEqual(len(cache._index), 1)
        self.assertEqual(cache._index.keys()[0], ())

    def test_lookup_root_uncached_no_acl_no_permission(self):
        cache = self._makeOne()
        root = self._makeModel(principals=())

        aces = cache.lookup(root)
        self.assertEqual(len(aces), 0)
        self.assertEqual(len(cache._index), 0)

    def test_lookup_root_uncached_w_acl_no_permission(self):
        from repoze.bfg.security import Allow
        cache = self._makeOne()
        root = self._makeModel()

        aces = cache.lookup(root)
        self.assertEqual(len(aces), 1)
        self.assertEqual(aces[0], (Allow, 'phreddy', 'testing'))
        self.assertEqual(len(cache._index), 1)

    def test_lookup_root_cached_w_acl_no_permission(self):
        from repoze.bfg.security import Allow
        cache = self._makeOne()
        root = self._makeModel()
        cache.index(root)
        root.__acl__.append(self._makeACE(principal='bob'))  # uncached

        aces = cache.lookup(root)
        self.assertEqual(len(aces), 1, aces)
        self.assertEqual(aces[0], (Allow, 'phreddy', 'testing'))
        self.assertEqual(len(cache._index), 1)

    def test_lookup_nonroot(self):
        from repoze.bfg.security import Allow
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=('bob',))
        grand = self._makeModel('grand', child, principals=('alice',))

        aces = cache.lookup(grand)
        self.assertEqual(len(aces), 3)
        self.assertEqual(aces[0], (Allow, 'alice', 'testing'))
        self.assertEqual(aces[1], (Allow, 'bob', 'testing'))
        self.assertEqual(aces[2], (Allow, 'phreddy', 'testing'))
        self.assertEqual(len(cache._index), 3)

    def test_lookup_nonroot_w_permission(self):
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=('bob',))
        grand = self._makeModel('grand', child, principals=('alice',))

        aces = cache.lookup(grand, 'view')
        self.assertEqual(len(aces), 0)
        self.assertEqual(len(cache._index), 3)

    def test_lookup_nonroot_sparse(self):
        from repoze.bfg.security import Allow
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=('bob',))
        grand = self._makeModel('grand', child, principals=())

        aces = cache.lookup(grand)
        self.assertEqual(len(aces), 2)
        self.assertEqual(aces[0], (Allow, 'bob', 'testing'))
        self.assertEqual(aces[1], (Allow, 'phreddy', 'testing'))
        self.assertEqual(len(cache._index), 2)

    def test_lookup_nonroot_sparse_w_permission(self):
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=('bob',))
        grand = self._makeModel('grand', child, principals=())

        aces = cache.lookup(grand, 'view')
        self.assertEqual(len(aces), 0)
        self.assertEqual(len(cache._index), 2)

    def test_lookup_nonroot_sparse_w_permission_w_all(self):
        from repoze.bfg.security import Allow
        from karl.security.policy import ALL
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=('bob',))
        grand = self._makeModel('grand', child, principals=())
        grand.__acl__ = [self._makeACE(True, 'alice', ALL)]

        aces = cache.lookup(grand, 'view')
        self.assertEqual(len(aces), 1)
        self.assertEqual(aces[0], (Allow, 'alice', ALL))
        self.assertEqual(len(cache._index), 3)

    def test_lookup_nonroot_sparse_w_allow_everyone(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Everyone
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=())
        child.__acl__ = [self._makeACE(True, Everyone)]
        grand = self._makeModel('grand', child, principals=('alice',))

        aces = cache.lookup(grand)
        self.assertEqual(len(aces), 2)
        self.assertEqual(aces[0], (Allow, 'alice', 'testing'))
        self.assertEqual(aces[1], (Allow, Everyone, 'testing'))
        self.assertEqual(len(cache._index), 2)

    def test_lookup_nonroot_sparse_w_deny_everyone(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        cache = self._makeOne()
        root = self._makeModel()
        child = self._makeModel('child', root, principals=())
        child.__acl__ = [self._makeACE(True, 'bob'),
                         self._makeACE(False, Everyone)]
        grand = self._makeModel('grand', child, principals=('alice',))

        aces = cache.lookup(grand)
        self.assertEqual(len(aces), 3)
        self.assertEqual(aces[0], (Allow, 'alice', 'testing'))
        self.assertEqual(aces[1], (Allow, 'bob', 'testing'))
        self.assertEqual(aces[2], (Deny, Everyone, 'testing'))
        self.assertEqual(len(cache._index), 2)

class TestACLChecker(unittest.TestCase):
    def _getTargetClass(self):
        from karl.security.policy import ACLChecker
        return ACLChecker

    def _makeOne(self, principals, permission):
        return self._getTargetClass()(principals, permission)

    def test_it(self):
        from repoze.bfg.security import Allow, Deny, Everyone
        from karl.security.policy import ALL
        acl_one = ((Allow, 'a', 'view'), (Allow, 'b', 'view'))
        acl_two = ((Allow, 'c', 'view'), (Allow, 'd', 'view'),)
        acl_three = ((Allow, 'd', ALL), (Allow, 'e', 'view'),
                     (Deny, Everyone, ALL),)
        from BTrees.IFBTree import IFSet
        data = []
        data.append([(0, [acl_one],), IFSet([0])])
        data.append([(1, [acl_one, acl_two]), IFSet([1,2,3])])
        data.append([(2, [acl_one, acl_two, acl_three]), IFSet([4,5,6])])
        data.append([(3, [acl_one]), IFSet()])

        checker = self._makeOne(('a', Everyone), 'view')
        result = checker(data)
        self.assertEqual(list(result), [0, 1, 2, 3])

        checker = self._makeOne(('b', Everyone), 'view')
        result = checker(data)
        self.assertEqual(list(result), [0, 1, 2, 3])

        checker = self._makeOne(('c', Everyone), 'view')
        result = checker(data)
        self.assertEqual(list(result), [1, 2, 3])

        checker = self._makeOne(('d', Everyone), 'view')
        result = checker(data)
        self.assertEqual(list(result), [1, 2, 3, 4, 5, 6])

        checker = self._makeOne(('e', Everyone), 'view')
        result = checker(data)
        self.assertEqual(list(result), [4,5,6])

        checker = self._makeOne(('nobody', Everyone), 'view')
        result = checker(data)
        self.assertEqual(list(result), [])



    
