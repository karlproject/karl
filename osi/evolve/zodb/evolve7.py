from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.utils import find_profiles
from karl.utils import find_users

from zope.component.event import objectEventNotify

def evolve(context):
    # Some users that are former stuff didn't have their categories properly
    # removed.  In OSI, no non-KarlStaff should be in any categories.
    profiles = find_profiles(context)
    users = find_users(context)

    for profile in profiles.values():
        username = profile.__name__
        if users.member_of_group(username, 'group.KarlStaff'):
            # No change needed for KarlStaff
            continue

        has_categories = filter(
            None, getattr(profile, 'categories',{}).values()
        )
        if has_categories:
            print "Removing categories for ", username, profile.categories
            objectEventNotify(ObjectWillBeModifiedEvent(profile))
            del profile.categories
            objectEventNotify(ObjectModifiedEvent(profile))

