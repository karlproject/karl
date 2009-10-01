import unittest

from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

class TestCachingCatalog(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.models.catalog import CachingCatalog
        return CachingCatalog

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_ICatalog(self):
        from zope.interface.verify import verifyClass
        from repoze.catalog.interfaces import ICatalog
        verifyClass(ICatalog, self._getTargetClass())

    def test_instance_conforms_to_ICatalog(self):
        from zope.interface.verify import verifyObject
        from repoze.catalog.interfaces import ICatalog
        verifyObject(ICatalog, self._makeOne())

    def _registerCache(self, cache):
        from karl.models.interfaces import ICatalogSearchCache
        testing.registerUtility(cache, ICatalogSearchCache)

    def test_clear(self):
        cache = DummyCache({1:1})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog.clear()
        self.assertEqual(cache, {})

    def test_index_doc(self):
        cache = DummyCache({1:1})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog.index_doc(1,1)
        self.assertEqual(cache, {})

    def test_reindex_doc(self):
        cache = DummyCache({1:1})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog.reindex_doc(1,1)
        self.assertEqual(cache, {})

    def test_unindex_doc(self):
        cache = DummyCache({1:1})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog.unindex_doc(1)
        self.assertEqual(cache, {})

    def test_setitem(self):
        cache = DummyCache({1:1})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        self.assertEqual(cache, {})

    def test_search(self):
        cache = DummyCache({})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        self.assertEqual(cache, {})
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))
        self.assertEqual(len(cache), 1)
        import cPickle
        key = cPickle.dumps(((), {'dummy':1}))
        self.failUnless(key in cache)
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))
        self.failUnless(key in cache)

    def test_search_no_catalog_cache_in_environ(self):
        cache = DummyCache({})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        class DummyOS:
            environ = {'NO_CATALOG_CACHE':1}
        catalog.os = DummyOS
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))
        self.assertEqual(len(cache), 0)

    def test_search_generation_0(self):
        cache = DummyCache({})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        class DummyOS:
            environ = {'NO_CATALOG_CACHE':1}
        catalog.os = DummyOS
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))

    def test_search_no_icatalog_search_cache(self):
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))

    def test_search_generation_None(self):
        cache = DummyCache({})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        catalog.generation = None
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))
        self.assertEqual(cache.generation, 0)

    def test_search_generation_gt_cachegen(self):
        from BTrees.Length import Length
        cache = DummyCache({})
        cache.generation = -1
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        catalog.generation = Length(1)
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))
        self.assertEqual(cache.generation, 2)

    def test_search_returns_generator(self):
        cache = DummyCache({})
        catalog = self._makeOne()
        self._registerCache(cache)
        def gen():
            yield 1
        def dummy(*arg, **kw):
            return (1, gen())
        catalog._search = dummy
        result = catalog.search(dummy=1)
        self.assertEqual(result, (1, [1]))
        self.assertEqual(len(cache), 1)

    def test_invalidate_generation_is_None(self):
        cache = DummyCache({})
        catalog = self._makeOne()
        self._registerCache(cache)
        catalog.generation = None
        catalog.invalidate()
        self.assertEqual(catalog.generation.value, 1)
        self.assertEqual(cache.generation, 1)

    def test_invalidate_generation_gt_sys_maxint(self):
        from BTrees.Length import Length
        import sys
        cache = DummyCache({})
        catalog = self._makeOne()
        self._registerCache(cache)
        catalog.generation = Length(sys.maxint + 1)
        catalog.invalidate()
        self.assertEqual(catalog.generation.value, 0)
        self.assertEqual(cache.generation, 0)

    def test_notify_on_query(self):
        handled = []
        from karl.models.interfaces import ICatalogQueryEvent
        testing.registerSubscriber(handled.append, ICatalogQueryEvent)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        result = catalog.search(dummy=1)
        self.assertEqual(result, (3, [1,2,3]))
        self.assertEqual(len(handled), 1)
        event = handled[0]
        self.assertEqual(event.catalog, catalog)
        self.assertEqual(event.query, {'dummy': 1})
        self.assertEqual(type(event.duration), float)
        self.assertEqual(event.result, result)

    def test_search_use_cache_is_false(self):
        cache = DummyCache({})
        self._registerCache(cache)
        catalog = self._makeOne()
        catalog['dummy'] = DummyIndex()
        catalog.index_doc(1,1)
        result = catalog.search(dummy=1,use_cache=False)
        self.assertEqual(result, (3, [1,2,3]))
        self.assertEqual(len(cache), 0)

