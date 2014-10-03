"""Reassign tags owned by users who no longer exist.
"""
import sys
import transaction

from karl.scripting import create_karl_argparser

def main(argv=sys.argv):
    parser = create_karl_argparser(
        description="Reassign tags owned by users who no longer exist."
        )
    parser.add_argument(
        '-a',
        '--assign_to',
        dest='assign_to',
        help='User to reassign tags to'
        )
    parser.add_argument(
        '--dry-run',
        dest='dryrun',
        action='store_true',
        help="Don't actually commit the transaction"
        )
    parser.set_defaults(assign_to='admin', dryrun=False)
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    profiles = root['profiles']
    engine = root.tags
    assign_to = args.assign_to
    print "searching for tags with non-existing user"
    for user in list(engine.getUsers()):
        if not user in profiles:
            print "Reassigning tags by missing user '%s' to '%s'"  % (
                user, assign_to)
            engine.reassign(user, assign_to)
    if args.dryrun:
        print '*** aborting ***'
        transaction.abort()
    else:
        print '*** committing ***'
        transaction.commit()
    closer()

