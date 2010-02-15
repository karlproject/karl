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
from karl.content.calendar.utils import is_all_day_event

class ListViewPresenter(BasePresenter):
    name = 'list'
    
    def _initialize(self):               
        monthname = calendar.month_name[self.focus_datetime.month]
        self.title = "Upcoming Events"
        self.feed_url = self.url_for('atom.xml')  

        self.events = []
        self.has_more = False
        self.per_page = 20
        self.page = 1
        
    def _init_navigation(self):
        nav = Navigation(self)

        base_url = '%s?year=%d&month=%d&day=%d&per_page=%d' % (
                     self.url_for(self.name + '.html'),
                     self.focus_datetime.year,
                     self.focus_datetime.month,
                     self.focus_datetime.day,
                     self.per_page)      

        # today_url
        if self.page == 1:
            nav.today_url = None
        else:
            nav.today_url = base_url + "&page=1"

        # prev_url
        if self.page == 1:
            nav.prev_url = None
        else:                                                
            prev_page = self.page - 1
            nav.prev_url = base_url + ("&page=%d" % prev_page)

        # next_url
        if not self.has_more:
            nav.next_url = None
        else:
            next_page = self.page + 1
            nav.next_url = base_url + ("&page=%d" % next_page)
            
        self.navigation = nav    

    
    def paint_events(self, events):
        for event in events:
            format = '%s?year=%d&month=%d&day=%d'
            dt = event.startDate
            start_day_url = format % (self.url_for('day.html'),
                                      dt.year, dt.month, dt.day)

            dt = event.endDate
            end_day_url = format % (self.url_for('day.html'),
                                    dt.year, dt.month, dt.day)
            
            listed_event = Event(catalog_event=event,
                                 show_url=self.url_for(context=event),
                                 start_day_url=start_day_url,
                                 end_day_url=end_day_url
                           )
            self.events.append(listed_event)          

    def paint_paginated_events(self, events, has_more, per_page, page):
        self.paint_events(events)
        self.has_more = has_more                     
        self.per_page = per_page
        self.page = page
        
        self._init_navigation()    
            

    @property
    def template_filename(self):
        return 'templates/calendar_list.pt'


class Event(object):
    DEFAULT_LAYER = '*default*'

    def __init__(self, catalog_event, 
                 show_url='#', edit_url='#', delete_url='#',
                 start_day_url='#', end_day_url='#'):

        self._catalog_event = catalog_event # ICalendarEvent                               

        self.show_url = show_url
        self.edit_url = edit_url
        self.delete_url = delete_url
        self.start_day_url = start_day_url
        self.end_day_url = end_day_url

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
            self.layer = title.rstrip(' layer')
        
    def _init_date_and_time_properties(self):    
        start_day  = self._catalog_event.startDate.strftime("%a, %b %e")
        start_time = self._format_time_of_day(self._catalog_event.startDate)

        end_day  = self._catalog_event.endDate.strftime("%a, %b %e")
        end_time = self._format_time_of_day(self._catalog_event.endDate)

        if start_day == end_day:
            self.first_line_day   = start_day
            self.first_line_time  = '%s - %s' % (start_time, end_time)
            self.second_line_day  = ''
            self.second_line_time = ''
        else:
            if is_all_day_event(self._catalog_event):
                one_day = datetime.timedelta(days=1)
                ends_at = self._catalog_event.endDate - one_day 
                end_day = ends_at.strftime("%a, %b %e")

                self.first_line_day   = start_day
                self.first_line_time  = 'all-day'
                self.second_line_day  = end_day
                self.second_line_time = ''
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
