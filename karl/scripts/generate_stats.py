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
import os
import sys

from karl.utilities import stats
from karl.scripting import create_karl_argparser

import logging

log = logging.getLogger(__name__)


def main(argv=sys.argv):
    parser = create_karl_argparser(
        description=__doc__
        )
    parser.add_argument('-O', '--output', dest='output', default='.',
        help="Path to the directory where reports should be written.",
        metavar='DIR')
    args = parser.parse_args(argv[1:])

    config_uri = args.config_uri
    env = args.bootstrap(config_uri)
    root, closer, registry = env['root'], env['closer'], env['registry']
    folder = registry.settings.get('statistics_folder')
    if folder is None:
        folder = os.path.abspath(args.output)
    if not os.path.exists(folder):
        os.makedirs(folder)
    generate_reports(root, folder)

def generate_reports(root, folder):
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
