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

from persistent import Persistent
from repoze.lemonade.content import create_content

from repoze.folder import Folder
from zope.interface import implements

from karl.content.interfaces import ICalendar
from karl.content.interfaces import IVirtualCalendar
from karl.content.interfaces import ICalendarEvent

from karl.content.models.attachments import AttachmentsFolder

from karl.models.tool import ToolFactory
from karl.models.interfaces import IToolFactory

from karl.utils import PersistentBBB

class Calendar(Folder):
    implements(ICalendar)
    title = u'Calendar'
    manifest = PersistentBBB('manifest', [])

    def __init__(self, *arg, **kw):
        Folder.__init__(self, *arg, **kw)
        self.manifest = []

class VirtualCalendar(Persistent):
    implements(IVirtualCalendar)

    def __init__(self, title):
        self.title = title

class CalendarEvent(Folder):
    implements(ICalendarEvent)
    modified_by = None
    virtual_calendar = u''

    def __init__(self, title, startDate, endDate, creator,
                 text=u'', location=u'', attendees=[],
                 contact_name = u'', contact_email = u'',
                 virtual_calendar=u''):
        Folder.__init__(self)
        self.title = unicode(title)
        self.startDate = startDate
        self.endDate = endDate
        self.location = location
        self.attendees = attendees
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.creator = unicode(creator)
        self.modified_by = self.creator
        if text is None:
            self.text = u''
        else:
            self.text = unicode(text)
        self.virtual_calendar = virtual_calendar
        self['attachments'] = AttachmentsFolder()


class CalendarToolFactory(ToolFactory):
    implements(IToolFactory)
    name = 'calendar'
    interfaces = (ICalendar, ICalendarEvent)
    def add(self, context, request):
        calendar = create_content(ICalendar)
        context['calendar'] = calendar

    def remove(self, context, request):
        del context['calendar']

calendar_tool_factory = CalendarToolFactory()
