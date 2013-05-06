import logging
import transaction

from karl.utilities.usersync import UserSync

from karlserve.instance import set_current_instance
from karlserve.log import set_subsystem


log = logging.getLogger(__name__)


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Sync users to external data source.')
    parser.add_argument('--username', '-U', default=None,
                        help='Username for BASIC Auth')
    parser.add_argument('--password', '-P', default=None,
                        help='Password for BASIC Auth')
    parser.add_argument('inst', metavar='instance', help='Karl instnace.')
    parser.add_argument('url', help="URL of data source.")
    parser.set_defaults(func=usersync, parser=parser,
                        subsystem='update_feeds', only_one=True)


def usersync(args):
    root, closer = args.get_root(args.inst)
    set_current_instance(args.inst)
    set_subsystem('usersync')
    log.info("Syncing users at %s" % args.url)
    sync = UserSync(root)
    sync(args.url, args.username, args.password)
    transaction.commit()


