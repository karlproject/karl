import unittest
from repoze.bfg import testing

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

class TestSecuredStateMachine(unittest.TestCase):
    def _getTargetClass(self):
        from osi.security import SecuredStateMachine
        return SecuredStateMachine

    def _makeOne(self, state_attr, states=None, initial_state=None):
        return self._getTargetClass()(state_attr, states, initial_state)

    def test_add_with_permission(self):
        machine = self._makeOne('state')
        machine.add('private', 'publish', 'public', None, permission='add')
        self.assertEqual(
            machine.states,
            {('private', 'publish'): ('public', None, {'permission': 'add'})}
            )

    def test_add_without_permission(self):
        machine = self._makeOne('state')
        machine.add('private', 'publish', 'public', None)
        self.assertEqual(
            machine.states,
            {('private', 'publish'): ('public', None, {'permission': None})}
            )

    def test_secured_transition_info_permissive(self):
        machine = self._makeOne('state')
        machine.add('private', 'publish', 'public', None)
        machine.add('private', 'reject', 'rejected', None, permission='add')
        testing.registerDummySecurityPolicy(permissive=True)
        request = testing.DummyRequest()
        context = testing.DummyModel()
        transitions = sorted(
            machine.secured_transition_info(context, request,
                                            'private'))
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]['permission'], None)
        self.assertEqual(transitions[1]['permission'], 'add')

    def test_secured_transition_info_not_permissive(self):
        machine = self._makeOne('state')
        machine.add('private', 'publish', 'public', None)
        machine.add('private', 'reject', 'rejected', None)
        testing.registerDummySecurityPolicy(permissive=False)
        request = testing.DummyRequest()
        context = testing.DummyModel()
        transitions = machine.secured_transition_info(context, request,
                                                      'private')
        self.assertEqual(len(transitions), 0)

    def test_secured_execute_permitted(self):
        args = []
        def dummy(state, newstate, transition_id, context, **kw):
            args.append((state, newstate, transition_id, context, kw))
        states = {('pending', 'publish'): ('published', dummy,
                                           {'permission':'add'}),
                  ('pending', 'reject'): ('private', dummy,
                                          {'permission':'add'}),
                  ('published', 'retract'): ('pending', dummy,
                                             {'permission':'add'}),
                  ('private', 'submit'): ('pending', dummy,
                                          {'permission':'add'}),
                  ('pending', None): ('published', dummy,
                                      {'permission':'add'}),}
        sm = self._makeOne('state', states=states, initial_state='pending')
        testing.registerDummySecurityPolicy(permissive=True)
        request = testing.DummyRequest()
        ob = testing.DummyModel()
        sm.secured_execute(ob, request, 'publish')
        self.assertEqual(ob.state, 'published')
        sm.secured_execute(ob, request, 'retract')
        self.assertEqual(ob.state, 'pending')
        sm.secured_execute(ob, request, 'reject')
        self.assertEqual(ob.state, 'private')
        sm.secured_execute(ob, request, 'submit')
        self.assertEqual(ob.state, 'pending')
        # catch-all
        sm.secured_execute(ob, request, None)
        self.assertEqual(ob.state, 'published')
        self.assertEqual(len(args), 5)
        self.assertEqual(args[0], ('pending', 'published', 'publish', ob,
                                   {'permission':'add'}))
        self.assertEqual(args[1], ('published', 'pending', 'retract', ob,
                                   {'permission':'add'}))
        self.assertEqual(args[2], ('pending', 'private', 'reject', ob,
                                   {'permission':'add'}))
        self.assertEqual(args[3], ('private', 'pending', 'submit', ob,
                                   {'permission':'add'}))
        self.assertEqual(args[4], ('pending', 'published', None, ob,
                                   {'permission':'add'}))
        from repoze.workflow.statemachine import StateMachineError
        self.assertRaises(StateMachineError, sm.secured_execute, ob, request,
                          'nosuch')

    def test_secured_execute_not_permitted(self):
        args = []
        def dummy(state, newstate, transition_id, context, **kw):
            args.append((state, newstate, transition_id, context, kw))
        states = {('pending', 'publish'): ('published', dummy,
                                           {'permission':'add'}),}

        sm = self._makeOne('state', states=states, initial_state='pending')
        testing.registerDummySecurityPolicy(permissive=False)
        request = testing.DummyRequest()
        ob = testing.DummyModel()
        from repoze.workflow.statemachine import StateMachineError
        self.assertRaises(StateMachineError, sm.secured_execute,
                          ob, request, 'publish')

    def test_secured_execute_request_is_None(self):
        args = []
        def dummy(state, newstate, transition_id, context, **kw):
            args.append((state, newstate, transition_id, context, kw))
        states = {('pending', 'publish'): ('published', dummy,
                                           {'permission':'add'}),}

        sm = self._makeOne('state', states=states, initial_state='pending')
        testing.registerDummySecurityPolicy(permissive=False)
        ob = testing.DummyModel()
        sm.secured_execute(ob, None, 'publish')
        self.assertEqual(ob.state, 'published')
