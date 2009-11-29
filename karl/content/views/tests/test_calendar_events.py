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
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp


class AddCalendarEventViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Create dummy site skeleton
        from karl.testing import DummyCommunity
        self.community = DummyCommunity()
        self.site = self.community.__parent__.__parent__
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import add_calendarevent_view
        return add_calendarevent_view(context, request)

    def test_notsubmitted(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/add_calendarevent.pt')
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        context = DummyCalendar()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({'form.submitted': '1'})
            )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/add_calendarevent.pt')
        self._registerSecurityWorkflow()
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)
        self.assertTrue('startDate' in renderer.fielderrors)

    def test_submitted_invalid_no_startdate(self):
        context = DummyCalendar()
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'startDate': '1/1/2009 16:00',
                })
            )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/add_calendarevent.pt')
        self._registerSecurityWorkflow()
        self._callFUT(context, request)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)
        self.assertFalse('startDate' in renderer.fielderrors)

    def test_submitted_valid(self):
        context = self.community
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'startDate': '1/1/2009 16:00',
                'endDate': '1/1/2009 17:00',
                'title': 'my event',
                'text': 'come to a party',
                'contact_email': 'me@example.com',
                'contact_name': 'Me',
                'location': 'NYC',
                'attendees': '',
                'security_state': 'public',
                'tags': 'thetesttag',
                'calendar_category': '',
                })
            )
        self._register()
        self._registerSecurityWorkflow()

        from karl.content.interfaces import ICalendarEvent
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/communities/community/my-event/')
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/communities/community/my-event-1/')

    def test_submitted_valid_sendalert(self):
        context = self.community
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'startDate': '1/1/2009 16:00',
                'endDate': '1/1/2009 17:00',
                'title': 'my event',
                'text': 'come to a party',
                'contact_email': 'me@example.com',
                'contact_name': 'Me',
                'location': 'NYC',
                'attendees': '',
                'sendalert': 'true',
                'security_state': 'public',
                'calendar_category': '',
                })
            )
        self._register()
        self._registerSecurityWorkflow()

        alerts = []

        class DummyAlerts(object):
            def emit(self, event, request):
                alerts.append((event, request))

        from karl.utilities.interfaces import IAlerts
        testing.registerUtility(DummyAlerts(), IAlerts)

        from karl.content.interfaces import ICalendarEvent
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/communities/community/my-event/')
        self.assertEqual(1, len(alerts))
        self.assertEqual(alerts[0][0].title, 'my event')


class EditCalendarEventViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _register(self):
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import edit_calendarevent_view
        return edit_calendarevent_view(context, request)

    def test_notsubmitted(self):
        context = DummyCalendarEvent()
        DummyCalendar()['anevent'] = context
        context.title = 'atitle'
        context.text = 'sometext'
        request = testing.DummyRequest()
        from webob import MultiDict
        request.POST = MultiDict()
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_calendarevent.pt')
        from karl.content.interfaces import ICalendarEvent
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fieldvalues['title'], 'atitle')
        self.assertEqual(renderer.fieldvalues['text'], 'sometext')

    def test_submitted_invalid(self):
        context = DummyCalendarEvent()
        DummyCalendar()['anevent'] = context
        context.title = 'atitle'
        context.text = 'sometext'
        from webob import MultiDict
        from karl.testing import DummyCatalog
        context.catalog = DummyCatalog()
        request = testing.DummyRequest(
            MultiDict({
                    'form.submitted': '1',
            })
            )
        self._register()
        renderer = testing.registerDummyRenderer(
            'templates/edit_calendarevent.pt')
        from karl.content.interfaces import ICalendarEvent
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        self._register()
        context = DummyCalendarEvent()
        DummyCalendar()['anevent'] = context
        from karl.testing import DummyCatalog
        context.catalog = DummyCatalog()
        from karl.models.interfaces import ISite
        from zope.interface import directlyProvides
        directlyProvides(context, ISite)
        from webob import MultiDict
        request = testing.DummyRequest(
            params=MultiDict({
                'form.submitted': '1',
                'startDate': '1/1/2009 16:00',
                'endDate': '1/1/2009 17:00',
                'title': 'My Event',
                'text': 'Come to a party!',
                'contact_email': 'me@example.com',
                'contact_name': 'Me',
                'location': 'NYC',
                'attendees': '',
                'sendalert': 'true',
                'security_state': 'public',
                'tags': 'thetesttag',
                'calendar_category': 'cal1',
                }))
        from karl.content.interfaces import ICalendarEvent
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)
        from karl.models.interfaces import IObjectModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        testing.registerDummySecurityPolicy('testeditor')
        response = self._callFUT(context, request)
        self.assertTrue(response.location.startswith(
            'http://example.com/anevent/'))
        self.assertEqual(len(L), 2)
        self.assertEqual(context.title, 'My Event')
        self.assertEqual(context.text, 'Come to a party!')
        self.assertEqual(context.modified_by, 'testeditor')
        self.assertEqual(context.calendar_category, 'cal1')


