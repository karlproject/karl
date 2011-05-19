from repoze.bfg.traversal import model_path

"""
Some profiles have wound up with photos owned by 'None'.  There is no profile
named, 'None', so certain things break as a result.  New profile photos have
creator set properly, so it is assumed that this inconsistent state is a fossil
of a long ago fixed bug.
"""

def evolve(root):
    profiles = root['profiles']
    for name in profiles.keys():
        profile = profiles[name]
        if 'photo' not in profile:
            continue
        photo = profile['photo']
        if photo.creator != name:
            print "Updating creator for %s" % model_path(photo)
            photo.creator = name