class TestReindexCatalog(unittest.TestCase):
    def _callFUT(self, context, **kw):
        from karl.models.catalog import reindex_catalog
        return reindex_catalog(context, **kw)

    def test_it(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ISite
        a = testing.DummyModel()
        testing.registerModels({'a':a})
        L = []
        output = L.append
        site = testing.DummyModel()
        site.update_indexes = lambda *arg: L.append('updated')
        catalog = DummyCatalog({'a':1})
        directlyProvides(site, ISite)
        site.catalog = catalog
        transaction = DummyTransaction()
        self._callFUT(site, output=output, transaction=transaction)
        self.assertEqual(catalog.reindexed, [1])
        self.assertEqual(L,
                         ['updating indexes',
                          'updated',
                          '*** committing ***',
                          'reindexing a',
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 2)

    def test_it_pathre(self):
        import re
        from zope.interface import directlyProvides
        from karl.models.interfaces import ISite
        a = testing.DummyModel()
        b = testing.DummyModel()
        testing.registerModels({'a':a, 'b':b})
        L = []
        output = L.append
        site = testing.DummyModel()
        site.update_indexes = lambda *arg: L.append('updated')
        catalog = DummyCatalog({'a':1, 'b':2})
        directlyProvides(site, ISite)
        site.catalog = catalog
        transaction = DummyTransaction()
        self._callFUT(site, output=output, transaction=transaction,
                      path_re=re.compile('a'))
        self.assertEqual(catalog.reindexed, [1])
        self.assertEqual(L,
                         ['updating indexes',
                          'updated',
                          '*** committing ***',
                          'reindexing a',
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 2)

    def test_it_dryrun(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ISite
        a = testing.DummyModel()
        b = testing.DummyModel()
        testing.registerModels({'a':a, 'b':b})
        L = []
        output = L.append
        site = testing.DummyModel()
        site.update_indexes = lambda *arg: L.append('updated')
        catalog = DummyCatalog({'a':1, 'b':2})
        directlyProvides(site, ISite)
        site.catalog = catalog
        transaction = DummyTransaction()
        self._callFUT(site, output=output, transaction=transaction,
                      dry_run=True)
        self.assertEqual(catalog.reindexed, [1, 2])
        self.assertEqual(L,
                         ['updating indexes',
                          'updated',
                          '*** aborting ***',
                          'reindexing a',
                          'reindexing b',
                          '*** aborting ***'])
        self.assertEqual(transaction.aborted, 2)
        self.assertEqual(transaction.committed, 0)

    def test_it_with_indexes(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ISite
        a = testing.DummyModel()
        testing.registerModels({'a':a})
        L = []
        output = L.append
        site = testing.DummyModel()
        site.update_indexes = lambda *arg: L.append('updated')
        catalog = DummyCatalog({'a':1})
        catalog.index = DummyIndex()
        directlyProvides(site, ISite)
        site.catalog = catalog
        transaction = DummyTransaction()
        self._callFUT(site, output=output, transaction=transaction,
                      indexes=('index',))
        self.assertEqual(L,
                         ['updating indexes',
                          'updated',
                          '*** committing ***',
                          "reindexing only indexes ('index',)",
                          'reindexing a',
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 2)
        self.assertEqual(catalog.index.indexed, {1:a})

from repoze.catalog.interfaces import ICatalogIndex
from zope.interface import implements

class DummyCatalog(object):
    def __init__(self, address_to_docid):
        self.document_map = testing.DummyModel()
        self.document_map.address_to_docid = address_to_docid
        self.reindexed = []

    def __getitem__(self, k):
        return getattr(self, k)

    def reindex_doc(self, docid, model):
        self.reindexed.append(docid)

class DummyTransaction(object):
    def __init__(self):
        self.committed = 0
        self.aborted = 0
        
    def commit(self):
        self.committed += 1

    def abort(self):
        self.aborted += 1
        

class DummyIndex:
    implements(ICatalogIndex)
    def __init__(self):
        self.indexed = {}

    def index_doc(self, docid, val):
        self.indexed[docid] = val

    reindex_doc = index_doc

    def apply(self, *arg, **kw):
        return [1,2,3]

class DummyCache(dict):
    generation = 0
