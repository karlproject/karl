import unittest

from karl import testing


class Test_clear_site_announce(unittest.TestCase):

    def _callFUT(self, root):
        from karl.scripts.site_announce import clear_site_announce
        return clear_site_announce(root)

    def test_it(self):
        root = testing.DummyModel(site_announcement='TESTING')
        previous, now = self._callFUT(root)
        self.assertEqual(previous, 'TESTING')
        self.assertEqual(now, '')
        self.assertEqual(root.site_announcement, '')


class Test_site_announce(unittest.TestCase):

    def _callFUT(self, root, *args):
        from karl.scripts.site_announce import set_site_announce
        return set_site_announce(root, *args)

    def test_no_args_no_current(self):
        root = testing.DummyModel()
        previous, now = self._callFUT(root)
        self.assertEqual(previous, '')
        self.assertEqual(now, '')
        self.failIf('site_announcement' in root.__dict__)

    def test_no_args_returns_current(self):
        root = testing.DummyModel(site_announcement='TESTING')
        previous, now = self._callFUT(root)
        self.assertEqual(previous, 'TESTING')
        self.assertEqual(now, 'TESTING')
        self.assertEqual(root.site_announcement, 'TESTING')

    def test_w_new_value(self):
        root = testing.DummyModel(site_announcement='TESTING')
        previous, now = self._callFUT(root, 'UPDATED')
        self.assertEqual(previous, 'TESTING')
        self.assertEqual(now, 'UPDATED')
        self.assertEqual(root.site_announcement, 'UPDATED')

    def test_w_new_value_multiple(self):
        root = testing.DummyModel(site_announcement='TESTING')
        previous, now = self._callFUT(root, 'MULTIPLE', 'ARGUMENTS')
        self.assertEqual(previous, 'TESTING')
        self.assertEqual(now, 'MULTIPLE ARGUMENTS')
        self.assertEqual(root.site_announcement, 'MULTIPLE ARGUMENTS')
