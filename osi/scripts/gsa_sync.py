# Copyright (C) 2008-2009 Open Society Institute
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
""" Run GSA sync against a given data source.
"""
import datetime
import logging
import sys

import transaction
from ZODB.POSException import ConflictError

from karl.application import is_normal_mode
from karl.scripting import create_karl_argparser
from karl.scripting import daemonize_function
from karl.scripting import only_one

from osi.sync.gsa_sync import GsaSync
from osi.sync.gsa_sync import get_last_sync


log = logging.getLogger(__name__)


def main(argv=sys.argv):
    default_interval = 120
    parser = create_karl_argparser(
        description='Sync staff profiles and login to OSI GSA.'
        )
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="Run in daemon mode.")
    parser.add_argument('-i', '--interval', type=int, default=default_interval,
                        help="Interval in seconds between executions in "
                        "daemon mode.  Default is %d." % default_interval)
    parser.add_argument('-u', '--user', help='Login username for GSA.')
    parser.add_argument('-p', '--password', help='Password for GSA.')
    parser.add_argument('-x', '--check-last-sync',
                        default=None,
                        help='Check that last sync w/ GSA happened w/in a'
                             'given interval (in minutes).  If not, exit with '
                             'a non-zero status code;  if os, exit normally.')
    parser.add_argument('url', help='URL of GSA datasource.')
    parser.add_argument('-t', '--timeout',
                        default=90,
                        help='Timeout for GSA request (default 15 sec).')

    args = parser.parse_args(sys.argv[1:])

    env = args.bootstrap(args.config_uri)
    
    if not is_normal_mode(env['registry']):
        log.info("Cannot run mailin: Running in maintenance mode.")
        sys.exit(2)

    f = only_one(_sync, env['registry'], 'gsa_sync')
    if args.daemon:
        daemonize_function(f, args.interval)(args, env)
    else:
        f(args, env)

def _sync(args, env):

    site, closer, registry = env['root'], env['closer'], env['registry']

    settings = registry.settings

    if args.check_last_sync is not None:
        minutes = int(args.check_last_sync)
        delta = datetime.timedelta(0, minutes * 60)
        now = datetime.datetime.now()
        when = get_last_sync(site, args.url)
        if when is None:
            log.error('sync never initialized')
            sys.exit(1)
        if (now - when > delta):
            log.error('sync stalled:  last success: %s' % when.isoformat())
            sys.exit(1)
        return

    if settings.get('package') != 'osi':
        args.parser.error("GSA Sync must be used with an OSI instance.")
    timeout = int(args.timeout)
    try:
        gsa_sync = GsaSync(site, args.url, args.user, args.password,
                           timeout=timeout)
    except Exception as e:
        log.info('Could not connect to GSA: %s' % str(e))
    else:
        tries = 0
        success = False
        RETRIES = 3
        while tries < RETRIES:
            transaction.begin()
            try:
                gsa_sync()
                transaction.commit()
            except ConflictError:
                tries += 1
                site._p_jar.sync()
            else:
                success = True
                break
        if not success:
            log.critical('GSA Sync retry failed after %s tries' % RETRIES)
    closer()
