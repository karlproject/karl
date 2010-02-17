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


def prior_month(year, month):
    if month == 1:
        return (year - 1, 12)
    return (year, month - 1)

def next_month(year, month):
    if month == 12:
        return (year + 1, 1)
    return (year, month + 1)

def is_all_day_event(event):
    hhmmss = (event.startDate.hour,   event.endDate.hour,
              event.startDate.minute, event.endDate.minute,
              event.startDate.second, event.endDate.second)
    return hhmmss == (0, 0, 0, 0, 0, 0)


class MonthSkeleton(object):
    '''
    Builds a calendar skeleton of the same list structure as
    ``calendar.monthcalendar``.  Unlike that function, each element in the
    lists is a ``datetime`` rather than an integer.
    
    Days in the skeleton outside of the current month are also properly
    inserted and available as ``datetime``, rather than ``0``.
    '''
    def __init__(self, year, month):
        self.year  = year
        self.month = month
        
        self._init_headings()
        self._init_monthcalender()
        self._init_days_from_prior_month()
        self._init_days_from_next_month()
    
    def _init_headings(self):
        firstday = calendar.firstweekday()

        day_names = list(calendar.day_name)
        self.day_names = day_names[firstday:] + day_names[:firstday]

        day_abbrs = list(calendar.day_abbr)
        self.day_abbrs = day_abbrs[firstday:] + day_names[:firstday]

    def _init_monthcalender(self):
        self.weeks = calendar.monthcalendar(self.year, self.month)

        for w, week in enumerate(self.weeks):
            for d, day in enumerate(week):
                if day != 0:
                    week[d] = self.make_day(self.year, self.month, day)
 
    def _init_days_from_prior_month(self):
        if 0 in self.weeks[0]:
            p_year, p_month = prior_month(self.year, self.month)

            last_day = calendar.monthrange(p_year, p_month)[1]
            days_of_prior_month = range(1, last_day + 1)
    
            zeroed_days_len = self.weeks[0].count(0)
            days = days_of_prior_month[-zeroed_days_len:]
        
            replacement_days = []
            for day in days:            
                replacement_days.append(
                    self.make_day(p_year, p_month, day)
                )                         

            self.weeks[0][0:zeroed_days_len] = replacement_days

    def _init_days_from_next_month(self):
        if 0 in self.weeks[-1]:
            n_year, n_month = next_month(self.year, self.month)

            zeroed_days_len = self.weeks[-1].count(0)
            days = range(1, zeroed_days_len + 1)
            
            replacement_days = []
            for day in days:
                replacement_days.append(
                    datetime.datetime(n_year, n_month, day)
                )
    
            first_zero = self.weeks[-1].index(0)
            last_zero  = first_zero + zeroed_days_len
            self.weeks[-1][first_zero:last_zero] = replacement_days

    def make_day(self, year, month, day):
        return datetime.datetime(year, month, day) 


class BubblePainter:
    def __init__(self, presenter, add_new_slots=False):
        self._presenter     = presenter 
        self._add_new_slots = add_new_slots

    def paint_event(self, event):
        days = self._presenter.days_in_range_of_event(event)
        slot_index = self._find_contiguous_slot_across_days(days)
        
        if slot_index is None:
            for day in days:
                day.overflowed_events.append(event)
            return
                                    
        days_len = len(days)
        for i, day in enumerate(days):
            tpl_event = self._presenter.make_event_for_template(day, event)
            day.event_slots[slot_index] = tpl_event

            tpl_event.bubbled = True

            # bubble rounded corners
            if i == 0:
                if days_len == 1:
                    tpl_event.rounding_class = 'full'
                else:
                    tpl_event.rounding_class = 'left'

                if day is self._presenter.all_days[0]:
                    first = self._presenter.all_days[0].first_moment
                    if event.startDate < first:
                        tpl_event.rounding_class = 'center'

            elif i == (days_len - 1):
                tpl_event.rounding_class = 'right'

                if day is self._presenter.all_days[-1]:
                    if event.endDate > self._presenter.last_moment:
                        tpl_event.rounding_class = 'center'
                       
            # bubble title
            if i == 0:
                tpl_event.bubble_title = tpl_event.title

    def should_paint_event(self, event):
        ''' An event should be bubbled if it spans multiple days or
        if it takes up an entire single day. '''
        starts_dt = event.startDate
        ends_dt   = event.endDate
    
        starts_ymd = (starts_dt.year, starts_dt.month, starts_dt.day)
        ends_ymd   = (ends_dt.year,   ends_dt.month,   ends_dt.day)
    
        should_bubble = False
        if (starts_ymd != ends_ymd): 
            should_bubble = True # event spans multiple days
        else:
            starts_hms = (starts_dt.hour, starts_dt.minute, starts_dt.second)
            ends_hms   = (ends_dt.hour,   ends_dt.minute,   ends_dt.second)
        
            if (starts_hms == (0, 0, 0)) and (ends_hms == (23, 59, 59)):
                should_bubble = True # event is an entire single day
        return should_bubble

    def _find_contiguous_slot_across_days(self, list_of_days):                
        ''' Find the index to a slot that is available in every day of 
        the list, or None if not possible. '''
        index_of_available_slot = None

        if list_of_days and list_of_days[0].event_slots:
            num_days          = len(list_of_days)
            num_slots_per_day = len(list_of_days[0].event_slots)

            for slot in range(0, num_slots_per_day):  
                slot_across_days = []

                for day in list_of_days:  
                    slot_across_days.append(day.event_slots[slot])

                if slot_across_days.count(None) == num_days:
                    index_of_available_slot = slot
                    break

        if (index_of_available_slot is None) and (self._add_new_slots):
            for day in list_of_days:
                day.event_slots.append(None)
            index_of_available_slot = len(list_of_days[0].event_slots) - 1
         
        return index_of_available_slot
