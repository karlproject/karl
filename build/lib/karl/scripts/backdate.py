import datetime
import transaction

from pyramid.traversal import find_resource

from karl.models.subscribers import reindex_content


def config_parser(name, subparsers, **helpers):
    parser =  subparsers.add_parser(name,
        help="Backdate created and modified timestamps of content.")
    parser.add_argument('inst')
    parser.add_argument('date', type=parse_date)
    parser.add_argument('path')
    parser.set_defaults(func=backdate, parser=parser)


def parse_date(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d:%H:%M')
    except ValueError:
        return datetime.datetime.strptime(s, '%Y-%m-%d')


def backdate(args):
    root, closer = args.get_root(args.inst)
    content = find_resource(root, args.path)
    content.created = content.modified = args.date
    reindex_content(content, None)
    transaction.commit()
