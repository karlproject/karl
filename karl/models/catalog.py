import logging
import os
import sys
import time
import cPickle

import transaction

from zope.event import notify
from zope.interface import implements
from zope.component import queryUtility
from perfmetrics import metricmethod
from perfmetrics import MetricMod

from pyramid.traversal import find_resource
from repoze.catalog import Range
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.interfaces import ICatalog
from repoze.catalog.interfaces import ICatalogIndex
from zope.index.interfaces import IStatistics

from karl.models.interfaces import ICatalogSearchCache
from karl.models.interfaces import ICatalogQueryEvent
from karl.utilities.lru import LRUCache
from karl.utils import find_site

from BTrees.Length import Length
from ZODB.utils import u64

logger = logging.getLogger(__name__)

LARGE_RESULT_SET = 500

kjunk = 'timeit', 'debugload', 'underprofile'
def kallers(f):
    if f.f_back is not None:
        r = kallers(f.f_back)
    else:
        r = []
    mod = f.f_globals.get('__name__', '')
    if mod.startswith('karl.'):
        mod = mod[5:]
        if mod not in kjunk:
            r.append("%s:%s" % (mod, f.f_lineno))
    return r

class CachingCatalog(Catalog):
    implements(ICatalog)

    os = os # for unit tests
    generation = None # b/c

    def __init__(self):
        super(CachingCatalog, self).__init__()
        self.generation = Length(0)

    def clear(self):
        self.invalidate()
        super(CachingCatalog, self).clear()

    def index_doc(self, *arg, **kw):
        self.invalidate()
        super(CachingCatalog, self).index_doc(*arg, **kw)

    def unindex_doc(self, *arg, **kw):
        self.invalidate()
        super(CachingCatalog, self).unindex_doc(*arg, **kw)

    def reindex_doc(self, *arg, **kw):
        self.invalidate()
        super(CachingCatalog, self).reindex_doc(*arg, **kw)

    def __setitem__(self, *arg, **kw):
        self.invalidate()
        super(CachingCatalog, self).__setitem__(*arg, **kw)

    @MetricMod('CS.%s')
    @metricmethod
    def search(self, *arg, **kw):
        use_cache = True

        if 'use_cache' in kw:
            use_cache = kw.pop('use_cache')

        if 'NO_CATALOG_CACHE' in self.os.environ:
            use_cache = False

        if 'tags' in kw:
            # The tags index changes without invalidating the catalog,
            # so don't cache any query involving the tags index.
            use_cache = False

        if not use_cache:
            return self._search(*arg, **kw)

        cache = queryUtility(ICatalogSearchCache)

        caller = "(%s) %s" % (u64(self._p_oid) if self._p_oid else '',
                              '>'.join(kallers(sys._getframe(1))))

        if cache is None:
            logger.info('NOCACHE %s %s', caller, kw)
            return self._search(*arg, **kw)

        key = cPickle.dumps((arg, kw))

        generation = self.generation

        if generation is None:
            generation = Length(0)

        genval = generation.value

        if (genval == 0) or (genval > cache.generation):
            # an update in another process requires that the local cache be
            # invalidated
            cache.clear()
            cache.generation = genval

        if cache.get(key) is None:
            start = time.time()
            num, docids = self._search(*arg, **kw)
            logger.info('MISS %s %s %s',
                        caller, kw, time.time() - start)

            # We don't cache large result sets because the time it takes to
            # unroll the result set turns out to be far more time than it
            # takes to run the search. In a particular instance using OSI's
            # catalog a search that took 0.015s but returned nearly 35,295
            # results took over 50s to unroll the result set for caching,
            # significantly slowing search performance.
            if num > LARGE_RESULT_SET:
                return num, docids

            # we need to unroll here; a btree-based structure may have
            # a reference to its connection
            docids = list(docids)
            cache[key] = (num, docids)
        else:
            logger.info('HIT %s %s', caller, kw)

        return cache.get(key)

    @metricmethod
    def _search(self, *arg, **kw):
        start = time.time()
        res = super(CachingCatalog, self).search(*arg, **kw)
        duration = time.time() - start
        notify(CatalogQueryEvent(self, kw, duration, res))
        return res

    def invalidate(self):
        # Increment the generation; this tells *another process* that
        # its catalog cache needs to be cleared
        generation = self.generation

        if generation is None:
            generation = self.generation = Length(0)

        if generation.value >= sys.maxint:
            # don't keep growing the generation integer; wrap at sys.maxint
            self.generation.set(0)
        else:
            self.generation.change(1)

        # Clear the cache for *this process*
        cache = queryUtility(ICatalogSearchCache)
        if cache is not None:
            cache.clear()
            cache.generation = self.generation.value

# the ICatalogSearchCache component (wired in via ZCML)
cache = LRUCache(1000)
cache.generation = 0


class CatalogQueryEvent(object):
    implements(ICatalogQueryEvent)
    def __init__(self, catalog, query, duration, result):
        self.catalog = catalog
        self.query = query
        self.duration = duration
        self.result = result

def reindex_catalog(context, path_re=None, commit_interval=200, dry_run=False,
                    output=None, transaction=transaction, indexes=None):

    def commit_or_abort():
        if dry_run:
            output and output('*** aborting ***')
            transaction.abort()
        else:
            output and output('*** committing ***')
            transaction.commit()

    site = find_site(context)
    catalog = site.catalog

    output and output('updating indexes')
    site.update_indexes()
    commit_or_abort()

    if indexes is not None:
        output and output('reindexing only indexes %s' % str(indexes))

    i = 1
    for path, docid in catalog.document_map.address_to_docid.items():
        if path_re is not None and path_re.match(path) is None:
            continue
        output and output('reindexing %s' % path)
        try:
            model = find_resource(context, path)
        except KeyError:
            output and output('error: %s not found' % path)
            continue

        if indexes is None:
            catalog.reindex_doc(docid, model)
        else:
            for index in indexes:
                catalog[index].reindex_doc(docid, model)
        if i % commit_interval == 0:
            commit_or_abort()
        i+=1
    commit_or_abort()


