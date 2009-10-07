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

from cStringIO import StringIO

from zope.component import queryUtility
from zope.interface import implements

from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow

from karl.adapters.interfaces import IMailinHandler
from karl.adapters.url import OfflineRequest
from karl.models.interfaces import IComment
from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from karl.views.utils import make_unique_name
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICommunityFile
from karl.content.models.attachments import AttachmentsFolder
from karl.content.views.utils import extract_description

offline_request = OfflineRequest()

def _addAttachments(att_folder, info, attachments):
    for filename, mimetype, data in attachments:
        stream = StringIO(data)
        name = make_unique_name(att_folder, filename)
        attachment = create_content(ICommunityFile,
                                    title = filename,
                                    stream = stream,
                                    mimetype = mimetype,
                                    filename = filename,
                                    creator = info['author'],
                                    )
        att_folder[name] = attachment

class BlogEntryMailinHandler(object):
    implements(IMailinHandler)

    def __init__(self, context):
        self.context = context

    def handle(self, message, info, text, attachments):
        """ See IMailinHandler.
        """
        target = self.context['comments']
        reply = create_content(
            IComment,
            title=info['subject'],
            creator=info['author'],
            text=text,
            description=extract_description(text),
        )

        reply.title = info['subject']
        reply.creator = info['author']
        reply.text = text

        target[target.next_id] = reply

        workflow = get_workflow(IComment, 'security', target)
        if workflow is not None:
            workflow.initialize(reply)

        if attachments:
            _addAttachments(reply, info, attachments)

        # Mailin always sends alerts
        alerts = queryUtility(IAlerts, default=Alerts())
        alerts.emit(reply, offline_request)

class BlogMailinHandler(object):
    implements(IMailinHandler)

    def __init__(self, context):
        self.context = context

    def handle(self, message, info, text, attachments):
        """ See IMailinHandler.
        """
        entry = create_content(
            IBlogEntry,
            title=info['subject'],
            creator=info['author'],
            text=text,
            description=extract_description(text),
            )

        if attachments:
            if 'attachments' not in entry:
                # XXX Not a likely code path, left here for safety
                entry['attachments'] = att_folder = AttachmentsFolder()
                att_folder.title = 'Attachments'
                att_folder.creator = info['author']
            else:
                att_folder = entry['attachments']
            _addAttachments(att_folder, info, attachments)

        entry_id = make_unique_name(self.context, entry.title)
        self.context[entry_id] = entry

        workflow = get_workflow(IBlogEntry, 'security', self.context)
        if workflow is not None:
            workflow.initialize(entry)

        alerts = queryUtility(IAlerts, default=Alerts())
        alerts.emit(entry, offline_request)

