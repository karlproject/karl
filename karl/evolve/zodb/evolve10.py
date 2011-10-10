from pyramid.traversal import resource_path
from repoze.lemonade.content import create_content

from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import INewsItem
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog


old_names = ("photo.jpg", "photo.gif", "photo.png")

def evolve(site):
    """
    Convert photos on news items and profiles to ICommunityFile, as per
    newer image handling policy.
    """
    search = ICatalogSearch(site)
    cnt, docids, resolver = search(interfaces=dict(
        query=[IProfile, INewsItem],
        operator='or',
    ))
    for docid in docids:
        obj = resolver(docid)
        if obj is None:
            continue # Work around catalog bug
        for name in old_names:
            if name in obj:
                print "Updating photo for %s" % resource_path(obj)
                old_photo = obj.get('source_photo')
                if old_photo is None:
                    old_photo = obj[name]
                new_photo = create_content(
                    ICommunityFile,
                    title='Photo of ' + obj.title,
                    stream=old_photo.blobfile.open(),
                    mimetype=getattr(old_photo, 'mimetype',
                                     getattr(old_photo, '_mimetype')),
                    filename=name,
                    creator=obj.creator
                )
                if new_photo.is_image:
                    obj['photo'] = new_photo
                else:
                    print "WARNING not an image"
                del obj[name]
                if 'source_photo' in obj:
                    del obj['source_photo']
