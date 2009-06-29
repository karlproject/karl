""" Run evolution steps for the OSI site  """

import getopt
import os
import sys

from repoze.evolution import ZODBEvolutionManager
from repoze.evolution import evolve_to_latest

from karl.scripting import get_default_config
from karl.scripting import open_root

def usage(e=None):
    if e is not None:
        print e
    print "evolve [--latest] [--set-db-version=num] "
    print "  Evolves news database with changes from scripts in osi.evolve"
    print "     - with no arguments, evolve just displays versions"
    print "     - with the --latest argument, evolve runs scripts as necessary"
    print "     - with the --set-db-version argument, evolve runs no scripts"
    print "       but just sets the database 'version number' to an "
    print "       arbitrary integer number"
    sys.exit(2)

def main(argv=sys.argv):
    name, argv = argv[0], argv[1:]
    latest = False
    set_version = None

    try:
        opts, args = getopt.getopt(argv, 'l?hs:',
                                         ['latest',
                                          'set-db-version=',
                                          'help',
                                         ])
    except getopt.GetoptError, e:
        usage(e)

    if args:
        usage('No arguments are allowed.')

    for k, v in opts:
        if k in ('-l', '--latest'):
            latest = True
        if k in ('-h', '-?', '--help'):
            usage()
        if k in ('-s', '--set-db-version'):
            try:
                set_version = int(v)
                if set_version < 0:
                    raise Exception
            except:
                usage('Bad version number %s' % v)

    if latest and (set_version is not None):
        usage('Cannot use both --latest and --set-version together')

    root, closer = open_root(get_default_config())

    from osi.evolve.zodb import VERSION
    manager = ZODBEvolutionManager(root, 'osi.evolve.zodb', VERSION)
    db_version = manager.get_db_version()
    print 'Code at software version %s' % VERSION
    print 'Database at version %s' % db_version
    if set_version is not None:
        manager._set_db_version(set_version)
        manager.transaction.commit()
        print 'Database version set to %s' % set_version
    else:
        if VERSION == db_version:
            print 'Nothing to do'
        elif latest:
            try:
                evolve_to_latest(manager)
            finally:
                print 'Evolved to %s' % manager.get_db_version()
        else:
            print 'Not evolving (use --latest to do actual evolution)'

if __name__ == '__main__':
    main()
