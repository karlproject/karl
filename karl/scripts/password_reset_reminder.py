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

"""Send email reminder about password expiration

  password_reset_reminder --hours <hours_ahead>
"""

import datetime
import sys

from karl.scripting import create_karl_argparser
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.utils import find_profiles
from karl.utils import get_setting
from pyramid.renderers import render
from repoze.postoffice.message import Message
from repoze.sendmail.interfaces import IMailDelivery
from zope.component import getUtility

import transaction

import logging
logging.basicConfig()


def send_reminders(env, start, end):
    print
    print "Sending reminders for passwords expiring between %s and %s" % (
        start.strftime('%Y-%m-%d %H:%M'), end.strftime('%Y-%m-%d %H:%M'))
    print
    root = env['root']
    registry = env['registry']
    request = env['request']

    system_name = get_setting(root, 'system_name', 'KARL')
    admin_email = get_setting(root, 'admin_email')
    site_url = get_setting(root, 'script_app_url')
    reset_url = "%s/reset_request.html" % site_url

    profiles = find_profiles(root)
    for profile in profiles.values():
        auth_method = profile.auth_method.lower()
        if auth_method != 'password':
            continue

        expiration = profile.password_expiration_date
        if expiration > start and expiration < end:
            mail = Message()
            mail["From"] = "%s Administrator <%s>" % (system_name, admin_email)
            mail["To"] = "%s <%s>" % (profile.title, profile.email)
            mail["Subject"] = "%s Password Expiration Reminder" % system_name
            body = render(
                "templates/password_expiration_reminder.pt",
                dict(login=profile.__name__,
                    reset_url=reset_url,
                    expiration_date=start.strftime('%Y-%m-%d'),
                    system_name=system_name),
                    request=request,
            )

            if isinstance(body, unicode):
                body = body.encode("UTF-8")

            mail.set_payload(body, "UTF-8")
            mail.set_type("text/html")

            recipients = [profile.email]
            mailer = getUtility(IMailDelivery)
            mailer.send(recipients, mail)
            print "Sent reminder to user '%s'" % profile.title.encode("UTF-8")

    print

def main():
    parser = create_karl_argparser(description="Send expiring password reminder emails")
    parser.add_argument('-H', '--hours', type=int, dest='hours_ahead', default=24,
        help="Hours ahead to remind user about password expiration")

    args = parser.parse_args(sys.argv[1:])
    env = args.bootstrap(args.config_uri)

    now = datetime.datetime.now()
    start = now + datetime.timedelta(hours=args.hours_ahead)
    end = start + datetime.timedelta(hours=24)

    try:
        send_reminders(env, start, end)
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()

if __name__ == '__main__':
    main()
