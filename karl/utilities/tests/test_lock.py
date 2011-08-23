import unittest
from karl import testing as karltesting
from repoze.bfg import testing

class TestLock(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def test_unlocked_by_default(self):
        from karl.utilities import lock
        context = karltesting.DummyModel()
        self.failIf(lock.is_locked(context))

    def test_lock(self):
        from datetime import datetime
        from karl.utilities import lock
        date = datetime(1985, 1, 1)
        context = karltesting.DummyModel()
        lock.lock(context, 'foo', date)
        self.failUnless(lock.is_locked(context, date))

    def test_lock_owner(self):
        context = karltesting.DummyModel()
        from karl.utilities import lock
        lock.lock(context, 'foo')
        self.failUnless(lock.owns_lock(context, 'foo'))
        self.failIf(lock.owns_lock(context, 'bar'))

    def test_lock_timeout(self):
        from datetime import datetime
        from karl.utilities import lock
        past = datetime(1955, 1, 1, 0, 0, 1)
        past_plus_1 = datetime(1955, 1, 1, 0, 0, 2)
        future = datetime(1985, 1, 1)
        context = karltesting.DummyModel()
        lock.lock(context, 'foo', past)
        self.failUnless(lock.is_locked(context, past_plus_1))
        self.failIf(lock.is_locked(context, future))

    def test_lockinfo(self):
        from datetime import datetime
        from karl.utilities import lock
        past = datetime(1985, 1, 1, 0, 0, 1)
        context = karltesting.DummyModel()
        lock.lock(context, 'foo', past)
        lockinfo = lock.lock_info(context)
        self.assertEqual('foo', lockinfo['userid'])
        self.assertEqual(past, lockinfo['time'])

    def test_clear(self):
        from karl.utilities import lock
        context = karltesting.DummyModel()
        lock.lock(context, 'foo')
        lock.clear(context)
        self.failIf(lock.is_locked(context))

    def test_lockdata(self):
        from datetime import datetime
        from karl.utilities import lock
        past = datetime(1985, 1, 1, 0, 0, 1)
        now = datetime(1985, 1, 1, 0, 0, 10)
        context = karltesting.DummyModel()
        request = testing.DummyRequest()
        site = karltesting.DummyRoot()
        site['bar'] = context
        lock.lock(context, 'foo', past)
        lockdata = lock.lock_info_for_view(context, request, now)
        self.failUnless(lockdata['is_locked'])
