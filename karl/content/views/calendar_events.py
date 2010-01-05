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
calendar.setfirstweekday(calendar.SUNDAY)
import datetime
import time

from urllib import quote

from zope.component.event import objectEventNotify
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component import queryAdapter

from webob.exc import HTTPFound
from formencode import Invalid
from formencode import validators

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
from karl.content.interfaces import ICalendarLayer
from karl.content.interfaces import ICalendarCategory
from karl.content.views.utils import extract_description
from karl.utils import get_layout_provider
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

def _default_dates_requested(context, request):
    try:
        starts = request.GET.get('starts', time.mktime(_now().timetuple()))
        ends   = request.GET.get('ends',   int(starts) + 3600)

        startDate = datetime.datetime.fromtimestamp(int(starts))
        endDate   = datetime.datetime.fromtimestamp(int(ends))
    except ValueError:
        startDate = _now()
        endDate   = startDate + datetime.timedelta(hours=1)
    return startDate, endDate

def _get_catalog_events(calendar, request, 
                        first_moment, last_moment, layer_name=None):

    searcher = ICatalogSearch(calendar)
    search_params = dict(
        allowed={'query': effective_principals(request), 'operator': 'or'},
        interfaces=[ICalendarEvent],
        sort_index='start_date',
        reverse=False,
        )

    if first_moment:
        end_date = (coarse_datetime_repr(first_moment), None)
        search_params['end_date'] = end_date

    if last_moment:
        start_date = (None, coarse_datetime_repr(last_moment))
        search_params['start_date'] = start_date

    docids_seen = set()

    for layer in _get_calendar_layers(calendar):
        if layer_name and layer.__name__ != layer_name:
            continue

        for category_path in layer.paths:
            total, docids, resolver = searcher(virtual=category_path, 
                                                **search_params) 
            events_in_category = []

            for docid in docids:
                if docid not in docids_seen:
                    docids_seen.add(docid)

                    event = resolver(docid)
                    event._v_layer_color = layer.color
                    event._v_layer_title = layer.title
                
                    events_in_category.append(event) 
        
            for event in events_in_category:
                yield event    

def _paginate_catalog_events(calendar, request, 
                             first_moment, last_moment, layer_name=None,
                             per_page=20, page=1):
    
    all_events = _get_catalog_events(calendar, request, 
                                     first_moment, last_moment, layer_name)

    offset = (page - 1) * per_page   
    limit  = per_page + 1
    
    events = []
    i = 0
    for event in all_events:
        if i >= offset:
            events.append(event)
        if len(events) == limit:
            break
        i += 1

    has_more = len(events) > per_page
    events   = events[:per_page]
    
    return events, has_more

def _calendar_filter(context, request):
    session = get_session(context, request)

    filt = request.params.get('filter', None)
    if filt is None:
        filt = session.get('calendar_filter', None)
    session['calendar_filter'] = filt
    return filt

def _calendar_setup_url(context, request):
    if has_permission('moderate', context, request):
        setup_url = model_url(context, request, 'setup.html')
    else:
        setup_url = None
    return setup_url

def _make_calendar_presenter_url_func(context, request):
    def url_for(*args, **kargs):
        ctx = kargs.pop('context', context)
        return model_url(ctx, request, *args, **kargs)
    return url_for

def _show_calendar_view(context, request, make_presenter):
    year, month, day = _date_requested(context, request)
    focus_datetime = datetime.datetime(year, month, day)
    now_datetime   = _now()

    # make the calendar presenter for this view
    url_for = _make_calendar_presenter_url_func(context, request)
    calendar = make_presenter(focus_datetime,
                              now_datetime,
                              url_for)

    # find events and paint them on the calendar
    selected_layer = _calendar_filter(context, request)

    events = _get_catalog_events(context, request,
                                 first_moment=calendar.first_moment,
                                 last_moment=calendar.last_moment,
                                 layer_name=selected_layer)
    calendar.paint_events(events)

    layers    = _get_calendar_layers(context)
    setup_url = _calendar_setup_url(context, request)

    # render
    api = TemplateAPI(context, request, calendar.title)
    return render_template_to_response(
        calendar.template_filename,
        api=api,
        setup_url=setup_url,
        calendar=calendar,
        selected_layer = selected_layer,
        layers = layers,
        quote = quote,
    )

def show_month_view(context, request):
    return _show_calendar_view(context, request, MonthViewPresenter)

def show_week_view(context, request):
    return _show_calendar_view(context, request, WeekViewPresenter)

def show_day_view(context, request):
    return _show_calendar_view(context, request, DayViewPresenter)

