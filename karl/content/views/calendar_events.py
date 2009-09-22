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

import calendar
calendar.setfirstweekday(6) # Fscking Europeans!
import datetime

from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility

from webob.exc import HTTPFound
from formencode import Invalid

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow

from repoze.enformed import FormSchema
from repoze.lemonade.content import create_content

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.models.interfaces import ICatalogSearch

from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from karl.utilities.interfaces import IKarlDates

from karl.utils import coarse_datetime_repr
from karl.utils import find_interface

from karl.security.workflow import get_security_states

from karl.views import baseforms
from karl.views.api import TemplateAPI
from karl.views.form import render_form_to_response
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name
from karl.views.baseforms import security_state as security_state_field

from karl.content.interfaces import ICalendar
from karl.content.interfaces import ICalendarEvent
from karl.content.views.utils import extract_description
from karl.views.interfaces import ILayoutProvider
from karl.content.views.interfaces import IShowSendalert

from karl.content.views.utils import fetch_attachments
from karl.content.views.utils import store_attachments

from karl.content.views.utils import add_security_state_field

_NOW = None

def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()

def get_catalog_events(context, request, year, month):
    """ Return a mapping, day_number -> [event_info], for the given month.
    """
    year = int(year)
    month = int(month)
    last_day = calendar.monthrange(year, month)[1]
    first_moment = datetime.datetime(year, month, 1)
    last_moment = datetime.datetime(year, month, last_day, 23, 59, 59)

    searcher =  ICatalogSearch(context)
    total, docids, resolver = searcher(
        path={'query': model_path(context)},
        allowed={'query': effective_principals(request), 'operator': 'or'},
        start_date=(None, coarse_datetime_repr(last_moment)),
        end_date=(coarse_datetime_repr(first_moment),None),
        interfaces=[ICalendarEvent],
        sort_index='start_date',
        reverse=False,
        )

    # compile a list of the days that have events
    event_days = {}

    now = _now()
    if first_moment <= now <= last_moment:
        today_day = now.day
    else:
        today_day = None

    # link to month on listing view; used to build day_href
    mu = model_url(context, request, 'listing.html',
                   query={'year':year, 'month':month})

    for day in range(1, last_day+1):
        info = event_days[day] = {'day': day, 'events': []}
        if day == today_day:
            info['day_class'] = 'today'
        else:
            info['day_class'] = 'this-month'

        info['day_href'] = "%s#day-%d" % (mu, day)

    for event in [resolver(docid) for docid in docids]:

        # we need to deal with events that end next month
        if event.startDate < first_moment:
            event_first = 1
        else:
            event_first = event.startDate.day

        if event.endDate > last_moment:
            event_last = last_day
        else:
            event_last = event.endDate.day

        for day in range(event_first, event_last + 1):
            events = event_days[day]['events']
            events.append({'title': event.title,
                           'href': model_url(event, request),
                          })

    return event_days

def get_calendar_skeleton(context, request, year, month):
    """ Return a sequence of sequence of mappings representing the given month.

    o The outermost sequeces are weeks in the month.

    o The innermost sequences are days in each week.

    o The mappings have the following keys:

      'day'
        the day number

      'day_class'
        CSS class, one of 'other-month' (padding days), 'this-month', 'today'

      'day_href'
        Hyperlink to the day on listing_calendar_view

      'events'
        a sequence if mappings describing events on the day.  Keys are
        'title' and 'href'.
    """
    year = int(year)
    month = int(month)
    # days_by_week is a list of days inside a list of weeks, like so:
    # [[0, 1, 2, 3, 4, 5, 6],
    #  [7, 8, 9, 10, 11, 12, 13],
    #  [14, 15, 16, 17, 18, 19, 20],
    #  [21, 22, 23, 24, 25, 26, 27],
    #  [28, 29, 30, 31, 0, 0, 0]]
    days_by_week = calendar.monthcalendar(year, month)
    weeks = []

    events = get_catalog_events(context, request, year, month)

    for week in days_by_week:
        days = []
        for day in week:
            if events.has_key(day):
                days.append(events[day])
            else:
                days.append({'day': day,
                             'day_class': 'other-month',
                             'events':[],
                            })

        weeks.append(days)

    return weeks

