from repoze.bfg.traversal import find_model
from repoze.lemonade.content import IContent
from karl.content.interfaces import ICalendarCategory
from karl.content.interfaces import ICalendarLayer
from karl.utils import find_catalog

def evolve(context):
    catalog = find_catalog(context)
    index = catalog['texts']
    for docid in index.index._docweight.keys():
        try:
            path = catalog.document_map.address_for_docid(docid)
            context = find_model(context, path)
            if (ICalendarLayer.providedBy(context) or
                ICalendarCategory.providedBy(context) or
                not IContent.providedBy(context)):
                index.unindex_doc(docid)

            if hasattr(context, '_p_deactivate'):
                context._p_deactivate()
        except KeyError:
            # Work around some bad data in the db--some calendar categories
            # got added with '/' characters in their ids.  Skip them for now
            # until we can figure out what to do with them.
            print "Bad path in catalog: ", path
