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

from email.message import Message
import logging
import traceback
from cStringIO import StringIO

import transaction

from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements

from repoze.bfg.chameleon_zpt import get_template
from repoze.sendmail.interfaces import IMailDelivery

from karl.models.interfaces import IProfile

from karl.utilities.interfaces import IAlerts
from karl.utilities.interfaces import IAlert
from karl.utils import find_community
from karl.utils import find_profiles
from karl.utils import get_setting

log = logging.getLogger(__name__)

class Alerts(object):
    implements(IAlerts)

    def emit(self, context, request):
        # Get community in which event occurred and alert members
        community = find_community(context)
        profiles = find_profiles(context)
        all_names = community.member_names | community.moderator_names
        for profile in [profiles[name] for name in all_names]:
            preference = profile.get_alerts_preference(community.__name__)
            if preference == IProfile.ALERT_IMMEDIATELY:
                self._send_immediately(context, profile, request)
            elif preference == IProfile.ALERT_DIGEST:
                self._queue_digest(context, profile, request)

    def _send_immediately(self, context, profile, request):
        mailer = getUtility(IMailDelivery)
        alert = getMultiAdapter((context, profile, request), IAlert)
        mailer.send(alert.mfrom, alert.mto, alert.message.as_string())

    def _queue_digest(self, context, profile, request):
        alert = getMultiAdapter((context, profile, request), IAlert)
        alert.digest = True
        message = alert.message
        body = message.get_payload()

        profile._pending_alerts.append(
            {"from": message["From"],
             "to": message["To"],
             "subject": message["Subject"],
             "body": body})

    def send_digests(self, context):
        mailer = getUtility(IMailDelivery)

        system_name = get_setting(context, "system_name", "KARL")
        system_email_domain = get_setting(context, "system_email_domain")
        sent_from = "%s@%s" % (system_name, system_email_domain)
        from_addr = "%s <%s>" % (system_name, sent_from)
        subject = "[%s] Your alerts digest" % system_name

        template = get_template("email_digest.pt")
        for profile in find_profiles(context).values():
            if not profile._pending_alerts:
                continue

            # Perform each in its own transaction, so a problem with one
            # user's email doesn't block all others
            transaction.manager.begin()
            try:
                msg = Message()
                msg["From"] = from_addr
                msg["To"] = "%s <%s>" % (profile.title, profile.email)
                msg["Subject"] = subject
                body = template(
                    system_name=system_name,
                    alerts=profile._pending_alerts,
                )

                if isinstance(body, unicode):
                    body = body.encode("UTF-8")

                msg.set_payload(body, "UTF-8")

                msg.set_type("text/html")
                mailer.send(sent_from, profile.email, msg.as_string())
                del profile._pending_alerts[:]
                transaction.manager.commit()

            except Exception, e:
                # Log error and continue
                log.error("Error sending digest to %s <%s>" %
                          (profile.title, profile.email))

                b = StringIO()
                traceback.print_exc(file=b)
                log.error(b.getvalue())
                b.close()

                transaction.manager.abort()
