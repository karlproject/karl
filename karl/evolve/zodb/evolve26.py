# Ensure that profiles with empty / invalid entries for 'country' get 
# mapped to the new 'XX' / 'Unknown' marker.

from karl.consts import countries
from karl.utils import find_catalog
from karl.utils import find_profiles

def evolve(context):
    catalog = find_catalog(context)
    profiles = find_profiles(context)
    for profile in profiles.values():
        if profile.country not in countries.as_dict:
            print ('Evolving profile %s country from "%s" to "XX"' %
                      (profile.__name__, profile.country))
            profile.country = 'XX'
            catalog.reindex_doc(profile.docid, profile)
