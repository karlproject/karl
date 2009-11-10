from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import Everyone
from repoze.bfg.traversal import find_interface
from repoze.bfg.traversal import model_path

from karl.models.interfaces import IIntranets
from karl.models.interfaces import IUserAddedGroup
from karl.models.interfaces import IUserRemovedGroup

from karl.security.policy import ADMINISTRATOR_PERMS
from karl.security.policy import GUEST_PERMS
from karl.security.policy import MODERATOR_PERMS
from karl.security.policy import MEMBER_PERMS
from karl.security.policy import CREATE
from karl.security.policy import NO_INHERIT
from karl.security.workflow import postorder
from karl.security.workflow import acl_diff
from karl.security.workflow import reset_security_workflow

from karl.utils import find_catalog
from karl.utils import find_community
from karl.utils import find_users
from karl.utils import find_profiles
from karl.views.communities import get_community_groups

#------------------------------------------------------------------------------
#   Helper methods
#------------------------------------------------------------------------------

_marker = object()

def _reindex(ob):
    catalog = find_catalog(ob)

    # XXX reindexing the 'path' index can be removed once we've
    # removed the last ACLChecker spelled in catalog queries from the
    # code; this is the "old" way of doing security filtering.
    path_index = catalog['path']
    path_index.reindex_doc(ob.docid, ob)

    # if the object is folderish, we need to reindex it plus all its
    # subobjects' 'allowed' index entries recursively; each object's
    # allowed value depends on its parents in the lineage
    allowed_index = catalog.get('allowed')
    if allowed_index is not None:
        for node in postorder(ob):
            if hasattr(node, 'docid'):
                allowed_index.reindex_doc(node.docid, node)

def ts(*args):
    return '\t'.join([str(x) for x in args])

#------------------------------------------------------------------------------
#   Electors
#------------------------------------------------------------------------------

def not_intranets_containment(context):
    return not intranets_containment(context)

def intranets_containment(context):
    if find_interface(context, IIntranets) is not None:
        return True
    return False

def private_community_containment(context):
    if not_intranets_containment(context):
        community = find_community(context)
        if community is None:
            return False
        return getattr(community, 'security_state', None) == 'private'
    return False

def public_community_containment(context):
    if not_intranets_containment(context):
        community = find_community(context)
        if community is None:
            return False
        return getattr(community, 'security_state', None) == 'public'
    return False
    
#------------------------------------------------------------------------------
#   Workflow for communities
#------------------------------------------------------------------------------
def community_to_private(ob, info):
    community = find_community(ob)
    acl = []
    moderators_group_name = community.moderators_group_name
    members_group_name = community.members_group_name
    acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
    acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
    acl.append((Allow, members_group_name, MEMBER_PERMS))
    acl.append(NO_INHERIT)
    msg = None
    added, removed = acl_diff(community, acl)
    if added or removed:
        community.__acl__ = acl
        msg = ts('community-private', model_path(community), added, removed)
    _reindex(community)
    return msg

def community_to_public(ob, info):
    community = find_community(ob)
    acl = []
    moderators_group_name = community.moderators_group_name
    members_group_name = community.members_group_name
    acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
    acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
    acl.append((Allow, members_group_name, MEMBER_PERMS))
    acl.append((Allow, 'group.KarlStaff', GUEST_PERMS))
    acl.append(NO_INHERIT)
    msg = None
    added, removed = acl_diff(community, acl)
    if added or removed:
        community.__acl__ = acl
        msg = ts('community-public', model_path(community), added, removed)
    _reindex(community)
    return msg

def community_to_intranet(ob, info):
    community = find_community(ob)
    acl = []
    moderators_group_name = community.moderators_group_name
    members_group_name = community.members_group_name
    acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
    acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
    acl.append((Allow, members_group_name, MEMBER_PERMS))
    # inherit from /offices
    #acl.append(NO_INHERIT)
    msg = None
    added, removed = acl_diff(community, acl)
    if added or removed:
        community.__acl__ = acl
        msg = ts('community-intranet', model_path(community), added, removed)
    _reindex(community)
    return msg

#------------------------------------------------------------------------------
#   Special workflow for blog entries.
#------------------------------------------------------------------------------
"""
o Only the creator and the admin is allowed to edit or delete an entry.
"""
def blogentry_to_inherits(ob, info):
    acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        (Allow, ob.creator, MEMBER_PERMS),
        (Deny, Everyone, ('edit', 'delete')),
        # Note:  don't add NO_INHERIT, ergo fall back to __parent__
    ]
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('blogentry-inherits', model_path(ob), added, removed)
    _reindex(ob)
    return msg

