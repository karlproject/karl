from BTrees.OOBTree import OOBTree

from karl.utils import find_chatter


def evolve(site):
    """Add oobtree for followed topics to chatter
    """
    chatter = find_chatter(site)
    chatter._followed_tags = OOBTree()

