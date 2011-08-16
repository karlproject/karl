import unittest
from pyramid import testing
from zope.testing.cleanup import cleanUp

class TestLiveSearchGroup(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.utilities.groupsearch import GroupSearch
        return GroupSearch

    def _makeOne(self, context, request, interfaces, term, containment=None):
        return self._getTargetClass()(context, request, interfaces, term,
                                      containment)

    def _register(self, batch):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        searchkw = {}
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                searchkw.update(kw)
                return len(batch), batch, resolver
            return search
        testing.registerAdapter(dummy_catalog_search, (Interface),
                                ICatalogSearch)
        return searchkw

    def test_makeCriteria(self):
        from pyramid.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('fred', ['group:foo', 'group:bar'])
        request = testing.DummyRequest()
        context = testing.DummyModel()
        from zope.interface import Interface
        thing = self._makeOne(context, request, [Interface], 'foo',
                              [Interface])
        criteria = thing._makeCriteria()
        self.assertEqual(criteria['texts'], 'foo')
        self.assertEqual(criteria['interfaces']['query'], [Interface])
        self.assertEqual(criteria['interfaces']['operator'], 'or')
        self.assertEqual(criteria['containment']['query'], [Interface])
        self.assertEqual(criteria['containment']['operator'], 'or')
        self.assertEqual(criteria['allowed']['query'],
                         ['system.Everyone', 'system.Authenticated',
                          'fred', 'group:foo', 'group:bar']
                         )
        self.assertEqual(criteria['allowed']['operator'], 'or')

    def test_makeCriteria_no_interfaces(self):
        from repoze.lemonade.interfaces import IContent
        from pyramid.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('fred', ['group:foo', 'group:bar'])
        request = testing.DummyRequest()
        context = testing.DummyModel()
        from zope.interface import Interface
        thing = self._makeOne(context, request, [], 'foo')
        criteria = thing._makeCriteria()
        self.assertEqual(criteria['texts'], 'foo')
        self.assertEqual(criteria['interfaces']['query'], [IContent])
        self.assertEqual(criteria['interfaces']['operator'], 'or')
        self.assertEqual(criteria['allowed']['query'],
                         ['system.Everyone', 'system.Authenticated',
                          'fred', 'group:foo', 'group:bar']
                         )
        self.assertEqual(criteria['allowed']['operator'], 'or')

    def test_call(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        from zope.interface import Interface
        self._register([1,2,3])
        thing = self._makeOne(context, request, [Interface], 'foo')
        num, docids, resolver = thing()
        self.assertEqual(docids, [1,2,3])
