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

import datetime
import unittest
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

_NOW = datetime.datetime.now()

class CalendarTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.calendar import Calendar
        return Calendar

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_ICalendar(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import ICalendar
        verifyClass(ICalendar, self._getTargetClass())

    def test_instance_conforms_to_ICalendar(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import ICalendar
        verifyObject(ICalendar, self._makeOne())

class CalendarEventTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.calendar import CalendarEvent
        return CalendarEvent

    def _makeOne(self, title=u'title',
                 creator=u'admin',
                 text=u'text',
                 location=u'location',
                 attendees=[],
                 contact_name=u'contact_name',
                 contact_email=u'contact_email',
                 ):
        startDate = _NOW
        endDate = _NOW
        return self._getTargetClass()(
            title, startDate, endDate, creator,
            text, location, attendees, contact_name, contact_email)

    def test_class_conforms_to_ICalendarEvent(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import ICalendarEvent
        verifyClass(ICalendarEvent, self._getTargetClass())

    def test_instance_conforms_to_ICalendarEvent(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import ICalendarEvent
        verifyObject(ICalendarEvent, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        self.assertEqual(instance.text, u'text')
        self.assertEqual(instance.location, u'location')
        self.assertEqual(instance.attendees, [])
        self.assertEqual(instance.contact_name, u'contact_name')
        self.assertEqual(instance.contact_email, u'contact_email')
        self.assertEqual(instance.startDate, _NOW)
        self.assertEqual(instance.endDate, _NOW)

    def test_instance_construct_with_none(self):
        instance = self._makeOne(text=None)
        self.assertEqual(instance.text, u'')

class TestCalendarToolFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from karl.content.models.calendar import calendar_tool_factory
        return calendar_tool_factory

    def test_factory(self):
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg, **kw: DummyContent, (None,),
                                IContentFactory)
        context = testing.DummyModel()
        request = testing.DummyRequest
        factory = self._makeOne()
        factory.add(context, request)
        self.failUnless(context['calendar'])
        self.failUnless(factory.is_present(context, request))
        factory.remove(context, request)
        self.failIf(factory.is_present(context, request))

class DummyContent:
    pass
