from repoze.bfg.traversal import model_path
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog

def evolve(context):
    """
    Retroactively prepend 'http://' to any profile website URLs that
    start with a bare 'www.'.
    """
    catalog = find_catalog(context)
    search = ICatalogSearch(context)
    cnt, docids, resolver = search(interfaces=[IProfile])
    for docid in docids:
        obj = resolver(docid)
        if obj is None:
            continue # Work around catalog bug
        if obj.website and obj.website.startswith('www.'):
            print "Prepend 'http://' to profile website URL: %s" % model_path(obj)
            obj.website = "http://%s" % obj.website
