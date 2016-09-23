from datetime import datetime
import logging
import sys
import transaction

from karl.scripting import create_karl_argparser


log = logging.getLogger(__name__)


def main(argv=sys.argv):
    parser = create_karl_argparser(
        description='Set password expiration date for user.'
        )
    parser.add_argument('username', help="Username.")
    parser.add_argument('date', help="Reset date (YYYY-MM-DD).")
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer, registry = env['root'], env['closer'], env['registry']
    profiles = root['profiles']
    if args.username not in profiles:
        log.info("User %s not found." % args.username)
    else:
        log.info("Setting password expiration date for user %s" % args.username)
        expiration_date = datetime.strptime(args.date, '%Y-%m-%d')
        profiles[args.username].password_expiration_date = expiration_date
        log.info("Date set to: %s" % expiration_date)
        transaction.commit()
    closer()
