import argparse
import sys
import transaction

from pyramid.paster import bootstrap
from pyramid.traversal import find_resource

from karl.models.subscribers import reindex_content
from karl.utils import find_profiles

def main(argv=sys.argv):
    parser =  argparse.ArgumentParser(description="Change creator of content.")
    parser.add_argument('user')
    parser.add_argument('path')
    parser.add_argument(
        '-C', '--config',
        metavar='FILE',
        default=None,
        dest='config_uri',
        help='Path to configuration ini file.'
        )
    args = parser.parse_args(argv[1:])
    env = bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    content = find_resource(root, args.path)
    profiles = find_profiles(root)
    if not args.user in profiles:
        args.parser.error("No such user: %s" % args.user)
    content.creator = content.modified_by = args.user
    reindex_content(content, None)
    transaction.commit()
    closer()
