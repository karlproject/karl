from karl.utilities.peopleconf import dump_peopledir
from karl.utilities.peopleconf import peopleconf
from karl.models.peopledirectory import PeopleDirectory

from lxml import etree
import transaction


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Dump or load a people directory configuration.')
    subparsers = parser.add_subparsers(
        title='command', help='People configuration commands.')
    config_dump(subparsers, **helpers)
    config_load(subparsers, **helpers)


def config_dump(subparsers, **helpers):
    parser = subparsers.add_parser(
        'dump', help='Dump people directory configuration.')
    parser.add_argument('inst', metavar='instance', help='Instance name.')
    parser.set_defaults(func=dump, parser=parser)


def config_load(subparsers, **helpers):
    parser = subparsers.add_parser(
        'load', help='Load people directory configuration.')
    parser.add_argument('inst', metavar='instance', help='Instance name.')
    parser.add_argument('-f', '--force-reindex', action='store_true',
                        help='Reindex the people directory unconditionally.')
    parser.add_argument('filename', help='Name of XML to load.')
    parser.set_defaults(func=load, parser=parser)


def dump(args):
    root, closer = args.get_root(args.inst)
    print >> args.out, dump_peopledir(root['people'])


def load(args):
    force_reindex = args.force_reindex
    root, closer = args.get_root(args.inst)
    tree = etree.parse(args.filename)

    if 'people' in root and not isinstance(root['people'], PeopleDirectory):
        # remove the old people directory
        del root['people']

    if 'people' not in root:
        root['people'] = PeopleDirectory()
        force_reindex = True

    peopleconf(root['people'], tree, force_reindex=force_reindex)
    transaction.commit()
