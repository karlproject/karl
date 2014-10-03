import datetime
import transaction
import sys

from pyramid.traversal import find_resource

from karl.scripting import create_karl_argparser
from karl.models.subscribers import reindex_content


def parse_date(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d:%H:%M')
    except ValueError:
        return datetime.datetime.strptime(s, '%Y-%m-%d')

def main(argv=sys.argv):
    parser = create_karl_argparser(
        "Backdate created and modified timestamps of content."
        )
    parser.add_argument('date', type=parse_date)
    parser.add_argument('path')
    args = parser.parse_args(argv[1:])
    config_uri = args.config_uri
    env = args.bootstrap(config_uri)
    root, closer = env['root'], env['closer']
    content = find_resource(root, args.path)
    content.created = content.modified = args.date
    reindex_content(content, None)
    transaction.commit()
    closer()
