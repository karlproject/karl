from zope.interface import implements
from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import Everyone
from repoze.folder.interfaces import IFolder
from repoze.workflow.statemachine import StateMachine

from karl.models.interfaces import IUserAddedGroup
from karl.models.interfaces import IUserRemovedGroup
from karl.security.policy import ADMINISTRATOR_PERMS
from karl.security.policy import GUEST_PERMS
from karl.security.policy import MODERATOR_PERMS
from karl.security.policy import MEMBER_PERMS
from karl.security.policy import NO_INHERIT
from karl.security.interfaces import ISecurityWorkflow
from karl.utils import find_catalog
from karl.utils import find_community
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_users
from karl.views.communities import get_community_groups

def postorder(startnode):
    def visit(node):
        if IFolder.providedBy(node):
            for child in node.values():
                for result in visit(child):
                    yield result
                    # attempt to not run out of memory
        yield node
        if hasattr(node, '_p_deactivate'):
            node._p_deactivate()
    return visit(startnode)

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
            allowed_index.reindex_doc(node.docid, node)

def _mapSharing(kw, default=None):
    if kw.get('sharing') in ('true', True):
        return 'private'
    if kw.get('sharing') in ('false', False):
        return 'public'
    return default


#------------------------------------------------------------------------------
#   Workflow for communities
#------------------------------------------------------------------------------
community = StateMachine('security_state', initial_state='public')

class CommunityTransitions(object):
    """ Two states, 'public' and 'private', with no inheritance.

    o N.B.:  No transition out of 'private':  once a community is made
             private, there is no going back.
    """
    def to_private(self, from_state, to_state, action, ob):
        community = find_community(ob)
        acl = []
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name
        acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
        acl.append((Allow, members_group_name, MEMBER_PERMS))
        acl.append(NO_INHERIT)
        ob.__acl__ = acl
        _reindex(ob)

    def to_public(self, from_state, to_state, action, ob):
        community = find_community(ob)
        acl = []
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name
        acl.append((Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS))
        acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
        acl.append((Allow, members_group_name, MEMBER_PERMS))
        acl.append(NO_INHERIT)
        ob.__acl__ = acl
        _reindex(ob)

    def do_nothing(self, from_state, to_state, action, ob):
        pass

c_trans = CommunityTransitions()

community.add('initial', 'public', 'public', c_trans.to_public)
community.add('public', 'public', 'public', c_trans.do_nothing)
# N.B.:  no transition from 'private' to 'public'!

community.add('initial', 'private', 'private', c_trans.to_private)
community.add('private', 'private', 'private', c_trans.do_nothing)
community.add('public', 'private', 'private', c_trans.to_private)

class CommunityWorkflow(object):
    implements(ISecurityWorkflow)
    def __init__(self, context):
        self.context = context

    def setInitialState(self, **kw):
        self.context.security_state = 'initial'
        self.execute(_mapSharing(kw, 'public'))

    def updateState(self, **kw):
        transition = _mapSharing(kw)
        if transition:
            self.execute(transition)

    def getStateMap(self):
        return {'sharing':
            getattr(self.context, 'security_state', None) == 'private'}

    def execute(self, transition_id):
        community.execute(self.context, transition_id)

def community_workflow_adapter(context):
    return CommunityWorkflow(context)


#------------------------------------------------------------------------------
#   Workflow for content within a community
#------------------------------------------------------------------------------
community_content = StateMachine('security_state', initial_state='inherits')

class CommunityContentTransitions(object):
    """ Three states, 'public', 'private', and 'inherits'

    o 'inherits' means no ACL at all (use the parent's ACL).
    """

    def to_inherits(self, from_state, to_state, action, ob):
        if hasattr(ob, '__acl__'):
            del ob.__acl__
            _reindex(ob)

    def to_private(self, from_state, to_state, action, ob):
        community = find_community(ob)
        acl = []
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name
        acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
        acl.append((Allow, members_group_name, MEMBER_PERMS))
        acl.append(NO_INHERIT)
        ob.__acl__ = acl
        _reindex(ob)

    def to_public(self, from_state, to_state, action, ob):
        community = find_community(ob)
        acl = []
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name
        acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
        acl.append((Allow, members_group_name, MEMBER_PERMS))
        acl.append(NO_INHERIT)
        ob.__acl__ = acl
        _reindex(ob)

    def do_nothing(self, from_state, to_state, action, ob):
        pass

cc_trans = CommunityContentTransitions()

community_content.add('initial', 'inherits', 'inherits', cc_trans.to_inherits)
community_content.add('private', 'inherits', 'inherits',cc_trans.to_inherits)
community_content.add('public', 'inherits', 'inherits', cc_trans.to_inherits)
community_content.add('inherits', 'inherits', 'inherits',cc_trans.do_nothing)

community_content.add('initial', 'public', 'public', cc_trans.to_public)
community_content.add('private', 'public', 'public', cc_trans.to_public)
community_content.add('public', 'public', 'public', cc_trans.do_nothing)
community_content.add('inherits', 'public', 'public', cc_trans.to_public)

community_content.add('initial', 'private', 'private', cc_trans.to_private)
community_content.add('private', 'private', 'private', cc_trans.do_nothing)
community_content.add('public', 'private', 'private', cc_trans.to_private)
community_content.add('inherits', 'private', 'private', cc_trans.to_private)

