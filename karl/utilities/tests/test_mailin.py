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

import unittest
from pyramid import testing

class MailinRunner2Tests(unittest.TestCase):

    def setUp(self):
        self.config = testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from karl.utilities.mailin import MailinRunner2
        return MailinRunner2

    def _makeOne(self, root=None):
        if root is None:
            root = testing.DummyModel()
        mailin = self._getTargetClass()(
            root, dummy_poroot(self.queue), '/postoffice', 'queue',
        )
        return mailin

    def _set_up_queue(self, messages):
        self.queue = DummyQueue(messages)

        from pyramid.testing import DummyModel
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.adapters.interfaces import IMailinDispatcher
        from karl.adapters.interfaces import IMailinHandler

        self.handlers = []
        def handler_factory(context):
            handler = DummyHandler(context)
            self.handlers.append(handler)
            return handler
        self.config.registry.registerAdapter(
            handler_factory, (DummyModel,), IMailinHandler)
        self.config.registry.registerAdapter(
            DummyDispatcher, (DummyModel,), IMailinDispatcher)

        self.mailer = DummyMailer()
        self.config.registry.registerUtility(self.mailer, IMailDelivery)

    def test_one_message_reply_no_attachments(self):
        from pyramid.testing import DummyModel
        info = {'targets': [{'report': None,
                            'community': 'testing',
                            'tool': 'random',
                            'in_reply_to': '7FFFFFFF', # token for docid 0
                            }],
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        self.config.testing_resources(
            {'/communities/testing/random/entry': entry})

        mailin()

        self.assertEqual(len(self.handlers), 1)
        handler = self.handlers[0]
        self.assertEqual(handler.context, entry)
        self.assertEqual(handler.handle_args,
                         (message, info, text, attachments))
        self.assertEqual(len(self.mailer), 0)

    def test_bounce_reply_to_non_existing(self):
        from pyramid.testing import DummyModel
        info = {'targets': [{'report': None,
                            'community': 'testing',
                            'tool': 'random',
                            'in_reply_to': '7FFFFFFF', # token for docid 0
                            }],
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        mailin()

        self.assertEqual(self.queue.bounced, [
            (message, None, 'Content no longer exists.', None)])
        self.assertEqual(len(self.mailer), 1)

    def test_process_message_reply_w_attachment(self):
        from pyramid.testing import DummyModel
        info = {'targets': [{'report': None,
                             'community': 'testing',
                             'tool': 'random',
                             'in_reply_to': '7FFFFFFF', # token for docid 0
                             }],
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        self.config.testing_resources(
            {'/communities/testing/random/entry': entry})

        mailin()

        self.assertEqual(len(self.handlers), 1)
        handler = self.handlers[0]
        self.assertEqual(handler.context, entry)
        self.assertEqual(handler.handle_args,
                         (message, info, text, attachments))
        self.assertEqual(len(self.mailer), 0)

    def test_process_message_report(self):
        from zope.interface import directlyProvides
        from pyramid.testing import DummyModel
        from karl.models.interfaces import IPeopleDirectory
        INFO = {'targets': [{'report': 'section+testing',
                             'community': None,
                             'tool': None,}],
                'author': 'phreddy',
                'subject': 'Feedback'
               }
        text = 'This entry stinks!'
        attachments = [('foo.txt', 'text/plain', 'My attachment')]
        message = DummyMessage(INFO, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        pd = mailin.root['people'] = DummyModel()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = DummyModel()
        testing = section['testing'] = DummyModel()

        mailin()

        self.assertEqual(len(self.handlers), 1)
        handler = self.handlers[0]
        self.failUnless(handler.context is testing)
        self.assertEqual(handler.handle_args,
                         (message, INFO, text, attachments))
        self.assertEqual(len(self.mailer), 0)

    def test_bounce_message(self):
        info = {'targets': [{'community': 'testing',
                             'tool': 'random',
                             'in_reply_to': '7FFFFFFF', # token for docid 0
                             'author': 'phreddy',
                             }],
                'subject': 'Feedback',
                'error': 'Not witty enough',
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        self._makeOne()()
        self.assertEqual(self.queue.bounced, [
            (message, None, 'Not witty enough', None)])
        self.assertEqual(len(self.mailer), 1)

    def test_bounce_message_for_target(self):
        info = {'targets': [{'community': 'testing',
                             'tool': 'random',
                             'in_reply_to': '7FFFFFFF', # token for docid 0
                             'author': 'phreddy',
                             'error': 'Not witty enough',
                             }],
                'subject': 'Feedback',
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        self._makeOne()()
        self.assertEqual(self.queue.bounced, [
            (message, None, 'Not witty enough', None)])
        self.assertEqual(len(self.mailer), 1)

    def test_bounce_message_throttled(self):
        self.config.testing_add_renderer(
            'karl.utilities:templates/bounce_email_throttled.pt')
        message = DummyMessage(None, 'Message body.', ())
        message['X-Postoffice-Rejected'] = 'Throttled'
        message['From'] = 'Clarence'
        self._set_up_queue([message,])

        mailin = self._makeOne()
        mailin()

        self.assertEqual(len(self.queue.bounced), 1)
        bounced = self.queue.bounced[0]
        self.assertEqual(bounced[0], message)
        self.assertEqual(bounced[1], None)
        self.assertEqual(bounced[2], None)
        self.assertEqual(bounced[3]['To'], 'Clarence')
        self.assertEqual(len(self.mailer), 1)

    def test_quarantine_message(self):
        from pyramid.testing import DummyModel
        info = {'targets': [{'community': 'testing',
                             'tool': 'random',
                             'in_reply_to': '7FFFFFFF', # token for docid 0
                             'author': 'phreddy',
                             }],
                'subject': 'Feedback',
                'exception': 'Not witty enough',
               }
        text = 'This entry stinks!'
        attachments = ()
        message = DummyMessage(info, text, attachments)
        self._set_up_queue([message,])

        mailin = self._makeOne()
        catalog = mailin.root.catalog = DummyCatalog()
        cf = mailin.root['communities'] = DummyModel()
        testing = cf['testing'] = DummyModel()
        tool = testing['random'] = DummyModel()
        entry = tool['entry'] = DummyModel()
        entry['comments'] = DummyModel()
        catalog.document_map._map[0] = '/communities/testing/random/entry'
        self.config.testing_resources(
            {'/communities/testing/random/entry': entry})

        mailin()
        q_message, error = self.queue.quarantined[0]
        self.assertEqual(q_message, message)
        self.failUnless('Not witty enough' in error)
        self.assertEqual(len(self.mailer), 1)

class DummyOptions:
    dry_run = False
    verbosity = 1
    pq_file = None
    log_file = None
    default_tool = None
    text_scrubber = None

class DummyHandler:
    handle_args = None

    def __init__(self, context=None):
        self.context = context

    def handle(self, message, info, text, attachments):
        self.handle_args = (message, info, text, attachments)
        if 'exception' in info:
            raise Exception(info['exception'])

class DummyDocumentMap:
    def __init__(self):
        self._map = {}

    def address_for_docid(self, docid):
        return self._map.get(docid, None)

class DummyCatalog:
    def __init__(self):
        self.document_map = DummyDocumentMap()

class DummyMessage(dict):
    def __init__(self, info=None, text=None, attachments=None):
        self.info = info
        self.text = text
        self.attachments = attachments
        self['Message-Id'] = '123456789'

def dummy_poroot(queue):
    return {'postoffice': {'queue': queue}}

class DummyQueue(list):
    def __init__(self, messages):
        super(DummyQueue, self).__init__(messages)
        self.bounced = []
        self.quarantined = []

    def pop_next(self):
        return self.pop(0)

    def quarantine(self, message, error, send, message_from):
        self.quarantined.append((message, error))
        send(message_from, ['foo@example.com'], "You're in quarantine!")

    def bounce(self, message, send, from_addr, error=None,
               bounce_message=None):
        self.bounced.append((message, from_addr, error, bounce_message))
        send(from_addr, ['foo@example.com'], message)


class DummyDispatcher(object):
    def __init__(self, context):
        self.context = context

    def crackHeaders(self, message):
        return message.info

    def crackPayload(self, message):
        return message.text, message.attachments


class DummyMailer(list):
    def send(self, to_addrs, message):
        self.append((to_addrs, message))

    bounce = send
