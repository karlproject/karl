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
