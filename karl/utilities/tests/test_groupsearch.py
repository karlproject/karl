import unittest
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

class TestLiveSearchGroup(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.utilities.groupsearch import GroupSearch
        return GroupSearch

    def _makeOne(self, context, request, interfaces, term):
        return self._getTargetClass()(context, request, interfaces, term)

    def _register(self, batch):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        searchkw = {}
        def dummy_catalog_search(context, request):
            def resolver(x):
                return x
            def search(**kw):
                searchkw.update(kw)
                return len(batch), batch, resolver
            return search
        testing.registerAdapter(dummy_catalog_search, (Interface, Interface),
                                ICatalogSearch)
        return searchkw

    def test_makeCriteria(self):
        from repoze.bfg.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('fred', ['group:foo', 'group:bar'])
        request = testing.DummyRequest()
        context = testing.DummyModel()
        from zope.interface import Interface
        thing = self._makeOne(context, request, [Interface], 'foo')
        criteria = thing._makeCriteria()
        self.assertEqual(criteria['texts'], 'foo')
        self.assertEqual(criteria['interfaces']['query'], [Interface])
        self.assertEqual(criteria['interfaces']['operator'], 'or')
        self.assertEqual(criteria['allowed']['query'],
                         ['system.Everyone', 'system.Authenticated',
                          'fred', 'group:foo', 'group:bar']
                         )
        self.assertEqual(criteria['allowed']['operator'], 'or')

    def test_get_batch(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        from zope.interface import Interface
        self._register([1,2,3])
        thing = self._makeOne(context, request, [Interface], 'foo')
        batch = thing.get_batch()
        self.assertEqual(batch['entries'], [1,2,3])

    def test_call(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        from zope.interface import Interface
        self._register([1,2,3])
        thing = self._makeOne(context, request, [Interface], 'foo')
        num, docids, resolver = thing()
        self.assertEqual(docids, [1,2,3])
