
from karl.utils import find_catalog
from karl.models.catalog import convert_to_granular
from karl.models.catalog import GranularIndex


def evolve(site):
    """Convert date indexes to GranularIndex.
    """
    catalog = find_catalog(site)
    for name in ['creation_date', 'modified_date', 'content_modified',
            'start_date', 'end_date', 'publication_date']:
        index = catalog[name]
        if not isinstance(index, GranularIndex):
            print "Converting field index '%s' to GranularIndex..." % name
            catalog[name] = convert_to_granular(index)
