from repoze.bfg.traversal import model_path

from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICalendarCategory

from karl.models.interfaces import ICatalogSearch
from karl.utils import find_catalog

def evolve(context):
    # fix up calendar events with an empty calendar_category (events
    # which were added before there was a physical _default_category_
    # category object).
    search = ICatalogSearch(context)
    default_category_name = ICalendarCategory.getTaggedValue('default_name')
    catalog = find_catalog(context)
    virtual = catalog['virtual']
        
    cnt, docids, resolver = search(interfaces=[ICalendarEvent])
    for docid in docids:
        event = resolver(docid)
        if event is None:
            continue
        if not getattr(event, 'calendar_category', ''):
            calendar = event.__parent__
            default_path = model_path(calendar) + '/' + default_category_name
            event.calendar_category = default_path
            virtual.reindex_doc(docid, event)
            
