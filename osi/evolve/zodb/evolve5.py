from karl.utils import find_profiles
from karl.utils import find_users

"""
Remove some users that were mistakenly imported into OSI from their initial
GSA sync.
"""
bad_users = [
    "A. Van Brunt",
    "Ben",
    "Ellen Sprenger",
    "asingh01",
    "bdonga",
    "elpatton",
    "jharrington1",
    "jkamuruhci",
    "jsmith",
    "komboli",
    "ldupervil",
    "rboris",
    "scoliver2007",
    "skeleton",
    "sshore",
]

def evolve(context):
    users = find_users(context)
    profiles = find_profiles(context)

    for id in bad_users:
        users.remove(id)
        del profiles[id]