def _prior_month(year, month):
    if month == 1:
        return (year - 1, 12)
    return (year, month - 1)

def _next_month(year, month):
    if month == 12:
        return (year + 1, 1)
    return (year, month + 1)

def get_calendar_actions(context, request):
    """Return the actions to display when looking at the calendar"""
    actions = []
    if has_permission('moderate', context, request):
        actions.append(
            ('Settings', 'settings.html'),
            )
    if has_permission('create', context, request):
        actions.append(
            ('Add Event', 'add_calendarevent.html'),
            )
    return actions

def monthly_calendar_view(context, request):

    now = _now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))

    p_year, p_month = _prior_month(year, month)
    n_year, n_month = _next_month(year, month)

    weeks_days = get_calendar_skeleton(context, request, year, month)

    page_title = '%s %d' % (calendar.month_name[month], year)
    api = TemplateAPI(context, request, page_title)

    actions = get_calendar_actions(context, request)

    url = model_url(context, request)

    previous = {
        'title': '%s %d' % (calendar.month_name[p_month], p_year),
        'href': '%s?year=%d&month=%d' % (url, p_year, p_month),
        }
    next = {
        'title': '%s %d' % (calendar.month_name[n_month], n_year),
        'href': '%s?year=%d&month=%d' % (url, n_year, n_month),
        }

    mu = model_url(context, request, 'listing.html',
                   query={'year':year, 'month':month})

    submenu = [
        {'label': 'Monthly View', 'href': mu, 'make_link': False},
        {'label': 'Listing View', 'href': mu, 'make_link': True},
        ]

    feed_url = model_url(context, request, "atom.xml")
    return render_template_to_response(
        'templates/monthly_calendar.pt',
        api=api,
        actions=actions,
        weeks_days=weeks_days,
        previous_month=previous,
        next_month=next,
        submenu=submenu,
        feed_url=feed_url,
        )


def listing_calendar_view(context, request):

    now = _now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))

    catalog_events = get_catalog_events(context, request, year, month)

    days_with_events = []
    for day in catalog_events.values():
        if day['events'] != []:
            date = datetime.date(year, month, day['day'])
            day['dow'] = date.strftime('%A')
            days_with_events.append(day)

    page_title = '%s %d' % (calendar.month_name[month], year)
    api = TemplateAPI(context, request, page_title)

    actions = get_calendar_actions(context, request)

    mu = model_url(context, request,
                   query={'year':year, 'month':month})

    submenu = [
        {'label': 'Monthly View', 'href': mu, 'make_link': True},
        {'label': 'Listing View', 'href': mu, 'make_link': False},
        ]

    feed_url = model_url(context, request, "atom.xml")
    return render_template_to_response(
        'templates/listing_calendar.pt',
        api=api,
        actions=actions,
        days_with_events=days_with_events,
        submenu=submenu,
        feed_url=feed_url,
        )



