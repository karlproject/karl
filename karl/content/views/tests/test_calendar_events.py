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

from zope.interface import implements
import unittest
from pyramid import testing
from pyramid_formish import ValidationError
from pyramid.testing import cleanUp
from karl.content.interfaces import ICalendarEvent

from karl.testing import registerLayoutProvider

d1 = 'Thursday, October 7, 2010 04:20 PM'
def dummy(date, flavor):
    return d1


class Test_redirect_to_add_form(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import redirect_to_add_form
        return redirect_to_add_form(context, request)

    def test_it(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                         'http://example.com/add_calendarevent.html')

class AddCalendarEventFormControllerTests(unittest.TestCase):
    test_states = [{'current': True, 'name': 'foo', 'transitions': True},
                   {'name': 'bar', 'transitions': True}]

    def setUp(self):
        cleanUp()
        # Create dummy site skeleton
        from karl.testing import DummyCommunity
        context = DummyCommunity()
        context.member_names = set(["b", "c",])
        context.moderator_names = set(["a",])
        self.site = context.__parent__.__parent__
        self.site.sessions = DummySessions()
        self.context = context
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        self._registerSecurityWorkflow()

        self.profiles = testing.DummyModel()
        self.site["profiles"] = self.profiles
        from karl.testing import DummyProfile
        self.profiles["a"] = DummyProfile()
        self.profiles["b"] = DummyProfile()
        self.profiles["c"] = DummyProfile()
        for profile in self.profiles.values():
            profile["alerts"] = testing.DummyModel()
        testing.registerDummySecurityPolicy('a')
        registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _attachStateInfoToController(self, controller):
        def dummy_state_info(content, request, context=None, from_state=None):
            return self.test_states
        controller.workflow.state_info = dummy_state_info

    def _register(self):
        # layout provider
        from zope.interface import Interface
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

        # tags
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        from pyramid.threadlocal import manager
        from pyramid.registry import Registry
        #manager.stack[0]['registry'] = Registry('testing')
        testing.registerUtility(self.mailer, IMailDelivery)

        # CalendarEventAlert adapter
        from karl.models.interfaces import IProfile
        from karl.content.interfaces import ICalendarEvent
        from karl.content.views.adapters import CalendarEventAlert
        from karl.utilities.interfaces import IAlert
        from pyramid.interfaces import IRequest
        testing.registerAdapter(CalendarEventAlert,
                                (ICalendarEvent, IProfile, IRequest),
                                IAlert)

        # IKarlDates
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)

        # content factories
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICalendarEvent
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(DummyFile, ICommunityFile)

    def _makeOne(self, context, request):
        from karl.content.views.calendar_events import AddCalendarEventFormController
        return AddCalendarEventFormController(context, request)

    def test__get_security_states(self):
        controller = self._makeOne(self.context, self.request)
        self._attachStateInfoToController(controller)
        security_states = controller._get_security_states()
        self.assertEqual(security_states, self.test_states)

    def test_form_defaults(self):
        from karl.content.views import calendar_events
        from datetime import datetime
        original_NOW = calendar_events._NOW
        calendar_events._NOW = datetime(2010, 10, 07, 16, 20)
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['start_date'],
                         datetime(2010, 10, 07, 16, 20))
        self.assertEqual(defaults['end_date'],
                         datetime(2010, 10, 07, 17, 20))
        self.failUnless('sendalert' in defaults and defaults['sendalert'])
        self.failIf('security_state' in defaults)
        calendar_events._NOW = original_NOW

        self._attachStateInfoToController(controller)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['security_state'], 'foo')

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('category' in fields)
        self.failUnless('all_day' in fields)
        self.failUnless('start_date' in fields)
        self.failUnless('end_date' in fields)
        self.failUnless('location' in fields)
        self.failUnless('text' in fields)
        self.failUnless('attendees' in fields)
        self.failUnless('contact_name' in fields)
        self.failUnless('contact_email' in fields)
        self.failUnless('attachments' in fields)
        self.failUnless('sendalert' in fields)
        self.failIf('security_state' in fields)
        self._attachStateInfoToController(controller)
        self.failUnless('security_state' in dict(controller.form_fields()))

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('category' in widgets)
        self.failUnless('all_day' in widgets)
        self.failUnless('start_date' in widgets)
        self.failUnless('end_date' in widgets)
        self.failUnless('location' in widgets)
        self.failUnless('text' in widgets)
        self.failUnless('attendees' in widgets)
        self.failUnless('contact_name' in widgets)
        self.failUnless('contact_email' in widgets)
        self.failUnless('attachments' in widgets)
        self.failIf('sendalert' in widgets)
        self.failIf('security_state' in widgets)
        widgets = controller.form_widgets({'security_state': True,
                                           'sendalert': True})
        self.failUnless('sendalert' in widgets)
        self.failUnless('security_state' in widgets)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Add Calendar Entry')
        self.failUnless('actions' in response)
        self.failUnless('layout' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location,
                         'http://example.com/communities/community/')

    def test_handle_submit_invalid_dates(self):
        controller = self._makeOne(self.context, self.request)
        from datetime import datetime
        from datetime import timedelta
        now = datetime.now()
        converted = {'start_date': now,
                     'end_date': now - timedelta(minutes=60),
                     'all_day': False}
        self.assertRaises(ValidationError, controller.handle_submit,
                          converted)
        converted['end_date'] = now
        self.assertRaises(ValidationError, controller.handle_submit,
                          converted)

    def test_handle_submit_with_times(self):
        context = self.context
        self._register()
        controller = self._makeOne(self.context, self.request)
        from datetime import datetime
        from datetime import timedelta
        start_date = datetime(2010, 10, 04, 16, 20)
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r'C:\My Documents\Ha Ha\test2.txt')
        converted = {'title': u'Event Title',
                     'start_date': start_date,
                     'end_date': start_date + timedelta(minutes=60),
                     'all_day': False,
                     'text': u'event text',
                     'location': u'event location',
                     'attendees': u'one\ntwo\nthree',
                     'contact_name': u'event contact name',
                     'contact_email': u'eventcontact@example.com',
                     'category': u'event/category',
                     'security_state': u'default',
                     'tags': [u'foo', u'bar'],
                     'attachments': [attachment1, attachment2],
                     'sendalert': True,
                     }
        testing.registerDummyRenderer(
            'karl.content.views:templates/email_calendar_event_alert.pt')

        controller.handle_submit(converted)
        self.failUnless('event-title' in context)
        event = context['event-title']
        # check basic attribute values
        self.assertEqual(event.title, u'Event Title')
        self.assertEqual(event.startDate, start_date)
        self.assertEqual(event.endDate, start_date+timedelta(minutes=60))
        self.assertEqual(event.text, u'event text')
        self.assertEqual(event.location, u'event location')
        self.assertEqual(event.attendees, [u'one', u'two', u'three'])
        self.assertEqual(event.contact_name, u'event contact name')
        self.assertEqual(event.contact_email, u'eventcontact@example.com')
        self.assertEqual(event.creator, u'a')
        self.assertEqual(event.calendar_category, u'event/category')
        # attachments were saved?
        attachments_folder = event['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        # alerts went out?
        self.assertEqual(len(self.mailer), 3)
        recips = [msg.mto[0] for msg in self.mailer]
        recips.sort()
        self.assertEqual(['a@x.org', 'b@x.org', 'c@x.org'], recips)
        # tags?
        self.assertEqual(self.site.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])

    def test_handle_submit_all_day(self):
        context = self.context
        self._register()
        controller = self._makeOne(self.context, self.request)
        from datetime import datetime
        from datetime import timedelta
        start_date = datetime(2010, 10, 07, 16, 20)
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r'C:\My Documents\Ha Ha\test2.txt')
        converted = {'title': u'Event Title',
                     'start_date': start_date,
                     'end_date': start_date + timedelta(minutes=60),
                     'all_day': True,
                     'text': u'event text',
                     'location': u'event location',
                     'attendees': u'one\ntwo\nthree',
                     'contact_name': u'event contact name',
                     'contact_email': u'eventcontact@example.com',
                     'category': u'event/category',
                     'security_state': u'default',
                     'tags': [u'foo', u'bar'],
                     'attachments': [attachment1, attachment2],
                     'sendalert': True,
                     }
        testing.registerDummyRenderer(
            'karl.content.views:templates/email_calendar_event_alert.pt')
        controller.handle_submit(converted)
        self.failUnless('event-title' in context)
        event = context['event-title']
        # check basic attribute values
        self.assertEqual(event.title, u'Event Title')
        self.assertEqual(event.startDate, datetime(2010, 10, 7, 0, 0, 0))
        self.assertEqual(event.endDate, datetime(2010, 10, 8, 0, 0, 0))
        self.assertEqual(event.text, u'event text')
        self.assertEqual(event.location, u'event location')
        self.assertEqual(event.attendees, [u'one', u'two', u'three'])
        self.assertEqual(event.contact_name, u'event contact name')
        self.assertEqual(event.contact_email, u'eventcontact@example.com')
        self.assertEqual(event.creator, u'a')
        self.assertEqual(event.calendar_category, u'event/category')
        # attachments were saved?
        attachments_folder = event['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        # alerts went out?
        self.assertEqual(len(self.mailer), 3)
        recips = [msg.mto[0] for msg in self.mailer]
        recips.sort()
        self.assertEqual(['a@x.org', 'b@x.org', 'c@x.org'], recips)
        # tags?
        self.assertEqual(self.site.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


class EditCalendarEventFormControllerTests(unittest.TestCase):
    """Edit and add calendar event form controllers share a lot of
    code, in cases where shared code is tested in the add form
    controller tests above the same code is not tested here."""
    test_states = [{'current': True, 'name': 'foo', 'transitions': True},
                   {'name': 'bar', 'transitions': True}]

    def setUp(self):
        cleanUp()
        # Create dummy site skeleton
        from karl.testing import DummyCommunity
        community = DummyCommunity()
        community.member_names = set(["b", "c",])
        community.moderator_names = set(["a",])
        self.site = community.__parent__.__parent__
        self.site.sessions = DummySessions()
        self.community = community
        tags = DummyTags()
        self.site.tags = tags
        from karl.testing import DummyCatalog
        self.site.catalog = DummyCatalog()
        from datetime import datetime
        from datetime import timedelta
        self.start_date = start_date = datetime.now()
        event = DummyCalendarEvent(
            title='Dummy Calendar Event Title',
            startDate=start_date,
            endDate=start_date + timedelta(hours=1),
            creator = 'a',
            text='event text',
            location='event location',
            attendees=[u'a', u'b', u'c'],
            contact_name='event contact name',
            contact_email='email@eventcontact.com',
            calendar_category='event category',
            )
        community['event'] = event
        self.context = event
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        self._registerSecurityWorkflow()

        self.profiles = testing.DummyModel()
        self.site["profiles"] = self.profiles
        from karl.testing import DummyProfile
        self.profiles["a"] = DummyProfile()
        self.profiles["b"] = DummyProfile()
        self.profiles["c"] = DummyProfile()
        for profile in self.profiles.values():
            profile["alerts"] = testing.DummyModel()
        testing.registerDummySecurityPolicy('a')

    def tearDown(self):
        cleanUp()

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def _attachStateInfoToController(self, controller):
        def dummy_state_info(content, request, context=None, from_state=None):
            return self.test_states
        controller.workflow.state_info = dummy_state_info
        self.context.state = 'foo'

    def _register(self):
        # layout provider
        from zope.interface import Interface
        from karl.views.interfaces import ILayoutProvider
        from karl.testing import DummyLayoutProvider
        ad = testing.registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

        # tags
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

        # mail utility
        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        self.mailer = DummyMailer()
        from pyramid.threadlocal import manager
        from pyramid.registry import Registry
        #manager.stack[0]['registry'] = Registry('testing')
        testing.registerUtility(self.mailer, IMailDelivery)

        # CalendarEventAlert adapter
        from karl.models.interfaces import IProfile
        from karl.content.interfaces import ICalendarEvent
        from karl.content.views.adapters import CalendarEventAlert
        from karl.utilities.interfaces import IAlert
        from pyramid.interfaces import IRequest
        testing.registerAdapter(CalendarEventAlert,
                                (ICalendarEvent, IProfile, IRequest),
                                IAlert)

        # IKarlDates
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(dummy, IKarlDates)

        # content factories
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(DummyFile, ICommunityFile)

    def _makeOne(self, context, request):
        from karl.content.views.calendar_events \
             import EditCalendarEventFormController
        return EditCalendarEventFormController(context, request)

    def test_form_defaults(self):
        from datetime import datetime
        from datetime import timedelta
        context = self.context
        controller = self._makeOne(context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'Dummy Calendar Event Title')
        self.assertEqual(defaults['text'], 'event text')
        self.assertEqual(defaults['start_date'], self.start_date)
        self.assertEqual(defaults['end_date'],
                         self.start_date + timedelta(hours=1))
        self.assertEqual(defaults['location'], 'event location')
        self.assertEqual(defaults['attendees'], u'a\nb\nc')
        self.assertEqual(defaults['contact_name'], 'event contact name')
        self.assertEqual(defaults['contact_email'], 'email@eventcontact.com')
        self.assertEqual(defaults['category'], 'event category')
        self.failIf(defaults['security_state'])
        self.failIf(defaults['all_day'])

        # now with security_state and all_day
        self._attachStateInfoToController(controller)
        all_day_start_date = datetime(2010, 10, 7, 0, 0, 0)
        context.startDate = all_day_start_date
        context.endDate = all_day_start_date + timedelta(days=1)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['security_state'], 'foo')
        self.failUnless(defaults['all_day'])
        self.assertEqual(defaults['end_date'], all_day_start_date)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('tags' in fields)
        self.failUnless('category' in fields)
        self.failUnless('all_day' in fields)
        self.failUnless('start_date' in fields)
        self.failUnless('end_date' in fields)
        self.failUnless('location' in fields)
        self.failUnless('text' in fields)
        self.failUnless('attendees' in fields)
        self.failUnless('contact_name' in fields)
        self.failUnless('contact_email' in fields)
        self.failUnless('attachments' in fields)
        self.failIf('security_state' in fields)
        self._attachStateInfoToController(controller)
        self.failUnless('security_state' in dict(controller.form_fields()))

    def test_form_widgets(self):
        # need to register so tag lookup will work
        from zope.interface import Interface
        from karl.models.interfaces import ITagQuery
        testing.registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('title' in widgets)
        self.failUnless('tags' in widgets)
        self.failUnless('category' in widgets)
        self.failUnless('all_day' in widgets)
        self.failUnless('start_date' in widgets)
        self.failUnless('end_date' in widgets)
        self.failUnless('location' in widgets)
        self.failUnless('text' in widgets)
        self.failUnless('attendees' in widgets)
        self.failUnless('contact_name' in widgets)
        self.failUnless('contact_email' in widgets)
        self.failUnless('attachments' in widgets)
        self.failIf('security_state' in widgets)
        widgets = controller.form_widgets({'security_state': True})
        self.failUnless('security_state' in widgets)

    def test_handle_submit_with_times(self):
        context = self.context
        self._register()
        controller = self._makeOne(self.context, self.request)
        from datetime import datetime
        from datetime import timedelta
        start_date = datetime(2010, 10, 04, 16, 20)
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r'C:\My Documents\Ha Ha\test2.txt')
        converted = {'title': u'Different Event Title',
                     'start_date': start_date,
                     'end_date': start_date + timedelta(minutes=60),
                     'all_day': False,
                     'text': u'new event text',
                     'location': u'new event location',
                     'attendees': u'one\ntwo\nthree\nmore',
                     'contact_name': u'new contact name',
                     'contact_email': u'newcontact@example.com',
                     'category': u'event/newcategory',
                     'security_state': u'new default',
                     'tags': [u'foo', u'bar'],
                     'attachments': [attachment1, attachment2],
                     }
        response = controller.handle_submit(converted)
        event = context
        # check basic attribute values
        self.assertEqual(event.title, u'Different Event Title')
        self.assertEqual(event.startDate, start_date)
        self.assertEqual(event.endDate, start_date+timedelta(minutes=60))
        self.assertEqual(event.text, u'new event text')
        self.assertEqual(event.location, u'new event location')
        self.assertEqual(event.attendees, [u'one', u'two', u'three', u'more'])
        self.assertEqual(event.contact_name, u'new contact name')
        self.assertEqual(event.contact_email, u'newcontact@example.com')
        self.assertEqual(event.modified_by, u'a')
        self.assertEqual(event.calendar_category, u'event/newcategory')
        # attachments were saved?
        attachments_folder = event['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        # tags?
        self.assertEqual(self.site.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])

    def test_handle_submit_all_day(self):
        context = self.context
        self._register()
        controller = self._makeOne(self.context, self.request)
        from datetime import datetime
        from datetime import timedelta
        start_date = datetime(2010, 10, 07, 16, 20)
        from karl.testing import DummyUpload
        attachment1 = DummyUpload(filename='test1.txt')
        attachment2 = DummyUpload(filename=r'C:\My Documents\Ha Ha\test2.txt')
        converted = {'title': u'Different Event Title',
                     'start_date': start_date,
                     'end_date': start_date + timedelta(minutes=60),
                     'all_day': True,
                     'text': u'new event text',
                     'location': u'new event location',
                     'attendees': u'one\ntwo\nthree\nmore',
                     'contact_name': u'new contact name',
                     'contact_email': u'newcontact@example.com',
                     'category': u'event/newcategory',
                     'security_state': u'new default',
                     'tags': [u'foo', u'bar'],
                     'attachments': [attachment1, attachment2],
                     }
        response = controller.handle_submit(converted)
        event = context
        # check basic attribute values
        self.assertEqual(event.title, u'Different Event Title')
        self.assertEqual(event.startDate, datetime(2010, 10, 7, 0, 0, 0))
        self.assertEqual(event.endDate, datetime(2010, 10, 8, 0, 0, 0))
        self.assertEqual(event.text, u'new event text')
        self.assertEqual(event.location, u'new event location')
        self.assertEqual(event.attendees, [u'one', u'two', u'three', u'more'])
        self.assertEqual(event.contact_name, u'new contact name')
        self.assertEqual(event.contact_email, u'newcontact@example.com')
        self.assertEqual(event.modified_by, u'a')
        self.assertEqual(event.calendar_category, u'event/newcategory')
        # attachments were saved?
        attachments_folder = event['attachments']
        self.failUnless('test1.txt' in attachments_folder)
        self.failUnless('test2.txt' in attachments_folder)
        # tags?
        self.assertEqual(self.site.tags._called_with[1]['tags'],
                         [u'foo', u'bar'])


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
        from pyramid.testing import DummyModel
        from pyramid.testing import DummyRequest
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


    def test_unicode_attendee(self):
        from datetime import datetime
        from icalendar import Calendar
        from icalendar import UTC
        from pyramid.testing import DummyModel
        from pyramid.testing import DummyRequest
        community = DummyModel()
        community.__name__ = 'testing'
        community['calendar'] = tool = DummyModel()
        tool['dummy'] = event = DummyModel()
        event.docid = 'DOCID'
        event.title = 'TITLE'
        event.description = 'DESCRIPTION'
        event.location = 'LOCATION'
        event.attendees = [u'R\xe8n & Stimpy']
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
        self.assertEqual(str(evt['attendee']), 'R\xc3\xa8n & Stimpy')

class CalendarCategoriesViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import calendar_setup_categories_view
        return calendar_setup_categories_view(context, request)

    # show

    def test_notsubmitted(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fielderrors_target, None)

    def test_builds_editable_categories_without_the_default_category(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarCategory('foo')
        context['bar'] = DummyCalendarCategory('bar')

        from karl.content.interfaces import ICalendarCategory
        default_name = ICalendarCategory.getTaggedValue('default_name')
        context[default_name] = DummyCalendarCategory(default_name)

        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)

        self.assert_(len(renderer.editable_categories), 2)
        names = [x.__name__ for x in renderer.editable_categories]
        self.assert_(default_name not in names)

    def test_sets_back_to_calendar_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)

        from pyramid.url import resource_url
        self.assertEqual(resource_url(context, request),
                         renderer.back_to_calendar_url)

    # delete

    def test_delete_does_not_allow_deletion_of_default_category(self):
        from pyramid.url import resource_url
        from karl.content.models.calendar import ICalendarCategory

        default_name = ICalendarCategory.getTaggedValue('default_name')

        context = DummyCalendar()
        request = testing.DummyRequest(post={'form.delete': default_name})
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'Cannot delete default category'})
        self.assertEqual(response.location, expected)

    def test_delete_reports_invalid_when_category_name_is_empty(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={'form.delete': ''})
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'Category is invalid'})
        self.assertEqual(response.location, expected)

    def test_delete_reports_invalid_when_category_name_is_invalid(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={'form.delete': 'invalid'})
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'Category is invalid'})
        self.assertEqual(response.location, expected)

    def test_delete_will_delete_a_valid_category_name(self):
        from pyramid.url import resource_url
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface

        event = testing.DummyModel()
        results = 1, [1], lambda *arg: event
        search = DummySearchAdapter(results)
        testing.registerAdapter(search, (Interface), ICatalogSearch)

        context = DummyCalendar()
        context['_default_layer_'].paths = ['/foo']
        context['foo'] = DummyCalendarCategory('foo-title')
        testing.registerModels({'/foo':context['foo']})

        request = testing.DummyRequest(post={'form.delete': 'foo'})
        response = self._callFUT(context, request)

        self.assertEqual(context.get('foo'), None)
        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'foo-title category removed'})
        self.assertEqual(response.location, expected)
        self.failIf('foo' in context)
        self.assertEqual(context['_default_layer_'].paths, [])
        self.assertEqual(context['_default_layer_']._p_changed, True)
        self.assertEqual(event.calendar_category, '/_default_category_')

    # add new category

    def test_submit_fails_if_title_is_already_taken(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarCategory('foo')

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        request = testing.DummyRequest(post={
            'form.submitted': 1,
            'category_title': 'foo'})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, '__add_category__')
        self.assertEqual(str(renderer.fielderrors['category_title']),
                         'Name is already used')

    def test_submit_fails_if_title_is_missing(self):
        context = DummyCalendar()

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        request = testing.DummyRequest(post={
            'form.submitted': 1,
            'category_title': ''})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, '__add_category__')
        self.assertEqual(str(renderer.fielderrors['category_title']),
                         'Please enter a value')

    def test_submit_adds_a_new_category(self):
        from pyramid.url import resource_url
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICalendarCategory
        context = DummyCalendar()
        testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        request = testing.DummyRequest(post={
            'form.submitted': 1,
            'category_title': 'Announcements',
            })
        class category_factory:
            def __init__(self, *arg):
                self.arg = arg
        registerContentFactory(category_factory, ICalendarCategory)
        response = self._callFUT(context, request)
        name, ann = find_nondefault(context)
        self.assertEqual(ann.arg, ('Announcements',))

        expected = resource_url(context, request, 'categories.html',
                             query={'status_message':'Calendar category added'})
        self.assertEqual(response.location, expected)
        self.assertEqual(context['_default_layer_'].paths, ['/'+name])
        self.assertEqual(context['_default_layer_']._p_changed, True)

    # edit an existing category

    def test_edit_does_not_allow_editing_the_default_category(self):
        from pyramid.url import resource_url
        from karl.content.models.calendar import ICalendarCategory

        default_name = ICalendarCategory.getTaggedValue('default_name')

        context = DummyCalendar()
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'category__name__': default_name
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'Cannot edit default category'})
        self.assertEqual(response.location, expected)

    def test_edit_reports_not_found_when_category_name_is_empty(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'category__name__': ''
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'Could not find category to edit'})
        self.assertEqual(response.location, expected)

    def test_edit_reports_not_found_when_category_name_is_invalid(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'category__name__': 'invalid'
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'categories.html',
                   query={'status_message':'Could not find category to edit'})
        self.assertEqual(response.location, expected)

    def test_edit_fails_if_title_is_missing(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarCategory('foo')

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'category__name__': 'foo',
            'category_title': ''
            })

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, 'foo_category')
        self.assertEqual(str(renderer.fielderrors['category_title']),
                         'Please enter a value')

    def test_edit_fails_if_title_is_already_taken(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarCategory('foo')
        context['bar'] = DummyCalendarCategory('bar')

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'category__name__': 'foo',
            'category_title': 'bar'
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, 'foo_category')
        self.assertEqual(str(renderer.fielderrors['category_title']),
                         'Name is already used')



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
        testing.registerDummyRenderer('karl.views:templates/formfields.pt')

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.calendar_events import calendar_setup_layers_view
        return calendar_setup_layers_view(context, request)

    # show

    def test_notsubmitted(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.fielderrors_target, None)

    def test_builds_editable_layers_without_the_default_layer(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarLayer('foo')
        context['bar'] = DummyCalendarLayer('bar')

        from karl.content.interfaces import ICalendarLayer
        default_name = ICalendarLayer.getTaggedValue('default_name')
        context[default_name] = DummyCalendarLayer(default_name)

        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)

        self.assert_(len(renderer.editable_layers), 2)
        names = [x.__name__ for x in renderer.editable_layers]
        self.assert_(default_name not in names)

    def test_sets_back_to_calendar_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        response = self._callFUT(context, request)

        from pyramid.url import resource_url
        self.assertEqual(resource_url(context, request),
                         renderer.back_to_calendar_url)

    # delete

    def test_delete_does_not_allow_deletion_of_default_layer(self):
        from pyramid.url import resource_url
        from karl.content.models.calendar import ICalendarLayer

        default_name = ICalendarLayer.getTaggedValue('default_name')

        context = DummyCalendar()
        request = testing.DummyRequest(post={'form.delete': default_name})
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'Cannot delete default layer'})
        self.assertEqual(response.location, expected)

    def test_delete_reports_invalid_when_layer_name_is_empty(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={'form.delete': ''})
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'Layer is invalid'})
        self.assertEqual(response.location, expected)

    def test_delete_reports_invalid_when_layer_name_is_invalid(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={'form.delete': 'invalid'})
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'Layer is invalid'})
        self.assertEqual(response.location, expected)

    def test_delete_will_delete_a_valid_layer_name(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        context['foo'] = DummyCalendarLayer('foo-title')

        request = testing.DummyRequest(post={'form.delete': 'foo'})
        response = self._callFUT(context, request)

        self.assertEqual(context.get('foo'), None)
        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'foo-title layer removed'})
        self.assertEqual(response.location, expected)

    # add new category

    def test_submit_fails_if_title_is_already_taken_by_a_layer(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarLayer('foo')
        context['bar'] = DummyCalendarLayer('bar')

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        from webob.multidict import MultiDict
        post = MultiDict({
            'form.edit': 1,
            'layer__name__': 'foo',
            'layer_color': 'red',
            'layer_title': 'bar',
            })
        post.add('category_paths', 'a/b')
        post.add('category_paths', 'c/d')
        request = testing.DummyRequest(post=post)

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, 'foo_layer')

        self.assertEqual(str(renderer.fielderrors['layer_title']),
                         'Name is already used')

    def test_submit_fails_if_title_is_missing(self):
        context = DummyCalendar()

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(post=MultiDict({
            'form.submitted': 1,
            'layer_color': 'red',
            'layer_title': ''}))

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, '__add_layer__')
        self.assertEqual(str(renderer.fielderrors['layer_title']),
                         'Please enter a value')

    def test_submit_fails_if_color_is_missing(self):
        context = DummyCalendar()

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(post=MultiDict({
            'form.submitted': 1,
            'layer_color': '',
            'layer_title': 'foo'}))

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, '__add_layer__')
        self.assertEqual(str(renderer.fielderrors['layer_color']),
                         'Please enter a value')

    def test_submit_adds_a_new_layer(self):
        from pyramid.url import resource_url
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICalendarLayer
        context = DummyCalendar()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(post=MultiDict({
            'form.submitted': 1,
            'layer_title': 'Announcements',
            'layer_color': 'blue',
            'category_paths': '/path',
            }))
        class layer_factory:
            def __init__(self, *arg):
                self.arg = arg
        registerContentFactory(layer_factory, ICalendarLayer)
        response = self._callFUT(context, request)
        name, ann = find_nondefault(context)

        self.assertEqual(ann.arg,
                         ('Announcements', 'blue', ['/path']))

        expected = resource_url(context, request, 'layers.html',
                             query={'status_message':'Calendar layer added'})
        self.assertEqual(response.location, expected)

    # edit an existing layer

    def test_edit_does_not_allow_editing_the_default_layer(self):
        from pyramid.url import resource_url
        from karl.content.models.calendar import ICalendarCategory

        default_name = ICalendarLayer.getTaggedValue('default_name')

        context = DummyCalendar()
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'layer__name__': default_name
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'Cannot edit default layer'})
        self.assertEqual(response.location, expected)

    def test_edit_reports_not_found_when_layer_name_is_empty(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'layer__name__': ''
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'Could not find layer to edit'})
        self.assertEqual(response.location, expected)

    def test_edit_reports_not_found_when_layer_name_is_invalid(self):
        from pyramid.url import resource_url
        context = DummyCalendar()
        request = testing.DummyRequest(post={
            'form.edit': 1,
            'layer__name__': 'invalid'
            })
        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        expected = resource_url(context, request, 'layers.html',
                   query={'status_message':'Could not find layer to edit'})
        self.assertEqual(response.location, expected)

    def test_edit_fails_if_title_is_missing(self):
        context = DummyCalendar()
        context['foo'] = DummyCalendarLayer('foo')

        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        from webob.multidict import MultiDict
        request = testing.DummyRequest(post=MultiDict({
            'form.edit': 1,
            'layer__name__': 'foo',
            'layer_title': ''
            }))

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(renderer.fielderrors_target, 'foo_layer')
        self.assertEqual(str(renderer.fielderrors['layer_title']),
                         'Please enter a value')

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
        testing.registerDummyRenderer(
            'karl.views:templates/formfields.pt')
        self._callFUT(context, request)

        from pyramid.url import resource_url
        self.assertEqual(resource_url(context, request),
                         renderer.back_to_calendar_url)

    def test_sets_categories_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        testing.registerDummyRenderer(
            'karl.views:templates/formfields.pt')
        self._callFUT(context, request)

        from pyramid.url import resource_url
        self.assertEqual(resource_url(context, request, 'categories.html'),
                         renderer.categories_url)

    def test_sets_layers_url(self):
        context = DummyCalendar()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/calendar_setup.pt')
        testing.registerDummyRenderer(
            'karl.views:templates/formfields.pt')
        self._callFUT(context, request)

        from pyramid.url import resource_url
        self.assertEqual(resource_url(context, request, 'layers.html'),
                         renderer.layers_url)

