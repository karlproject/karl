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
"""Process mail-in content from a repoze.mailin IMailStore / IPendingQueue.

'maildir_root' is the path to the folder containing the
IMailStore-enabled maildir. The actual maildir must be named 'Maildir'
within that folder.
"""
from __future__ import with_statement

import datetime
import logging
import re
import sys
import traceback
import transaction

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.traversal import find_model
from repoze.mailin.maildir import MaildirStore
from repoze.mailin.pending import PendingQueue
from repoze.postoffice.message import Message
from repoze.postoffice.queue import open_queue
from repoze.sendmail.interfaces import IMailDelivery
from zope.component import getUtility

from karl.adapters.interfaces import IMailinDispatcher
from karl.adapters.interfaces import IMailinHandler
from karl.utils import find_catalog
from karl.utils import find_communities
from karl.utils import find_peopledirectory
from karl.utils import get_setting
from karl.utils import hex_to_docid

#BLOG_ENTRY_REGX = re.compile(r'objectuid([a-zA-Z0-9]{32})\@')
REPLY_REGX = re.compile(r'(?P<community>\w+)\+(?P<tool>\w+)-(?P<reply>\w+)@')
TOOL_REGX = re.compile(r'(?P<community>\w+)\+(?P<tool>\w+)@')
LOG_FMT = '%s %s %s %s\n'

log = logging.getLogger('karl.mailin')

class MailinRunner: # pragma NO COVERAGE (deprecated)

    def __init__(self, root, maildir_root, options, testing=False):
        self.root = root
        self.maildir_root = maildir_root
        self.dry_run = options.dry_run  # boolean
        self.verbosity = options.verbosity  # integer
        self.pq_file = options.pq_file
        self.log_file = options.log_file
        self.default_tool = options.default_tool
        self.text_scrubber = options.text_scrubber
        self.testing = testing
        self.printed = []
        self.exited = None

    def exit(self, rc):
        if not self.testing:
            sys.exit(rc)
        self.exited = rc

    def print_(self, message=''):
        if not self.testing:
            print message
        else:
            self.printed.append(message)

    def section(self, message, sep='-', verbosity=0):
        if self.verbosity > verbosity:
            self.print_(sep * 65)
            self.print_(message)
            self.print_(sep * 65)

    def log(self, status, message_id, extra=''):
        now = datetime.datetime.now()
        with open(self.log_file, 'a', -1) as f:
            f.write(LOG_FMT % (now.isoformat(), status, message_id, extra))

    def setup(self):
        self.dispatcher = IMailinDispatcher(self.root)
        self.dispatcher.default_tool = self.default_tool
        self.dispatcher.text_scrubber = self.text_scrubber

        self.mailstore = MaildirStore(self.maildir_root)
        self.pending = PendingQueue(path='', dbfile=self.pq_file,
                                    isolation_level='DEFERRED')

    def processMessage(self, message, info, text, attachments):
        report_name = info.get('report')
        if report_name is not None:
            pd = find_peopledirectory(self.root)
            target = find_model(pd, report_name.split('+'))
        else:
            community = find_communities(self.root)[info['community']]
            target = tool = community[info['tool']]

            # XXX this should be more like:
            if info['in_reply_to'] is not None:
                docid = int(hex_to_docid(info['in_reply_to']))
                catalog = find_catalog(target)
                path = catalog.document_map.address_for_docid(docid)
                item = find_model(self.root, path)
                target = item

        IMailinHandler(target).handle(message, info, text, attachments)

    def bounceMessage(self, message, info):
        return

    def handleMessage(self, message_id):
        # return 'True' if processed, 'False' if bounced.
        try:
            message = self.mailstore[message_id]
            info = self.dispatcher.crackHeaders(message)
            if info.get('error'):
                self.bounceMessage(message, info)
                self.log('BOUNCED', message_id,
                    '%s %s' % (info['error'], repr(info)))
                if self.verbosity > 1:
                    print 'Bounced  : %s\n  %s' % (message_id, info['error'])
                return False
            else:
                text, attachments = self.dispatcher.crackPayload(message)
                self.processMessage(message, info, text, attachments)
                extra = ['%s:%s' % (x, info.get(x))
                            for x in ('community',
                                      'in_reply_to',
                                      'tool',
                                      'author',
                                     )
                                if info.get(x) is not None]
                self.log('PROCESSED', message_id, ','.join(extra))
                if self.verbosity > 1:
                    print 'Processed: %s\n  %s' % (message_id, ','.join(extra))
                return True
        except:
            error_msg = traceback.format_exc()
            self.pending.quarantine(message_id, error_msg)
            self.log('QUARANTINED', message_id, error_msg)
            if self.verbosity > 1:
                print 'Quarantined: ', message_id
                print error_msg
            return False

    def __call__(self):
        processed = bounced = 0
        self.section('Processing mail-in content', '=')
        if self.verbosity > 0:
            print 'Maildir root:   ', self.maildir_root
            print 'Pending queue:  ', self.pq_file
            print '=' * 65
        self.setup()

        while self.pending:
            message_id = list(self.pending.pop())[0]
            if self.verbosity > 0:
                print 'Processing message:', message_id
            if self.handleMessage(message_id):
                processed += 1
            else:
                bounced += 1

        if self.verbosity > 0:
            print '=' * 65
            print 'Processed %d messages' % processed
            print 'Bounced %d messages' % bounced
            print
            sys.stdout.flush()
        if not self.dry_run:
            transaction.commit()
            self.pending.sql.commit()

