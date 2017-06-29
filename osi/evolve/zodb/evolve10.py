from pyramid.traversal import model_path
from karl.utils import find_peopledirectory_catalog
from karl.utils import find_profiles
from karl.utils import find_users

def evolve(context):
    """
    Remove any people directory categories set for non-Staff users.
    """
    profiles = find_profiles(context)
    users = find_users(context)
    catalog = find_peopledirectory_catalog(context)
    docid_for_address = catalog.document_map.docid_for_address
    for profile in profiles.values():
        user = users.get_by_id(profile.__name__)
        if user is None:
            continue

        if 'group.KarlStaff' not in user['groups']:
            if getattr(profile, 'categories', None):
                print "Removing categories for", profile.__name__
                profile.categories = {}
                docid = docid_for_address(model_path(profile))
                catalog.reindex_doc(docid, profile)
