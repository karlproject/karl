import feedparser
import logging
import sys
import transaction

from repoze.lemonade.content import create_content

from karl.models.interfaces import IFeed
from karl.models.interfaces import IFeedsContainer
from karl.scripting import create_karl_argparser
from karl.scripting import daemonize_function
from karl.application import is_normal_mode

log = logging.getLogger(__name__)


def add_feed(argv=sys.argv):
    parser = create_karl_argparser(description='Add a new feed.')
    parser.add_argument('-t', '--title', help='Override title of feed.')
    parser.add_argument('-m', '--max', type=int, default=0,
                        help='Maximum number of entries to keep at a time.')
    parser.add_argument('name', help='Identifier of feed in database.')
    parser.add_argument('url', help='URL of feed.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    feed = get_feed(root, args.name)
    if feed is not None:
        args.parser.error("Feed already exists with name: %s" % args.name)
    name = args.name
    override_title = args.title
    max_entries = args.max
    url = args.url
    container = root.get('feeds')
    if container is None:
        container = create_content(IFeedsContainer)
        root['feeds'] = container

    assert name not in container, "Feed already exists: %s" % name
    feed = create_content(IFeed, override_title)
    feed.url = url
    feed.max_entries = max_entries
    container[name] = feed
    feed.override_title = bool(override_title)
    transaction.commit()

def edit_feed(argv=sys.argv):
    parser = create_karl_argparser(description='Edit a feed.')
    parser.add_argument('name', help='Identifier of feed in database.')
    parser.add_argument('-t', '--title', help='Override title of feed.')
    parser.add_argument('--use-feed-title', action='store_true',
                        help='Use feed title. Undoes previous override.')
    parser.add_argument('-m', '--max', type=int,
                        help='Maximum number of entries to keep at a time.')
    parser.add_argument('-u', '--url', help='URL of feed.')
    parser.set_defaults(func=edit_feed, parser=parser)
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    feed = get_feed(root, args.name)
    if feed is None:
        args.parser.error("No such feed: %s"  % args.name)
    if args.max is not None:
        feed.max_entries = args.max
    if args.url is not None:
        feed.url = args.url
    if args.use_feed_title:
        feed.title = None
        feed.override_title = False
    elif args.title is not None:
        feed.title = args.title
        feed.override_title = True
    transaction.commit()

def list_feeds(argv=sys.argv):
    parser = create_karl_argparser(description='List feeds.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    feeds = root.get('feeds')
    if feeds is None or len(feeds) == 0:
        print >> args.out, 'No feeds configured.'
        return
    for name in sorted(feeds.keys()):
        feed = feeds.get(name)
        print >> args.out, "%s:" % name
        print >> args.out, "\turl: %s" % feed.url
        print >> args.out, "\ttitle: %s" % feed.title
        print >> args.out, "\tmax entries: %d" % feed.max_entries

def remove_feed(argv=sys.argv):
    parser = create_karl_argparser(description='Remove a feed.')
    parser.add_argument('name', help='Name of feed.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    feeds = root.get('feeds')
    if not feeds or args.name not in feeds:
        args.parser.error("No such feed: %s" % args.name)
    del feeds[args.name]
    transaction.commit()

def update_feeds(argv=sys.argv):
    default_interval = 1800  # 30 minutes
    parser = create_karl_argparser(
        description='Get new entries from feeds.'
        )
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="Run in daemon mode.")
    parser.add_argument('-i', '--interval', type=int, default=default_interval,
                        help="Interval in seconds between executions in "
                        "daemon mode.  Default is %d." % default_interval)
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force reload of feed entries.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    
    if args.daemon:
        daemonize_function(_update_feeds, args.interval)(args, env)
    else:
        _update_feeds(args, env)


def _update_feeds(args, env):
    registry = env['registry']
    root = env['root']
    if not is_normal_mode(registry):
        log.info("Cannot update feeds: Running in maintenance mode.")
        return
    container = root.get('feeds')
    if container is None:
        return

    force = args.force

    for name in sorted(container.keys()):
        feed = container.get(name)
        log.info("Updating feed: %s: %s", name, feed.url)
        _update_feed(feed, log, force)
    transaction.commit()


def get_feed(root, name):
    container = root.get('feeds')
    if container is None:
        return None
    return container.get(name)

def _update_feed(feed, log, force=False):
    kw = {}
    if not force:
        if feed.etag:
            kw['etag'] = feed.etag
        if feed.feed_modified:
            kw['modified'] = feed.feed_modified

    parser = feedparser.parse(feed.url, **kw)
    status = parser.get('status', '(failed)')

    if status == 200:
        log.info('200 (ok)')
    elif status == 301:
        log.info('301 (moved)')
        log.info('Feed has moved. Updating URL to %s', parser.href)
        feed.url = parser.href
    elif status == 304:
        log.info('304 (unchanged)')
        return
    elif status == 410:
        log.info('410 (gone)')
        log.warn('Feed has gone away. You probably want to delete it: %',
                 feed.__name__)
    else:
        log.info(str(status))

    if parser.bozo:
        exc = parser.bozo_exception
        log.warn("Warning for feed '%s': %s", feed.__name__, exc)

    if parser.feed:
        title = feed.title
        max_entries = feed.max_entries
        feed.update(parser)
        if max_entries and len(feed.entries) > max_entries:
            del feed.entries[max_entries:]
        if feed.override_title:
            feed.title = title
    else:
        log.info("No data for feed '%s'. Skipping.", feed.__name__)
