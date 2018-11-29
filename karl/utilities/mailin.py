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
"""Process mail-in content from repoze.postoffice.

'maildir_root' is the path to the folder containing the
IMailStore-enabled maildir. The actual maildir must be named 'Maildir'
within that folder.
"""
from __future__ import with_statement

import logging
import re
import traceback

from pyramid.renderers import render
from pyramid.traversal import find_resource
from repoze.postoffice.message import Message
from repoze.postoffice.queue import find_queue
from repoze.sendmail.interfaces import IMailDelivery
from zope.component import getUtility

from karl.adapters.interfaces import IMailinDispatcher
from karl.adapters.interfaces import IMailinHandler
from karl.utils import find_catalog
from karl.utils import find_communities
from karl.utils import find_peopledirectory
from karl.utils import get_setting
from karl.utils import hex_to_docid

# BLOG_ENTRY_REGX = re.compile(r'objectuid([a-zA-Z0-9]{32})\@')
REPLY_REGX = re.compile(r'(?P<community>\w+)\+(?P<tool>\w+)-(?P<reply>\w+)@')
TOOL_REGX = re.compile(r'(?P<community>\w+)\+(?P<tool>\w+)@')
LOG_FMT = '%s %s %s %s\n'

log = logging.getLogger('karl.mailin')


class MailinRunner2(object):
    def __init__(self, root, poroot, zodb_path, queue_name):
        self.root = root
        self.queue = find_queue(poroot, queue_name, zodb_path)
        dispatcher = IMailinDispatcher(self.root)
        dispatcher.default_tool = 'blog'
        dispatcher.text_scrubber = 'karl.utilities.textscrub:text_scrubber'
        self.dispatcher = dispatcher

    def __call__(self):
        processed = bounced = 0

        if not self.queue:
            return

        queue_length = len(self.queue._messages.keys())

        log.info("Total in queue: %s" % queue_length)

        # Sometimes we have a thousand tracer messages backed up in the
        # queue. We only need to process one
        already_tracer = False

        # Only process 100 of the queue messages at once
        upper_limit = 100
        current_limit = 0

        while self.queue and current_limit<upper_limit:
            current_limit += 1
            message = self.queue.pop_next()
            message_subject = message.get('Subject')

            if message_subject == 'Mailin Trace Message' and already_tracer:
                log.info("Skipping duplicate subject %s" % message_subject)
            else:
                if message_subject == 'Mailin Trace Message':
                    already_tracer = True
                message_id = message.get('Message-Id', 'No message id')
                message_to = message.get('To')
                log.info("Processing message: %s, %s, %s" % (message_id, message_subject,
                                                             message_to))
                if self.handle_message(message):
                    processed += 1
                else:
                    bounced += 1

        log.info('Processed %d messages' % processed)
        log.info('Bounced %d messages' % bounced)

    def handle_message(self, message):
        # return 'True' if processed, 'False' if bounced.
        try:
            message_id = message.get('Message-Id', 'No message id')
            info = self.dispatcher.crackHeaders(message)
            error = message.get('X-Postoffice-Rejected')
            if not error:
                error = info.get('error')
            if error:
                # Special case throttle errors
                if error == 'Throttled':
                    self.bounce_message_throttled(message)
                else:
                    self.bounce_message(message, error)
                log.info('Bounced %s %s %s' % (
                    message_id, error, repr(info)))
                return False
            else:

                # If payload is too big, bounce
                size = len(message.as_string())
                size_limit_mb = 14  # 12 Mb, plus base64 encoding
                size_limit = size_limit_mb * 1000000
                if size > size_limit:
                    self.bounce_message(message, 'Email is larger than %s MB' % size_limit_mb)
                    log.info('Bounced %s too large: %s' % (message_id, size))
                    return False

                text, attachments = self.dispatcher.crackPayload(message)
                success = False
                for target in info['targets']:
                    error = target.get('error')
                    if error:
                        self.bounce_message(message, error)
                        log.info('Bounced %s %s %s' % (
                            message_id, error, repr(info)))
                        continue
                    process_error = self.process_message(message, info, target,
                                                         text, attachments)
                    if process_error:
                        self.bounce_message(message, process_error)
                        log.info('Bounced %s %s %s' % (
                            message_id, error, repr(info)))
                        continue
                    extra = ['%s:%s' % (x, info.get(x))
                             for x in ('community', 'in_reply_to', 'tool',
                                       'author') if info.get(x) is not None]
                    log.info('Processed %s %s', message_id, ','.join(extra))
                    success = True
                return success
        except:
            error_msg = self.quarantine_message(message)
            log.error('Quarantined %s %s', message_id, error_msg)
            return False

    def process_message(self, message, info, target, text, attachments):
        report_name = target.get('report')
        if report_name is not None:
            pd = find_peopledirectory(self.root)
            context = find_resource(pd, report_name.split('+'))
        else:
            community = find_communities(self.root)[target['community']]
            context = community[target['tool']]

            if target['in_reply_to'] is not None:
                docid = int(hex_to_docid(target['in_reply_to']))
                catalog = find_catalog(context)
                path = catalog.document_map.address_for_docid(docid)
                if path is None:
                    # replied-to content doesn't exist anymore.
                    # Do not process.
                    return 'Content no longer exists.'
                item = find_resource(self.root, path)
                context = item

        IMailinHandler(context).handle(message, info, text, attachments)

    def bounce_message(self, message, error):
        mailer = getUtility(IMailDelivery)
        from_email = get_setting(self.root, 'postoffice.bounce_from_email')
        if from_email is None:
            from_email = get_setting(self.root, 'admin_email')
        self.queue.bounce(message, wrap_send(mailer.bounce), from_email, error)

    def bounce_message_throttled(self, message):
        mailer = getUtility(IMailDelivery)
        from_email = get_setting(self.root, 'postoffice.bounce_from_email')
        if from_email is None:
            from_email = get_setting(self.root, 'admin_email')

        bounce_message = Message()
        bounce_message['From'] = from_email
        bounce_message['To'] = message['From']
        bounce_message['Subject'] = 'Your submission to Karl has bounced.'
        bounce_message.set_type('text/html')
        bounce_message.set_payload(render(
            'templates/bounce_email_throttled.pt',
            dict(subject=message.get('Subject'),
                 system_name=get_setting(self.root, 'system_name', 'KARL'),
                 admin_email=get_setting(self.root, 'admin_email'),
                 ),
        ).encode('UTF-8'), 'UTF-8')

        self.queue.bounce(
            message, wrap_send(mailer.bounce), from_email,
            bounce_message=bounce_message
        )

    def quarantine_message(self, message):
        mailer = getUtility(IMailDelivery)
        from_email = get_setting(self.root, 'postoffice.bounce_from_email')
        if from_email is None:
            from_email = get_setting(self.root, 'admin_email')
        error = traceback.format_exc()
        self.queue.quarantine(message, error, wrap_send(mailer.bounce),
                              from_email)
        log.error("Message quarantined by mailin.", exc_info=True)
        return error


def wrap_send(send):
    def wrapper(mfrom, mto, message):
        send(mto, message)

    return wrapper
