from BTrees import OOBTree
from persistent.mapping import PersistentMapping

from karl.utils import find_tags

def evolve(site):
    """
    Add precomputed cloud data to Tags.
    """
    tags = find_tags(site)
    tags._global_cloud = PersistentMapping()
    tags._community_clouds = OOBTree.OOBTree()
    for tag in tags._tagid_to_obj.values():
        update_clouds(tags, tag)


def update_clouds(tags, tag):
    if tag.community:
        community_cloud = tags._community_clouds.get(tag.community)
        if community_cloud is None:
            tags._community_clouds[tag.community] = \
                    community_cloud = PersistentMapping()
        clouds = (tags._global_cloud, community_cloud)
    else:
        clouds = (tags._global_cloud,)
    for cloud in clouds:
        if tag.name in cloud:
            cloud[tag.name] += 1
        else:
            cloud[tag.name] = 1


