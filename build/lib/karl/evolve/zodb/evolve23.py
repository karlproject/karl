# Find and fix photos whose 'creator' was mis-identified as their container's
# '__name__' (anywhere but profiles, really).  See LP #633191 for details.

from pyramid.traversal import resource_path

from karl.content.interfaces import ICommunityFile
from karl.models.interfaces import ICatalogSearch
from karl.utils import find_profiles

def evolve(context):
    search = ICatalogSearch(context)
    profiles = find_profiles(context)
    cnt, docids, resolver = search(interfaces=[ICommunityFile], name='photo')
    for photo in [resolver(docid) for docid in docids]:
        if photo is None:
            print 'Invalid photo docid: %s' % docid
        elif photo.creator not in profiles:
            print 'Fixing bad creator for profile: %s' % resource_path(photo)
            photo.creator = photo.__parent__.creator
