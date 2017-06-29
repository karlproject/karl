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
Save some metrics report data to zodb for admin views
"""

import transaction

from BTrees.OOBTree import OOBTree
from datetime import datetime
from repoze.folder import Folder
from zope.interface import alsoProvides

from karl.content.calendar.utils import prior_month
from karl.scripting import create_karl_argparser
from osi.interfaces import IMetricsContainerFolder
from osi.interfaces import IMetricsMonthFolder
from osi.interfaces import IMetricsYearFolder
from osi.utilities import metrics
from osi.utilities.metrics import month_string
from osi.utilities.metrics import find_metrics
from karl.utils import find_site

import logging
import sys

log = logging.getLogger(__name__)
logging.basicConfig()

def create_metrics_container(context):
    site = find_site(context)
    metrics_container = Folder()
    alsoProvides(metrics_container, IMetricsContainerFolder)
    site['metrics'] = metrics_container
    return metrics_container

def find_or_create_metrics_container(context):
    return find_metrics(context) or create_metrics_container(context)

def main(argv=sys.argv):
    parser = create_karl_argparser(
        description="Save metrics to the ZODB"
        )
    parser.add_argument('--year', dest='year', action='store',
                        help="4 digit year")
    parser.add_argument('--month', dest='month', action='store',
                        help="Integer month (January is 1)")
    parser.add_argument('--monthly', dest='monthly', action='store',
                        help='Generate metrics for the previous month.'
                        ' Useful for cron.')
    parser.add_argument('--range-year-begin', dest='range_year_begin',
                        action='store',
                        help='Beginning year for metrics generation.')
    parser.add_argument('--range-year-end', dest='range_year_end',
                        action='store',
                        help='End year for metrics generation (inclusive).')
    parser.add_argument('--range-month-begin', dest='range_month_begin',
                        action='store',
                        help='Beginning month for metrics generation.')
    parser.add_argument('--range-month-end', dest='range_month_end',
                        action='store',
                        help='End month for metrics generation (inclusive).')

    args = parser.parse_args(sys.argv[1:])

    env = args.bootstrap(args.config_uri)

    site, registry, closer = env['root'], env['registry'], env['closer']

    if args.monthly is not None:
        # in cron jobs, generate metrics for the previous month
        # this is much easier to specify than on the last possible
        # moment of the current month
        now = datetime.now()
        cur_year, cur_month = now.year, now.month
        prev_year, prev_month = prior_month(cur_year, cur_month)
        generate_metrics(site, prev_year, prev_month)

    elif args.range_year_begin is not None:
        # when mass generating metrics, provide year/month start/end ranges
        year_begin, year_end = (int(args.range_year_begin),
                                int(args.range_year_end))
        assert year_begin > 2000, 'Invalid begin year'
        assert year_end > 2000, 'Invalid end year'
        assert year_end >= year_begin, 'Begin year > End year'

        month_begin, month_end = (int(args.range_month_begin),
                                  int(args.range_month_end))
        assert month_begin >= 1 and month_begin <= 12, 'Bad begin month'
        assert month_end >= 1 and month_end <= 12, 'Bad end month'

        for year in range(year_begin, year_end + 1):
            if year == year_begin:
                monthstart = month_begin
            else:
                monthstart = 1
            if year == year_end:
                monthend = month_end
            else:
                monthend = 12
            for month in range(monthstart, monthend + 1):
                print 'generating metrics for %s/%s' % (year, month)
                generate_metrics(site, year, month)
                transaction.commit()

    elif args.year:
        # generate metrics for a particular year/month
        year, month = int(args.year), int(args.month)
        assert year > 2000, "Invalid year"
        assert month >= 1 and month <= 12, "Invalid month"

        generate_metrics(site, year, month)

    transaction.commit()

def generate_metrics(root, year, month):
    contenttype = metrics.collect_contenttype_metrics(root, year, month)
    profiles = metrics.collect_profile_metrics(root, year, month)
    users = metrics.collect_user_metrics(root, year, month)
    communities = metrics.collect_community_metrics(root, year, month)

    metrics_folder = find_or_create_metrics_container(root)

    year_folder = metrics_folder.get(str(year), None)
    if year_folder is None:
        year_folder = Folder()
        alsoProvides(year_folder, IMetricsYearFolder)
        metrics_folder[str(year)] = year_folder

    month_folder = year_folder.get(month_string(month), None)
    if month_folder is None:
        month_folder = Folder()
        alsoProvides(month_folder, IMetricsMonthFolder)
        year_folder[month_string(month)] = month_folder

    month_folder.contenttypes = OOBTree(contenttype)
    month_folder.profiles = OOBTree(profiles)
    month_folder.users = OOBTree(users)
    month_folder.communities = OOBTree(communities)
