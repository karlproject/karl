from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import Everyone
from pyramid.traversal import model_path
from repoze.folder.interfaces import IFolder

from karl.models.interfaces import ICatalogSearch
from karl.content.interfaces import IBlogEntry
from karl.security.policy import ADMINISTRATOR_PERMS
from karl.security.policy import MEMBER_PERMS
from karl.utils import find_catalog

def evolve(context):
    # Need to fix up acl's for blog entries in 'inherits' state.
    # See LP #407011
    search = ICatalogSearch(context)
    cnt, docids, resolver = search(interfaces=[IBlogEntry])
    for docid in docids:
        doc = resolver(docid)
        if (getattr(doc, 'security_state', 'inherits') == 'inherits'):
            print model_path(doc)
            doc.__acl__ = [
                (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
                (Allow, doc.creator, MEMBER_PERMS),
                (Deny, Everyone, ('edit', 'delete')),
                ]
            doc.security_state = 'inherits'
            _reindex(doc)

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
