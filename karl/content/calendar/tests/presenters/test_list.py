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

import unittest
import sys
import datetime
import time
import calendar
from karl.content.calendar.tests.presenters.test_base import dummy_url_for
from karl.content.calendar.tests.presenters.test_base import DummyCatalogEvent


class ListViewPresenterTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    def test_has_a_name_of_list(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.name, 'list') 

    def test_title_is_month_name_and_year(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.title, 'August 2009')

    # first & last moment

    def test_computes_first_moment_within_current_month_only(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        expected = datetime.datetime(2009, 8, 1, 0, 0, 0)
        self.assertEqual(presenter.first_moment, expected)

    def test_computes_last_moment_within_current_month_only(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        expected = datetime.datetime(2009, 8, 31, 23, 59, 59)
        self.assertEqual(presenter.last_moment, expected)

    # prior & next month
    
    def test_computes_prior_month_preserving_day_if_in_range(self):
        focus_at = datetime.datetime(2009, 8, 31)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.prior_month.year, 2009)
        self.assertEqual(presenter.prior_month.month, 7)
        self.assertEqual(presenter.prior_month.day, 31)
        
    def test_computes_prior_month_adjusting_out_of_range_day(self):
        focus_at = datetime.datetime(2009, 7, 31) # 31 not in june
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.prior_month.year, 2009)
        self.assertEqual(presenter.prior_month.month, 6)
        self.assertEqual(presenter.prior_month.day, 30) # adjusted

    def test_computes_next_month_preserving_day_if_in_range(self):
        focus_at = datetime.datetime(2009, 7, 31) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.next_month.year, 2009)
        self.assertEqual(presenter.next_month.month, 8)
        self.assertEqual(presenter.next_month.day, 31) 

    def test_computes_next_month_adjusting_out_of_range_day(self):
        focus_at = datetime.datetime(2009, 8, 31) # 31 not in september
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.next_month.year, 2009)
        self.assertEqual(presenter.next_month.month, 9)
        self.assertEqual(presenter.next_month.day, 30) # adjusted

    # left navigation
    
    def test_sets_navigation_today_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.today_href.endswith(
            'list.html?year=2009&month=8&day=26'
        ))

    def test_sets_navigation_prev_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.prev_href.endswith(
            'list.html?year=2009&month=7&day=1'
        ))

    def test_sets_navigation_next_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.next_href.endswith(
            'list.html?year=2009&month=9&day=1'
        ))

    # paint_events 
 
    def test_paint_events_paints_each_day_with_events_in_order(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        
        events = [                                                                       
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 8, 7, 14, 30,  0),
                endDate=  datetime.datetime(2009, 8, 7, 16,  0,  0), 
                title='Finish design proposal' # aug 7, 2:30pm - 4pm
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 8, 7, 0,  0,  0),
                endDate=  datetime.datetime(2009, 8, 7, 23, 59, 59),
                title='Summer vacation' # aug 7, all-day
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 8, 15, 12,  0, 0),
                endDate=  datetime.datetime(2009, 8, 15, 14, 30, 0), 
                title='Team meeting' # aug 15, 12pm - 2:30pm
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 8, 7, 10, 0,  0),
                endDate=  datetime.datetime(2009, 8, 7, 11, 0, 0), 
                title='Cable install' # aug 7, 10am - 11am
            ),
        ]

        presenter.paint_events(events)
        self.assertEqual(len(presenter.days), 2)
        
        friday = presenter.days[0]
        self.assertEqual(friday.day_in_words, 'Fri, Aug  7')

        self.assertEqual(friday.events[0].time_in_words, 'all-day')
        self.assertEqual(friday.events[0].title, 'Summer vacation')

        self.assertEqual(friday.events[1].time_in_words, '10am - 11am')
        self.assertEqual(friday.events[1].title, 'Cable install')
        
        self.assertEqual(friday.events[2].time_in_words, '2:30pm - 4pm')
        self.assertEqual(friday.events[2].title, 'Finish design proposal')

        saturday = presenter.days[1]
        self.assertEqual(saturday.day_in_words, 'Sat, Aug 15')

        self.assertEqual(saturday.events[0].time_in_words, '12pm - 2:30pm')
        self.assertEqual(saturday.events[0].title, 'Team meeting')
    
    def test_paint_events_shades_every_other_row(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)         
        
        events = [                                                                       
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 1, 1, 0, 0), # sep 1
                endDate=  datetime.datetime(2009, 9, 1, 2, 0, 0)
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 3, 1, 0, 0), # sep 3
                endDate=  datetime.datetime(2009, 9, 3, 2, 0, 0)
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 5, 1, 0, 0), # sep 5
                endDate=  datetime.datetime(2009, 9, 5, 2, 0, 0)
            )
        ]

        presenter.paint_events(events)
        self.assertTrue(presenter.days[0].shaded_row)
        self.assertFalse(presenter.days[1].shaded_row)
        self.assertTrue(presenter.days[2].shaded_row)

    # _make_days_events_dict
    
    def test__make_days_events_dict_uses_day_numbers_as_outer_keys(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)         
        
        events = [                                                                       
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 1, 1, 0, 0), # sep 1
                endDate=  datetime.datetime(2009, 9, 1, 2, 0, 0)
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 3, 1, 0, 0), # sep 3
                endDate=  datetime.datetime(2009, 9, 3, 2, 0, 0)
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 5, 1, 0, 0), # sep 5
                endDate=  datetime.datetime(2009, 9, 5, 2, 0, 0)
            )
        ]

        days_events = presenter._make_days_events_dict(events)
        self.assertEqual(sorted(days_events.keys()), [1,3,5]) # sep 1,3,5

    def test__make_days_events_dict_spans_event_across_days(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)         
        
        events = [                                                                       
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 1, 1, 0, 0), # sep 1-5
                endDate=  datetime.datetime(2009, 9, 5, 2, 0, 0)
            ),
        ]

        days_events = presenter._make_days_events_dict(events)
        self.assertEqual(sorted(days_events.keys()), [1,2,3,4,5]) # sep 1-5

    def test__make_days_events_dict_inner_keys_are_start_unixtime(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)         
        
        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 1, 1, 0, 0),
                    endDate=  datetime.datetime(2009, 9, 1, 2, 0, 0)
                )
        events = [ event ]

        days_events = presenter._make_days_events_dict(events)
        
        unixtime = time.mktime(events[0].startDate.timetuple())           
        self.assertEqual(days_events[1][unixtime], events)

    def test__make_days_events_dict_constraints_start_time_within_day(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)         
        
        events = [
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 8, 31, 0, 0, 0), # aug 31
                endDate=  datetime.datetime(2009, 9, 1,  2, 0, 0)  # sep 1
            )
        ]

        days_events = presenter._make_days_events_dict(events)

        unixtime = time.mktime(presenter.first_moment.timetuple())              
        self.assertEqual(days_events[1][unixtime], events)

       
    def test__make_days_events_dict_handles_multiple_events_at_time(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)         
        
        events = [                                                                       
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 7, 1, 0, 0), # sep 7
                endDate=  datetime.datetime(2009, 9, 7, 2, 0, 0)
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 7, 1, 0, 0), # sep 7
                endDate=  datetime.datetime(2009, 9, 7, 2, 0, 0)
            ),
            DummyCatalogEvent(
                startDate=datetime.datetime(2009, 9, 7, 1, 0, 0), # sep 7
                endDate=  datetime.datetime(2009, 9, 7, 2, 0, 0)
            )
        ]  
        
        days_events = presenter._make_days_events_dict(events) 
        self.assertEqual(len(days_events.keys()), 1)
        
        unixtime = time.mktime(events[0].startDate.timetuple())
        self.assertEqual(len(days_events[7][unixtime]), 3)


   # _day_range_of_event
    
    def test__day_range_of_event_computes_days_for_event(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        starts_at = datetime.datetime(2009, 9, 3)
        ends_at   = datetime.datetime(2009, 9, 5)
        event = DummyCatalogEvent(startDate=starts_at, endDate=ends_at)

        expected = range(3, 5 + 1) # sep 3-5
        self.assertEqual(presenter._day_range_of_event(event), expected)
    
    
    def test__day_range_of_event_constrains_limits_of_month_displayed(self):
        focus_at = datetime.datetime(2009, 9, 1) 
        now_at   = datetime.datetime(2009, 9, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        starts_at = datetime.datetime(2009, 8, 26) # less than 9/1
        ends_at   = datetime.datetime(2009, 10, 3) # more than 9/30
        event = DummyCatalogEvent(startDate=starts_at, endDate=ends_at)

        expected = range(1, 30 + 1) # sep 1-30
        self.assertEqual(presenter._day_range_of_event(event), expected)
        
    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.list import ListViewPresenter
        return ListViewPresenter(*args, **kargs)


class DayOnListViewTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)
        
    # year, month day
    
    def test_assigns_year_month_day(self):
        day = self._makeOne(2009, 9, 7)
        self.assertEqual(day.year,  2009)
        self.assertEqual(day.month, 9)
        self.assertEqual(day.day,   7)
        
    # shaded_row
    
    def test_shaded_row_defaults_to_false(self):
        day = self._makeOne(2009, 9, 7)
        self.assertFalse(day.shaded_row)
    
    def test_shaded_row_can_be_assigned_in_ctor(self):
        day = self._makeOne(2009, 9, 7, shaded_row=True)
        self.assertTrue(day.shaded_row)

    # first and last moment
    
    def test_computes_first_moment_at_beginning_of_day(self):
        day = self._makeOne(2009, 9, 7) 

        self.assertEqual(day.first_moment.year,  2009)
        self.assertEqual(day.first_moment.month, 9)
        self.assertEqual(day.first_moment.day,   7)
        self.assertEqual(day.first_moment.hour,   0)
        self.assertEqual(day.first_moment.minute, 0)
        self.assertEqual(day.first_moment.second, 0)           
                   
    def test_computes_first_moment_at_ending_of_day(self):
        day = self._makeOne(2009, 9, 7) 

        self.assertEqual(day.last_moment.year,   2009)
        self.assertEqual(day.last_moment.month,  9)
        self.assertEqual(day.last_moment.day,    7)
        self.assertEqual(day.last_moment.hour,   23)
        self.assertEqual(day.last_moment.minute, 59)
        self.assertEqual(day.last_moment.second, 59)           

    # day_in_words
    
    def test_day_in_words_is_weekday_then_month_and_day(self):
        day = self._makeOne(2009, 9, 7) 

        weekday  = day.first_moment.strftime('%a')
        month    = day.first_moment.strftime('%b')
        expected = "%s, %s  %d" % (weekday, month, 7)

        self.assertEqual(day.day_in_words, expected)
 
    # shade_class
    
    def test_shaded_class_is_shade_when_shaded_row_is_true(self):
        day = self._makeOne(2009, 9, 7)
        day.shaded_row = True
        
        self.assertEqual(day.shade_class, 'shade')

    def test_shaded_class_is_empty_when_shaded_row_is_false(self):
        day = self._makeOne(2009, 9, 7)
        day.shaded_row = False
        
        self.assertEqual(day.shade_class, '')
    
    # helpers
    
    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.list import DayOnListView
        return DayOnListView(*args, **kargs)
