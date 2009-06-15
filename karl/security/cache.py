from zope.interface import Interface
from zope.interface import implements
from repoze.bfg.location import lineage
from repoze.bfg.security import Everyone
from karl.security.policy import AllPermissionsList

class IACLPathCache(Interface):
    """ Utility:  maps an object's path to the nodes "above" it having ACLs.
    """
    def clear(model=None):
        """ Clear the cache for 'model' and any descendants.

        o If 'model' is None, clear the whole cache.
        """

    def index(model):
        """ Index model's ACL, if it has one.

        o If "DENY ALL" not in the ACL, recurse to model's __parent__.
        """

    def lookup(model, permission=None):
        """ Return the ACEs for 'model' relevant to 'permission'.

        o If 'permission' is None, return all ACEs.

        o Crawl the parent chain until we get to the root, or until we
          find an allow or a deny for the given permission to Everyone.

        o If cache is populated for any node, use that value.

        o Populate the cache as we search.
        """

class ACLPathCache(object):
    implements(IACLPathCache)
    def __init__(self):
        self._index = {}

    def _getPath(self, model):
        rpath = []
        for location in lineage(model):
            if location.__name__ is None:
                break
            rpath.insert(0, location.__name__)
        return tuple(rpath)

    def clear(self, model=None):
        """ See IACLPathCache.
        """
        if model is None:
            self._index.clear()
            return
        path = self._getPath(model)
        lpath = len(path)
        purged = [x for x in self._index.keys() if x[:lpath] == path]
        for key in purged:
            del self._index[key]

    def index(self, model):
        """ See IACLPathCache.
        """
        for obj in lineage(model):
            acl = getattr(obj, '__acl__', None)
            if acl is not None:
                self._index[self._getPath(obj)] = acl[:]

    def lookup(self, model, permission=None):
        """ See IACLPathCache.
        """
        aces = []
        for obj in lineage(model):
            path = self._getPath(obj)
            acl = self._index.get(path)
            if acl is None:
                acl = getattr(obj, '__acl__', ())
                if acl:
                    self._index[path] = acl
            if permission is not None:
                acl = [x for x in acl
                        if x[2] == permission
                            or isinstance(x[2], AllPermissionsList)]
            aces.extend(acl)
            if [x for x in acl if x[1] is Everyone]:
                break
        return aces
