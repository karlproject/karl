from repoze.bfg.traversal import model_path
from repoze.folder import Folder
from karl.models.interfaces import ICatalogSearch
from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IWikiPage
from karl.utils import find_catalog

def evolve(context):
    """
    Upgrades required for new Image Drawer functionality.
    """
    # Add IImage marker to instances of ICommunityFile which are images.
    catalog = find_catalog(context)
    search = ICatalogSearch(context)
    cnt, docids, resolver = search(interfaces=[ICommunityFile])
    for docid in docids:
        obj = resolver(docid)
        if obj is None:
            continue  # Work around catalog bug
        obj._init_image()
        if obj.is_image:
            print "Image: %s" % model_path(obj)
            catalog.reindex_doc(obj.docid, obj)

    # Convert WikiPages to Folders so they can contain attachments
    cnt, docids, resolver = search(interfaces=[IWikiPage])
    for docid in docids:
        obj = resolver(docid)
        if obj is None:
            continue # Work around catalog bug
        print "Convert wiki page to folder: %s" % model_path(obj)
        Folder.__init__(obj)
        catalog.reindex_doc(obj.docid, obj)