_marker = object()


class GranularIndex(CatalogFieldIndex):
    """Indexes integer values using multiple granularity levels.

    The multiple levels of granularity make it possible to query large
    ranges without loading many IFTreeSets from the forward index.
    """
    implements(
        ICatalogIndex,
        IStatistics,
    )

    def __init__(self, discriminator, levels=(1000,)):
        """Create an index.

        levels is a sequence of integer coarseness levels.
        The default is (1000,).
        """
        self._levels = tuple(levels)
        super(GranularIndex, self).__init__(discriminator)

    def clear(self):
        """Initialize all mappings."""
        # The forward index maps an indexed value to IFSet(docids)
        self._fwd_index = self.family.IO.BTree()
        # The reverse index maps a docid to its index value
        self._rev_index = self.family.II.BTree()
        self._num_docs = Length(0)
        # self._granular_indexes: [(level, BTree(value -> IFSet([docid])))]
        self._granular_indexes = [(level, self.family.IO.BTree())
            for level in self._levels]

    def index_doc(self, docid, obj):
        if callable(self.discriminator):
            value = self.discriminator(obj, _marker)
        else:
            value = getattr(obj, self.discriminator, _marker)

        if value is _marker:
            # unindex the previous value
            self.unindex_doc(docid)
            return

        if not isinstance(value, int):
            raise ValueError(
                'GranularIndex cannot index non-integer value %s' % value)

        rev_index = self._rev_index
        if docid in rev_index:
            if docid in self._fwd_index.get(value, ()):
                # There's no need to index the doc; it's already up to date.
                return
            # unindex doc if present
            self.unindex_doc(docid)

        # Insert into forward index.
        set = self._fwd_index.get(value)
        if set is None:
            set = self.family.IF.TreeSet()
            self._fwd_index[value] = set
        set.insert(docid)

        # increment doc count
        self._num_docs.change(1)

        # Insert into reverse index.
        rev_index[docid] = value

        for level, ndx in self._granular_indexes:
            v = value // level
            set = ndx.get(v)
            if set is None:
                set = self.family.IF.TreeSet()
                ndx[v] = set
            set.insert(docid)

    def unindex_doc(self, docid):
        rev_index = self._rev_index
        value = rev_index.get(docid)
        if value is None:
            return  # not in index

        del rev_index[docid]

        self._num_docs.change(-1)

        ndx = self._fwd_index
        try:
            set = ndx[value]
            set.remove(docid)
            if not set:
                del ndx[value]
        except KeyError:
            pass

        for level, ndx in self._granular_indexes:
            v = value // level
            try:
                set = ndx[v]
                set.remove(docid)
                if not set:
                    del ndx[v]
            except KeyError:
                pass

    def search(self, queries, operator='or'):
        sets = []
        for query in queries:
            if isinstance(query, Range):
                query = query.as_tuple()
            else:
                query = (query, query)

            set = self.family.IF.multiunion(self.docids_in_range(*query))
            sets.append(set)

        result = None

        if len(sets) == 1:
            result = sets[0]
        elif operator == 'and':
            sets.sort()
            for set in sets:
                result = self.family.IF.intersection(set, result)
        else:
            result = self.family.IF.multiunion(sets)

        return result

    def docids_in_range(self, min, max):
        """List the docids for an integer range, inclusive on both ends.

        min or max can be None, making them unbounded.

        Returns an iterable of IFSets.
        """
        for level, ndx in sorted(self._granular_indexes, reverse=True):
            # Try to fill the range using coarse buckets first.
            # Use only buckets that completely fill the range.
            # For example, if start is 2 and level is 10, then we can't
            # use bucket 0; only buckets 1 and greater are useful.
            # Similarly, if end is 18 and level is 10, then we can't use
            # bucket 1; only buckets 0 and less are useful.
            if min is not None:
                a = (min + level - 1) // level
            else:
                a = None
            if max is not None:
                b = (max - level + 1) // level
            else:
                b = None
            # a and b are now coarse bucket values (or None).
            if a is None or b is None or a <= b:
                sets = []
                if a is not None and min < a * level:
                    # include the gap before
                    sets.extend(self.docids_in_range(min, a * level - 1))
                sets.extend(ndx.values(a, b))
                if b is not None and (b + 1) * level - 1 < max:
                    # include the gap after
                    sets.extend(self.docids_in_range((b + 1) * level, max))
                return sets

        return self._fwd_index.values(min, max)


def convert_to_granular(index, levels=(1000,)):
    """Create a GranularIndex from a FieldIndex.

    Copies the data without resolving the objects.
    """
    g = GranularIndex(index.discriminator, levels=levels)
    treeset = g.family.IF.TreeSet
    for value, docids in index._fwd_index.iteritems():
        g._fwd_index[value] = treeset(docids)
        for level, ndx in g._granular_indexes:
            v = value // level
            set = ndx.get(v)
            if set is None:
                set = treeset()
                ndx[v] = set
            set.update(docids)
    g._rev_index.update(index._rev_index)
    g._num_docs.value = index._num_docs()
    return g
