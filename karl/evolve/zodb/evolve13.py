from karl.utilities.broken import prune_catalog
from karl.utilities.broken import remove_broken_objects
from karl.utils import find_catalog

import sys

def evolve(root):
    # Probably a fossil left over from Karl2 to Karl3 migration.  Some
    # addresses are in the catalog document_map as unicode objects, when they
    # should be UTF-8 encoded strings.
    docmap = find_catalog(root).document_map
    for docid, path in docmap.docid_to_address.items():
        if isinstance(path, unicode):
            print "Converting unicode path in document map:"
            print "\t%s" % path
            del docmap.address_to_docid[path]
            path = path.encode('UTF-8')
            docmap.address_to_docid[path] = docid
            docmap.docid_to_address[docid] = path

    # Prune catalog
    prune_catalog(root, sys.stdout)

    # We have a few broken objects again.  Why?
    remove_broken_objects(root, sys.stdout)
