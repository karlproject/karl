from BTrees.IFBTree import multiunion
from BTrees.IFBTree import IFSet

from zope.interface import implements
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.location import lineage
from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import ACLAllowed
from repoze.bfg.security import ACLDenied
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

class AllPermissionsList(object):
    """ Stand in 'permission list' to represent all permissions """
    def __iter__(self):
        return ()
    def __contains__(self, other):
        return True
    def __eq__(self, other):
        return isinstance(other, self.__class__)

VIEW = 'view'
EDIT = 'edit'
CREATE = 'create'
DELETE = 'delete'
MODERATE = 'moderate'
ADMINISTER = 'administer'
COMMENT = 'comment'

GUEST_PERMS = (VIEW, COMMENT)
MEMBER_PERMS = GUEST_PERMS + (EDIT, CREATE, DELETE)
MODERATOR_PERMS = MEMBER_PERMS + (MODERATE,)
ADMINISTRATOR_PERMS = MODERATOR_PERMS + (ADMINISTER,)

ALL = AllPermissionsList()
NO_INHERIT = (Deny, Everyone, ALL)

# the below security policy is identical to the BFG 0.8's
# "InheritingACLSecurityPolicy"; our KARL configuration that uses it
# should be changed to use this "InheritingACLSecurityPolicy" once we
# migrate to BFG 0.8, and the security policy below should disappear.

class KARLSecurityPolicy(object):
    """ A security policy which uses ACLs in the following ways:

    - When checking whether a user is permitted (via the ``permits``
      method), the security policy consults the ``context`` for an ACL
      first.  If no ACL exists on the context, or one does exist but
      the ACL does not explicitly allow or deny access for any of the
      effective principals, consult the context's parent ACL, and so
      on, until the lineage is exhausted or we determine that the
      policy permits or denies.

      During this processing, if any ``Deny`` ACE is found matching
      any effective principal, stop processing by returning an
      ``ACLDenied`` (equals False) immediately.  If any ``Allow`` ACE
      is found matching any effective principal, stop processing by
      returning an ``ACLAllowed`` (equals True) immediately.  If we
      exhaust the context's lneage, and no ACE has explicitly
      permitted or denied access, return an ``ACLDenied``.  This
      differs from the non-inheriting security policy (the
      ``ACLSecurityPolicy``) by virtue of the fact that it does not
      stop looking for ACLs in the object lineage after it finds the
      first one.

    - When computing principals allowed by a permission via the
      ``principals_allowed_by_permission`` method, we compute the set
      of principals that are explicitly granted the ``permission``.
      We do this by walking 'up' the object graph *from the root* to
      the context.  During this walking process, if we find an
      explicit ``Allow`` ACE for a principal that matches the
      ``permission``, the principal is included in the allow list.
      However, if later in the walking process that user is mentioned
      in any ``Deny`` ACE for the permission, the user is removed from
      the allow list.  If a ``Deny`` to the principal ``Everyone`` is
      encountered during the walking process that matches the
      ``permission``, the allow list is cleared for all principals
      encountered in previous ACLs.  The walking process ends after
      we've processed the any ACL directly attached to ``context``; a
      list of principals is returned.

    - Other aspects of this policy are the same as those in the
      ACLSecurityPolicy (e.g. ``effective_principals``,
      ``authenticated_userid``).
    """
    implements(ISecurityPolicy)
    
    def __init__(self, get_principals):
        self.get_principals = get_principals

    def permits(self, context, request, permission):
        """ Return ``ACLAllowed`` if the policy permits access,
        ``ACLDenied`` if not. """
        principals = set(self.effective_principals(request))
        
        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                if ace_principal in principals:
                    if not hasattr(ace_permissions, '__iter__'):
                        ace_permissions = [ace_permissions]
                    if permission in ace_permissions:
                        if ace_action == Allow:
                            return ACLAllowed(ace, acl, permission,
                                              principals, location)
                        else:
                            return ACLDenied(ace, acl, permission,
                                             principals, location)

        # default deny if no ACL in lineage at all
        return ACLDenied(None, None, permission, principals, context)

    def authenticated_userid(self, request):
        principals = self.get_principals(request)
        if principals:
            return principals[0]

    def effective_principals(self, request):
        effective_principals = [Everyone]
        principal_ids = self.get_principals(request)

        if principal_ids:
            effective_principals.append(Authenticated)
            effective_principals.extend(principal_ids)

        return effective_principals

    def principals_allowed_by_permission(self, context, permission):
        allowed = set()

        for location in reversed(list(lineage(context))):
            # NB: we're walking *up* the object graph from the root
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            allowed_here = set()
            denied_here = set()
            
            for ace_action, ace_principal, ace_permissions in acl:
                if not hasattr(ace_permissions, '__iter__'):
                    ace_permissions = [ace_permissions]
                if ace_action == Allow and permission in ace_permissions:
                    if not ace_principal in denied_here:
                        allowed_here.add(ace_principal)
                if ace_action == Deny and permission in ace_permissions:
                    denied_here.add(ace_principal)
                    if ace_principal == Everyone:
                        # clear the entire allowed set, as we've hit a
                        # deny of Everyone ala (Deny, Everyone, ALL)
                        allowed = set()
                        break
                    elif ace_principal in allowed:
                        allowed.remove(ace_principal)

            allowed.update(allowed_here)

        return allowed
def get_who_principals(request):
    identity = request.environ.get('repoze.who.identity')
    if not identity:
        return []
    principals = [identity['repoze.who.userid']]
    principals.extend(identity.get('groups', []))
    return principals

def RepozeWhoKARLSecurityPolicy():
    """
    A security policy which

    - examines the request.environ for the ``repoze.who.identity``
      dictionary.  If one is found, the principal ids for the request
      are composed of ``repoze.who.identity['repoze.who.userid']``
      plus ``repoze.who.identity.get('groups', [])``.

    - uses a KARLSecurityPolicy to perform security policy duties.
    """
    return KARLSecurityPolicy(get_who_principals)

class ACLChecker(object):
    """ 'Checker' object used as a ``attr_checker`` callback for a
    path index set up to use the __acl__ attribute as an
    ``attr_discriminator`` """
    def __init__(self, principals, permission='view'):
        self.principals = principals
        self.permission = permission

    def __call__(self, result):
        sets = []
        for (docid, acls), set in result:
            if not set:
                continue
            if self.check_acls(acls):
                sets.append(set)
        if not sets:
            return IFSet()
        return multiunion(sets)

    def check_acls(self, acls):
        acls = list(reversed(acls))
        for acl in acls:
            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                if ace_principal in self.principals:
                    if not hasattr(ace_permissions, '__iter__'):
                        ace_permissions = [ace_permissions]
                    if self.permission in ace_permissions:
                        if ace_action == Allow:
                            return True
                        else:
                            # deny of any means deny all of everything
                            return False
        return False
    
