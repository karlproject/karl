import transaction

from pyramid.traversal import find_resource

from karl.models.subscribers import reindex_content
from karl.utils import find_profiles


def config_parser(name, subparsers, **helpers):
    parser =  subparsers.add_parser(name,
        help="Backdate created and modified timestamps of content.")
    parser.add_argument('inst')
    parser.add_argument('user')
    parser.add_argument('path')
    parser.set_defaults(func=chown, parser=parser)


def chown(args):
    root, closer = args.get_root(args.inst)
    content = find_resource(root, args.path)
    profiles = find_profiles(root)
    if not args.user in profiles:
        args.parser.error("No such user: %s" % args.user)
    content.creator = content.modified_by = args.user
    reindex_content(content, None)
    transaction.commit()
