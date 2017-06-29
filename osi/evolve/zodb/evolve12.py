import logging

log = logging.getLogger(__name__)

from karl.models.peopledirectory import (
    reindex_peopledirectory
    )


def evolve(root):
    peopledir = root['people']
    if peopledir.update_indexes():
        reindex_peopledirectory(peopledir)


