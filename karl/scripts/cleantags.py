"""Reassign tags owned by users who no longer exist.
"""
import argparse
import sys
import transaction

from pyramid.paster import bootstrap

from karl.scripting import get_default_config

def main(argv=sys.argv):
    parser =  argparse.ArgumentParser(
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
    parser.add_argument(
        '-C', '--config',
        metavar='FILE',
        default=None,
        dest='config_uri',
        help='Path to configuration ini file (defaults to $CWD/etc/karl.ini).'
        )
    parser.set_defaults(assign_to='admin', dryrun=False)
    args = parser.parse_args(argv[1:])
    config_uri = args.config_uri
    if config_uri is None:
        config_uri = get_default_config()
    env = bootstrap(config_uri)
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

