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

""" Remove the '_extracted_data' cache attr from files.
"""

import transaction

import logging
log = logging.getLogger(__name__)

from karl.utilities.cleanup import remove_extracted_data as RED


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Removed cached _extracted_data from files.')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Dry run?')
    parser.add_argument('inst', metavar='instance', help='Karl instance.')
    parser.set_defaults(func=remove_extracted_data, parser=parser,
                        subsystem='remove_extracted_data', dry_run=False)

def remove_extracted_data(args):
    root, closer = args.get_root(args.inst)

    for i, doc in enumerate(RED(root, log)):
        if args.dry_run:
            transaction.abort()
        else:
            transaction.commit()
        root._p_jar.sync()
    closer()
