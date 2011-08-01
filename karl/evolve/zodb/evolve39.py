    from repoze.bfg.traversal import model_path
from zope.component.event import objectEventNotify

from karl.content.models.adapters import extract_text_from_html
from karl.content.interfaces import IWikiPage
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.models.interfaces import ICatalogSearch


def evolve(site):
    """
    Clean up Wiki page titles so links will still work after change where
    we start stripping html from the link for purposes of matching the title
    and setting the title for new wiki pages.
    """
    count, docids, resolver = ICatalogSearch(site)(interfaces=[IWikiPage])
    for docid in docids:
        page = resolver(docid)
        cleaned = extract_text_from_html(page.title)
        if page.title != cleaned:
            print "Updating title for %s" % model_path(page)
            objectEventNotify(ObjectWillBeModifiedEvent(page))
            page.title = cleaned
            objectEventNotify(ObjectModifiedEvent(page))

