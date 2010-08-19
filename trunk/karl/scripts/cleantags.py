"""Reassign tags owned by users who no longer exist.
"""
from karl.scripting import get_default_config
from karl.scripting import open_root
import logging
import optparse
import sys
import transaction

log = logging.getLogger("cleantags")

def cleantags(site, assign_to):
    profiles = site['profiles']
    engine = site.tags
    for user in list(engine.getUsers()):
        if not user in profiles:
            log.warn("Reassigning tags by missing user '%s' to '%s'",
                user, assign_to)
            engine.reassign(user, assign_to)

def main(argv=sys.argv, root=None):
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('--assign-to', '-a', dest='assign_to',
        default='system', metavar='USER',
        help="Assign tags for missing users to USER (default: system)")
    parser.add_option('--dry-run', '-n', dest='dry_run',
        action='store_true', default=False,
        help="Don't actually commit any transaction")
    options, args = parser.parse_args(argv[1:])

    logging.basicConfig()

    if root is None:
        config = options.config
        if config is None:
            config = get_default_config()
        root, closer = open_root(config)

    try:
        cleantags(root, options.assign_to)
    except:
        transaction.abort()
        raise
    else:
        if options.dry_run:
            print '*** aborting ***'
            transaction.abort()
        else:
            print '*** committing ***'
            transaction.commit()

if __name__ == '__main__':
    main()
