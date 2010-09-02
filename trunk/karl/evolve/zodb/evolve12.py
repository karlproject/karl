from karl.models.peopledirectory import reindex_peopledirectory
from karl.utils import find_peopledirectory
from karl.utilities.broken import remove_broken_objects
import sys

def evolve(context):
    remove_broken_objects(context['profiles'], sys.stdout)

    print "Reindexing people directory"
    peopledir = find_peopledirectory(context)
    reindex_peopledirectory(peopledir)
