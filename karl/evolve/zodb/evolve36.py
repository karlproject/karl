from repoze.bfg.security import Allow
from karl.security.policy import EMAIL


def evolve(site):
    """
    Add email permission to site acl.
    """
    principals = set()
    new_acl = []
    for what, principal, perms in site.__acl__:
        principals.add(principal)
        if principal == 'group.KarlAdmin':
            if EMAIL not in perms:
                perms += (EMAIL,)
        new_acl.append((what, principal, perms))

    if 'group.KarlCommunications' not in principals:
        new_acl.append((Allow, 'group.KarlCommunications', (EMAIL,)))

    site.__acl__ = new_acl
