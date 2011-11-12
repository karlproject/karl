import unittest

from pyramid import testing

import karl.testing


class TestCachingCatalog(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        karl.testing.registerUtility(cache, ICatalogSearchCache)

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
        karl.testing.registerSubscriber(handled.append, ICatalogQueryEvent)
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
        karl.testing.registerModels({'a':a})
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
        karl.testing.registerModels({'a':a, 'b':b})
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
        karl.testing.registerModels({'a':a, 'b':b})
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
        karl.testing.registerModels({'a':a})
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


class TestGranularIndex(unittest.TestCase):

    def _class(self):
        from karl.models.catalog import GranularIndex
        return GranularIndex

    def _make(self, *args, **kw):
        return self._class()(*args, **kw)

    def _make_default(self):
        def discriminator(value, default):
            return value

        return self._make(discriminator)

    def test_verifyImplements_ICatalogIndex(self):
        from zope.interface.verify import verifyClass
        from repoze.catalog.interfaces import ICatalogIndex
        verifyClass(ICatalogIndex, self._class())

    def test_verifyProvides_ICatalogIndex(self):
        from zope.interface.verify import verifyObject
        from repoze.catalog.interfaces import ICatalogIndex
        verifyObject(ICatalogIndex, self._make_default())

    def test_verifyImplements_IStatistics(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IStatistics
        verifyClass(IStatistics, self._class())

    def test_verifyProvides_IStatistics(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IStatistics
        verifyObject(IStatistics, self._make_default())

    def test_verifyImplements_IInjection(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IInjection
        verifyClass(IInjection, self._class())

    def test_verifyProvides_IInjection(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IInjection
        verifyObject(IInjection, self._make_default())

    def test_verifyImplements_IIndexSearch(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IIndexSearch
        verifyClass(IIndexSearch, self._class())

    def test_verifyProvides_IIndexSearch(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IIndexSearch
        verifyObject(IIndexSearch, self._make_default())

    def test_verifyImplements_IIndexSort(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IIndexSort
        verifyClass(IIndexSort, self._class())

    def test_verifyProvides_IIndexSort(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IIndexSort
        verifyObject(IIndexSort, self._make_default())

    def test_verifyImplements_IPersistent(self):
        from zope.interface.verify import verifyClass
        from persistent.interfaces import IPersistent
        verifyClass(IPersistent, self._class())

    def test_verifyProvides_IPersistent(self):
        from zope.interface.verify import verifyObject
        from persistent.interfaces import IPersistent
        verifyObject(IPersistent, self._make_default())

    def test_ctor(self):
        obj = self._make_default()
        self.assertEqual(len(obj._granular_indexes), 1)
        self.assertEqual(obj._granular_indexes[0][0], 1000)
        self.assertFalse(obj._granular_indexes[0][1])
        self.assertEqual(obj._num_docs(), 0)

    def test_index_doc_with_new_doc(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        self.assertEqual(sorted(obj._fwd_index.keys()), [9000])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 9000)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9])
        self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_attr_discriminator(self):
        obj = self._make('x')
        obj.index_doc(5, testing.DummyModel(x=9005))
        self.assertEqual(sorted(obj._fwd_index.keys()), [9005])
        self.assertEqual(sorted(obj._fwd_index[9005]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 9005)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9])
        self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_discriminator_returns_default(self):
        def discriminator(obj, default):
            return default

        obj = self._make(discriminator)
        obj.index_doc(5, testing.DummyModel())
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_index_doc_with_non_integer_value(self):
        obj = self._make_default()
        self.assertRaises(ValueError, obj.index_doc, 5, 'x')

    def test_index_doc_with_changed_doc(self):
        obj = self._make_default()
        obj.index_doc(5, 14000)
        self.assertEqual(sorted(obj._fwd_index.keys()), [14000])
        self.assertEqual(sorted(obj._fwd_index[14000]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 14000)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [14])
        self.assertEqual(sorted(ndx[14]), [5])

        obj.index_doc(5, 9000)
        self.assertEqual(sorted(obj._fwd_index.keys()), [9000])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5])
        self.assertEqual(sorted(obj._rev_index.keys()), [5])
        self.assertEqual(obj._rev_index[5], 9000)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9])
        self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_no_changes(self):
        obj = self._make_default()
        for _i in range(2):
            obj.index_doc(5, 9000)
            self.assertEqual(sorted(obj._fwd_index.keys()), [9000])
            self.assertEqual(sorted(obj._fwd_index[9000]), [5])
            self.assertEqual(sorted(obj._rev_index.keys()), [5])
            self.assertEqual(obj._rev_index[5], 9000)
            ndx = obj._granular_indexes[0][1]
            self.assertEqual(sorted(ndx.keys()), [9])
            self.assertEqual(sorted(ndx[9]), [5])
        self.assertEqual(obj._num_docs(), 1)

    def test_index_doc_with_multiple_docs(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        self.assertEqual(sorted(obj._fwd_index.keys()), [9000, 9001, 11005])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5, 6])
        self.assertEqual(sorted(obj._fwd_index[9001]), [7])
        self.assertEqual(sorted(obj._fwd_index[11005]), [8])
        self.assertEqual(sorted(obj._rev_index.keys()), [5, 6, 7, 8])
        self.assertEqual(obj._rev_index[5], 9000)
        self.assertEqual(obj._rev_index[6], 9000)
        self.assertEqual(obj._rev_index[7], 9001)
        self.assertEqual(obj._rev_index[8], 11005)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9, 11])
        self.assertEqual(sorted(ndx[9]), [5, 6, 7])
        self.assertEqual(sorted(ndx[11]), [8])
        self.assertEqual(obj._num_docs(), 4)

    def test_unindex_doc_with_normal_indexes(self):
        obj = self._make_default()
        obj.index_doc(5, 14000)
        obj.unindex_doc(5)
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_unindex_doc_with_incomplete_trees(self):
        obj = self._make_default()
        obj.index_doc(5, 14000)
        del obj._fwd_index[14000]
        del obj._granular_indexes[0][1][14]
        obj.unindex_doc(5)
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_apply_with_one_value(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        self.assertEqual(sorted(obj.apply(9001)), [7])

    def test_apply_with_two_values(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        q = {'query': [9001, 11005]}
        self.assertEqual(sorted(obj.apply(q)), [7, 8])

    def test_apply_with_small_range(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(9000, 9001)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7])

    def test_apply_with_large_range(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7])

    def test_apply_with_multiple_ranges(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000), Range(11000, 11005)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

    def test_apply_with_union_ranges(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000), Range(9001, 11005)],
            'operator': 'or'}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

    def test_apply_with_intersecting_ranges(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(8000, 10000), Range(9001, 11005)],
            'operator': 'and'}
        self.assertEqual(sorted(obj.apply(q)), [7])

    def test_apply_with_range_that_excludes_9000(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(9001, 12000)]}
        self.assertEqual(sorted(obj.apply(q)), [7, 8])

    def test_apply_with_range_that_excludes_11006(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        obj.index_doc(9, 11006)
        from repoze.catalog import Range
        q = {'query': [Range(9000, 11005)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])

    def test_apply_without_maximum(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(9001, None)]}
        self.assertEqual(sorted(obj.apply(q)), [7, 8])

    def test_apply_without_minimum(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)
        from repoze.catalog import Range
        q = {'query': [Range(None, 11004)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7])

    def test_apply_with_unbounded_range(self):
        obj = self._make_default()
        obj.index_doc(5, 9000)
        obj.index_doc(6, 9000)
        obj.index_doc(7, 9001)
        obj.index_doc(8, 11005)

        # The operation should use _granular_indexes, not _fwd_index.
        del obj._fwd_index

        from repoze.catalog import Range
        q = {'query': [Range(None, None)]}
        self.assertEqual(sorted(obj.apply(q)), [5, 6, 7, 8])


