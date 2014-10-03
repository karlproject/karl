import sys
import BTrees
import logging
import transaction

from pyramid.traversal import find_model
from repoze.catalog.indexes.text import CatalogTextIndex
from ZODB.POSException import ConflictError

from karl.models.site import get_textrepr
from karl.models.site import get_weighted_textrepr
from karl.utils import find_catalog

from karl.textindex import KarlPGTextIndex
from karl.scripting import create_karl_argparser

log = logging.getLogger(__name__)

IF = BTrees.family32.IF

BATCH_SIZE = 500

def main(argv=sys.argv): 
    parser = create_karl_argparser(
        description='Switches the text index of an instance to use '
        'either zope.index or pgtextindex.'
    )
    parser.add_argument('--pg', dest='convert_to', action='store_const',
        const='pg', help='Convert the database to pgtextindex.')
    parser.add_argument('--zope', dest='convert_to', action='store_const',
        const='zope', help='Convert the database to zope.index.')
    parser.add_argument('--show', action='store_true', default=False,
                        help='Show which index type in currently in use. '
                        'Performs no action.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    site, closer = env['root'], env['closer']
    if args.show:
        print >> args.out, (
            'Current text index type: %s' % get_index_type(args, site))
        return

    status = getattr(site, '_reindex_text_status', None)
    if status == 'reindexing':
        reindex_text(args, site)
    else:
        switch_text_index(args, site)
        reindex_text(args, site)


def get_index_type(args, site):
    """Get the type name of the current index.
    """
    catalog = find_catalog(site)
    index = catalog['texts']
    if isinstance(index, KarlPGTextIndex):
        return 'pg'
    elif isinstance(index, CatalogTextIndex):
        return 'zope'
    else:
        return 'other (%s)' % type(index)


def switch_text_index(args, site):
    """
    It turns out, for OSI at least, that reindexing every document is too large
    of a transaction to fit in memory at once. This strategy seeks to address
    this problem along with a couple of other design goals:

      1) Production site can be running in read/write mode while documents
         are reindexed.

      2) This operation can be interrupted and pick back up where it left off.

    To accomplish this, in this function we create the new text index without
    yet replacing the old text index. We then store the set of document ids of
    documents which need to be reindexed. The 'reindex_text' function then
    reindexes documents in small batches, each batch in its own transaction.
    Because the old index has not yet been replaced, users can use the site
    normally while this occurs. When all documents have been reindexed,
    'reindex_text' looks to see if any new documents have been indexed in the
    old index in the meantime and creates a new list of documents to reindex.
    When the old_index and new_index are determined to contain the exact same
    set of document ids, then the new_index is put in place of the old_index
    and the migration is complete.
    """
    new_type = args.convert_to
    old_type = get_index_type(args, site)
    if new_type is None:
        new_type = old_type
    else:
        if new_type != old_type:
            log.info("Converting to %s." % new_type)
    catalog = find_catalog(site)
    if new_type == 'pg':
        new_index = KarlPGTextIndex(get_weighted_textrepr)
        if old_type == 'pg':
            new_index.drop_and_create()
    elif new_type == 'zope':
        new_index = CatalogTextIndex(get_textrepr)
    else:
        raise ValueError("Unknown text index type: %s" % new_type)
    catalog['new_texts'] = new_index  # temporary location
    new_index.to_index = IF.Set()
    new_index.indexed = IF.Set()
    transaction.commit()
    site._reindex_text_status = 'reindexing'


def reindex_text(args, site):
    catalog = find_catalog(site)
    old_index = catalog['texts']
    new_index = catalog['new_texts']

    done = False
    while not done:
        try:
            if len(new_index.to_index) == 0:
                calculate_docids_to_index(catalog, old_index, new_index)
                if len(new_index.to_index) == 0:
                    catalog['texts'] = new_index
                    del new_index.to_index
                    del new_index.indexed
                    del site._reindex_text_status
                    done = True
                    log.info("Finished.")
            else:
                reindex_batch(args, site)
            transaction.commit()
            site._p_jar.db().cacheMinimize()
        except ConflictError:
            log.warn("Conflict error: retrying....")
            transaction.abort()


def calculate_docids_to_index(catalog, old_index, new_index):
    log.info("Calculating docids to reindex...")
    old_docids = IF.Set(get_catalog_docids(catalog))
    new_docids = IF.Set(get_index_docids(new_index))

    # Include both docids actually in the new index and docids we have tried to
    # index, since some docids might not actually be in the index if their
    # discriminator returns no value for texts.
    to_index = IF.difference(old_docids, new_docids)
    new_index.to_index = IF.difference(to_index, new_index.indexed)
    new_index.n_to_index = len(new_index.to_index)

    # Set of docids to unindex (user may have deleted something during reindex)
    # should be pretty small.  Just go ahead and handle that here.
    to_unindex = IF.difference(new_docids, old_docids)
    for docid in to_unindex:
        new_index.unindex_doc(docid)


def get_index_docids(index):
    # We have to peek inside the index because listing the docids
    # is not an exposed API.
    if isinstance(index, KarlPGTextIndex):
        cursor = index.cursor
        cursor.execute("SELECT docid from %(table)s" % index._subs)
        return (row[0] for row in cursor)
    elif isinstance(index, CatalogTextIndex):
        return index.index._docwords.keys()
    else:
        raise TypeError("Don't know how to get_index_docids from %s" % index)


def get_catalog_docids(catalog):
    return catalog.document_map.docid_to_address.keys()


def reindex_batch(args, site):
    catalog = find_catalog(site)
    addr = catalog.document_map.address_for_docid
    new_index = catalog['new_texts']
    to_index = new_index.to_index
    indexed = new_index.indexed
    l = new_index.n_to_index
    offset = l - len(to_index)
    batch = []
    for i in xrange(min(BATCH_SIZE, len(to_index))):
        batch.append(to_index[i])
    for i, docid in enumerate(batch):
        to_index.remove(docid)
        indexed.add(docid)
        path = addr(docid)
        if path is None:
            continue
        try:
            doc = find_model(site, path)
        except KeyError:
            log.warn("No object at path: %s", path)
            continue

        log.info("Reindexing (%d/%d) %s", i + offset + 1, l, path)
        new_index.index_doc(docid, doc)
        deactivate = getattr(doc, '_p_deactivate', None)
        if deactivate is not None:
            deactivate()

