from zope.interface import alsoProvides

from karl.content.interfaces import IPhoto
from karl.content.interfaces import INewsItem
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog

def evolve(site):
    """
    Add the IPhoto marker interface to profile and news item photos.
    """
    catalog = find_catalog(site)
    search = ICatalogSearch(site)
    count, docids, resolver = search(
        interfaces={'operator': 'or', 'query': [INewsItem, IProfile]})
    for docid in docids:
        doc = resolver(docid)
        photo = doc.get('photo')
        if photo is not None and not IPhoto.providedBy(photo):
            alsoProvides(photo, IPhoto)
            catalog.reindex_doc(photo.docid, photo)