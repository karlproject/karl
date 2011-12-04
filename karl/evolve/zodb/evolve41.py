
from karl.utils import find_catalog
from repoze.catalog.indexes.keyword import CatalogKeywordIndex


def evolve(site):
    """Optimize CatalogKeywordIndexes.

    Requires zope.index 3.6.3.
    """
    catalog = find_catalog(site)
    for name, idx in catalog.items():
        if isinstance(idx, CatalogKeywordIndex):
            print "Optimizing keyword index '%s'..." % name
            idx.optimize()
