import sys
try:
    from repoze.pgtextindex.index import PGTextIndex
except ImportError:
    print >>sys.stderr, (
        "In order to use this experimental functionality, you must install\n"
        "repoze.pgtextindex from subversion as a development egg. The source\n"
        "code is located here:\n\n"
        "http://svn.repoze.org/repoze.pgtextindex/trunk/"
    )
    sys.exit(1)

from karl.models.catalog import reindex_catalog
from karl.models.site import get_weighted_textrepr
from karl.scripting import get_default_config
from karl.scripting import open_root
from optparse import OptionParser

import transaction

def main(args=sys.argv):
    parser = OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")
    parser.add_option('-D', '--dsn', dest='dsn', default=None,
                      help="dsn to connect to postgresql database")
    parser.add_option('-n', '--database-name', dest='database_name',
                      default=None,
                      help="Name of database to connect to")
    parser.add_option('-d', '--dry-run', dest='dry_run',
        action="store_true", default=False,
        help="Don't commit the transactions")
    parser.add_option('-i', '--interval', dest='commit_interval',
        action="store", default=200,
        help="Commit every N transactions")

    options, args = parser.parse_args()
    if args:
        parser.error("Too many parameters: %s" % repr(args))

    commit_interval = int(options.commit_interval)

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    def output(msg):
        print msg

    try:
        index = PGTextIndex(
            get_weighted_textrepr,
            options.dsn, # "dbname=karl user=karl host=localhost password=karl",
            database_name=options.database_name
        )

        if options.dry_run:
            transaction.abort()
        else:
            transaction.commit()

        # reindex_catalog commits its own transactions
        catalog = root.catalog
        catalog['texts'] = index
        reindex_catalog(root, commit_interval=commit_interval,
                         dry_run=options.dry_run, output=output)
    except:
        transaction.abort()
        raise