def show_list_view(context, request):
    year, month, day = _date_requested(context, request)
    focus_datetime = datetime.datetime(year, month, day)
    now_datetime   = _now()

    page     = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))

    # make the calendar presenter for this view
    url_for = _make_calendar_presenter_url_func(context, request)
    calendar = ListViewPresenter(focus_datetime,
                                 now_datetime,
                                 url_for)

    # find events and paint them on the calendar
    selected_layer = _calendar_filter(context, request)

    events, has_more = _paginate_catalog_events(context, request,
                                           first_moment=now_datetime,
                                           last_moment=None,
                                           layer_name=selected_layer,
                                           per_page=per_page,
                                           page=page)
    calendar.paint_paginated_events(events, has_more, per_page, page)

    layers    = _get_calendar_layers(context)
    setup_url = _calendar_setup_url(context, request)

    # render
    api = TemplateAPI(context, request, calendar.title)
    return render_template_to_response(
        calendar.template_filename,
        api=api,
        setup_url=setup_url,
        calendar=calendar,
        selected_layer = selected_layer,
        layers = layers,
        quote = quote,
    )


def _get_calendar_categories(context):
    return [ x for x in context.values() if ICalendarCategory.providedBy(x) ]

def _get_calendar_layers(context):
    layers = [ x for x in context.values() if ICalendarLayer.providedBy(x) ]
    for layer in layers:
        layer._v_categories = []
        for path in layer.paths:
            category = {}
            try:
                calendar = find_model(context, path)
                title = _calendar_category_title(calendar)
                category['title'] = title
                layer._v_categories.append(category)
            except KeyError:
                continue
    return layers

