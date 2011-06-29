from karl.utils import find_profiles
from karl.utils import find_catalog


def evolve(site):
    catalog = find_catalog(site)
    profiles = find_profiles(site)

    text_index = catalog['texts']
    for profile in profiles.values():
        if profile.security_state != 'inactive':
            profile._p_deactivate()
            continue

        print "Reindexing profile: ", profile.__name__
        text_index.reindex_doc(profile.docid, profile)
