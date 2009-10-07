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
from zope.component import queryAdapter

from webob.exc import HTTPFound
from formencode import Invalid

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_model

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
from karl.utils import find_community
from karl.utils import get_session

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
from karl.content.interfaces import IVirtualCalendar
from karl.content.views.utils import extract_description
from karl.views.interfaces import ILayoutProvider
from karl.content.views.interfaces import IShowSendalert

from karl.content.views.utils import fetch_attachments
from karl.content.views.utils import store_attachments

from karl.content.calendar.presenters.day import DayViewPresenter
from karl.content.calendar.presenters.week import WeekViewPresenter
from karl.content.calendar.presenters.month import MonthViewPresenter
from karl.content.calendar.presenters.list import ListViewPresenter

_NOW = None

def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()

def _date_requested(context, request):
    now = _now()
    session = get_session(context, request)
    if 'year' in request.GET:
        year  = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
        day   = int(request.GET.get('day', now.day))
        value = (year, month, day)
        session['calendar_date_requested'] = value
    elif 'calendar_date_requested' in session:
        value = session['calendar_date_requested']
    else:
        value = (now.year, now.month, now.day)
    return value

def _get_catalog_events(calendar, request, first_moment, last_moment,
                        calendar_path=None):
    searcher =  ICatalogSearch(calendar)

    shared_params = dict(
        allowed={'query': effective_principals(request), 'operator': 'or'},
        start_date=(None, coarse_datetime_repr(last_moment)),
        end_date=(coarse_datetime_repr(first_moment),None),
        interfaces=[ICalendarEvent],
        sort_index='start_date',
        reverse=False,
        )

    def _resolve(docids, resolver):
        return [ resolver(docid) for docid in docids ]

    def _color(obs, color):
        for ob in obs:
            ob._v_color = color
        return obs

    events = []

    if calendar_path:
        total, docids, resolver = searcher(virtual=calendar_path,
                                           **shared_params)
        events.append(_color(_resolve(docids, resolver), 'blue'))

    else:
        calendar_path = model_path(calendar)
        # events that were not assigned to a virtual calendar
        total, docids, resolver = searcher(virtual=calendar_path,
                                           **shared_params)
        events.append(_color(_resolve(docids, resolver), 'blue'))

        # events that were assigned to a virtual calendar
        for virtual in calendar.manifest:
            color = virtual['color']
            total, docids, resolver = searcher(virtual=virtual['path'],
                                               **shared_params)
            events.append(_color(_resolve(docids, resolver), color))

    return events

def _calendar_filter(context, request):
    session = get_session(context, request)

    filt = request.params.get('filter', None)
    if filt is None:
        filt = session.get('calendar_filter', None)
    session['calendar_filter'] = filt
    return filt

def _show_calendar_view(context, request, make_presenter):
    year, month, day = _date_requested(context, request)
    focus_datetime = datetime.datetime(year, month, day)
    now_datetime   = _now()

    filt = _calendar_filter(context, request)
    

    def url_for(*args, **kargs):
        ctx = kargs.pop('context', context)
        return model_url(ctx, request, *args, **kargs)          

    # make the calendar presenter for this view
    calendar = make_presenter(focus_datetime, 
                              now_datetime, 
                              url_for)

    # find events and paint them on the calendar 
    events = _get_catalog_events(context, request,
                                 calendar.first_moment,
                                 calendar.last_moment,
                                 filt)

    flattened_events = []
    for event_stream in events: # XXX each sequence in 'events' is an event stream
        flattened_events.extend(event_stream)

    calendar.paint_events(flattened_events)

    settings_url = model_url(context, request, 'settings.html')

    # render
    api = TemplateAPI(context, request, calendar.title)    
    return render_template_to_response(
        calendar.template_filename,
        api=api,          
        feed_url=calendar.feed_href,                         
        settings_url=settings_url,
        calendar=calendar,
        selected_cal = filt,
    )    

def show_list_view(context, request):
    return _show_calendar_view(context, request, ListViewPresenter)

def show_month_view(context, request):
    return _show_calendar_view(context, request, MonthViewPresenter)

def show_week_view(context, request):
    return _show_calendar_view(context, request, WeekViewPresenter)
    
def show_day_view(context, request):
    return _show_calendar_view(context, request, DayViewPresenter)


def get_calendar_actions(context, request):
    """Return the actions to display when looking at the calendar"""
    actions = []
    # temporarily disable settings action until virtual calendaring is
    # solid
