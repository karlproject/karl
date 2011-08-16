from pyramid.traversal import find_model
from repoze.catalog.indexes.keyword import CatalogKeywordIndex

from karl.models.site import get_containment
from karl.utils import find_catalog


def evolve(site):
    """
    Add the new containment index to the catalog.
    """
    catalog = find_catalog(site)
    if 'containment' in catalog:
        print 'Nothing to do.'
        return

    index = CatalogKeywordIndex(get_containment)
    catalog['containment'] = index
    for docid, address in catalog.document_map.docid_to_address.items():
        print 'Indexing containment: %s' % address
        model = find_model(site, address)
        index.index_doc(docid, model)
        model._p_deactivate()