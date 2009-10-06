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

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from karl.models.interfaces import ICatalogSearch
from karl.utils import coarse_datetime_repr

from karl.views.api import TemplateAPI
from karl.content.interfaces import ICalendarEvent
from karl.content.newcalendar.presenters.day import DayViewPresenter
from karl.content.newcalendar.presenters.week import WeekViewPresenter
from karl.content.newcalendar.presenters.month import MonthViewPresenter
from karl.content.newcalendar.presenters.list import ListViewPresenter


_NOW = None

def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()

def _date_requested(request):
    now = _now()
    year  = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    day   = int(request.GET.get('day', now.day)) 
    return (year, month, day)

def _get_catalog_events(context, request, first_moment, last_moment):
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

    events = []       
    for docid in docids:
        events.append(resolver(docid))
        
    return events

def _show_calendar_view(context, request, make_presenter):
    year, month, day = _date_requested(request)
    focus_datetime = datetime.datetime(year, month, day)
    now_datetime   = _now()

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
                                 calendar.last_moment)                                                       
    calendar.paint_events(events)

    # render
    api = TemplateAPI(context, request, calendar.title)    
    return render_template_to_response(
        calendar.template_filename,
        api=api,          
        feed_url=calendar.feed_href,
        calendar=calendar        
    )    

def show_list_view(context, request):
    return _show_calendar_view(context, request, ListViewPresenter)

def show_month_view(context, request):
    return _show_calendar_view(context, request, MonthViewPresenter)

def show_week_view(context, request):
    return _show_calendar_view(context, request, WeekViewPresenter)
    
def show_day_view(context, request):
    return _show_calendar_view(context, request, DayViewPresenter)
    
