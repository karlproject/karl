import logging
import sys
import transaction

from ZODB.POSException import ConflictError

from karl.utilities.mailin import MailinRunner2

from karl.application import is_normal_mode
from karl.scripting import create_karl_argparser
from karl.scripting import daemonize_function
from karl.scripting import only_one

log = logging.getLogger(__name__)

def main(argv=sys.argv):
    default_interval = 300
    parser = create_karl_argparser(description='Process incoming mail.')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="Run in daemon mode.")
    parser.add_argument('-i', '--interval', type=int, default=default_interval,
                        help="Interval in seconds between executions in "
                        "daemon mode.  Default is %d." % default_interval)

    args = parser.parse_args(sys.argv[1:])

    env = args.bootstrap(args.config_uri)

    if not is_normal_mode(env['registry']):
        log.info("Cannot run mailin: Running in maintenance mode.")
        sys.exit(2)
        

    if args.daemon:
        daemonize_function(mailin, args.interval)(args, env, parser)
    else:
        mailin(args, env, parser)

def mailin(args, env, parser):
    log.info('Processing mailin')
    env = args.bootstrap(args.config_uri)
    root, closer, registry = env['root'], env['closer'], env['registry']

    settings = registry.settings

    zodb_uri = settings.get('zodbconn.uri.postoffice', None)
    if zodb_uri is None:
        # Backwards compatible
        zodb_uri = settings.get('postoffice.zodb_uri')
    zodb_path = settings.get('postoffice.zodb_path', '/postoffice')
    queue = settings.get('postoffice.queue')

    if zodb_uri is None:
        parser.error("zodbconn.uri.postoffice must be set in config file")

    if queue is None:
        parser.error("postoffice.queue must be set in config file")

    only_one(go, registry, 'mailin')(root, zodb_uri, zodb_path, queue, closer)

def go(root, zodb_uri, zodb_path, queue, closer):
    runner = None

    try:
        runner = MailinRunner2(root, zodb_uri, zodb_path, queue)
        runner()
        transaction.commit()

        p_jar = getattr(root, '_p_jar', None)
        if p_jar is not None:
            # Attempt to fix memory leak
            p_jar.db().cacheMinimize()

    except ConflictError:
        transaction.abort()
        log.info('ZODB conflict error:  retrying later')

    except:
        transaction.abort()
        raise

    finally:
        closer()
        if runner is not None:
            runner.close()
