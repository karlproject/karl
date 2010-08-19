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
"""Reconfigure the people directory based on an XML file.

Reindex if necessary.
"""
from ConfigParser import ConfigParser
from karl.models.peopledirectory import PeopleDirectory
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.utilities.peopleconf import peopleconf
from lxml import etree
import optparse
import os
import sys
import transaction

def run_peopleconf(root, config, peopleconf_func=peopleconf,
        force_reindex=False):
    cp = ConfigParser()
    cp.read(config)
    fn = os.path.join(os.path.dirname(config), cp.get('peopleconf', 'file'))
    tree = etree.parse(fn)

    if 'people' in root and not isinstance(root.get('people'), PeopleDirectory):
        # remove the old people directory
        del root['people']
    if 'people' not in root:
        root['people'] = PeopleDirectory()
        force_reindex = True
    peopleconf_func(root['people'], tree, force_reindex=force_reindex)

def main(argv=sys.argv, root=None, peopleconf_func=peopleconf):
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('-f', '--force-reindex', dest='force_reindex',
        action='store_true', default=False,
        help="Reindex the people catalog unconditionally")
    parser.add_option('--dry-run', dest='dryrun',
        action='store_true', default=False,
        help="Don't actually commit the transaction")
    options, args = parser.parse_args(argv[1:])
    if args:
        parser.error("Too many parameters: %s" % repr(args))

    config = options.config
    if config is None:
        config = get_default_config()
    if root is None:
        root, closer = open_root(config)

    try:
        run_peopleconf(root, config, peopleconf_func,
            force_reindex=options.force_reindex)
    except:
        transaction.abort()
        raise
    else:
        if options.dryrun:
            transaction.abort()
        else:
            transaction.commit()

if __name__ == '__main__':
    main()
