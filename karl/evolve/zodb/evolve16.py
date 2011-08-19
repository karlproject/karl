from pyramid.traversal import find_resource
from karl.utils import find_catalog

def evolve(root):
    """
    We've added a modified_by index to the catalog to support renaming of
    users and reassignment of content from one user to another.  Without the
    index we'd have to walk the entire content tree in order to update
    modified_by attributes on documents.
    """
    print "Adding the 'modified_by' index to the catalog."
    root.update_indexes()
    catalog = find_catalog(root)
    index = catalog['modified_by']
    entries = list(catalog.document_map.docid_to_address.items())
    n_docs = len(entries)
    for n, (docid, addr) in enumerate(entries):
        if n % 500 == 0:
            print "Indexed %d/%d documents" % (n, n_docs)
        doc = find_resource(root, addr)
        index.index_doc(docid, doc)
        doc._p_deactivate()