class MailinRunner2(object):
    """ Compatible with repoze.postoffice.
    """

    def __init__(self, root, zodb_uri, zodb_path, queue_name,
                 factory=open_queue):
        self.root = root
        self.queue, self.closer = factory(zodb_uri, queue_name, zodb_path)
        dispatcher = IMailinDispatcher(self.root)
        dispatcher.default_tool = 'blog'
        dispatcher.text_scrubber = 'karl.utilities.textscrub:text_scrubber'
        self.dispatcher = dispatcher

    def __call__(self):
        processed = bounced = 0
        while self.queue:
            message = self.queue.pop_next()
            message_id = message.get('Message-Id', 'No message id')
            log.info("Processing message: %s", message_id)
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
                text, attachments = self.dispatcher.crackPayload(message)
                self.process_message(message, info, text, attachments)
                extra = ['%s:%s' % (x, info.get(x))
                            for x in ('community', 'in_reply_to', 'tool',
                                      'author') if info.get(x) is not None]
                log.info('Processed %s %s', message_id, ','.join(extra))
                return True
        except:
            error_msg = self.quarantine_message(message)
            log.error('Quarantined %s %s', message_id, error_msg)
            return False

    def process_message(self, message, info, text, attachments):
        report_name = info.get('report')
        if report_name is not None:
            pd = find_peopledirectory(self.root)
            target = find_model(pd, report_name.split('+'))
        else:
            community = find_communities(self.root)[info['community']]
            target = tool = community[info['tool']]

            if info['in_reply_to'] is not None:
                docid = int(hex_to_docid(info['in_reply_to']))
                catalog = find_catalog(target)
                path = catalog.document_map.address_for_docid(docid)
                item = find_model(self.root, path)
                target = item

        IMailinHandler(target).handle(message, info, text, attachments)

    def bounce_message(self, message, error):
        mailer = getUtility(IMailDelivery)
        from_email = get_setting(self.root, 'postoffice.bounce_from_email')
        if from_email is None:
            from_email = get_setting(self.root, 'admin_email')
        self.queue.bounce(message, mailer.send, from_email, error)

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
        bounce_message.set_payload(render_template(
            'templates/bounce_email_throttled.pt',
            subject=message.get('Subject'),
            system_name=get_setting(self.root, 'system_name', 'KARL'),
            admin_email=get_setting(self.root, 'admin_email'),
        ).encode('UTF-8'), 'UTF-8')

        self.queue.bounce(
            message, mailer.send, from_email,
            bounce_message=bounce_message
        )

    def quarantine_message(self, message):
        mailer = getUtility(IMailDelivery)
        from_email = get_setting(self.root, 'postoffice.bounce_from_email')
        if from_email is None:
            from_email = get_setting(self.root, 'admin_email')
        error = traceback.format_exc()
        self.queue.quarantine(message, error, mailer.send, from_email)
        return error

    def close(self):
        self.closer()
