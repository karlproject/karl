
from repoze.bfg.security import Allow
from repoze.bfg.security import DENY_ALL
from karl.utils import find_peopledirectory

def evolve(root):
    pd = find_peopledirectory(root)
    for name, section in pd.items():
        acl = getattr(section, '__acl__', [])
        no_inherit = bool(acl) and acl[-1] == DENY_ALL
        if no_inherit:
            acl = acl[:-1]
        acl.append((Allow, 'group.KarlStaff', ('email',)))
        if no_inherit:
            acl.append(DENY_ALL)
        section.__acl__ = acl
