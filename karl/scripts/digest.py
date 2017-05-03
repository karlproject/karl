import logging
import sys

from karl.scripting import create_karl_argparser
from karl.scripting import daemonize_function
from karl.scripting import only_one

from karl.utilities.alerts import Alerts

from karl.application import is_normal_mode

log = logging.getLogger(__name__)

def digest(root, closer, registry, frequency):
    if not is_normal_mode(registry):
        log.info("Cannot send mails; running in maintenance mode.")
        sys.exit(1)
    alerts = Alerts()
    freq = frequency
    alerts.send_digests(root, freq)

def main(argv=sys.argv):
    default_interval = 6 * 3600  # 6 hours
    parser =  create_karl_argparser(
        description='Send digest emails.'
        )
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="Run in daemon mode.")
    parser.add_argument('-i', '--interval', type=int, default=default_interval,
                        help="Interval in seconds between executions in "
                        "daemon mode.  Default is %d." % default_interval)
    parser.add_argument('-f', '--frequency', dest='frequency', default='daily',
                      help='Digest frequency:  daily/weekly/biweekly.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer, registry = env['root'], env['closer'], env['registry']
    if args.daemon:
        f = daemonize_function(digest, args.interval)
        only_one(f, registry, 'digest')(root, closer, registry, args.frequency)
    else:
        only_one(digest, registry, 'digest')(
            root, closer, registry, args.frequency)
    closer()
    import gc; gc.collect() # Work around relstorage cache bug.
