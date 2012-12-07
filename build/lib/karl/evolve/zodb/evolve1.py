from karl.models.catalog import reindex_catalog

def evolve(context):
    # add 'virtual' index to database and reindex
    def output(msg):
        print msg
    reindex_catalog(context, output=output, indexes=('virtual',))


