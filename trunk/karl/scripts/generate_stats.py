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
from repoze.bfg.scripting import get_root

from karl.scripting import get_default_config
from karl.utilities import stats

def main(argv=sys.argv):
    parser = optparse.OptionParser(
        description=__doc__,
        usage="%prog [options]",
        )
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('-O', '--output', dest='output', default='.',
        help="Path to the directory where reports should be written.",
        metavar='DIR')
    options, args = parser.parse_args(argv[1:])

    if args:
        parser.error("Too many arguments. " + str(args))

    config = options.config
    if config is None:
        config = get_default_config()
    app = loadapp('config:%s' % config, name='karl')

    root, closer = get_root(app)
    folder = os.path.abspath(options.output)

    # Communities report
    path = os.path.join(folder, 'communities.csv')
    fd = open(path, 'wb')
    out_csv = csv.DictWriter(fd, stats.COMMUNITY_COLUMNS)
    out_csv.writerow(dict([(name,name) for name in stats.COMMUNITY_COLUMNS]))
    for row in stats.collect_community_stats(root):
        out_csv.writerow(_unicode(row))
    fd.close()

    # Profiles report
    path = os.path.join(folder, 'profiles.csv')
    fd = open(path, 'wb')
    out_csv = csv.DictWriter(fd, stats.PROFILE_COLUMNS)
    out_csv.writerow(dict([(name,name) for name in stats.PROFILE_COLUMNS]))
    for row in stats.collect_profile_stats(root):
        out_csv.writerow(_unicode(row))
    fd.close()

def _unicode(row):
    converted = {}
    for k,v in row.items():
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        converted[k] = v
    return converted

if __name__ == '__main__':
    main()