def add_calendarevent_view(context, request):

    tags_list=request.POST.getall('tags')
    form = AddCalendarEventForm(tags_list=tags_list)
    workflow = get_workflow(ICalendarEvent, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, None, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            name = make_unique_name(context, converted['title'])

            creator = authenticated_userid(request)
            if converted['contact_email'] is None:
                # Couldn't convince the email validator to call
                # _to_python
                converted['contact_email'] = u''
            calendarevent = create_content(ICalendarEvent,
                                           converted['title'],
                                           converted['startDate'],
                                           converted['endDate'],
                                           creator,
                                           converted['text'],
                                           converted['location'],
                                           converted['attendees'],
                                           converted['contact_name'],
                                           converted['contact_email'],
                                           virtual_calendar=
                                            converted['virtual_calendar'],
                                           )
            calendarevent.description = extract_description(converted['text'])
            calname = make_unique_name(context, calendarevent.title)

            context[calname] = calendarevent

            # Set up workflow
            if workflow is not None:
                workflow.initialize(calendarevent)
                if 'security_state' in converted:
                    workflow.transition_to_state(calendarevent, request,
                                                 converted['security_state'])

            # Save the tags on it.
            set_tags(calendarevent, request, converted['tags'])
            store_attachments(calendarevent['attachments'],
                              request.params, creator)

            if converted['sendalert']:
                alerts = queryUtility(IAlerts, default=Alerts())
                alerts.emit(calendarevent, request)

            location = model_url(calendarevent, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            tags_field = dict(
                records = [dict(tag=t) for t in request.POST.getall('tags')]
                )

    else:
        fielderrors = {}
        now = _now()
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.initial_state
        fill_values = dict(
            startDate = now,
            endDate = now + datetime.timedelta(hours=1),
            tags = u'',
            security_state = security_state,
            )
        fill_values['contact_email'] = u''
        tags_field = dict(records=[])

    # Render the form and shove some default values in
    page_title = 'Add Calendar Event'
    api = TemplateAPI(context, request, page_title)

    # Get a little policy.  Should we suppress alerts?
    show_sendalert = queryMultiAdapter((context, request), IShowSendalert)
    if show_sendalert is not None:
        show_sendalert_field = show_sendalert.show_sendalert
    else:
        show_sendalert_field = True

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('community')

    calendar = find_interface(context, ICalendar)
    if calendar is not None:
        virtual_calendars = calendar.virtual_calendars
    else:
        virtual_calendars = []

    return render_form_to_response(
        'templates/add_calendarevent.pt',
        form,
        fill_values,
        head_data=convert_to_script(dict(
                tags_field = tags_field,
                )),
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        virtual_calendars=virtual_calendars,
        show_sendalert_field=show_sendalert_field,
        layout=layout,
        security_states = security_states,
        )

def show_calendarevent_view(context, request):

    page_title = context.title

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Edit', 'edit.html'),
            )
        actions.append(
            ('Delete', 'delete.html'),
            )
    api = TemplateAPI(context, request, page_title)

    container  = context.__parent__
    backto = {
        'href': model_url(container, request),
        'title': container.title,
        }

    # Flatten the data into ZPT-friendly info
    karldates = getUtility(IKarlDates)
    title = context.title
    startDate = karldates(context.startDate, 'longform')
    endDate = karldates(context.endDate, 'longform')
    attendees = None
    if context.attendees is not []:
        attendees = '; '.join(context.attendees)
    location = context.location
    contact_name = context.contact_name
    contact_email = context.contact_email

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('community')

    return render_template_to_response(
        'templates/show_calendarevent.pt',
        api=api,
        actions=actions,
        head_data=convert_to_script(dict(
            tagbox = get_tags_client_data(context, request),
            )),
        title=title,
        startDate=startDate,
        endDate=endDate,
        attendees=attendees,
        location=location,
        contact_name=contact_name,
        contact_email=contact_email,
        attachments=fetch_attachments(context['attachments'], request),
        backto=backto,
        layout=layout,
        )

def show_calendarevent_ics_view(context, request):
    from icalendar import Calendar
    from icalendar import Event
    from icalendar import vUri
    from webob import Response
    calendar = Calendar()
    calendar.add('prodid', '-//KARL3//Event//')
    calendar.add('version', '2.0')
    calendar.add('method', 'PUBLISH')
    event = Event()
    event['uid'] = '%s:%s' % (context.__parent__.__parent__.__name__,
                              context.docid)
    event.add('summary', context.title)
    if context.description:
        event.add('description', context.description)
    if context.location:
        event.add('location', context.location)
    event.add('dtstamp', context.modified)
    event.add('last-modified', context.modified)
    event.add('created', context.created)
    event.add('dtstart', context.startDate)
    event.add('dtend', context.endDate)

    contacts = []
    if context.contact_name:
        contacts.append(context.contact_name)
    if context.contact_email:
        contacts.append(context.contact_email)
    if contacts:
        event.add('contact', ', '.join(contacts))

    for name in context.attendees:
        event.add('attendee', name)

    for f in context['attachments'].values():
        attachment = vUri(model_url(f, request))
        attachment.params['fmttype'] = f.mimetype
        event.add('attach', attachment)

    calendar.add_component(event)
    return Response(body=calendar.as_string(),
                    content_type='text/calendar',
                    charset='UTF8',
                   )


def edit_calendarevent_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditCalendarEventForm(tags_list=tags_list)
    workflow = get_workflow(ICalendarEvent, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))
            if workflow is not None:
                if 'security_state' in converted:
                    workflow.transition_to_state(context, request,
                                                 converted['security_state'])

            context.title = converted['title']
            context.startDate = converted['startDate']
            context.endDate = converted['endDate']
            context.text = converted['text']
            context.location = converted['location']
            context.attendees = converted['attendees']
            context.contact_name = converted['contact_name']
            context.contact_email = converted['contact_email']
            context.virtual_calendar = converted['virtual_calendar']
            context.description = extract_description(converted['text'])

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            # Save new attachments
            creator = authenticated_userid(request)
            store_attachments(context['attachments'], request.params, creator)

            # Modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = "?status_message=Calendar%20Event%20edited"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(
            title=context.title,
            text=context.text,
            startDate=context.startDate,
            endDate=context.endDate,
            location=context.location,
            attendees=context.attendees,
            contact_name=context.contact_name,
            contact_email=context.contact_email,
            virtual_calendar=context.virtual_calendar,
            security_state = security_state,
            )
        if fill_values['contact_email'] is None:
            fill_values['contact_email'] = u''

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    client_json_data = convert_to_script(dict(
        tags_field = get_tags_client_data(context, request),
        ))

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('community')

    calendar = find_interface(context, ICalendar)
    if calendar is not None:
        virtual_calendars = calendar.virtual_calendars
    else:
        virtual_calendars = []

    return render_form_to_response(
        'templates/edit_calendarevent.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        virtual_calendars=virtual_calendars,
        head_data=client_json_data,
        layout=layout,
        security_states=security_states,
        )

