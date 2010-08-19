import codecs
import sys

from repoze.workflow import get_workflow
from karl.models.interfaces import IProfile
from karl.utils import find_profiles
from karl.utils import find_users

def has_custom_acl(ob):
    if hasattr(ob, '__custom_acl__'):
        if getattr(ob, '__acl__', None) == ob.__custom_acl__:
            return True
    return False

def evolve(context):
    out = codecs.getwriter('UTF-8')(sys.stdout)

    # Fix strange user db inconsistency from (hopefully) distant past.
    # Some users in the db have user info but their login is missing from
    # the logins dict.
    users = find_users(context)
    logins = users.logins
    for id in users.byid.keys():
        login = users.get_by_id(id)['login']
        if login not in logins:
            logins[login] = id

    # Convert profiles to new workflow.
    workflow = get_workflow(IProfile, 'security')
    for profile in find_profiles(context).values():
        print >>out, ("Updating security workflow for profile: %s" %
                      profile.__name__)
        if not hasattr(profile, 'security_state'):
            # 'formeruser' was added without initializing workflow, oops.
            workflow.initialize(profile)
            workflow.transition_to_state(profile, None, 'inactive')
            continue
        assert profile.security_state == 'profile'
        assert not has_custom_acl(profile)
        profile.security_state = 'active'
        workflow.reset(profile)

    # It's possible some more users were deleted since evolve18 was run.
    # Run that one again just to make sure.
