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
"""Dump / reload the people directory configuration as an XML file.

  $ bin/peopleconf dump  # writes to standard output.

  $ bin/peopleconf load <filename>

Reindexes the peopledir catalog if necessary.
"""
import optparse
import transaction

from lxml import etree

from karl.models.peopledirectory import PeopleDirectory
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.utilities.peopleconf import peopleconf
from karl.utilities.peopleconf import dump_peopledir


class HelpFormatter(optparse.IndentedHelpFormatter):

    def format_description(self, description):
        return '%s\n' % description


def dump_peopleconf(root):
    print dump_peopledir(root['people']).encode('utf8')

def load_peopleconf(root, filename,
                    force_reindex=False,
                    peopleconf_func=peopleconf,
                   ):

    tree = etree.parse(filename)

    if 'people' in root and not isinstance(root.get('people'), PeopleDirectory):
        # remove the old people directory
        del root['people']

    if 'people' not in root:
        root['people'] = PeopleDirectory()
        force_reindex = True

    peopleconf_func(root['people'], tree, force_reindex=force_reindex)

def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv

    parser = optparse.OptionParser(description=__doc__,
                                   formatter=HelpFormatter(),
                                  )

    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')

    parser.add_option('-f', '--force-reindex', dest='force_reindex',
        action='store_true', default=False,
        help="Reindex the people catalog unconditionally")

    parser.add_option('--dry-run', dest='dry_run',
        action='store_true', default=False,
        help="Don't actually commit the transaction")

    options, args = parser.parse_args(argv[1:])
    if not args or args[0] not in ('dump', 'load'):
        parser.error("Must specify either 'dump' or 'load <filename>'"
                        % repr(args))

    kw = {}

    if args[0] == 'dump':
        if len(args) > 1:
            parser.error("Must specify either 'dump' or 'load <filename>'"
                            % repr(args))
        if options.force_reindex:
            parser.error("--force-reindex invalid for 'dump'")
        func = dump_peopleconf
        do_commit = False
    else: # 'load'
        if len(args) != 2:
            parser.error("Must specify either 'dump' or 'load <filename>'"
                            % repr(args))
        func = load_peopleconf
        kw['filename'] = args[1]
        if options.force_reindex:
            kw['force_reindex'] = True
        do_commit = not options.dry_run
 
    config = options.config
    if config is None:
        config = get_default_config()

    root, closer = open_root(config)

    func(root, **kw)

    if do_commit:
        transaction.commit()

if __name__ == '__main__':
    import sys
    main(sys.argv)
