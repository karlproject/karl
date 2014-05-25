import sys
import transaction

from pyramid.traversal import find_resource

from karl.scripting import create_karl_argparser
from karl.models.subscribers import reindex_content
from karl.utils import find_profiles

def main(argv=sys.argv):
    parser =  create_karl_argparser("Change creator of content.")
    parser.add_argument('user')
    parser.add_argument('path')
    args = parser.parse_args(argv[1:])
    config_uri = args.config_uri
    env = args.bootstrap(config_uri)
    root, closer = env['root'], env['closer']
    content = find_resource(root, args.path)
    profiles = find_profiles(root)
    if not args.user in profiles:
        args.parser.error("No such user: %s" % args.user)
    content.creator = content.modified_by = args.user
    reindex_content(content, None)
    transaction.commit()
    closer()
