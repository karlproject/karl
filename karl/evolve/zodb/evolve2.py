from datetime import datetime
from zope.component import getSiteManager

from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IObjectWillBeAddedEvent

from repoze.lemonade.content import create_content

from karl.content.interfaces import ICalendar
from karl.content.interfaces import ICalendarLayer
from karl.content.interfaces import ICalendarCategory

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IContent
from karl.models.subscribers import set_created

def evolve(context):
    # add default category and layer to all calendars
    # Prevent 'set_created' event handler from being called since it will,
    # in turn, set the content_modified attribute of community which is used
    # as the "Last Activity" in the user interface.  We don't want this tweak
    # to impact a community's last activity.  This means we need to set created
    # and modified on the new layers and categories ourselves.
    registry = getSiteManager()
    registry.adapters.unsubscribe(
        (IContent, IObjectWillBeAddedEvent), None, set_created)
    try:
        search = ICatalogSearch(context)
        default_category_name = ICalendarCategory.getTaggedValue('default_name')
        default_layer_name = ICalendarLayer.getTaggedValue('default_name')
        now = datetime.now()

        cnt, docids, resolver = search(interfaces=[ICalendar])
        for docid in docids:
            calendar = resolver(docid)
            default_category = create_content(ICalendarCategory, 'Default')
            default_category.created = default_category.modified = now
            if not default_category_name in calendar:
                calendar[default_category_name] = default_category
                local_layer = create_content(ICalendarLayer,
                                             "This Calendar's Events Only", 'blue',
                                             [model_path(default_category)])
                local_layer.created = local_layer.modified = now
                if not default_layer_name in calendar:
                    calendar[default_layer_name] = local_layer
    finally:
        registry.adapters.subscribe(
            (IContent, IObjectWillBeAddedEvent), None, set_created)