class CommunityContentWorkflow(object):
    implements(ISecurityWorkflow)
    def __init__(self, context):
        self.context = context

    def setInitialState(self, **kw):
        self.context.security_state = 'initial'
        self.execute(_mapSharing(kw, 'inherits'))

    def updateState(self, **kw):
        transition = _mapSharing(kw)
        if transition:
            self.execute(transition)

    def getStateMap(self):
        return {'sharing':
            getattr(self.context, 'security_state', None) == 'private'}

    def execute(self, transition_id):
        community_content.execute(self.context, transition_id)
 
def community_content_workflow_adapter(context):
    return CommunityContentWorkflow(context)

#------------------------------------------------------------------------------
#   Special workflow for blog entries.
#------------------------------------------------------------------------------
blogentry = StateMachine('security_state', initial_state='initial')

class BlogentryTransitions:
    """ Same three states as CommunityContentTransitions, except:

    o Only the creator is allowed to edit or delete an entry / comment.
    """
    def to_inherits(self, from_state, to_state, action, ob):
        acl = ob.__acl__ = [
            (Allow, ob.creator, MEMBER_PERMS),
            (Deny, Everyone, ('edit', 'delete')),
            # Note:  don't add NO_INHERIT, ergo fall back to __parent__
        ]
        _reindex(ob)

    def to_private(self, from_state, to_state, action, ob):
        community = find_community(ob)
        acl = [(Allow, ob.creator, MEMBER_PERMS)]
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name
        acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
        acl.append((Allow, members_group_name, GUEST_PERMS))
        acl.append(NO_INHERIT)
        ob.__acl__ = acl
        _reindex(ob)

    def to_public(self, from_state, to_state, action, ob):
        site = find_site(ob)
        acl = []
        community = find_community(ob)
        acl.append((Allow, ob.creator, MEMBER_PERMS))
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name
        acl.append((Allow, moderators_group_name, MODERATOR_PERMS))
        acl.append((Allow, members_group_name, GUEST_PERMS))
        acl.append(NO_INHERIT)
        ob.__acl__ = acl
        _reindex(ob)

    def do_nothing(self, from_state, to_state, action, ob):
        pass

be_trans = BlogentryTransitions()

blogentry.add('initial', 'inherits', 'inherits', be_trans.to_inherits)
blogentry.add('private', 'inherits', 'inherits', be_trans.to_inherits)
blogentry.add('public', 'inherits', 'inherits',  be_trans.to_inherits)
blogentry.add('inherits', 'inherits', 'inherits', be_trans.do_nothing)

blogentry.add('initial', 'public', 'public', be_trans.to_public)
blogentry.add('private', 'public', 'public', be_trans.to_public)
blogentry.add('public', 'public', 'public', be_trans.do_nothing)
blogentry.add('inherits', 'public', 'public', be_trans.to_public)

blogentry.add('initial', 'private', 'private', be_trans.to_private)
blogentry.add('private', 'private', 'private', be_trans.do_nothing)
blogentry.add('public', 'private', 'private', be_trans.to_private)
blogentry.add('inherits', 'private', 'private', be_trans.to_private)

class BlogentryWorkflow(object):
    implements(ISecurityWorkflow)
    def __init__(self, context):
        self.context = context

    def setInitialState(self, **kw):
        self.context.security_state = 'initial'
        self.execute(_mapSharing(kw, 'inherits'))

    def updateState(self, **kw):
        transition = _mapSharing(kw)
        if transition:
            self.execute(transition)

    def getStateMap(self):
        return {'sharing':
            getattr(self.context, 'security_state', None) == 'private'}

    def execute(self, transition_id):
        blogentry.execute(self.context, transition_id)

#------------------------------------------------------------------------------
#   Special workflow for profiles
#------------------------------------------------------------------------------
profile = StateMachine('security_state', initial_state='inherits')

class ProfileTransitions:

    def to_inherits(self, from_state, to_state, action, ob):
        acl = ob.__acl__ = [
            (Allow, ob.creator, MEMBER_PERMS),
        ]
        users = find_users(ob)
        groups = users.get_by_id(ob.creator)['groups']
        for group, role in get_community_groups(groups):
            c_group = 'group.community:%s:%s' % (group, role)
            acl.append((Allow, c_group, GUEST_PERMS))
        acl.append(NO_INHERIT)
        _reindex(ob)


pf_trans = ProfileTransitions()

profile.add('inherits', 'inherits', 'inherits', pf_trans.to_inherits)

class ProfileWorkflow(object):
    implements(ISecurityWorkflow)
    def __init__(self, context):
        self.context = context

    def setInitialState(self, **kw):
        self.context.security_state = 'inherits'
        self.execute('inherits')

    def updateState(self, **kw):
        transition = _mapSharing(kw)
        if transition:
            self.execute(transition)

    def getStateMap(self):
        return {}

    def execute(self, transition_id):
        profile.execute(self.context, transition_id)


def revise_profile_acl(event):
    """ Subscriber for IUserAddedGroup and IUserRemovedGroup events.

    o Find the profile corresponding to the user and update its ACL
      via the 'inherits' transition.
    """
    if (not IUserAddedGroup.providedBy(event) and
        not IUserRemovedGroup.providedBy(event)):
        return

    profiles = find_profiles(event.site)
    profile = profiles[event.id]
    ProfileWorkflow(profile).execute('inherits')

