from BTrees.OOBTree import OOBTree
from karl.utilities.peopleconf import clear_mailinglist_aliases
from karl.utilities.peopleconf import find_mailinglist_aliases

def evolve(root):
    list_aliases = getattr(root, 'list_aliases', None)
    if list_aliases is None:
        list_aliases = root.list_aliases = OOBTree()
    clear_mailinglist_aliases(root['people'])
    find_mailinglist_aliases(root['people'])