from formencode import validators
class AddCalendarEventForm(FormSchema):
    chained_validators = baseforms.start_end_constraints
    #
    title = baseforms.title
    tags = baseforms.tags
    virtual_calendar = validators.UnicodeString(strip=True)
    startDate = baseforms.start_date
    endDate = baseforms.end_date
    location = validators.UnicodeString(strip=True)
    text = baseforms.text
    attendees = baseforms.TextAreaToList(strip=True)
    contact_name = validators.UnicodeString(strip=True)
    contact_email = validators.Email(not_empty=False, strip=True)
    sendalert = baseforms.sendalert

class EditCalendarEventForm(FormSchema):
    chained_validators = baseforms.start_end_constraints
    #
    title = baseforms.title
    tags = baseforms.tags
    virtual_calendar = validators.UnicodeString(strip=True)
    startDate = baseforms.start_date
    endDate = baseforms.end_date
    location = validators.UnicodeString(strip=True)
    text = baseforms.text
    attendees = baseforms.TextAreaToList(strip=True)
    contact_name = validators.UnicodeString(strip=True)
    contact_email = validators.Email(not_empty=False, strip=True)

class CalendarSettingsForm(FormSchema):
    virtual_calendars = baseforms.TextAreaToList(strip=True)

def calendar_settings_view(context, request):
    form = CalendarSettingsForm()

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            context.virtual_calendars = tuple(
                converted['virtual_calendars'])
            location = model_url(context, request)
            msg = "?status_message=Calendar%20settings%20changed"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        fill_values = dict(
            virtual_calendars=context.virtual_calendars,
            )

    # Render the form and shove some default values in
    page_title = 'Calendar Settings'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/calendar_settings.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        )
