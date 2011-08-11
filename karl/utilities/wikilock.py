from karl.utils import find_profiles
from repoze.bfg.url import model_url

def lock_info_from_wikilock(wikilock, request):
    """return a structure suitable for the snippet macro from the adapter"""

    if wikilock.is_locked():
        is_locked = True
        lock_info = wikilock.lock_info()
        userid = lock_info['userid']
        # assuming context is accessible
        profiles = find_profiles(wikilock.context)
        profile = profiles.get(userid, None)
        if profile is not None:
            return dict(
                is_locked = is_locked,
                url = model_url(profile, request),
                name = '%s %s' % (profile.firstname,
                                            profile.lastname),
                email = profile.email,
                )
        else:
            return dict(
                is_locked = is_locked,
                url = model_url(profiles, request),
                name = 'Unknown',
                email = '',
                )
    else:
        return dict(
            is_locked = False,
            url = None,
            name = None,
            email = None,
            )
