# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

""" startover [OPTIONS]

Reset the site to its inital, empty state:

o Delete / recreate the site.

Options
=======

o --yes                    commit the transaction.

o --no                     Don't commit the transaction.

o --quiet (-q)             Quiet:  no extraneous output.

o --verbose (-v)           Increase verbosity of output.
"""

import getopt
import sys
import transaction

class StartOver:

    do_commit = False
    verbosity = 1

    def __init__(self, argv):
        self.parseCommandLine(argv)

    def usage(self, message=None, rc=1):
        print __doc__
        if message is not None:
            print message
            print
        sys.exit(rc)

    def section(self, message, sep='-', verbosity=0):
        if self.verbosity > verbosity:
            print sep * 65
            print message
            print sep * 65

    def parseCommandLine(self, argv):

        self.name, argv = argv[0], argv[1:]

        try:
            opts, args = getopt.getopt(argv, 'qvynz:p:?h',
                                             ['yes',
                                              'no',
                                              'quiet',
                                              'verbose',
                                              'help',
                                             ])
        except getopt.GetoptError, e:
            self.usage(e)

        if args:
            self.usage('No arguments are allowed!')

        for k, v in opts:
            if k in ('-y', '--yes'):
                self.do_commit = True
            elif k in ('-n', '--no'):
                self.do_commit = False
            elif k in ('-q', '--quiet'):
                self.verbosity = 0
            elif k in ('-v', '--verbose'):
                self.verbosity += 1
            elif k in ('-h', '-?', '--help'):
                self.usage(rc=2)

    def setup(self):
        from karl.scripting import get_default_config
        from karl.scripting import open_root
        root, self.closer = open_root(get_default_config())
        self.root = root._p_jar.root()

    def deleteSite(self):
        self.section('Deleting site.')
        try:
            del self.root['site']
        except KeyError:
            pass

    def createSite(self):
        from zope.component import queryUtility
        from karl.bootstrap.bootstrap import populate
        from karl.bootstrap.interfaces import IBootstrapper
        self.section('Creating site.')
        bootstrap = queryUtility(IBootstrapper, default=populate)
        bootstrap(self.root, do_transaction_begin=False)

    def __call__(self):
        self.setup()
        self.deleteSite()
        self.createSite()

        if self.do_commit:
            transaction.commit()
        else:
            transaction.abort()
        self.closer()

def main():
    StartOver(sys.argv)()

if __name__ == '__main__':
    main()
