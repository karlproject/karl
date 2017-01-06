import sys

from karl.scripting import create_karl_argparser

from j1m.relstoragejsonsearch.updater import main as updater


def main(argv=sys.argv):
    parser = create_karl_argparser(description='Process incoming mail.')

    args = parser.parse_args(sys.argv[1:])

    env = args.bootstrap(args.config_uri)

    root, registry = env['root'], env['registry']

    settings = registry.settings
    url = settings['repozitory_db_string']
    print 'DB url string: %s' % url

    print 'Starting JSON Updater...'
    updater(args=[url])