##     if has_permission('moderate', context, request):
##         actions.append(
##             ('Settings', 'settings.html'),
##             )
    if has_permission('create', context, request):
        actions.append(
            ('Add Event', 'add_calendarevent.html'),
            )
    return actions


def _get_virtual_calendars(calendar):
    return [ x for x in calendar.values() if IVirtualCalendar.providedBy(x) ]

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
    if calendar:
        virtual_calendars = [ {'title':x.title, 'path':model_path(x)} for x in
                              _get_virtual_calendars(calendar) ]
        virtual_calendars.sort(key=lambda x: x['title'])
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
        virtual_calendars = [ {'title':x.title, 'path':model_path(x)} for x in
                              _get_virtual_calendars(calendar) ]
        virtual_calendars.sort(key=lambda x: x['title'])
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
    calendar_path = validators.UnicodeString(strip=True, not_empty=False)
    calendar_name = validators.UnicodeString(strip=True, not_empty=True)
    calendar_color = validators.UnicodeString(strip=True, not_empty=True)

def _virtual_calendar_title(ob):
    community = find_community(ob)
    title = community and community.title or ''
    if ICalendar.providedBy(ob):
        title = title + ' (default)'
    else:
        title = title + ' (%s)' % ob.title
    return title

def calendar_settings_view(context, request):
    form = CalendarSettingsForm()
    here_path = model_path(context)
    calendar_names = [ x['name'] for x in context.manifest ]

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.delete' in request.GET:
        calendar_name = request.GET['form.delete']
        if calendar_name in calendar_names:
            idx = calendar_names.index(calendar_name)
            del context.manifest[idx]
            ob = context.get(calendar_name)
            if IVirtualCalendar.providedBy(ob):
                del context[calendar_name]
            context._p_changed = True
        location = model_url(
            context, request,
            'settings.html',
            query={'status_message':'%s calendar removed' % calendar_name})
        return HTTPFound(location=location)

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            calendar_path = converted['calendar_path']
            calendar_name = converted['calendar_name']
            calendar_color = converted['calendar_color']

            if calendar_name in calendar_names:
                idx = calendar_names.index(calendar_name)
                context.manifest[idx]['color'] = calendar_color
                category = context.get(calendar_name)
                if IVirtualCalendar.providedBy(category):
                    category.title = calendar_name

            else:
                if not calendar_path:
                    category = create_content(IVirtualCalendar, calendar_name)
                    context[calendar_name] = category
                    calendar_path = model_path(category)
                context.manifest.append({'path':calendar_path,
                                         'color':calendar_color,
                                         'name':calendar_name})
                
            context._p_changed = True

            location = model_url(
                context, request,
                'settings.html',
                query={'status_message':'Calendar settings changed'})
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        fill_values = dict(
            calendar_path='',
            calendar_name='',
            calendar_color='red'
            )

    # Render the form and shove some default values in
    page_title = 'Calendar Settings'
    api = TemplateAPI(context, request, page_title)

    manifest = []
    used_remote = {}

    for item in context.manifest:
        path = item['path']
        local = path.startswith(here_path)
        d = {}
        if local:
            d['title'] = '*Local*'
        else:
            used_remote[path] = True
            try:
                remote = find_model(context, item['path'])
                d['title'] = _virtual_calendar_title(remote)
            except KeyError:
                continue
        d.update(item)
        manifest.append(d)

    remote_calendars = []

    searcher =  queryAdapter(context, ICatalogSearch)

    if searcher is not None:
        total, docids, resolver = searcher(
            allowed={'query': effective_principals(request), 'operator': 'or'},
            interfaces={'query':[ICalendar, IVirtualCalendar],'operator':'or'},
            reverse=False,
            )

        for docid in docids:
            ob = resolver(docid)
            calendar_path = model_path(ob)
            if not calendar_path.startswith(here_path):
                if not calendar_path in used_remote:
                    title = _virtual_calendar_title(ob)
                    remote_calendars.append({'title':title,
                                             'path':calendar_path})

    remote_calendars.sort(key=lambda x: x['path'])

    return render_form_to_response(
        'templates/calendar_settings.pt',
        form,
        fill_values,
        post_url=request.path_url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        manifest = manifest,
        remote_calendars = remote_calendars,
        colors = ("red", "pink", "purple", "blue", "aqua", "green", "mustard",
                  "orange", "silver", "olive"),
        api=api,
        )
