from repoze.bfg.traversal import model_path

from repoze.lemonade.content import create_content

from karl.content.interfaces import ICalendar
from karl.content.interfaces import ICalendarLayer
from karl.content.interfaces import ICalendarCategory

from karl.models.interfaces import ICatalogSearch

def evolve(context):
    # add default category and layer to all calendars
    search = ICatalogSearch(context)
    default_category_name = ICalendarCategory.getTaggedValue('default_name')
    default_layer_name = ICalendarLayer.getTaggedValue('default_name')

    cnt, docids, resolver = search(interfaces=[ICalendar])
    for docid in docids:
        calendar = resolver(docid)
        default_category = create_content(ICalendarCategory, 'Default')
        if not default_category_name in calendar:
            calendar[default_category_name] = default_category
            local_layer = create_content(ICalendarLayer,
                                         "This Calendar's Events Only", 'blue',
                                         [model_path(default_category)])
            if not default_layer_name in calendar:
                calendar[default_layer_name] = local_layer

