import logging
import sys
import transaction

from karl.scripting import create_karl_argparser, only_one

from karl.utilities.usersync import UserSync

log = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser =  create_karl_argparser(
        description='Sync users to external data source.'
        )
    parser.add_argument('--username', '-U', default=None,
                        help='Username for BASIC Auth')
    parser.add_argument('--password', '-P', default=None,
                        help='Password for BASIC Auth')
    parser.add_argument('--password-file', '-F', default=None,
                        help='Read password for BASIC Auth from file')
    parser.add_argument('url', help="URL of data source.")
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer, registry = env['root'], env['closer'], env['registry']
    if args.password and args.password_file:
        args.parser.error('cannot set both --password and --password-file')
    if args.password_file:
        with open(args.password_file) as f:
            password = f.read().strip('\n')
    else:
        password = args.password
    log.info("Syncing users at %s" % args.url)
    sync = UserSync(root)
    only_one(sync, registry, 'usersync')(args.url, args.username, password)
    transaction.commit()
    closer()
