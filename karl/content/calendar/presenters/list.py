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
import datetime
import time
from karl.content.calendar.presenters.base import BasePresenter
from karl.content.calendar.presenters.base import BaseEvent
from karl.content.calendar.navigation import Navigation 
from karl.content.calendar.utils import MonthSkeleton
from karl.content.calendar.utils import next_month
from karl.content.calendar.utils import prior_month                   


class ListViewPresenter(BasePresenter):
    name = 'list'
    
    def _initialize(self):               
        monthname = calendar.month_name[self.focus_datetime.month]
        self.title = "%s %d" % (monthname, self.focus_datetime.year)
        self.feed_href = self.url_for('atom.xml')  

        self.events = []

        self._init_prior_month()
        self._init_next_month()
        
        self._init_navigation()

    def _init_prior_month(self):
        prior = prior_month(self.focus_datetime.year, 
                            self.focus_datetime.month)
        monthrange = calendar.monthrange(prior[0], prior[1])  
                                         
        if self.focus_datetime.day <= monthrange[1]:
            day = self.focus_datetime.day
        else:
            day = monthrange[1]    
            
        self.prior_month = datetime.datetime(prior[0], prior[1], day)

    def _init_next_month(self):
        next = next_month(self.focus_datetime.year, 
                          self.focus_datetime.month)
        monthrange = calendar.monthrange(next[0], next[1])

        if self.focus_datetime.day <= monthrange[1]:
            day = self.focus_datetime.day
        else:
            day = monthrange[1]

        self.next_month = datetime.datetime(next[0], next[1], day)        
    
    def _init_navigation(self):
        nav = Navigation(self)

        # left side
        format = '%s?year=%d&month=%d&day=%d'
        url = self.url_for('list.html')

        nav.prev_url = format % (url, self.prior_month.year, 
                                      self.prior_month.month,
                                      self.prior_month.day)
        nav.next_url = format % (url, self.next_month.year, 
                                      self.next_month.month,
                                      self.prior_month.day)

        nav.today_url = format % (url, self.now_datetime.year,
                                       self.now_datetime.month,
                                       self.now_datetime.day)
        self.navigation = nav

    def paint_events(self, events):
        shaded_row = True
        for event in events:
            listed_event = Event(catalog_event=event,
                                shaded_row=shaded_row,
                                show_url=self.url_for(context=event)
                           )
            self.events.append(listed_event)          
            shaded_row = not(shaded_row)

    @property
    def first_moment(self):
        return datetime.datetime(self.focus_datetime.year, 
                                 self.focus_datetime.month, 
                                 1, 
                                 0, 0, 0)

    @property
    def last_moment(self):
        last_day = calendar.monthrange(self.focus_datetime.year, 
                                       self.focus_datetime.month)[1]
        return datetime.datetime(self.focus_datetime.year, 
                                 self.focus_datetime.month,
                                 last_day, 
                                 23, 59, 59)

    @property
    def template_filename(self):
        return 'templates/calendar_list.pt'


class Event(object):
    DEFAULT_LAYER = '*default*'
    LAYER_SUFFIX  = ' layer'

    def __init__(self, catalog_event, shaded_row=True,
                 show_url='#', edit_url='#', delete_url='#'):

        self._catalog_event = catalog_event # ICalendarEvent                               

        self.shaded_row = shaded_row
        self.show_url = show_url
        self.edit_url = edit_url
        self.delete_url = delete_url

        self._init_properties()
        self._init_layer_properties()
        self._init_date_and_time_properties()
 
    def _init_properties(self):
        self.title       = self._catalog_event.title
        self.location    = self._catalog_event.location
        self.description = self._catalog_event.description

    def _init_layer_properties(self):
        self.color = self._catalog_event._v_layer_color 

        if self._catalog_event._v_layer_title == self.DEFAULT_LAYER:
            self.layer = None
        else: 
            title = self._catalog_event._v_layer_title
            self.layer = title.rstrip(self.LAYER_SUFFIX)
        
    @property
    def shade_class(self):
        if self.shaded_row:
            return 'shade'
        else:
            return ''

    # date & time info: first line
    
    def _init_date_and_time_properties(self):    
        start_day  = self._catalog_event.startDate.strftime("%a, %b %e")
        start_time = self._format_time_of_day(self._catalog_event.startDate)

        end_day  = self._catalog_event.endDate.strftime("%a, %b %e")
        end_time = self._format_time_of_day(self._catalog_event.endDate)

        if start_day == end_day:
            self.first_line_day   = start_day
            self.first_line_time  = '%s - %s' % (start_time, end_time)
            self.second_line_time = ''
            self.second_line_day  = ''

        else:
            self.first_line_day   = start_day
            self.first_line_time  = '%s - ' % start_time
            self.second_line_day  = end_day
            self.second_line_time = end_time

    def _format_time_of_day(self, dt):
        ''' Format a time like "2pm" or "3:15pm". '''
        fmt = dt.strftime('%l:%M%p').lstrip(' ')
        time, ampm = fmt[:-2], fmt[-2:].lower()
        if time.endswith(':00'):
            time = time[:-3]
        return time + ampm

    
    @property
    def first_line_day_show_url(self):
        return '#'

    @property
    def second_line_day_show_url(self):
        return ''
