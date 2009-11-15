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

        self.days = []

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

        nav.prev_href = format % (url, self.prior_month.year, 
                                       self.prior_month.month,
                                       self.prior_month.day)
        nav.next_href = format % (url, self.next_month.year, 
                                       self.next_month.month,
                                       self.prior_month.day)

        nav.today_href = format % (url, self.now_datetime.year,
                                        self.now_datetime.month,
                                        self.now_datetime.day)
        self.navigation = nav

    def paint_events(self, events):
        days_events = self._make_days_events_dict(events)

        self.days = []     
        for day_num in sorted(days_events.keys()):
            # url to view this day
            format = '%s?year=%d&month=%d&day=%d'
            url = format % (self.url_for('day.html'),
                            self.focus_datetime.year, 
                            self.focus_datetime.month, day_num)  

            day = DayOnListView(self.focus_datetime.year,
                                self.focus_datetime.month,
                                day_num,
                                show_day_url=url)
            self.days.append(day)

            for start_unixtime in sorted(days_events[day_num].keys()):
                for event in days_events[day_num][start_unixtime]:
                    listed_event = Event(
                                        day=day, catalog_event=event,
                                        show_url=self.url_for(context=event)
                                   )
                    day.events.append(listed_event)

        shaded = True
        for day in self.days:
            day.shaded_row = shaded
            shaded = not(shaded)        
        
    def _make_days_events_dict(self, events):
        ''' 
        days_events = {day_num: {start_unixtime: [event, event], 
                                 start_unixtime: [event, event]}, 
                       day_num: ...}
        '''
        days_events = {}
        for event in events:
            for day_num in self._day_range_of_event(event):
                if not days_events.has_key(day_num):
                    days_events[day_num] = {}

                if event.startDate < self.first_moment:
                    starts_at = self.first_moment
                else:
                    starts_at = event.startDate
                unixtime = time.mktime(starts_at.timetuple())
                
                if not days_events[day_num].has_key(unixtime):
                    days_events[day_num][unixtime] = []
                
                days_events[day_num][unixtime].append(event)                    
        return days_events        

    def _day_range_of_event(self, event):
        ''' Given a catalog event, return a range of days in this
        month that the event falls on. '''

        if event.startDate < self.first_moment:
            first_day_of_event = 1
        else:
            first_day_of_event = event.startDate.day

        if event.endDate > self.last_moment:
            last_day_of_event = self.last_moment.day
        else:
            last_day_of_event = event.endDate.day
        
        return range(first_day_of_event, last_day_of_event + 1)        

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


class DayOnListView(object):
    def __init__(self, year, month, day, shaded_row=False, show_day_url='#'):
        self.year = year
        self.month = month
        self.day = day
        self.events = []
        self.shaded_row = shaded_row
        self.show_day_url = show_day_url

    @property
    def first_moment(self):
        return datetime.datetime(self.year, self.month, self.day, 0, 0, 0)
        
    @property
    def last_moment(self):
        return datetime.datetime(self.year, self.month, self.day, 23, 59, 59)

    @property 
    def day_in_words(self):
        return self.first_moment.strftime("%a, %b %e")
        
    @property
    def shade_class(self):
        css_class = ''
        if self.shaded_row:
            css_class = 'shade'
        return css_class


class Event(BaseEvent):
    pass

