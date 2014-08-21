from pyramid.traversal import resource_path

from karl.models.interfaces import ICatalogSearch
from karl.content.interfaces import ICommunityFile


def remove_extracted_data(context, out=None):
    """ Remove the '_extracted_data' cache attr from files.
    """
    search = ICatalogSearch(context)
    count, docids, resolver = search(interfaces=[ICommunityFile])

    for docid in docids:
        doc = resolver(docid)
        if getattr(doc, '_extracted_data', None) is not None:
            path = resource_path(doc)
            if out is not None:
                print >>out, "Removing _extracted_data: %s." % path
            del doc._extracted_data
            yield doc
        doc._p_deactivate()
