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
"""Send digest alerts to all users with pending digest alerts.
"""
import optparse
import logging
from paste.deploy import loadapp
from repoze.bfg.scripting import get_root

from karl.log import set_subsystem
from karl.scripting import get_default_config
from karl.scripting import run_daemon
from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from zope.component import queryUtility

def main():
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config',
        default=None,
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('-l', '--log-file', dest='log_file',
        default=None,
        help="log file name (default to stderr)")
    parser.add_option('--daemon', '-D', dest='daemon',
                      action='store_true', default=False,
                      help='Run in daemon mode.')
    parser.add_option('--interval', '-i', dest='interval', type='int',
                      default=6*3600,
                      help='Interval, in seconds, between executions when in '
                           'daemon mode.')

    options, args = parser.parse_args()

    if options.log_file:
        logging.basicConfig(filename=options.log_file)
    else:
        logging.basicConfig() # log to stderr

    config = options.config
    if config is None:
        config = get_default_config()
    app = loadapp('config:%s' % config, 'karl')
    alerts = queryUtility(IAlerts, default=Alerts())

    def run():
        set_subsystem('digest')
        root, closer = get_root(app)
        alerts.send_digests(root)
        closer()

    if options.daemon:
        run_daemon('digest', run, options.interval)
    else:
        run()

if __name__ == '__main__':
    main()
