from pyramid.traversal import resource_path

from karl.content.interfaces import ICommunityFile
from karl.models.interfaces import ICatalogSearch
from karl.utils import find_catalog

import mimetypes

def evolve(root):
    catalog = find_catalog(root)
    mimetype_index = catalog['mimetype']
    search = ICatalogSearch(root)
    docid_for_addr = catalog.document_map.docid_for_address
    count, docids, resolver = search(
        interfaces=[ICommunityFile],
        mimetype={
            'operator': 'or',
            'query': [
                'application/x-download',
                'application/x-application',
                'application/binary',
                'application/octet-stream',
                ]}
    )

    for docid in docids:
        doc = resolver(docid)
        mimetype = mimetypes.guess_type(doc.filename)[0]
        if mimetype is not None and mimetype != doc.mimetype:
            addr = resource_path(doc)
            print "Updating mimetype for %s: %s" % (addr, mimetype)
            doc.mimetype = mimetype
            mimetype_index.reindex_doc(docid_for_addr(addr), doc)
