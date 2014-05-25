import sys
import transaction

from repoze.evolution import IEvolutionManager
from repoze.evolution import evolve_to_latest

from zope.component import getUtilitiesFor

from karl.scripting import create_karl_argparser

def main(argv=sys.argv):
    parser = create_karl_argparser(
        description='Bring database up to date with code.'
        )
    parser.add_argument('--latest', action='store_true',
                        help='Update to latest versions.')
    args = parser.parse_args(argv[1:])
    out =  args.out

    env = args.bootstrap(args.config_uri)

    root, closer = env['root'], env['closer']

    print >> out, "=" * 78

    managers = list(getUtilitiesFor(IEvolutionManager))

    for pkg_name, factory in managers:
        __import__(pkg_name)
        pkg = sys.modules[pkg_name]
        VERSION = pkg.VERSION
        print >> out, 'Package %s' % pkg_name
        manager = factory(root, pkg_name, VERSION, 0)
        db_version = manager.get_db_version()
        print >> out, 'Code at software version %s' % VERSION
        print >> out, 'Database at version %s' % db_version
        if VERSION <= db_version:
            print >> out, 'Nothing to do'
        elif args.latest:
            evolve_to_latest(manager)
            ver = manager.get_db_version()
            print >> out, 'Evolved %s to %s' % (pkg_name, ver)
        else:
            print >> out, 'Not evolving (use --latest to do actual evolution)'
        print >> out, ''

    transaction.commit()
