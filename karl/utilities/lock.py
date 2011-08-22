from datetime import datetime
from karl.utils import find_profiles
from repoze.bfg.url import model_url

LOCK_TIMEOUT_SECONDS = 30 * 60

def lock_info(context):
    """returns a dict that represents the lock on the context

    This will return the empty dict if no lock exists.

    This structure has two keys:
    1. userid - the id of the user that locked this object
    2. time - a datetime that stores when it was locked
    """
    return getattr(context, 'lock', {})

def lock(context, userid, lock_time=None):
    """ lock a particular page with a particular userid

    if lock_time is specified, it locks with that time, otherwise it
    defaults to now """
    if lock_time is None:
        lock_time = datetime.now()
    context.lock = dict(
        userid = userid,
        time = lock_time,
        )

def is_locked(context, from_time=None):
    """ returns whether somebody is actively editing this page

    if from_time is specified, it uses that to calculate if the lock has
    expired, otherwise it defaults to now """
    if from_time is None:
        from_time = datetime.now()
    lock = lock_info(context)
    lock_time = lock.get('time', None)
    if lock_time is None:
        return False
    delta = from_time - lock_time
    if delta.seconds == 0:
        # if the difference is too great, seconds can be 0
        return from_time == lock_time
    return delta.seconds < LOCK_TIMEOUT_SECONDS

def clear(context):
    """ remove the current active lock from the page """
    context.lock = {}

def owns_lock(context, userid):
    """ return whether the active lock is owned by the given userid """
    lock = lock_info(context)
    return lock.get('userid', None) == userid

def lock_data(context, request, from_time=None):
    """return a structure suitable for displaying in a template"""

    if is_locked(context, from_time):
        lock = lock_info(context)
        userid = lock['userid']
        profiles = find_profiles(context)
        profile = profiles.get(userid, None)
        if profile is not None:
            return dict(
                is_locked = True,
                url = model_url(profile, request),
                name = '%s %s' % (profile.firstname,
                                            profile.lastname),
                email = profile.email,
                )
        else:
            return dict(
                is_locked = True,
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
