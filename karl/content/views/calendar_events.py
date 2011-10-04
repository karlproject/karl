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
import copy

from urllib import quote

from validatish import validator
import formish
import schemaish

from zope.component.event import objectEventNotify
from zope.component import getUtility
from zope.component import queryUtility
from zope.component import queryAdapter

from pyramid.httpexceptions import HTTPFound

from pyramid.renderers import render_to_response
from pyramid_formish import ValidationError
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource

from pyramid.url import resource_url
from repoze.workflow import get_workflow

from repoze.lemonade.content import create_content

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.models.interfaces import ICatalogSearch

from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from karl.utilities.interfaces import IKarlDates
from karl.utilities.randomid import unfriendly_random_id

from karl.utils import coarse_datetime_repr
from karl.utils import find_interface
from karl.utils import find_community

from karl.security.policy import CREATE
from karl.security.workflow import get_security_states

from karl.views.api import TemplateAPI
from karl.views.forms import attr as karlattr
from karl.views.forms import widgets as karlwidgets
from karl.views.forms import validators as karlvalidator
from karl.views.forms.filestore import get_filestore
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name

from karl.content.interfaces import ICalendar
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICalendarLayer
from karl.content.interfaces import ICalendarCategory
from karl.content.views.utils import extract_description
from karl.content.views.utils import split_lines
from karl.content.views.utils import upload_attachments
from karl.utils import get_layout_provider

from karl.content.views.utils import fetch_attachments
from karl.content.views.utils import get_show_sendalert

from karl.content.calendar.presenters.day import DayViewPresenter
from karl.content.calendar.presenters.day import DayEventHorizon
from karl.content.calendar.presenters.week import WeekViewPresenter
from karl.content.calendar.presenters.week import WeekEventHorizon
from karl.content.calendar.presenters.month import MonthViewPresenter
from karl.content.calendar.presenters.month import MonthEventHorizon
from karl.content.calendar.presenters.list import ListViewPresenter
from karl.content.calendar.utils import is_all_day_event

# The name of the cookie that makes the calendar view sticky.
# Possible cookie values are 'day', 'week', 'month', 'list'.
# In case of no value or unknown value, 'day' is considered
# as default.
KARL_CALENDAR_VIEW_COOKIE = 'karl.calendar_view'
KARL_CALENDAR_DATE_COOKIE = 'karl.calendar.date'
KARL_CALENDAR_FILTER_COOKIE = 'karl.calendar.filter'

_NOW = None

def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()


KARL_CALENDAR_COOKIE = 'karl.calendar.cookie'

def _get_calendar_cookies(context, request):
    now = _now()

    # fetch the cookies
    cookie = request.cookies.get(KARL_CALENDAR_COOKIE, '')
    try:
        viewtype, term, year, month, day = cookie.split(',')
        year = int(year)
        month = int(month)
        day = int(day)
    except (AttributeError, TypeError, ValueError), exc:
        viewtype, term, year, month, day = '', '', now.year, now.month, now.day

    # request parameters override the cookies
    viewtype = request.GET.get('viewtype', viewtype)
    term = request.GET.get('term', term)
    year = int(request.GET.get('year', year))
    month = int(request.GET.get('month', month))
    day = int(request.GET.get('day', day))

    return dict(
        viewtype=viewtype,
        term=term,
        year=year,
        month=month,
        day=day,
    )

def _set_calendar_cookies(response, selection):
    value = ','.join([
        selection['viewtype'],
        selection['term'],
        str(selection['year']),
        str(selection['month']),
        str(selection['day']),
    ])
    response.set_cookie(KARL_CALENDAR_COOKIE, value)


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

    events = []

    for layer in _get_calendar_layers(calendar):
        if layer_name and layer.__name__ != layer_name:
            continue

        total, docids, resolver = searcher(
            virtual={'query':layer.paths, 'operator':'or'},
            **search_params)

        for docid in docids:
            if docid not in docids_seen:

                # We need to clone the event, because if an event is
                # shown in multiple layers, then we want to show it multiple
                # times.
                # This also means that making the color and title
                # volatile, serves no purpose any more. It used to serve
                # a purpose when the same event could only have
                # been displayed once.
                #
                # It's important to perform a shallow copy of the event. A deep
                # copy can leak out and try to copy the entire database through
                # the parent reference

                event = copy.copy(resolver(docid))
                event._v_layer_color = layer.color.strip()
                event._v_layer_title = layer.title

                # but... showing an event multiple times, for each
                # layer it is in,
                # currently only makes sense for all-day
                # events. As, for normal events, this would make
                # them undisplayable.
                # So we only add the event to the seen ones, if
                # it is a normal, and not an all-day event.
                # A special case is list views when we want the normal
                # events duplicated too. The characteristics of a list
                # view is that the end date is open.
                all_day = event.startDate.hour == 0 and \
                    event.startDate.minute == 0 and \
                    event.endDate.hour == 0 and \
                    event.endDate.minute == 0
                in_list_view = last_moment is None
                if not in_list_view and not all_day:
                    docids_seen.add(docid)

                events.append(event)

    # The result set needs to be sorted by start_date.
    # XXX maybe we can do this directly from the catalog?
    events.sort(key=lambda event: event.startDate)

    return events

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

