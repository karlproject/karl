import argparse
import datetime
import transaction
import sys

from pyramid.traversal import find_resource
from pyramid.paster import bootstrap

from karl.scripting import get_default_config
from karl.models.subscribers import reindex_content


def parse_date(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d:%H:%M')
    except ValueError:
        return datetime.datetime.strptime(s, '%Y-%m-%d')

def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description="Backdate created and modified timestamps of content."
        )
    parser.add_argument(
        '-C', '--config',
        metavar='FILE',
        default=None,
        dest='config_uri',
        help='Path to configuration ini file (defaults to $CWD/etc/karl.ini).'
        )
    parser.add_argument('date', type=parse_date)
    parser.add_argument('path')
    args = parser.parse_args(argv[1:])
    config_uri = args.config_uri
    if config_uri is None:
        config_uri = get_default_config()
    env = bootstrap(config_uri)
    root, closer = env['root'], env['closer']
    content = find_resource(root, args.path)
    content.created = content.modified = args.date
    reindex_content(content, None)
    transaction.commit()
    closer()