class Test__get_catalog_events(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, calendar, request, first_moment, last_moment,
                 layer_name=None, flatten_layers=False):
        from karl.content.views.calendar_events import _get_catalog_events
        return _get_catalog_events(calendar, request, first_moment,
                                   last_moment, layer_name)

    def test_returns_a_single_flat_list_of_events(self):
        import datetime
        from zope.interface import Interface
        calendar = DummyCalendar()
        layer = DummyCalendarLayer('layer')
        layer.paths = ['/foo/bar']
        calendar['layer'] = layer
        request = testing.DummyRequest()
        now = datetime.datetime.now()
        from karl.models.interfaces import ICatalogSearch
        event = testing.DummyModel()
        results = 1, [1], lambda *arg: event
        search = DummySearchAdapter(results)
        testing.registerAdapter(search, (Interface), ICatalogSearch)
        event = DummyCalendarEvent('foo')
        testing.registerModels({'/foo/bar':event})
        result = self._callFUT(calendar, request,
                               first_moment=now,
                               last_moment=now,
                               layer_name=None)
        # We won't have an equality, as this is a clone.
        # So, check its dict instead.
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].startDate, event.startDate)
        self.assertEqual(result[0].endDate, event.endDate)
        # ... and so on.

class ShowCalendarViewTests(unittest.TestCase):
    """Test cases to check interaction of different calendar views
    """

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

        # This is the cookie that stores the sticky state of the view
        from karl.content.views import calendar_events
        self.view_cookie = calendar_events.KARL_CALENDAR_COOKIE
        self.date_cookie = calendar_events.KARL_CALENDAR_DATE_COOKIE

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

        from karl.models.interfaces import ICatalogSearch
        from karl.models.adapters import CatalogSearch
        testing.registerAdapter(CatalogSearch, (Interface, ), ICatalogSearch)

    def _registerSecurityWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def assert_cookie(self, response, cookie_name, cookie_value):
        from webob.cookies import Morsel
        for name, value in response.headerlist:
            if name == 'Set-Cookie' and value.startswith(cookie_name):
                m = Morsel(cookie_name, cookie_value)
                m.path = '/'
                self.assertEqual(value, m.serialize())
                break
        else:
            raise AssertionError('Cookie not set: %s' % cookie_name)

    def test_day(self):
        from karl.content.views import calendar_events
        calendar_events._NOW = datetime.datetime(1969, 9, 23)
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_navigation.pt')
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_day.pt')
        self._registerSecurityWorkflow()

        from karl.content.views.calendar_events import show_day_view
        response = show_day_view(context, request)

        # check if calendar view has been made sticky
        self.assert_cookie(response, self.view_cookie, 'calendar,day,1969,9,23')

    def test_week(self):
        from karl.content.views import calendar_events
        calendar_events._NOW = datetime.datetime(1969, 9, 23)
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_week.pt')
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_navigation.pt')
        self._registerSecurityWorkflow()

        from karl.content.views.calendar_events import show_week_view
        response = show_week_view(context, request)

        # check if calendar view has been made sticky
        self.assert_cookie(response, self.view_cookie, 'calendar,week,1969,9,23')

    def test_month(self):
        from karl.content.views import calendar_events
        calendar_events._NOW = datetime.datetime(1969, 9, 23)
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_month.pt')
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_navigation.pt')
        self._registerSecurityWorkflow()

        from karl.content.views.calendar_events import show_month_view
        response = show_month_view(context, request)

        # check if calendar view has been made sticky
        self.assert_cookie(response, self.view_cookie, 'calendar,month,1969,9,23')

    def test_list(self):
        from karl.content.views import calendar_events
        calendar_events._NOW = datetime.datetime(1969, 9, 23)
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_navigation.pt')
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_list.pt')
        self._registerSecurityWorkflow()

        from karl.content.views.calendar_events import show_list_view
        response = show_list_view(context, request)

        # check if calendar view has been made sticky
        self.assert_cookie(response, self.view_cookie, 'list,day,1969,9,23')

    def test_list_request_date(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest(params={
            'year': '2010', 'month': '5', 'day': '12'})
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_navigation.pt')
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_list.pt')
        self._registerSecurityWorkflow()

        from karl.content.views.calendar_events import show_list_view
        response = show_list_view(context, request)

        # check if calendar view has been made sticky
        self.assert_cookie(response, self.view_cookie, 'list,day,2010,5,12')

    def test_list_cookie_date(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.cookies[self.view_cookie] = 'calendar,,2010,5,12'
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_navigation.pt')
        testing.registerDummyRenderer(
            'karl.content.views:templates/calendar_list.pt')
        self._registerSecurityWorkflow()

        from karl.content.views.calendar_events import show_list_view
        response = show_list_view(context, request)

        # check if calendar view has been made sticky
        self.assert_cookie(response, self.view_cookie, 'list,day,2010,5,12')

    def test_default(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        self._registerSecurityWorkflow()

        # There is no cookie set, which means no view
        # had been made sticky yet
        from karl.content.views.calendar_events import show_view
        response = show_view(context, request)

        # Redirect is expected to the default view, which is 'day'.
        from pyramid.url import resource_url
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, resource_url(context, request, 'day.html'))

    def test_default_day(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        self._registerSecurityWorkflow()

        # Test with 'day' view selected as sticky
        request.cookies[self.view_cookie] = 'day'

        from karl.content.views.calendar_events import show_view
        response = show_view(context, request)

        # Redirect is expected to the sticky view
        from pyramid.url import resource_url
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, resource_url(context, request, 'day.html'))

    def test_default_week(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        self._registerSecurityWorkflow()

        # Test with 'week' view selected as sticky
        request.cookies[self.view_cookie] = 'calendar,week,1969,9,23'

        from karl.content.views.calendar_events import show_view
        response = show_view(context, request)

        # Redirect is expected to the sticky view
        from pyramid.url import resource_url
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, resource_url(context, request, 'week.html'))

    def test_default_month(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        self._registerSecurityWorkflow()

        # Test with 'month' view selected as sticky
        request.cookies[self.view_cookie] = 'calendar,month,2011,9,29'

        from karl.content.views.calendar_events import show_view
        response = show_view(context, request)

        # Redirect is expected to the sticky view
        from pyramid.url import resource_url
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, resource_url(context, request, 'month.html'))

    def test_default_list(self):
        context = DummyCalendar(sessions=DummySessions())
        context['1'] = DummyCalendarCategory('1')
        context.catalog = self.site.catalog
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        from webob.multidict import MultiDict
        request.POST = MultiDict()
        self._register()
        self._registerSecurityWorkflow()

        # Test with 'list' view selected as sticky
        request.cookies[self.view_cookie] = 'list,week,2011,9,29'

        from karl.content.views.calendar_events import show_view
        response = show_view(context, request)

        # Redirect is expected to the sticky view
        from pyramid.url import resource_url
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, resource_url(context, request, 'list.html'))


class DummyContentFactory:
    def __init__(self, klass):
        self._klass = klass
        self.created_instances = []

    def __call__(self, *args, **kargs):
        content_object = self._klass(*args, **kargs)
        self.created_instances.append(content_object)
        return content_object


import datetime
startDate = datetime.datetime(2011, 9, 22, 9, 0)
endDate = datetime.datetime(2011, 9, 23, 10, 0)

class DummyCalendarEvent(testing.DummyModel):
    implements(ICalendarEvent)

    def __init__(self, title='', startDate=startDate, endDate=endDate, creator=0,
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
from karl.content.interfaces import ICalendarCategory
from karl.content.interfaces import ICalendarLayer

class DummyCalendar(testing.DummyModel):
    implements(ICalendar)
    def __init__(self, **kw):
        testing.DummyModel.__init__(self, **kw)
        self['_default_category_'] = DummyCalendarCategory('Default')
        self['_default_layer_'] = DummyCalendarLayer('Default')

class DummyCalendarCategory(testing.DummyModel):
    implements(ICalendarCategory)
    def __init__(self, title, **kw):
        testing.DummyModel.__init__(self, **kw)
        self.title = title

class DummyCalendarLayer(testing.DummyModel):
    implements(ICalendarLayer)
    def __init__(self, title, **kw):
        testing.DummyModel.__init__(self, **kw)
        self.title = title
        self.color = 'red'
        self.paths = []

class DummySearchAdapter:
    def __init__(self, result):
        self.result = result

    def __call__(self, context):
        def search(**kw):
            self.kw = kw
            return self.result

        return search

class DummyCatalogEvent(testing.DummyModel):
    pass

def find_nondefault(context):
    items = context.items()
    for k, v in items:
        if not k.startswith('_default'):
            return k, v

class DummySessions(dict):
    def get(self, name, default=None):
        if name not in self:
            self[name] = {}
        return self[name]

class DummyFile:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.size = 0
