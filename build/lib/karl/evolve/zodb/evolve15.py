from pyramid.traversal import resource_path
from karl.content.views.files import ie_types
from karl.models.interfaces import ICatalogSearch
from karl.utils import find_catalog

def evolve(root):
    search = ICatalogSearch(root)
    catalog = find_catalog(root)
    index = catalog['mimetype']
    for old_type, new_type in ie_types.items():
        cnt, docids, resolver = search(mimetype=old_type)
        for docid in docids:
            doc = resolver(docid)
            print "Adjusting mimetype for %s" % resource_path(doc)
            doc.mimetype = new_type
            index.reindex_doc(docid, doc)
