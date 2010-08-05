from karl.utils import find_tags

from BTrees import IOBTree
from BTrees import OOBTree

def evolve(context):
    # Added a community index to tags
    print "Addinng a community index to tags..."
    tags = find_tags(context)
    assert not hasattr(tags, '_community_to_tagids')
    index = OOBTree.OOBTree()
    tags._community_to_tagids = index
    tag_objects = tags._tagid_to_obj.items()
    n_tags = len(tag_objects)
    for count, (id, tag) in enumerate(tag_objects):
        print "Updating %d/%d" % (count, n_tags), tag.name
        ids = index.get(tag.community)
        if ids is None:
            index[tag.community] = IOBTree.IOSet((id,))
        else:
            ids.insert(id)
