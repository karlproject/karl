import re
import urllib

from repoze.bfg.traversal import find_model
from repoze.bfg.traversal import find_root
from repoze.bfg.traversal import model_path

from karl.content.interfaces import ICalendarCategory
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICalendarLayer
from karl.models.interfaces import ICatalogSearch
from karl.models.subscribers import index_content
from karl.models.subscribers import reindex_content
from karl.utilities.randomid import unfriendly_random_id

def evolve(context):
    root = find_root(context)
    searcher = ICatalogSearch(root)
    categories_and_layers_query = dict(
        interfaces={'query':[ICalendarCategory, ICalendarLayer],
                    'operator':'or'},
        )
    total, docids, resolver = searcher(**categories_and_layers_query)
    changed_categories = {}
    for docid in docids:
        ob = resolver(docid)
        if ob is None:
            # slash in path, likely
            path = root.catalog.document_map.docid_to_address.get(docid)
            if path is not None:
                container_path, ob_name = path.rsplit('/', 1)
                container = find_model(root, container_path)
                name = urllib.unquote(ob_name)
                ob = container.get(name)
            
        if ob is not None:
            ob_name = ob.__name__
            if not (ob_name.startswith('_default_') or is_opaque_id(ob_name)):
                old_path = model_path(ob)
                container = ob.__parent__
                new_name = generate_name(container)
                del container[ob_name]
                ob.__name__ = new_name # XXX required?
                container.add(new_name, ob, send_events=False)
                new_path = model_path(ob)
                index_content(ob, None)
                print 'path fixed: %s -> %s' % (old_path, new_path)
                if ICalendarCategory.providedBy(ob):
                    changed_categories[old_path] = new_path

    if changed_categories:
        # fix layer.paths
        layers_query = dict(interfaces=[ICalendarLayer])
        total, docids, resolver = searcher(**layers_query)
        for docid in docids:
            layer = resolver(docid)
            if layer is not None:
                new_paths = []
                changed = []
                for path in layer.paths:
                    if path in changed_categories:
                        new_paths.append(changed_categories[path])
                        changed.append((path, changed_categories[path]))
                    else:
                        new_paths.append(path)

                if changed:
                    layer.paths = new_paths
                    reindex_content(layer, None)
                    print 'layer fixed: %s, %s' % (
                        model_path(layer), [ '%s -> %s' % x for x in changed ])

        # fix the category of events
        events_query = dict(
            interfaces=[ICalendarEvent],
            )
        total, docids, resolver = searcher(**events_query)
        for docid in docids:
            event = resolver(docid)
            if event is not None:
                category = event.calendar_category
                if category in changed_categories:
                    old_category = event.calendar_category
                    new_category = changed_categories[category]
                    event.calendar_category = new_category
                    reindex_content(event, None)
                    print 'event fixed: %s, %s -> %s' % (
                        model_path(event),
                        old_category,
                        new_category)

def generate_name(context):
    while True:
        name = unfriendly_random_id()
        if not (name in context):
            return name

opaque_id = re.compile(r'^[A-Z0-9]{10}$')
is_opaque_id = opaque_id.match
