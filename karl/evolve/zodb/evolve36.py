from repoze.bfg.security import Allow
from karl.security.policy import EMAIL


def evolve(site):
    """
    Add email permission to site acl.
    """
    site.__acl__ += ((Allow, 'group.KarlCommunications', EMAIL),)
