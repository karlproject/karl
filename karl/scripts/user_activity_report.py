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

"""
Generate some statistics about usage.
"""

import csv
import optparse
import os
import sys

from paste.deploy import loadapp
from pyramid.scripting import get_root

from karl.scripting import get_default_config
from karl.utilities import stats

import logging
logging.basicConfig()

def main(argv=sys.argv):
    parser = optparse.OptionParser(
        description=__doc__,
        usage="%prog [options] [user1, user2, ...]",
        )
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('-f', '--filter', dest='filter', action='store_true',
        help='Limit results to users specified by username in stdin.  Users'
             ' should be whitespace delimited.', default=False)
    options, args = parser.parse_args(argv[1:])

    ids = None
    if options.filter:
        ids = sys.stdin.read().split()

    if args:
        if ids is not None:
            ids.extend(args)
        else:
            ids = args

    config = options.config
    if config is None:
        config = get_default_config()
    app = loadapp('config:%s' % config, name='karl')

    root, closer = get_root(app)

    out_csv = csv.writer(sys.stdout)
    out_csv.writerow(['username', 'community', 'last_activity'])
    for row in stats.user_activity_report(root, ids):
        username, community, last_activity = row
        out_csv.writerow([username, community.__name__, last_activity.ctime()])

if __name__ == '__main__':
    main()
