from pyramid.traversal import model_path
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
        changed = False
        websites = obj.websites
        new_websites = []
        for website in websites:
            if website.startswith('www'):
                print "Fix website for %s" % obj.__name__
                website = 'http://' + website
                changed = True
            new_websites.append(website)

        if changed:
            obj.websites = tuple(new_websites)
