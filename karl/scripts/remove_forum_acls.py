"""Remove local Deny ACLs from forums.
"""
import sys
import transaction

from karl.content.interfaces import IForumTopic
from karl.models.interfaces import ICatalogSearch
from karl.scripting import create_karl_argparser


DENY_ACL = ('Deny', 'system.Everyone', ('edit', 'delete'))


def main(argv=sys.argv):
    parser = create_karl_argparser(
        description="Remove local Deny ACLs from forums."
        )
    parser.add_argument(
        '-l',
        '--limit',
        dest='limit',
        help='Number of forums to process'
        )
    parser.add_argument(
        '--dry-run',
        dest='dryrun',
        action='store_true',
        help="Don't actually commit the transaction"
        )
    parser.add_argument('path')
    parser.set_defaults(limit=0, dryrun=False)
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    searcher = ICatalogSearch(root)
    kw = {'interfaces': [IForumTopic], 'path': args.path}
    numdocs, docids, resolver = searcher(**kw)
    limit = int(args.limit)
    print "Removing Deny acl from forum topics under %s" % args.path
    if limit > 0:
        print "Limiting to %d topics" % limit
    if limit == 0:
        limit = numdocs
    # make sure it's a list and not a btree
    docids = list(docids)
    for docid in docids[:limit]:
        topic = resolver(docid)
        if DENY_ACL in topic.__acl__:
            acl = topic.__acl__
            acl.remove(DENY_ACL)
            topic.__acl__ = acl
            print "Removed Deny ACL from %s" % topic.title
    if args.dryrun:
        print '*** aborting ***'
        transaction.abort()
    else:
        print '*** committing ***'
        transaction.commit()
    closer()
