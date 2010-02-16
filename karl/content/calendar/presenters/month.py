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
import operator
import time
from karl.content.calendar.presenters.base import BasePresenter
from karl.content.calendar.presenters.base import BaseEvent
from karl.content.calendar.utils import BubblePainter
from karl.content.calendar.utils import MonthSkeleton
from karl.content.calendar.utils import next_month
from karl.content.calendar.utils import prior_month                   


class MonthViewPresenter(BasePresenter):
    name = 'month'

    def _initialize(self):
        monthname = calendar.month_name[self.focus_datetime.month]
        self.title = "%s %d" % (monthname, self.focus_datetime.year)
        self.feed_url = self.url_for('atom.xml')
        
        self._init_weeks_skeleton()
        self._init_day_indexes_from_weeks()
        
        self._init_prev_datetime()
        self._init_next_datetime()

        self._init_navigation()
        self._init_bubble_painter()

    def _init_weeks_skeleton(self):
        skeleton = MonthSkeleton(self.focus_datetime.year,
                                 self.focus_datetime.month)

        self.day_headings = skeleton.day_names

        weeks = skeleton.weeks
        nine_hours = datetime.timedelta(hours=9)
        for week in weeks:
            for d, dt in enumerate(week):
                # determine if this day is on the month in focus
                same_year  = (self.focus_datetime.year  == dt.year)
                same_month = (self.focus_datetime.month == dt.month)
                is_focus_month = (same_year and same_month)

                # determine if this day is today's date (now)
                same_year  = (self.now_datetime.year  == dt.year)
                same_month = (self.now_datetime.month == dt.month)
                same_day   = (self.now_datetime.day   == dt.day)
                is_today = (same_year and same_month and same_day)

                # url to add an event to this day
                day_at_9am = dt + nine_hours
                starts = time.mktime(day_at_9am.timetuple())
                add_event_url = self.url_for('add_calendarevent.html',
                                 query={'starts':int(starts)}) 

                # url to view this day
                format = '%s?year=%d&month=%d&day=%d'
                show_url = format % (self.url_for('day.html'),
                                     dt.year, dt.month, dt.day)  
                
                day = DayOnMonthView(dt.year, dt.month, dt.day,
                                     current_month=is_focus_month,
                                     current_day=is_today,
                                     add_event_url=add_event_url,
                                     show_day_url=show_url)

                week[d] = day
        self.weeks = weeks                                          

    def _init_day_indexes_from_weeks(self):
        md_index = {} 
        all_days = []

        for week in self.weeks:
            for day in week:
                md_index.setdefault(day.month, {})[day.day] = day
                all_days.append(day)

        self._idx_month_day = md_index
        self._all_days = all_days         

    def _init_prev_datetime(self):
        prior = prior_month(self.focus_datetime.year, 
                            self.focus_datetime.month)
        monthrange = calendar.monthrange(prior[0], prior[1])  
                                         
        if self.focus_datetime.day <= monthrange[1]:
            day = self.focus_datetime.day
        else:
            day = monthrange[1]    
            
        self.prev_datetime = datetime.datetime(prior[0], prior[1], day)

    def _init_next_datetime(self):
        next = next_month(self.focus_datetime.year, 
                          self.focus_datetime.month)
        monthrange = calendar.monthrange(next[0], next[1])

        if self.focus_datetime.day <= monthrange[1]:
            day = self.focus_datetime.day
        else:
            day = monthrange[1]

        self.next_datetime = datetime.datetime(next[0], next[1], day)        

    def _init_bubble_painter(self):
        self._bubble_painter = BubblePainter(self)
        
    def paint_events(self, events):
        by_start_date = operator.attrgetter('startDate')

        for event in sorted(events, key=by_start_date):
            if self._bubble_painter.should_paint_event(event):
                self._bubble_painter.paint_event(event)
            else:
                self._paint_event_without_bubble(event)
                 
        self._add_bubble_titles_to_successive_weeks()

    def _paint_event_without_bubble(self, event):
        days = self.days_in_range_of_event(event)

        for day in days:
            if None in day.event_slots:
                slot_index = day.event_slots.index(None)
                tpl_event = self.make_event_for_template(day, event)
                tpl_event.bubbled = False
                day.event_slots[slot_index] = tpl_event
            else:
                day.overflowed_events.append(event)

    def days_in_range_of_event(self, event):
        ''' Find all of the days (DayOnMonthView) that are affected
        by an event. '''
        days = []

        if event.startDate < self.first_moment:
            starts_at = self.first_moment
        else:
            starts_at = event.startDate
        
        if event.endDate > self.last_moment:
            ends_at = self.last_moment
        else:
            ends_at = event.endDate

        dt = starts_at
        one_day = datetime.timedelta(days=1)
        while dt < ends_at:                             
            days.append(
                self._idx_month_day[dt.month][dt.day]       
            )
            dt += one_day

        return days

    def _add_bubble_titles_to_successive_weeks(self):
        for week in self.weeks:
            leftmost_day = week[0]

            for event in leftmost_day.event_slots:
                if event and event.bubbled:
                    event.bubble_title = event.title                 

    def make_event_for_template(self, day, catalog_event):
        tpl_event = EventOnMonthView(
                        day, catalog_event,
                        show_url=self.url_for(context=catalog_event)
                    )
        return tpl_event

    @property    
    def first_moment(self):                      
        day = self.weeks[0][0]
        return datetime.datetime(day.year, day.month, day.day) 

    @property    
    def last_moment(self):
        day = self.weeks[-1][-1]
        return datetime.datetime(day.year, day.month, day.day, 23, 59, 59)

    @property
    def template_filename(self):
        return 'templates/calendar_month.pt'


class DayOnMonthView(object):   
    def __init__(self, year, month, day, 
                 current_month=True, current_day=False, 
                 add_event_url='#', show_day_url='#'):
        self.year = year
        self.month = month
        self.day = day
        self.current_month = current_month
        self.current_day = current_day
        self.add_event_url = add_event_url
        self.show_day_url = show_day_url

        self.event_slots = [None]*5

        self.overflowed_events = []

        self.first_moment = datetime.datetime(year, month, day,  0,  0,  0)
        self.last_moment  = datetime.datetime(year, month, day, 23, 59, 59)

    @property
    def events(self):
        events = []
        for possible_event in self.event_slots:
            if possible_event is not None:
                events.append(possible_event)
        return events


class EventOnMonthView(BaseEvent):
    def __init__(self, day, catalog_event, 
                 show_url='#', edit_url='#', delete_url='#'): 

        BaseEvent.__init__(self, day, catalog_event, 
                       show_url, edit_url, delete_url)         
        
        self.bubbled = False
        self.rounding_class = 'center'
        self.bubble_title = '&nbsp;'
        
    @property
    def type_class(self):
        if self.bubbled:
            return 'all_day'
        else:
            return 'at_time'

