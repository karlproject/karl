from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from ZODB.broken import Broken
from repoze.folder.interfaces import IFolder
from repoze.bfg.traversal import model_path

def _traverse(startnode):
    def visit(node, path, container):
        if IFolder.providedBy(node):
            for key in node.keys():
                child = node[key]
                path.append(key)
                for result, desc_path, desc_container in visit(child, path, node):
                    yield result, desc_path, desc_container
                path.pop(-1)

        yield node, path, container
        if hasattr(node, '_p_deactivate'):
            node._p_deactivate()
    return visit(startnode, model_path(startnode).split('/'), None)

def remove_broken_objects(root, out=None):
    for obj, path, container in _traverse(root):
        if isinstance(obj, Broken):
            if out is not None:
                print >>out, 'Removing broken object:', '/'.join(path)
                name = path[-1]
                data = dict(container.data.items())
                del data[name]
                container.data = OOBTree(data)
                container._num_objects = Length(len(data))

