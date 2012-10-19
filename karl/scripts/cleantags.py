"""Reassign tags owned by users who no longer exist.
"""
from karlserve.instance import set_current_instance
import transaction


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(name,
        help="Reassign tags owned by users who no longer exist.")
    parser.add_argument('-a', '--assign_to', dest='assign_to',
        help='User to reassign tags to')
    parser.add_argument('--dry-run', dest='dryrun',
        action='store_true',
        help="Don't actually commit the transaction")
    helpers['config_choose_instances'](parser)
    parser.set_defaults(func=main, parser=parser,
        assign_to='admin', dryrun=False)


def main(args):
    for instance in args.instances:
        cleantags(args, instance)

def cleantags(args, instance):
    root, closer = args.get_root(instance)
    set_current_instance(instance)
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

