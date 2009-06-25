import os
import sys
import time
import cPickle

from zope.event import notify
from zope.interface import implements
from zope.component import queryUtility

from repoze.catalog.catalog import Catalog
from repoze.catalog.interfaces import ICatalog

from karl.models.interfaces import ICatalogSearchCache
from karl.models.interfaces import ICatalogQueryEvent
from karl.utilities.lru import LRUCache

from BTrees.Length import Length

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

        if cache is None:
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
            num, docids = self._search(*arg, **kw)
            # we need to unroll here; a btree-based structure may have
            # a reference to its connection
            docids = list(docids)
            cache[key] = (num, docids)

        return cache.get(key)

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