class Test_show_calendarevent_ics_view(unittest.TestCase):

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events \
            import show_calendarevent_ics_view
        return show_calendarevent_ics_view(context, request)

    def test_simple(self):
        from datetime import datetime
        from icalendar import Calendar
        from icalendar import UTC
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        community = DummyModel()
        community.__name__ = 'testing'
        community['calendar'] = tool = DummyModel()
        tool['dummy'] = event = DummyModel()
        event.docid = 'DOCID'
        event.title = 'TITLE'
        event.description = 'DESCRIPTION'
        event.location = 'LOCATION'
        event.attendees = []
        event.contact_name = ''
        event.contact_email = ''
        event['attachments'] = DummyModel()
        start = event.startDate = datetime(2009,3,16,22,0,0,tzinfo=UTC)
        end = event.endDate = datetime(2009,3,16,23,59,59,tzinfo=UTC)
        created = event.created = datetime(2009,3,16,16,45,0,tzinfo=UTC)
        modified = event.modified = datetime(2009,3,16,16,45,0,tzinfo=UTC)

        request = DummyRequest()

        response = self._callFUT(event, request)
        self.assertEqual(response.content_type, 'text/calendar')
        self.assertEqual(response.charset, 'UTF8')

        cal = Calendar.from_string(response.body)
        self.assertEqual(str(cal['prodid']), '-//KARL3//Event//')
        self.assertEqual(str(cal['version']), '2.0')
        self.assertEqual(str(cal['method']), 'PUBLISH')
        self.assertEqual(len(cal.subcomponents), 1)
        evt = cal.subcomponents[0]
        self.assertEqual(str(evt['uid']), 'testing:DOCID')
        self.assertEqual(str(evt['summary']), 'TITLE')
        self.assertEqual(str(evt['description']), 'DESCRIPTION')
        self.assertEqual(str(evt['location']), 'LOCATION')
        self.assertEqual(evt['dtstamp'].dt, modified)
        self.assertEqual(evt['created'].dt, created)
        self.assertEqual(evt['dtstart'].dt, start)
        self.assertEqual(evt['dtend'].dt, end)


class CalendarCategoriesViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import calendar_setup_categories_view
        return calendar_setup_categories_view(context, request)

    def test_notsubmitted(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup_categories.pt')
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fieldvalues['category_title'], '')

    def test_submitted_valid_local(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICalendarCategory
        from karl.content.interfaces import ICalendarLayer
        context = DummyCalendar()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup_categories.pt')
        request = testing.DummyRequest({
            'form.submitted': 1,
            'category_title': 'Announcements',
            'layer_color': 'red',
            })
        class factory:
            def __init__(self, *arg):
                self.arg = arg
        registerContentFactory(factory, ICalendarCategory)
        registerContentFactory(factory, ICalendarLayer)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/categories.html?status_message=Calendar+category+added')
        self.assertEqual(context['Announcements'].arg, ('Announcements',))

    def test_submitted_invalid(self):
        context = DummyCalendar()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup_categories.pt')
        request = testing.DummyRequest({
            'form.submitted': 1,
            })
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_sets_back_to_setup_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup_categories.pt')
        response = self._callFUT(context, request)

        from repoze.bfg.url import model_url 
        self.assertEqual(model_url(context, request, 'setup.html'),
                         renderer.back_to_setup_url)


ICS_TEMPLATE = """
BEGIN:VCALENDAR
PRODID:-//KARL3.0//Event//EN
VERSION:2.0
METHOD:PUBLISH
BEGIN:VEVENT
DTSTAMP:20090316T234105Z
CREATED:20090316T233822Z
UID:ATEvent-66a67e1c698bc669eafa907940be858c
LAST-MODIFIED:20090316T234057Z
SUMMARY:Test Event
DTSTART:20090316T221500Z
DTEND:20090316T231500Z
DESCRIPTION:Now is the time for **all** good men to come to the aid of
  the Party!
LOCATION:Sammy T's
CONTACT:Tres Seaver\, tseaver@agendaless.com
CLASS:PUBLIC
END:VEVENT
END:VCALENDAR
"""


class CalendarLayersViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import calendar_setup_layers_view
        return calendar_setup_layers_view(context, request)

    def test_sets_back_to_setup_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup_layers.pt')
        response = self._callFUT(context, request)

        from repoze.bfg.url import model_url 
        self.assertEqual(model_url(context, request, 'setup.html'),
                         renderer.back_to_setup_url)


class CalendarSetupViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import calendar_setup_view
        return calendar_setup_view(context, request)

    def test_sets_back_to_calendar_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)
        
        from repoze.bfg.url import model_url 
        self.assertEqual(model_url(context, request), 
                         renderer.back_to_calendar_url)

    def test_sets_categories_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)
        
        from repoze.bfg.url import model_url 
        self.assertEqual(model_url(context, request, 'categories.html'), 
                         renderer.categories_url)

    def test_sets_layers_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)
        
        from repoze.bfg.url import model_url 
        self.assertEqual(model_url(context, request, 'layers.html'), 
                         renderer.layers_url)


class DummyCalendarEvent(testing.DummyModel):

    def __init__(self, title='', startDate=None, endDate=None, creator=0,
                 text='', location='', attendees=[], contact_name='',
                 contact_email='', calendar_category=''):
        testing.DummyModel.__init__(self)
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
        self.creator = creator
        self.text = text
        self.location = location
        self.attendees = attendees
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.calendar_category = calendar_category
        self.__parent__ = testing.DummyModel()
        self.__name__ = 'calendarevent'
        self['attachments'] = testing.DummyModel()
        from datetime import datetime
        self.created = datetime.now()

class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyTagQuery(DummyAdapter):
    tagswithcounts = []
    docid = 'ABCDEF01'

class DummyTags:
    def update(self, *args, **kw):
        self._called_with = (args, kw)

from zope.interface import implements
from karl.content.interfaces import ICalendar

class DummyCalendar(testing.DummyModel):
    implements(ICalendar)
    def __init__(self, **kw):
        testing.DummyModel.__init__(self, **kw)
        self.manifest = []
        
