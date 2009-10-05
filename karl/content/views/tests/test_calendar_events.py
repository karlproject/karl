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
                'virtual_calendar': '',
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
                'virtual_calendar': '',
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
                'virtual_calendar': 'cal1',
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
        self.assertEqual(context.virtual_calendar, 'cal1')


class Test_get_catalog_events(unittest.TestCase):

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()
        self._setNow(None)

    def _setNow(self, value):
        from karl.content.views import calendar_events
        calendar_events._NOW = value

    def _callFUT(self, context, request, year, month):
        from karl.content.views.calendar_events import get_catalog_events
        return get_catalog_events(context, request, year, month)

    def test_w_current_month(self):
        from datetime import datetime
        from zope.interface import Interface
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from karl.content.interfaces import ICalendarEvent
        from karl.models.interfaces import ICatalogSearch
        from karl.utils import coarse_datetime_repr

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        request = DummyRequest()

        searchkw = {}
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                searchkw.update(kw)
                return 0, [], lambda x: 1/0
            return search

        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)

        event_days = self._callFUT(context, request, 2009, 3)

        for day in range(1, 32):
            info = event_days[day]

            self.assertEqual(info['day'], day)

            if day == 11:
                self.assertEqual(info['day_class'], 'today')
            else:
                self.assertEqual(info['day_class'], 'this-month')

            self.assertEqual(len(info['events']), 0)

        self.assertEqual(searchkw['path']['query'], '/')
        self.assertEqual(searchkw['start_date'],
                         (None, coarse_datetime_repr(
                            datetime(2009, 3, 31, 23, 59, 59))))
        self.assertEqual(searchkw['end_date'],
                         (
            coarse_datetime_repr(datetime(2009, 3, 1, 0, 0, 0)), None))
        self.assertEqual(list(searchkw['interfaces']), [ICalendarEvent])
        self.assertEqual(searchkw['sort_index'], 'start_date')
        self.failIf(searchkw['reverse'])

    def test_w_other_month_no_events(self):
        from datetime import datetime
        from zope.interface import Interface
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.url import model_url
        from karl.models.interfaces import ICatalogSearch

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        request = DummyRequest()

        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return 0, [], lambda x: 1/0
            return search

        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)

        event_days = self._callFUT(context, request, 2009, 4)

        for day in range(1, 31):
            info = event_days[day]

            self.assertEqual(info['day'], day)
            self.assertEqual(info['day_class'], 'this-month')
            self.assertEqual(len(info['events']), 0)

            mu = model_url(context, request, 'listing.html',
                            query={'year':2009, 'month':4})
            expected_href = "%s#day-%d" % (mu, day)
            self.assertEqual(info['day_href'], expected_href)

    def test_w_event_no_overlap(self):
        from datetime import datetime
        from zope.interface import Interface
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ICatalogSearch

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        request = DummyRequest()

        event = DummyModel(title='Dummy Event',
                           startDate=datetime(2009, 3, 10, 13, 30, 0),
                           endDate=datetime(2009, 3, 10, 14, 30, 0),
                          )
        event.__name__ = 'test_event'
        event.__parent__ = context
        batch = [event]
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return len(batch), batch, resolver
            return search

        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)

        event_days = self._callFUT(context, request, 2009, 3)

        for day in range(1, 32):
            info = event_days[day]

            if day == 10:
                self.assertEqual(len(info['events']), 1)
                event = info['events'][0]
                self.assertEqual(event['title'], 'Dummy Event')
                self.assertEqual(event['href'],
                                 'http://example.com/test_event/')
            else:
                self.assertEqual(len(info['events']), 0)


    def test_w_event_w_overlap_start(self):
        from datetime import datetime
        from zope.interface import Interface
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ICatalogSearch

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        request = DummyRequest()

        entry = DummyModel(title='Dummy Event',
                           startDate=datetime(2009, 2, 25, 9, 30, 0),
                           endDate=datetime(2009, 3, 3, 17, 30, 0),
                          )
        entry.__name__ = 'test_event'
        entry.__parent__ = context
        batch = [entry]
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return len(batch), batch, resolver
            return search

        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)

        event_days = self._callFUT(context, request, 2009, 3)

        for day in range(1, 32):
            info = event_days[day]

            if day <= 3:
                self.assertEqual(len(info['events']), 1)
                event = info['events'][0]
                self.assertEqual(event['title'], 'Dummy Event')
                self.assertEqual(event['href'],
                                 'http://example.com/test_event/')
            else:
                self.assertEqual(len(info['events']), 0)


    def test_w_event_w_overlap_end(self):
        from datetime import datetime
        from zope.interface import Interface
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ICatalogSearch

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        request = DummyRequest()

        entry = DummyModel(title='Dummy Event',
                           startDate=datetime(2009, 3, 25, 9, 30, 0),
                           endDate=datetime(2009, 4, 3, 17, 30, 0),
                          )
        entry.__name__ = 'test_event'
        entry.__parent__ = context
        batch = [entry]
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return len(batch), batch, resolver
            return search

        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)

        event_days = self._callFUT(context, request, 2009, 3)

        for day in range(1, 32):
            info = event_days[day]

            if day >= 25:
                self.assertEqual(len(info['events']), 1)
                event = info['events'][0]
                self.assertEqual(event['title'], 'Dummy Event')
                self.assertEqual(event['href'],
                                 'http://example.com/test_event/')
            else:
                self.assertEqual(len(info['events']), 0)


