import sys

from karl.utilities.peopleconf import dump_peopledir
from karl.utilities.peopleconf import peopleconf
from karl.models.peopledirectory import PeopleDirectory
from karl.scripting import create_karl_argparser

from lxml import etree
import transaction


def dump(argv=sys.argv):
    parser = create_karl_argparser(
        description='Dump people directory configuration.'
        )
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    print >> args.out, dump_peopledir(root['people'])


def load(argv=sys.argv):
    parser = create_karl_argparser(
        description='Load people directory configuration.'
        )
    parser.add_argument('-f', '--force-reindex', action='store_true',
                        help='Reindex the people directory unconditionally.')
    parser.add_argument('filename', help='Name of XML to load.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    force_reindex = args.force_reindex
    root, closer = env['root'], env['closer']
    tree = etree.parse(args.filename)

    if 'people' in root and not isinstance(root['people'], PeopleDirectory):
        # remove the old people directory
        del root['people']

    if 'people' not in root:
        root['people'] = PeopleDirectory()
        force_reindex = True

    peopleconf(root['people'], tree, force_reindex=force_reindex)
    transaction.commit()
