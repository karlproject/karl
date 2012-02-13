from karl.models.chatter import Chatterbox
from karl.utils import find_chatter


def evolve(site):
    """Add the chatterbox.
    """
    chatter = find_chatter(site)
    if chatter is None:
        print "Adding chatterbox"
        site['chatter'] = Chatterbox()