class Test_get_calendar_skeleton(unittest.TestCase):

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()
        self._setNow(None)

    def _setNow(self, value):
        from karl.content.views import calendar_events
        calendar_events._NOW = value

    def _callFUT(self, context, request, year, month):
        from karl.content.views.calendar_events import get_calendar_skeleton
        return get_calendar_skeleton(context, request, year, month)

    def test_five_by_seven(self):
        from datetime import datetime
        from zope.interface import Interface
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from karl.models.interfaces import ICatalogSearch

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        request = DummyRequest()

        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return 0, [], lambda x: 1/0
            return search

        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)

        result = self._callFUT(context, request, 2009, 3)

        self.assertEqual(len(result), 5)
        for rownum, row in enumerate(result):
            self.assertEqual(len(row), 7)
            for daynum, day in enumerate(row):
                if rownum < 4 or daynum < 3:
                    # March 1 2009 falls on Sunday, which makes this easy
                    self.assertEqual(day['day'], (rownum * 7) + daynum + 1)
                else:
                    self.assertEqual(day['day'], 0)
                    self.assertEqual(day['day_class'], 'other-month')
                    self.assertEqual(len(day['events']), 0)

class Test_monthly_calendar_view(unittest.TestCase):

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()
        self._setNow(None)

    def _setNow(self, value):
        from karl.content.views import calendar_events
        calendar_events._NOW = value

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import monthly_calendar_view
        return monthly_calendar_view(context, request)

    def test_render(self):
        from datetime import datetime
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.testing import registerDummyRenderer
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ISite

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        context = DummyModel()
        directlyProvides(context, ISite)
        request = DummyRequest()

        event = DummyModel(title='Dummy Event',
                           startDate=datetime(2009, 3, 10, 13, 30, 0),
                           endDate=datetime(2009, 3, 10, 14, 30, 0),
                          )
        event.__name__ = 'test_event'
        event.__parent__ = context
        batch = [event]
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return len(batch), batch, resolver
            return search
        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)
        renderer = registerDummyRenderer('templates/monthly_calendar.pt')

        self._callFUT(context, request)

        self.assertEqual(len(renderer.weeks_days), 5)
        self.assertEqual(len(renderer.weeks_days[0]), 7)
        self.assertEqual(renderer.api.page_title, 'March 2009')
        self.assertEqual(renderer.previous_month['title'], 'February 2009')
        self.assertEqual(renderer.previous_month['href'],
                         'http://example.com/?year=2009&month=2')
        self.assertEqual(renderer.next_month['title'], 'April 2009')
        self.assertEqual(renderer.next_month['href'],
                         'http://example.com/?year=2009&month=4')


