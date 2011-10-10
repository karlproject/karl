from pyramid.traversal import find_resource
from karl.utils import find_catalog
import transaction

def _exists(context, path):
    try:
        find_resource(context, path)
        return True
    except KeyError:
        return False

def evolve(context):
    catalog = find_catalog(context)
    for path, docid in catalog.document_map.address_to_docid.items():
        if _exists(context, path):
            continue

        print "Unindexing:", path
        catalog.unindex_doc(docid)