# XXX XXX TODO: remove the session, make a cookie
def _calendar_filter(context, request):
    filt = request.params.get('filter', None)
    if filt is None:
        filt = request.cookies.get(KARL_CALENDAR_FILTER_COOKIE, None)
    return filt

def _calendar_setup_url(context, request):
    if has_permission('moderate', context, request):
        setup_url = resource_url(context, request, 'setup.html')
    else:
        setup_url = None
    return setup_url

def _make_calendar_presenter_url_func(context, request):
    def url_for(*args, **kargs):
        ctx = kargs.pop('context', context)
        return resource_url(ctx, request, *args, **kargs)
    return url_for


def _select_calendar_layout(context, request):
    # Check if we are in /offices/calendar.
    # If yes, we will need to put a css marker class "karl-calendar-wide"
    # on the outside of the template, and we will also use the generic
    # layout instead of the community layout.
    # XXX TODO we will also restrict permissions.
    context_path = resource_path(context)
    wide_calendar = context_path.startswith('/offices/calendar')
    if wide_calendar:
        calendar_format_class = 'karl-calendar-wide'
        calendar_layout_template = 'generic_layout'
    else:
        calendar_format_class = None
        calendar_layout_template = 'community_layout'
    return dict(
        wide_calendar = wide_calendar,
        calendar_format_class = calendar_format_class,
        calendar_layout_template = calendar_layout_template,
    )


def _show_calendar_view(context, request, make_presenter, selection):
    # Check if we are in /offices/calendar.
    calendar_layout = _select_calendar_layout(context, request)

    year, month, day = selection['year'], selection['month'], selection['day']
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
    api.karl_client_data['calendar_selection'] = selection
    response = render_to_response(
        calendar.template_filename,
        dict(
            calendar_format_class = calendar_layout['calendar_format_class'],
            calendar_layout_template = calendar_layout['calendar_layout_template'],
            api=api,
            setup_url=setup_url,
            calendar=calendar,
            selected_layer = selected_layer,
            layers = layers,
            quote = quote,
            may_create = has_permission(CREATE, context, request)),
        request=request,
    )
    return response

def show_month_view(context, request):
    selection = _get_calendar_cookies(context, request)
    selection['viewtype'] = 'calendar'
    selection['term'] = 'month'
    response = _show_calendar_view(context, request, MonthViewPresenter, selection)
    _set_calendar_cookies(response, selection)
    return response

def show_week_view(context, request):
    selection = _get_calendar_cookies(context, request)
    selection['viewtype'] = 'calendar'
    selection['term'] = 'week'
    response = _show_calendar_view(context, request, WeekViewPresenter, selection)
    _set_calendar_cookies(response, selection)
    return response

def show_day_view(context, request):
    selection = _get_calendar_cookies(context, request)
    selection['viewtype'] = 'calendar'
    selection['term'] = 'day'
    response = _show_calendar_view(context, request, DayViewPresenter, selection)
    _set_calendar_cookies(response, selection)
    return response