class Test_listing_calendar_view(unittest.TestCase):

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        cleanUp()
        self._setNow(None)

    def _setNow(self, value):
        from karl.content.views import calendar_events
        calendar_events._NOW = value

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import listing_calendar_view
        return listing_calendar_view(context, request)

    def test_sets_year_and_month_from_request(self):
        from datetime import datetime
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.testing import registerDummyRenderer
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ISite

        batch = []
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return len(batch), batch, resolver
            return search
        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)
        renderer = registerDummyRenderer('templates/listing_calendar.pt')

        context = DummyModel()
        directlyProvides(context, ISite)
        request = DummyRequest(GET={'year':1994, 'month':1})

        testing_now = datetime(2009, 3, 11, 15, 47, 22)
        self._setNow(testing_now)

        self._callFUT(context, request)
        self.assertEqual(renderer.api.page_title, 'January 1994')

    def test_render(self):
        from datetime import datetime
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerAdapter
        from repoze.bfg.testing import registerDummyRenderer
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ISite

        event = DummyModel(title='Dummy Event',
                           startDate=datetime(2009, 4, 3, 13, 30, 0),
                           endDate=datetime(2009, 4, 3, 14, 30, 0),
                          )
        batch = [event]
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                return len(batch), batch, resolver
            return search
        registerAdapter(dummy_catalog_search, (Interface), ICatalogSearch)
        renderer = registerDummyRenderer('templates/listing_calendar.pt')

        context = DummyModel()
        directlyProvides(context, ISite)
        request = DummyRequest()

        testing_now = datetime(2009, 4, 11, 15, 47, 22)
        self._setNow(testing_now)

        self._callFUT(context, request)
        self.assertEqual(renderer.api.page_title, 'April 2009')
        self.assertEqual(len(renderer.days_with_events), 1)
        first = renderer.days_with_events[0]
        self.assertEqual(first['dow'], 'Friday')
        self.assertEqual(first['day'], 3)
        self.assertEqual(len(first['events']), 1)


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


class CalendarSettingsViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import calendar_settings_view
        return calendar_settings_view(context, request)

    def test_notsubmitted(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_settings.pt')
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fieldvalues['calendar_name'], '')
        self.assertEqual(renderer.fieldvalues['calendar_path'], '')
        self.assertEqual(renderer.fieldvalues['calendar_color'], 'red')

    def test_submitted_valid_local(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IVirtualCalendar
        context = DummyCalendar()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_settings.pt')
        request = testing.DummyRequest({
            'form.submitted': 1,
            'calendar_name': 'Announcements',
            'calendar_color': 'red',
            'calendar_path': '',
            })
        class factory:
            def __init__(self, title):
                self.title = title
        registerContentFactory(factory, IVirtualCalendar)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/settings.html?status_message=Calendar+settings+changed')
        self.assertEqual(context['Announcements'].title, 'Announcements')
        self.assertEqual(context.manifest,
                         [{'color': u'red', 'path': '/Announcements',
                           'name': u'Announcements'}])

    def test_submitted_valid_remote(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IVirtualCalendar
        context = DummyCalendar()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_settings.pt')
        request = testing.DummyRequest({
            'form.submitted': 1,
            'calendar_name': 'Announcements',
            'calendar_color': 'red',
            'calendar_path': '/foo',
            })
        class factory:
            def __init__(self, title):
                self.title = title
        registerContentFactory(factory, IVirtualCalendar)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/settings.html?status_message=Calendar+settings+changed')
        self.assertEqual(context.manifest,
                         [{'color': u'red', 'path': u'/foo',
                           'name': u'Announcements'}] )
                            

    def test_submitted_invalid(self):
        context = DummyCalendar()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_settings.pt')
        request = testing.DummyRequest({
            'form.submitted': 1,
            })
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)


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


class DummyCalendarEvent(testing.DummyModel):

    def __init__(self, title='', startDate=None, endDate=None, creator=0,
                 text='', location='', attendees=[], contact_name='',
                 contact_email='', virtual_calendar=''):
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
        self.virtual_calendar = virtual_calendar
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
        
