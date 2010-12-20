import unittest

class TestOfflineContextURL(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _getTargetClass(self):
        from karl.adapters.url import OfflineContextURL
        return OfflineContextURL

    def _makeOne(self, model=None):
        from repoze.bfg.testing import DummyModel
        if model is None:
            model = DummyModel()
        return self._getTargetClass()(model, None)

    def test_class_conforms_to_IContextURL(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import IContextURL
        verifyClass(IContextURL, self._getTargetClass())

    def test_instance_conforms_to_IContextURL(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IContextURL
        verifyObject(IContextURL, self._makeOne())

    def test_virtual_root_raises(self):
        url = self._makeOne()
        self.assertRaises(NotImplementedError, url.virtual_root)

    def test___call___no_settings(self):
        from repoze.bfg.testing import DummyModel
        context = DummyModel()
        url = self._makeOne(context)
        self.assertRaises(ValueError, url)

    def test___call___app_url_trailing_slash(self):
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerUtility
        class DummySettings(dict):
            offline_app_url = "http://offline.example.com/app/"
        registerUtility(DummySettings(), ISettings)
        parent = DummyModel()
        context = parent['foo'] = DummyModel()
        url = self._makeOne(context)
        self.assertEqual(url(), 'http://offline.example.com/app/foo')

    def test___call___no_parent(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import registerSettings
        registerSettings()
        context = DummyModel()
        url = self._makeOne(context)
        self.assertEqual(url(), 'http://offline.example.com/app/')

    def test___call___w_parent(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import registerSettings
        registerSettings()
        parent = DummyModel()
        context = parent['foo'] = DummyModel()
        url = self._makeOne(context)
        self.assertEqual(url(), 'http://offline.example.com/app/foo')

    def test___call___w_parent_chain(self):
        from repoze.bfg.testing import DummyModel
        from karl.testing import registerSettings
        registerSettings()
        parent = DummyModel()
        foo = parent['foo'] = DummyModel()
        context = foo['bar'] = DummyModel()
        url = self._makeOne(context)
        self.assertEqual(url(), 'http://offline.example.com/app/foo/bar')