def show_list_view(context, request):
    selection = _get_calendar_cookies(context, request)
    selection['viewtype'] = 'list'
    # Check if we are in /offices/calendar.
    calendar_layout = _select_calendar_layout(context, request)

    year, month, day = selection['year'], selection['month'], selection['day']
    focus_datetime = datetime.datetime(year, month, day)
    now_datetime   = _now()

    page     = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))

    # make the calendar presenter for this view
    url_for = _make_calendar_presenter_url_func(context, request)
    calendar = ListViewPresenter(focus_datetime,
                                 now_datetime,
                                 url_for)
    # Also make an event horizon for the selected term
    # (day, week or month)
    if not selection['term']:
        selection['term'] = 'day'
    event_horizon = {
        'day': DayEventHorizon,
        'week': WeekEventHorizon,
        'month': MonthEventHorizon,
        }[selection['term']](focus_datetime,
                                 now_datetime,
                                 url_for)

    # find events and paint them on the calendar
    selected_layer = _calendar_filter(context, request)

    events, has_more = _paginate_catalog_events(context, request,
                                           first_moment=event_horizon.first_moment,
                                           last_moment=event_horizon.last_moment,
                                           layer_name=selected_layer,
                                           per_page=per_page,
                                           page=page)
    calendar.paint_paginated_events(events, has_more, per_page, page)

    layers    = _get_calendar_layers(context)
    setup_url = _calendar_setup_url(context, request)

    # render
    api = TemplateAPI(context, request, calendar.title)
    api.karl_client_data['calendar_selection'] = selection
    response = render_to_response(
        calendar.template_filename,
        dict(
            calendar_format_class = calendar_layout['calendar_format_class'],
            calendar_layout_template = calendar_layout['calendar_layout_template'],
            api=api,
            setup_url=setup_url,
            calendar=calendar,
            selected_layer = selected_layer,
            layers = layers,
            quote = quote,
            may_create = has_permission(CREATE, context, request)),
        request=request,
    )
    _set_calendar_cookies(response, selection)
    return response



def show_view(context, request):
    """Select the last used view from month, week, day, and list.
    State is stored in a browser cookie.

    We do redirect in order to maintain the working of links.
    """
    selection = _get_calendar_cookies(context, request)
    if selection['viewtype'] == 'list':
        view_name = 'list.html'
    else:
        view_name = {
            'month': 'month.html',
            'week': 'week.html',
            'day': 'day.html',
            }.get(selection['term'], 'day.html')
    response = HTTPFound(location=resource_url(context, request, view_name))
    _set_calendar_cookies(response, selection)
    return response


def redirect_to_add_form(context, request):
    return HTTPFound(
            location=resource_url(context, request, 'add_calendarevent.html'))


def _get_calendar_categories(context):
    return [ x for x in context.values() if ICalendarCategory.providedBy(x) ]

def _get_calendar_layers(context):
    layers = [ x for x in context.values() if ICalendarLayer.providedBy(x) ]
    for layer in layers:
        layer._v_categories = []
        for path in layer.paths:
            category = {}
            try:
                calendar = find_resource(context, path)
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
            path = resource_path(ob)
            folder = path.rsplit('/', 1)[0]
            title = _calendar_category_title(ob)
            calendar_categories.append({'title':title, 'path':path,
                                        'folder':folder})

    calendar_categories.sort(key=lambda x: (x['folder'], x['title']))
    return calendar_categories


tags_field = schemaish.Sequence(schemaish.String())
category_field = schemaish.String()
all_day_field = schemaish.Boolean()
start_date_field = karlattr.KarlDateTime(
    validator=validator.All(validator.Required(), karlvalidator.DateTime())
    )
end_date_field = karlattr.KarlDateTime(
    validator=validator.All(validator.Required(), karlvalidator.DateTime())
    )
location_field = schemaish.String()
text_field = schemaish.String(title='Description')
attendees_field = schemaish.String(description='One per line')
contact_name_field = schemaish.String()
contact_email_field = schemaish.String(
    validator=validator.Any(validator.Email(), validator.Equal(''))
    )
attachments_field = schemaish.Sequence(
    schemaish.File(),
    title='Attachments',
    )
sendalert_field = schemaish.Boolean(
    title='Send email alert to community members?')
security_field = schemaish.String(
    title='Is this private?',
    validator=validator.Required(),
    description=('Items marked as private can only be seen by '
                 'members of this community.'))


