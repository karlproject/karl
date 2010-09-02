# Ensure that the 'content_modified' index is added and populated.
from karl.models.catalog import reindex_catalog

def evolve(context):
    reindex_catalog(context, indexes=['content_modified'])