class Test_convert_to_granular(unittest.TestCase):

    def _call(self, index, levels=(1000,)):
        from karl.models.catalog import convert_to_granular
        return convert_to_granular(index, levels)

    def test_with_empty_index(self):
        def discriminator(value, default):
            return value

        from repoze.catalog.indexes.field import CatalogFieldIndex
        src = CatalogFieldIndex(discriminator)
        obj = self._call(src)
        self.assertEqual(sorted(obj._fwd_index.keys()), [])
        self.assertEqual(sorted(obj._rev_index.keys()), [])
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [])
        self.assertEqual(obj._num_docs(), 0)

    def test_with_contents(self):
        def discriminator(value, default):
            return value

        from repoze.catalog.indexes.field import CatalogFieldIndex
        src = CatalogFieldIndex(discriminator)
        src.index_doc(5, 9000)
        src.index_doc(6, 9000)
        src.index_doc(7, 9001)
        src.index_doc(8, 11005)

        obj = self._call(src)

        self.assertEqual(sorted(obj._fwd_index.keys()), [9000, 9001, 11005])
        self.assertEqual(sorted(obj._fwd_index[9000]), [5, 6])
        self.assertEqual(sorted(obj._fwd_index[9001]), [7])
        self.assertEqual(sorted(obj._fwd_index[11005]), [8])
        self.assertEqual(sorted(obj._rev_index.keys()), [5, 6, 7, 8])
        self.assertEqual(obj._rev_index[5], 9000)
        self.assertEqual(obj._rev_index[6], 9000)
        self.assertEqual(obj._rev_index[7], 9001)
        self.assertEqual(obj._rev_index[8], 11005)
        ndx = obj._granular_indexes[0][1]
        self.assertEqual(sorted(ndx.keys()), [9, 11])
        self.assertEqual(sorted(ndx[9]), [5, 6, 7])
        self.assertEqual(sorted(ndx[11]), [8])
        self.assertEqual(obj._num_docs(), 4)