class CalendarEventFormControllerBase(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(ICalendarEvent, 'security', context)
        self.filestore = get_filestore(context, request, 'calendar-event')

    def _get_security_states(self):
        return get_security_states(self.workflow, None, self.request)

    def form_fields(self):
        fields = [('tags', tags_field),
                  ('category', category_field),
                  ('all_day', all_day_field),
                  ('start_date', start_date_field),
                  ('end_date', end_date_field),
                  ('location', location_field),
                  ('text', text_field),
                  ('attendees', attendees_field),
                  ('contact_name', contact_name_field),
                  ('contact_email', contact_email_field),
                  ('attachments', attachments_field),
                  ]
        security_states = self._get_security_states()
        if security_states:
            fields.append(('security_state', security_field))
        return fields

    def form_widgets(self, fields):
        # compute category values
        calendar_categories = []
        default_category = None
        calendar = find_interface(self.context, ICalendar)
        if calendar:
            default_category_name = ICalendarCategory.getTaggedValue('default_name')
            for category in _get_calendar_categories(calendar):
                category_tuple = (resource_path(category), category.title)
                if category.__name__ == default_category_name:
                    default_category = category_tuple
                else:
                    calendar_categories.append(category_tuple)
            calendar_categories.sort(key=lambda x: x[1])
        category_widget = formish.SelectChoice(calendar_categories)
        if default_category:
            category_widget.none_option = default_category
        widgets = {
            'title': formish.Input(empty=''),
            'category': category_widget,
            'all_day': formish.Hidden(),
            'start_date': karlwidgets.DateTime(),
            'end_date': karlwidgets.DateTime(),
            'location': formish.Input(empty=''),
            'text': karlwidgets.RichTextWidget(empty=''),
            'attendees': formish.TextArea(rows=5, cols=60),
            'contact_name': formish.Input(empty=''),
            'contact_email': formish.Input(empty=''),
            'attachments': karlwidgets.AttachmentsSequence(sortable=False,
                                                           min_start_fields=0),
            'attachments.*': karlwidgets.FileUpload2(filestore=self.filestore),
            }
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[(s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets

    def __call__(self):
        context = self.context
        request = self.request
        api = TemplateAPI(context, request, self.page_title)
        layout_provider = get_layout_provider(context, request)
        layout = layout_provider('community')
        api.karl_client_data['text'] = dict(
                enable_imagedrawer_upload = True,
                )
        return {'api': api, 'actions': (), 'layout': layout}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

    def handle_submit(self, converted):
        # first do the start / end date validation
        start_date = converted['start_date']
        end_date = converted['end_date']
        if end_date < start_date:
            errors = {'end_date': u'End date must follow start date'}
            raise ValidationError(**errors)
        elif converted['all_day']:
            # massage into all day values if necessary
            converted['start_date'] = datetime.datetime(
                start_date.year, start_date.month, start_date.day,
                0, 0, 0
                )
            converted['end_date'] = datetime.datetime(
                end_date.year, end_date.month, end_date.day,
                0, 0, 0
                ) + datetime.timedelta(days=1)
        elif (end_date - start_date) < datetime.timedelta(minutes=1):
            errors = {'end_date':
                      u'Event duration must be at least one minute'}
            raise ValidationError(**errors)

        # split the lines for the attendees
        if converted['attendees']:
            converted['attendees'] = split_lines(converted['attendees'])


class AddCalendarEventFormController(CalendarEventFormControllerBase):
    page_title = u'Add Calendar Entry'

    def __init__(self, context, request):
        super(AddCalendarEventFormController, self).__init__(context, request)
        self.show_sendalert = get_show_sendalert(self.context, self.request)

    def form_defaults(self):
        start_date, end_date = _default_dates_requested(self.context,
                                                        self.request)
        defaults ={'start_date': start_date,
                   'end_date': end_date,
                   }
        if self.show_sendalert:
            defaults['sendalert'] = True
        security_states = self._get_security_states()
        if security_states:
            defaults['security_state'] = security_states[0]['name']
        return defaults

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                )
            )
        fields = [('title', title_field)]
        fields.extend(super(AddCalendarEventFormController, self).form_fields())
        if self.show_sendalert:
            fields.insert(-1, ('sendalert', sendalert_field),)
        return fields

    def form_widgets(self, fields):
        widgets = super(AddCalendarEventFormController, self).form_widgets(fields)
        widgets['tags'] = karlwidgets.TagsAddWidget()
        if 'sendalert' in dict(fields):
            widgets['sendalert'] = karlwidgets.SendAlertCheckbox()
        return widgets

    def handle_submit(self, converted):
        # base class does some validation and simple massaging
        super(AddCalendarEventFormController, self).handle_submit(converted)

        # we create the event and handle other details
        context = self.context
        request = self.request
        creator = authenticated_userid(request)
        attendees = converted.get('attendees') or []
        calendar_event = create_content(ICalendarEvent,
                                        converted['title'],
                                        converted['start_date'],
                                        converted['end_date'],
                                        creator,
                                        converted['text'],
                                        converted['location'],
                                        attendees,
                                        converted['contact_name'],
                                        converted['contact_email'],
                                        calendar_category=converted['category'],
                                        )
        calendar_event.description = extract_description(converted['text'])
        calname = make_unique_name(context, calendar_event.title)
        context[calname] = calendar_event

        # set up workflow
        workflow = get_workflow(ICalendarEvent, 'security', context)
        if workflow is not None:
            workflow.initialize(calendar_event)
            if 'security_state' in converted:
                workflow.transition_to_state(calendar_event, request,
                                             converted['security_state'])

        # save tags and attachments
        set_tags(calendar_event, request, converted['tags'])
        upload_attachments(converted['attachments'],
                           calendar_event['attachments'],
                           creator, request)

        # send alert
        if converted.get('sendalert', False):
            alerts = queryUtility(IAlerts, default=Alerts())
            alerts.emit(calendar_event, request)

        self.filestore.clear()
        return HTTPFound(location=resource_url(calendar_event, request))


def show_calendarevent_view(context, request):

    page_title = context.title

    actions = []
    if has_permission('edit', context, request):
        actions.append(('Edit', 'edit.html'))
    if has_permission('delete', context, request):
        actions.append(('Delete', 'delete.html'))
    if has_permission('administer', context, request):
        actions.append(('Advanced', 'advanced.html'))

    api = TemplateAPI(context, request, page_title)

    container  = context.__parent__
    backto = {
        'href': resource_url(container, request),
        'title': container.title,
        }

    # Flatten the data into ZPT-friendly info
    karldates = getUtility(IKarlDates)
    title = context.title
    startDate = karldates(context.startDate, 'longform')
    endDate = karldates(context.endDate, 'longform')
    attendees = None
    if context.attendees:
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
            titles[resource_path(cat)] = cat.title
        category_title = titles.get(context.calendar_category)
    else:
        category_title = None

    return render_to_response(
        'templates/show_calendarevent.pt',
        dict(api=api,
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
             ),
        request=request,
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
        if isinstance(name, unicode):
            name = name.encode('UTF-8')
        event.add('attendee', name)

    for f in context['attachments'].values():
        attachment = vUri(resource_url(f, request))
        attachment.params['fmttype'] = f.mimetype
        event.add('attach', attachment)

    calendar.add_component(event)
    return Response(body=calendar.as_string(),
                    content_type='text/calendar',
                    charset='UTF8',
                   )


class EditCalendarEventFormController(CalendarEventFormControllerBase):
    def __init__(self, context, request):
        super(EditCalendarEventFormController, self).__init__(context, request)
        self.page_title = 'Edit %s' % context.title

    def form_defaults(self):
        context = self.context
        if self.workflow is None:
            security_state = ''
        else:
            security_state = self.workflow.state_of(context)
        attendees = getattr(context, 'attendees', [])
        defaults = dict(
            title=context.title,
            text=context.text,
            start_date=context.startDate,
            end_date=context.endDate,
            location=context.location,
            attendees=u'\n'.join([i for i in attendees if i]),
            contact_name=context.contact_name,
            contact_email=context.contact_email,
            category=context.calendar_category,
            security_state = security_state,
            )

        if defaults['contact_email'] is None:
            defaults['contact_email'] = u''

        if is_all_day_event(context):
            defaults['all_day'] = True
            defaults['end_date'] -= datetime.timedelta(days=1)
        else:
            defaults['all_day'] = False
        return defaults

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                )
            )
        fields = [('title', title_field)]
        fields.extend(super(EditCalendarEventFormController, self).form_fields())
        return fields

    def form_widgets(self, fields):
        widgets = super(EditCalendarEventFormController, self).form_widgets(fields)
        tagdata = get_tags_client_data(self.context, self.request)
        widgets['tags'] = karlwidgets.TagsEditWidget(tagdata=tagdata)
        return widgets

    def handle_submit(self, converted):
        # base class does some validation and simple massaging
        super(EditCalendarEventFormController, self).handle_submit(converted)

        context = self.context
        request = self.request
        # *will be* modified event
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        if self.workflow is not None:
            if 'security_state' in converted:
                self.workflow.transition_to_state(context, request,
                                                  converted['security_state'])

        context.title = converted['title']
        context.startDate = converted['start_date']
        context.endDate = converted['end_date']
        context.text = converted['text']
        context.location = converted['location']
        context.attendees = converted.get('attendees') or []
        context.contact_name = converted['contact_name']
        context.contact_email = converted['contact_email']
        context.calendar_category = converted['category']
        context.description = extract_description(converted['text'])

        # Save the tags on it
        set_tags(context, request, converted['tags'])

        # Save new attachments
        userid = authenticated_userid(request)
        attachments_folder = context['attachments']
        upload_attachments(converted['attachments'], attachments_folder,
                           userid, request)

        # Modified
        context.modified_by = userid
        objectEventNotify(ObjectModifiedEvent(context))

        self.filestore.clear()
        location = resource_url(context, request)
        msg = "?status_message=Calendar%20Event%20edited"
        return HTTPFound(location='%s%s' % (location, msg))


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

    return render_to_response(
        'templates/calendar_setup.pt',
        dict(back_to_calendar_url=resource_url(context, request),
             categories_url=resource_url(context, request, 'categories.html'),
             layers_url=resource_url(context, request, 'layers.html'),
             formfields=api.formfields,
             fielderrors=fielderrors,
             fielderrors_target = fielderrors_target,
             api=api,
             editable_categories = categories,
             editable_layers = layers,
             all_categories = _get_all_calendar_categories(context, request),
             colors = _COLORS),
        request = request,
        )


