import os
from karl.utils import find_profiles

DIRNAME = 'bios'

def evolve(context):
    profiles = find_profiles(context)
    for fname in os.listdir(DIRNAME):
        if fname.startswith('.'):
            continue

        profile = profiles.get(fname, None)
        if profile is None:
            print "Profile no longer exists: ", fname
            continue

        if not profile.biography:
            print "Restoring profile to ", fname
            bio = open(os.path.join(DIRNAME, fname), 'rb').read()
            bio = bio.decode('UTF-8')
            profile.biography = bio