def blogentry_to_private(ob, info):
    community = find_community(ob)
    acl = [(Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS)]
    acl.append((Allow, ob.creator, MEMBER_PERMS))
    moderators_group_name = community.moderators_group_name
    members_group_name = community.members_group_name
    acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
    acl.append((Allow, members_group_name, GUEST_PERMS))
    acl.append(NO_INHERIT)
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('blogentry-private', model_path(ob), added, removed)
    _reindex(ob)
    return msg

#------------------------------------------------------------------------------
#   Special workflow for comments.
#------------------------------------------------------------------------------
"""
o Only the creator and the admin is allowed to edit or delete a comment.
"""
def comment_to_inherits(ob, info):
    acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        (Allow, ob.creator, MEMBER_PERMS),
        (Deny, Everyone, ('edit', 'delete')),
        # Note:  don't add NO_INHERIT, ergo fall back to __parent__
    ]
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('comment-inherits', model_path(ob), added, removed)
    _reindex(ob)
    return msg

#------------------------------------------------------------------------------
#   Workflow for forums and forum topics
#------------------------------------------------------------------------------

def forum_to_inherits(ob, info):
    acl = [(Allow, 'group.KarlStaff', (CREATE,))]
    # Note:  don't add NO_INHERIT, ergo fall back to __parent__
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('forum-inherited', model_path(ob), added, removed)
    _reindex(ob)
    return msg

def forum_topic_to_inherits(ob, info):
    acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        (Allow, ob.creator, MEMBER_PERMS),
        (Deny, Everyone, ('edit', 'delete')),
        # Note:  don't add NO_INHERIT, ergo fall back to __parent__
        ]
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('forum-topic-inherited', model_path(ob), added, removed)
    _reindex(ob)
    return msg

#------------------------------------------------------------------------------
#   Special workflow for profiles
#------------------------------------------------------------------------------

def to_profile(ob, info):
    acl  = [
        (Allow, ob.creator, MEMBER_PERMS),
    ]
    acl.append((Allow, 'group.KarlUserAdmin', ADMINISTRATOR_PERMS))
    acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
    acl.append((Allow, 'group.KarlStaff', GUEST_PERMS))
    users = find_users(ob)
    user = users.get_by_id(ob.creator)
    if user is not None:
        groups = user['groups']
        for group, role in get_community_groups(groups):
            c_group = 'group.community:%s:%s' % (group, role)
            acl.append((Allow, c_group, GUEST_PERMS))
    acl.append(NO_INHERIT)
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('to-profile', model_path(ob), added, removed)
    _reindex(ob)
    return msg

#------------------------------------------------------------------------------
#   Workflow for content within a community
#------------------------------------------------------------------------------

def content_to_inherits(ob, info):
    msg = None
    added, removed = acl_diff(ob, {})
    if hasattr(ob, '__acl__'):
        del ob.__acl__
        msg =  ts('content-inherited', model_path(ob), added, removed)
    _reindex(ob)
    return msg

def content_to_private(ob, info):
    community = find_community(ob)
    acl = []
    moderators_group_name = community.moderators_group_name
    members_group_name = community.members_group_name
    acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
    acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
    acl.append((Allow, members_group_name, MEMBER_PERMS))
    acl.append(NO_INHERIT)
    msg = None
    added, removed = acl_diff(ob, acl)
    if added or removed:
        ob.__acl__ = acl
        msg = ts('content-private', model_path(ob), added, removed)
    _reindex(ob)
    return msg 

#------------------------------------------------------------------------------
#   Workflow for intranet content
#
# This workflow applies to communities and community content in the context
# of intranet sites.
#------------------------------------------------------------------------------

def intranet_content_to_inherits(ob, info):
    acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        (Allow, ob.creator, MEMBER_PERMS),
        (Deny, Everyone, ('edit', 'delete')),
        # Note:  don't add NO_INHERIT, ergo fall back to __parent__
        ]
    msg = None
    added, removed = acl_diff(ob, acl)
    if (added or removed):
        ob.__acl__ = acl
        msg = ts('intranet-content-inherited', model_path(ob), added, removed)
    _reindex(ob)
    return msg

# subscribers

def reset_profile(event):
    """ Subscriber for IUserAddedGroup and IUserRemovedGroup events.

    o Find the profile corresponding to the user and update its ACL
      by resettings its security workflow
    """
    if (not IUserAddedGroup.providedBy(event) and
        not IUserRemovedGroup.providedBy(event)):
        return

    profiles = find_profiles(event.site)
    profile = profiles.get(event.id)
    if profile is not None:
        reset_security_workflow(profile)