class Invalid(Exception):
    def __init__(self, msg, error_dict=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.error_dict = error_dict

def convert_to_unicode(value, field_name, encoding='utf-8'):
    """Stolen from formencode.validators.UnicodeString."""
    if isinstance(value, unicode):
        return value
    if not isinstance(value, unicode):
        if hasattr(value, '__unicode__'):
            value = unicode(value)
            return value
        else:
            value = str(value)
    try:
        return unicode(value, encoding)
    except UnicodeDecodeError:
        msg = 'Invalid data or incorrect encoding'
        raise Invalid(msg, error_dict={field_name: msg})
    except TypeError:
        msg = 'Invalid type'
        raise Invalid(msg, error_dict={field_name: msg})

def calendar_setup_categories_view(context, request):
    default_category_name = ICalendarCategory.getTaggedValue('default_name')
    default_category = context[default_category_name]
    default_category_path = resource_path(default_category)
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
            categ_path = resource_path(categ)
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

        location = resource_url(context, request, 'categories.html',
                             query={'status_message': message})
        return HTTPFound(location=location)

    fielderrors = {}
    fielderrors_target = None

    if 'form.edit' in request.POST:
        category_name = request.POST['category__name__']

        if category_name == default_category_name:
            location = resource_url(
                context,
                request, 'categories.html',
                query={'status_message':'Cannot edit default category'})
            return HTTPFound(location=location)

        if not category_name or not category_name in category_names:
            location = resource_url(
                context,
                request, 'categories.html',
                query={'status_message':'Could not find category to edit'})
            return HTTPFound(location=location)

        category = context[category_name]

        try:
            title = request.POST['category_title'].strip()
            if not title:
                msg = 'Please enter a value'
                raise Invalid(msg, error_dict={'category_title': msg})
            title = convert_to_unicode(title, 'category_title')

            if title in [ x.title for x in categories]:
                msg = "Name is already used"
                raise Invalid(msg=msg, error_dict={'category_title': msg})

            else:
                category.title = title
                location = resource_url(
                    context, request,
                    'categories.html',
                    query={'status_message':'Calendar category updated'})
                return HTTPFound(location=location)

        except Invalid, e:
            fielderrors_target = ("%s_category" % category_name)
            fielderrors = e.error_dict

    if 'form.submitted' in request.POST:
        try:
            title = request.POST['category_title'].strip()
            if not title:
                msg = 'Please enter a value'
                raise Invalid(msg, error_dict={'category_title': msg})
            name = generate_name(context)
            title = convert_to_unicode(title, 'category_title')

            if title in [ x.title for x in categories ]:
                msg = "Name is already used"
                raise Invalid(msg=msg, error_dict={'category_title': msg})

            category = create_content(ICalendarCategory, title)
            context[name] = category
            default_layer.paths.append(resource_path(category))
            default_layer._p_changed = True

            location = resource_url(
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

    return render_to_response(
        'templates/calendar_setup.pt',
        dict(back_to_calendar_url=resource_url(context, request),
             categories_url=resource_url(context, request, 'categories.html'),
             layers_url=resource_url(context, request, 'layers.html'),
             fielderrors=fielderrors,
             fielderrors_target = fielderrors_target,
             api=api,
             editable_categories = editable_categories,
             editable_layers = editable_layers,
             all_categories = _get_all_calendar_categories(context, request),
             colors = _COLORS),
        request = request,
        )

def calendar_setup_layers_view(context, request):
    default_layer_name = ICalendarLayer.getTaggedValue('default_name')
    layers = filter(lambda x: x.__name__ != default_layer_name,
                    _get_calendar_layers(context))
    layer_titles = [ x.title for x in layers]
    layer_names = [ x.__name__ for x in layers ]

    default_category_name = ICalendarCategory.getTaggedValue('default_name')
    categories = filter(lambda x: x.__name__ != default_category_name,
                        _get_calendar_categories(context))

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

        location = resource_url(context, request, 'layers.html',
                             query={'status_message': message})
        return HTTPFound(location=location)

    fielderrors_target = None
    fielderrors = {}

    if 'form.submitted' in request.POST:
        try:
            error_dict = {}
            category_paths = list(set(request.POST.getall('category_paths')))
            category_paths = [path for path in category_paths if path]
            if not category_paths:
                error_dict['category_paths'] = 'Please enter a value'
            layer_title = request.POST['layer_title']
            if not layer_title:
                error_dict['layer_title'] = 'Please enter a value'
            layer_color = request.POST.get('layer_color')
            if not layer_color:
                error_dict['layer_color'] = 'Please enter a value'
            if error_dict:
                raise Invalid(msg='Please correct the following errors',
                              error_dict=error_dict)
            layer_title = convert_to_unicode(layer_title, 'layer_title')
            layer_color = convert_to_unicode(layer_color, 'layer_color')

            layer_name = generate_name(context)
            if layer_title in layer_titles:
                msg = "Name is already used"
                raise Invalid(msg=msg, error_dict={'layer_title': msg})

            layer = create_content(ICalendarLayer,
                                   layer_title, layer_color, category_paths)
            context[layer_name] = layer

            location = resource_url(
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
            location = resource_url(
                context,
                request, 'layers.html',
                query={'status_message':'Cannot edit default layer'})
            return HTTPFound(location=location)

        if not layer_name or not layer_name in layer_names:
            location = resource_url(
                context,
                request, 'layers.html',
                query={'status_message':'Could not find layer to edit'})
            return HTTPFound(location=location)

        layer = context[layer_name]

        try:
            error_dict = {}
            category_paths = list(set(request.POST.getall('category_paths')))
            category_paths = [path for path in category_paths if path]
            if not category_paths:
                error_dict['category_paths'] = 'Please enter a value'
            layer_title = request.POST.get('layer_title')
            if not layer_title:
                error_dict['layer_title'] = 'Please enter a value'
            layer_color = request.POST.get('layer_color')
            if not layer_color:
                error_dict['layer_color'] = 'Please enter a value'
            if error_dict:
                raise Invalid(msg='Please correct the following errors',
                              error_dict=error_dict)
            layer_title = convert_to_unicode(layer_title, 'layer_title')
            layer_color = convert_to_unicode(layer_color, 'layer_color')

            if (layer_title != layer.title) and (layer_title in layer_titles):
                msg = "Name is already used"
                raise Invalid(msg=msg, error_dict={'layer_title': msg})

            else:
                layer.title = layer_title
                layer.paths = category_paths
                layer.color = layer_color

                location = resource_url(
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

    return render_to_response(
        'templates/calendar_setup.pt',
        dict(back_to_calendar_url=resource_url(context, request),
             categories_url=resource_url(context, request, 'categories.html'),
             layers_url=resource_url(context, request, 'layers.html'),
             formfields=api.formfields,
             fielderrors=fielderrors,
             fielderrors_target=fielderrors_target,
             editable_categories = categories,
             editable_layers = layers,
             all_categories = _get_all_calendar_categories(context, request),
             colors = _COLORS,
             api=api),
        request=request,
        )

def generate_name(context):
    while True:
        name = unfriendly_random_id()
        if not (name in context):
            return name
