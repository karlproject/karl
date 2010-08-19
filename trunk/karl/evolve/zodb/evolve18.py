from repoze.bfg.traversal import model_path
from repoze.lemonade.content import create_content

from karl.views.utils import make_unique_name
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog
from karl.utils import find_profiles

def evolve(root):
    former_id = None # Create lazily, in case we don't need it

    profiles = find_profiles(root)
    search = ICatalogSearch(root)
    catalog = find_catalog(root)
    creators = catalog['creator']._fwd_index.keys()
    modifiers = catalog['modified_by']._fwd_index.keys()
    userids = set(creators) | set(modifiers)
    for userid in userids:
        if userid not in profiles:
            if former_id is None:
                former_id = make_unique_name(profiles, 'formeruser')

                print "Creating profile for former user content:", former_id
                former_profile = create_content(
                    IProfile, firstname='Former', lastname='User'
                )
                profiles[former_id] = former_profile

            count, docids, resolver = search(creator=userid)
            for docid in docids:
                doc = resolver(docid)
                print "Updating 'creator' for", model_path(doc)
                doc.creator = former_id


            count, docids, resolver = search(modified_by=userid)
            for docid in docids:
                doc = resolver(docid)
                print "Updating 'modified_by' for", model_path(doc)
                doc.modified_by = former_id
