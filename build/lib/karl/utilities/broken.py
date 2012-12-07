from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from ZODB.broken import Broken
from repoze.folder.interfaces import IFolder
from pyramid.traversal import find_resource
from pyramid.traversal import resource_path

from karl.utils import find_catalog

def _traverse(startnode):
    def visit(node, path, container):
        if IFolder.providedBy(node):
            for key in node.keys():
                child = node[key]
                path.append(key)
                for result, desc_path, desc_container in visit(
                    child, path, node):
                    yield result, desc_path, desc_container
                path.pop(-1)

        yield node, path, container
        if hasattr(node, '_p_deactivate'):
            node._p_deactivate()
    return visit(startnode, resource_path(startnode).split('/'), None)

def remove_broken_objects(root, out=None):
    """
    We had some old, obsolote objects that were supposed to have been deleted
    from the db before their classes were removed from the code.  Somehow or
    another, though, we've wound up with obsolete objects outliving
    """
    to_remove = []
    for obj, path, container in _traverse(root):
        if isinstance(obj, Broken):
            if out is not None:
                print >>out, 'Removing broken object:', '/'.join(path)
                name = path[-1]
                # avoid mutating tree while traversing it
                to_remove.append((container, name))

    # Delayed removal
    for container, name in to_remove:
        data = dict(container.data.items())
        del data[name]
        container.data = OOBTree(data)
        container._num_objects = Length(len(data))

def prune_catalog(root, out=None):
    """
    Under some circumstances (an error of some sort) we can wind up with
    documents in the catalog that no longer exist in real life.  This prunes
    the catalog of dead records.
    """
    catalog = find_catalog(root)
    for path, docid in list(catalog.document_map.address_to_docid.items()):
        try:
            model = find_resource(root, path)
        except KeyError:
            if out is not None:
                print >>out, "Removing dead catalog record: %s" % path
            catalog.unindex_doc(docid)
            catalog.document_map.remove_docid(docid)
