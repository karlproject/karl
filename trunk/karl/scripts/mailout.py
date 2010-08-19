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
Send queued outbound email.
"""

import optparse
import logging
from paste.deploy import loadapp
from repoze.bfg.scripting import get_root
from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.queue import QueueProcessor

from karl.log import set_subsystem
from karl.scripting import get_default_config
from karl.scripting import run_daemon
from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from zope.component import queryUtility

def main():
    parser = optparse.OptionParser(
        description=__doc__,
        usage="%prog [options] queue_path",
    )
    parser.add_option('-C', '--config', dest='config',
        default=None,
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('--daemon', '-D', dest='daemon',
                      action='store_true', default=False,
                      help='Run in daemon mode.')
    parser.add_option('--interval', '-i', dest='interval', type='int',
                      default=6*3600,
                      help='Interval, in seconds, between executions when in '
                           'daemon mode.')
    parser.add_option('--server', '-s', dest='hostname', default="localhost",
                      help='SMTP server host name', metavar='HOST')
    parser.add_option('--port', '-P', dest='port', type='int', default=25,
                      help='Port of SMTP server', metavar='PORT')
    parser.add_option('--username', '-u', dest='username', default=None,
                      help='Username, if authentication is required')
    parser.add_option('--password', '-p', dest='password', default=None,
                      help='Password, if authentication is required')
    parser.add_option('--force-tls', '-f', dest='force_tls',
                      action='store_true', default=False,
                      help='Require that TLS be used.')
    parser.add_option('--no-tls', '-n', dest='no_tls',
                      action='store_true', default=False,
                      help='Require that TLS not be used.')

    options, args = parser.parse_args()

    if not args:
        parser.error('Please specify queue path.')
    elif len(args) > 1:
        parser.error('Too many arguments.')
    queue_path = args[0]

    config = options.config
    if config is None:
        config = get_default_config()
    app = loadapp('config:%s' % config, 'karl')
    set_subsystem('mailout')

    mailer = SMTPMailer(
        hostname=options.hostname,
        port=options.port,
        username=options.username,
        password=options.password,
        no_tls=options.no_tls,
        force_tls=options.force_tls
    )
    qp = QueueProcessor(mailer, queue_path)

    if options.daemon:
        run_daemon('digest', qp.send_messages, options.interval)
    else:
        qp.send_messages()
