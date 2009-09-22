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
from karl.content.newcalendar.presenters.base import BasePresenter
from karl.content.newcalendar.presenters.base import BaseEvent
from karl.content.newcalendar.navigation import Navigation
from karl.content.newcalendar.utils import next_month
from karl.content.newcalendar.utils import prior_month


class DayViewPresenter(BasePresenter):
    name = 'day'
    
    def _initialize(self):
        self._init_title()
        self.feed_href = self.url_for('atom.xml')  

        self._init_prior_day()
        self._init_next_day()
        self._init_navigation()
        
        self._init_hour_labels()
        self._init_time_slots()

    def _init_title(self):
        day_num = calendar.weekday(self.focus_datetime.year,
                                   self.focus_datetime.month,
                                   self.focus_datetime.day)
        day_name = calendar.day_name[day_num]                                   

        self.title = "%s %d/%d" % (day_name, 
                                   self.focus_datetime.month,
                                   self.focus_datetime.day)

        self.title_year = self.focus_datetime.year

    def _init_prior_day(self):
        minus_one  = self.focus_datetime.day - 1
        
        if (minus_one < 1):
            year, month = prior_month(self.focus_datetime.year,
                                      self.focus_datetime.month) 
            day = calendar.monthrange(year, month)[1]                                       
        else:
            year  = self.focus_datetime.year
            month = self.focus_datetime.month
            day   = minus_one

        self.prior_day = datetime.datetime(year, month, day)
 
    def _init_next_day(self):
        last_day = calendar.monthrange(self.focus_datetime.year,
                                       self.focus_datetime.month)[1]

        plus_one = self.focus_datetime.day + 1
        
        if (plus_one > last_day):
            year, month = next_month(self.focus_datetime.year,
                                     self.focus_datetime.month)
            day = 1
        else:
            year  = self.focus_datetime.year
            month = self.focus_datetime.month
            day   = plus_one

        self.next_day = datetime.datetime(year, month, day)            

    def _init_navigation(self):
        nav = Navigation(self)

        # left side
        format = '%s?year=%d&month=%d&day=%d'
        url = self.url_for('newday.html')

        nav.prev_href = format % (url, self.prior_day.year, 
                                       self.prior_day.month,
                                       self.prior_day.day)
        nav.next_href = format % (url, self.next_day.year, 
                                       self.next_day.month,
                                       self.next_day.day)

        nav.today_href = format % (url, self.now_datetime.year,
                                        self.now_datetime.month,
                                        self.now_datetime.day)
        self.navigation = nav

    def _init_hour_labels(self):
        self.hour_labels = []
        for hour in range(0, 24):
            if hour == 0:
                label = '12 AM'
            elif hour == 12:
                label = '12 PM'
            elif hour < 12:
                label = '%d AM' % hour
            else:
                label = '%d PM' % (hour - 12)
            self.hour_labels.append(label)

    def _init_time_slots(self):
        self.half_hour_slots = []
        for i in range(0, 48):
           if (i < 16) or (i > 35):
               is_shaded = True
           else:
               is_shaded = False

           if i % 2:
               is_half_hour = True
           else:
               is_half_hour = False
           
           slot = TimeSlot(shaded_row=is_shaded, 
                           is_half_hour=is_half_hour)
           self.half_hour_slots.append(slot)

    def paint_events(self, events):
        return

    @property
    def first_moment(self):
        return datetime.datetime(self.focus_datetime.year, 
                                 self.focus_datetime.month, 
                                 self.focus_datetime.day, 
                                 0, 0, 0)
    
    @property
    def last_moment(self):
        return datetime.datetime(self.focus_datetime.year, 
                                 self.focus_datetime.month, 
                                 self.focus_datetime.day, 
                                 23, 59, 59)

    @property
    def template_filename(self):
        return 'templates/newcalendar_day.pt'


class TimeSlot(object):
    def __init__(self, shaded_row=False, is_half_hour=False):
        self.shaded_row   = shaded_row
        self.is_half_hour = is_half_hour
    
    @property
    def shade_class(self):
        if self.shaded_row:
            return 'shade'
        else:
            return ''
    
    @property
    def hour_class(self):
        if self.is_half_hour:
            return 'cal_half_hour'
        else:
            return 'cal_hour'    