def _get_all_calendar_categories(context, request):
    calendar_categories = []

    searcher = queryAdapter(context, ICatalogSearch)
    if searcher is not None:
        total, docids, resolver = searcher(
            allowed={'query': effective_principals(request), 'operator': 'or'},
            interfaces={'query':[ICalendarCategory],'operator':'or'},
            reverse=False,
            )

        for docid in docids:
            ob = resolver(docid)
            path = model_path(ob)
            title = _calendar_category_title(ob)
            calendar_categories.append({'title':title, 'path':path})

    calendar_categories.sort(key=lambda x: x['path'])
    return calendar_categories


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
            if 'calendar_category' not in request.POST:
                # FormEncode doesn't let us mark certain keys as being missable
                # Either any key can be missing from form or none, so we just
                # manually massage calendar_category, which may be missing,
                # before performing validation.
                request.POST['calendar_category'] = None

            converted = form.validate(request.POST)

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
                                           calendar_category=
                                            converted['calendar_category'],
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
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.initial_state

        startDate, endDate = _default_dates_requested(context, request)

        fill_values = dict(
            startDate = startDate,
            endDate = endDate,
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
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    calendar = find_interface(context, ICalendar)
    if calendar:
        calendar_categories = [ {'title':x.title, 'path':model_path(x)} for x in
                              _get_calendar_categories(calendar) ]
        calendar_categories.sort(key=lambda x: x['title'])
    else:
        calendar_categories = []

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
        calendar_categories=calendar_categories,
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
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    # find this event's calendar category title
    calendar = find_interface(context, ICalendar)
    if calendar is not None:
        titles = {}
        for cat in _get_calendar_categories(calendar):
            titles[model_path(cat)] = cat.title
        category_title = titles.get(context.calendar_category)
    else:
        category_title = None

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
        category_title=category_title,
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
            if 'calendar_category' not in request.POST:
                # FormEncode doesn't let us mark certain keys as being missable
                # Either any key can be missing from form or none, so we just
                # manually massage calendar_category, which may be missing,
                # before performing validation.
                request.POST['calendar_category'] = None

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
            context.calendar_category = converted['calendar_category']
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
            calendar_category=context.calendar_category,
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
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    calendar = find_interface(context, ICalendar)
    if calendar is not None:
        calendar_categories = [ {'title':x.title, 'path':model_path(x)} for x in
                              _get_calendar_categories(calendar) ]
        calendar_categories.sort(key=lambda x: x['title'])
    else:
        calendar_categories = []

    return render_form_to_response(
        'templates/edit_calendarevent.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        calendar_categories=calendar_categories,
        head_data=client_json_data,
        layout=layout,
        security_states=security_states,
        )

class AddCalendarEventForm(FormSchema):
    chained_validators = baseforms.start_end_constraints
    #
    title = baseforms.title
    tags = baseforms.tags
    calendar_category = validators.UnicodeString(strip=True)
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
    calendar_category = validators.UnicodeString(strip=True)
    startDate = baseforms.start_date
    endDate = baseforms.end_date
    location = validators.UnicodeString(strip=True)
    text = baseforms.text
    attendees = baseforms.TextAreaToList(strip=True)
    contact_name = validators.UnicodeString(strip=True)
    contact_email = validators.Email(not_empty=False, strip=True)

class CalendarCategoriesForm(FormSchema):
    category_title = validators.UnicodeString(strip=True, not_empty=True)

def _calendar_category_title(ob):
    community = find_community(ob)
    title = community and community.title or ''
    title = title + ' (%s)' % ob.title
    return title

_COLORS = ("red", "pink", "purple", "blue", "aqua", "green", "mustard",
           "orange", "silver", "olive")

def calendar_setup_view(context, request):
    default_category_name = ICalendarCategory.getTaggedValue('default_name')
    categories = filter(lambda x: x.__name__ != default_category_name,
                        _get_calendar_categories(context))

    default_layer_name = ICalendarLayer.getTaggedValue('default_name')
    layers = filter(lambda x: x.__name__ != default_layer_name,
                    _get_calendar_layers(context))

    fielderrors = {}
    fielderrors_target = None

    page_title = 'Calendar Setup'
    api = TemplateAPI(context, request, page_title)

    return render_template_to_response(
        'templates/calendar_setup.pt',
        back_to_calendar_url=model_url(context, request),
        categories_url=model_url(context, request, 'categories.html'),
        layers_url=model_url(context, request, 'layers.html'),
        formfields=api.formfields,
        fielderrors=fielderrors,
        fielderrors_target = fielderrors_target,
        api=api,
        editable_categories = categories,
        editable_layers = layers,
        all_categories = _get_all_calendar_categories(context, request),
        colors = _COLORS,
        )


def calendar_setup_categories_view(context, request):
    form = CalendarCategoriesForm()

    default_category_name = ICalendarCategory.getTaggedValue('default_name')
    default_category = context[default_category_name]
    default_category_path = model_path(default_category)
    categories = _get_calendar_categories(context)
    editable_categories = filter(lambda x: x.__name__ != default_category_name,
                                 categories)
    category_names = [ x.__name__ for x in categories ]

    default_layer_name = ICalendarLayer.getTaggedValue('default_name')
    default_layer = context[default_layer_name]
    layers = _get_calendar_layers(context)
    editable_layers = filter(lambda x: x.__name__ != default_layer_name,
                             layers)

    if 'form.delete' in request.POST:
        category_name = request.POST['form.delete']
        if category_name == default_category_name:
            message = 'Cannot delete default category'
        elif category_name and category_name in category_names:
            categ = context[category_name]
            title = categ.title
            categ_path = model_path(categ)
            if categ_path in default_layer.paths:
                default_layer.paths.remove(categ_path)
                default_layer._p_changed = True

            # uncategorize events that were previously in this
            # category (put them in the default category)
            query = dict(
                interfaces=[ICalendarEvent],
                virtual = categ_path,
                )
            searcher = ICatalogSearch(context)
            total, docids, resolver = searcher(**query)
            for event in [ resolver(x) for x in docids ]:
                event.calendar_category = default_category_path
                objectEventNotify(ObjectModifiedEvent(event))

            del context[category_name]

            message = '%s category removed' % title
        else:
            message = 'Category is invalid'



        location = model_url(context, request, 'categories.html',
                             query={'status_message': message})
        return HTTPFound(location=location)

    fielderrors = {}
    fielderrors_target = None

    if 'form.edit' in request.POST:
        category_name = request.POST['category__name__']

        if category_name == default_category_name:
            location = model_url(
                context,
                request, 'categories.html',
                query={'status_message':'Cannot edit default category'})
            return HTTPFound(location=location)

        if not category_name or not category_name in category_names:
            location = model_url(
                context,
                request, 'categories.html',
                query={'status_message':'Could not find category to edit'})
            return HTTPFound(location=location)

        category = context[category_name]

        try:
            converted = form.validate(request.POST)
            title = converted['category_title']

            if title in [ x.title for x in categories]:
                msg = "Name is already used"
                raise Invalid(value=title, state=None,
                          msg=msg, error_list=None,
                          error_dict={'category_title': msg})

            else:
                category.title = title
                location = model_url(
                    context, request,
                    'categories.html',
                    query={'status_message':'Calendar category updated'})
                return HTTPFound(location=location)

        except Invalid, e:
            fielderrors_target = ("%s_category" % category_name)
            fielderrors = e.error_dict

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            title = converted['category_title']

            if title in [ x.title for x in categories ]:
                msg = "Name is already used"
                raise Invalid(value=title, state=None,
                          msg=msg, error_list=None,
                          error_dict={'category_title': msg})

            category = create_content(ICalendarCategory, title)
            context[title] = category
            default_layer.paths.append(model_path(category))
            default_layer._p_changed = True

            location = model_url(
                context, request,
                'categories.html',
                query={'status_message':'Calendar category added'})
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors_target = '__add_category__'
            fielderrors = e.error_dict

    # Render the form and shove some default values in
    page_title = 'Calendar Categories'
    api = TemplateAPI(context, request, page_title)

    return render_template_to_response(
        'templates/calendar_setup.pt',
        back_to_calendar_url=model_url(context, request),
        categories_url=model_url(context, request, 'categories.html'),
        layers_url=model_url(context, request, 'layers.html'),
        formfields=api.formfields,
        fielderrors=fielderrors,
        fielderrors_target = fielderrors_target,
        api=api,
        editable_categories = editable_categories,
        editable_layers = editable_layers,
        all_categories = _get_all_calendar_categories(context, request),
        colors = _COLORS,
        )

class CalendarLayersForm(FormSchema):
    layer_title = validators.UnicodeString(strip=True, not_empty=True)
    layer_color = validators.UnicodeString(strip=True, not_empty=True)

def calendar_setup_layers_view(context, request):
    form = CalendarLayersForm()

    default_layer_name = ICalendarLayer.getTaggedValue('default_name')
    layers = filter(lambda x: x.__name__ != default_layer_name,
                    _get_calendar_layers(context))
    layer_names = [ x.__name__ for x in layers]

    categories = _get_calendar_categories(context)
    category_names = [ x.__name__ for x in categories ]

    if 'form.delete' in request.POST:
        layer_name = request.POST['form.delete']
        if layer_name == default_layer_name:
            message = 'Cannot delete default layer'
        elif layer_name and layer_name in layer_names:
            title = context[layer_name].title
            del context[layer_name]
            message = '%s layer removed' % title
        else:
            message = 'Layer is invalid'

        location = model_url(context, request, 'layers.html',
                             query={'status_message': message})
        return HTTPFound(location=location)

    fielderrors_target = None
    fielderrors = {}

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            category_paths = list(set(request.POST.getall('category_paths')))
            layer_title = converted['layer_title']
            layer_color = converted['layer_color']

            if layer_title in category_names:
                msg = "Name is already used by a category"
                raise Invalid(value=layer_title, state=None,
                          msg=msg, error_list=None,
                          error_dict={'layer_title': msg})

            if layer_title in layer_names:
                msg = "Name is already used"
                raise Invalid(value=layer_title, state=None,
                          msg=msg, error_list=None,
                          error_dict={'layer_title': msg})

            layer = create_content(ICalendarLayer,
                                   layer_title, layer_color, category_paths)
            context[layer_title] = layer

            location = model_url(
                context, request,
                'layers.html',
                query={'status_message':'Calendar layer added'})
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors_target = '__add_layer__'
            fielderrors = e.error_dict

    if 'form.edit' in request.POST:
        layer_name = request.POST['layer__name__']

        if layer_name == default_layer_name:
            location = model_url(
                context,
                request, 'layers.html',
                query={'status_message':'Cannot edit default layer'})
            return HTTPFound(location=location)

        if not layer_name or not layer_name in layer_names:
            location = model_url(
                context,
                request, 'layers.html',
                query={'status_message':'Could not find layer to edit'})
            return HTTPFound(location=location)

        layer = context[layer_name]

        try:
            converted = form.validate(request.POST)
            layer_title = converted['layer_title']
            category_paths = list(set(request.POST.getall('category_paths')))
            layer_color = converted['layer_color']

            if layer_title in category_names:
                msg = "Name is already used by a category"
                raise Invalid(value=layer_title, state=None,
                          msg=msg, error_list=None,
                          error_dict={'layer_title': msg})

            if (layer_title != layer.title) and (layer_title in layer_names):
                msg = "Name is already used"
                raise Invalid(value=layer_title, state=None,
                          msg=msg, error_list=None,
                          error_dict={'layer_title': msg})

            else:
                layer.title = layer_title
                layer.paths = list(set(request.POST.getall('category_paths')))
                layer.color = layer_color

                location = model_url(
                    context, request,
                    'layers.html',
                    query={'status_message':'Calendar layer updated'})
                return HTTPFound(location=location)

        except Invalid, e:
            fielderrors_target = ("%s_layer" % layer_name)
            fielderrors = e.error_dict

    # Render the form and shove some default values in
    page_title = 'Calendar Layers'
    api = TemplateAPI(context, request, page_title)

    return render_template_to_response(
        'templates/calendar_setup.pt',
        back_to_calendar_url=model_url(context, request),
        categories_url=model_url(context, request, 'categories.html'),
        layers_url=model_url(context, request, 'layers.html'),
        formfields=api.formfields,
        fielderrors=fielderrors,
        fielderrors_target=fielderrors_target,
        editable_categories = categories,
        editable_layers = layers,
        all_categories = _get_all_calendar_categories(context, request),
        colors = _COLORS,
        api=api,
        )
