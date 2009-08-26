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
import os
import re
import sys
import time
import traceback
import transaction

from karl.adapters.interfaces import IMailinDispatcher
from karl.adapters.interfaces import IMailinHandler
from karl.utils import find_catalog
from karl.utils import find_communities
from karl.utils import hex_to_docid
from repoze.bfg.traversal import find_model
from repoze.mailin.maildir import MaildirStore
from repoze.mailin.pending import PendingQueue


#BLOG_ENTRY_REGX = re.compile(r'objectuid([a-zA-Z0-9]{32})\@')
REPLY_REGX = re.compile(r'(?P<community>\w+)\+(?P<tool>\w+)-(?P<reply>\w+)@')
TOOL_REGX = re.compile(r'(?P<community>\w+)\+(?P<tool>\w+)@')
LOG_FMT = '%s %s %s %s\n'

class MailinRunner:

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
        pass

    def handleMessage(self, message_id):
        # return 'True' if processed, 'False' if bounced.
        try:
            message = self.mailstore[message_id]
            info = self.dispatcher.crackHeaders(message)
            if info.get('error'):
                self.bounceMessage(message, info)
                self.log('BOUNCED', message_id,
                    '%s %s' % (info['reason'], repr(info)))
                if self.verbosity > 1:
                    print 'Bounced  : %s\n  %s' % (message_id, info['reason'])
                return False
            else:
                text, attachments = self.dispatcher.crackPayload(message)
                self.processMessage(message, info, text, attachments)
                extra = ['%s:%s' % (x, info.get(x))
                            for x in ('community', 'in_reply_to', 'tool', 'author')
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
        if not self.dry_run:
            transaction.commit()
            self.pending.sql.commit()
