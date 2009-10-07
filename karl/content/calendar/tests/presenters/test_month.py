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
from karl.content.calendar.tests.presenters.test_base import DummyDayWithEvents


class MonthViewPresenterTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    def test_has_a_name_of_month(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now() 

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.name, 'month') 

    def test_title_is_month_name_and_year(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.title, 'August 2009')

    def test_has_feed_href_url(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertTrue(presenter.feed_href.endswith('atom.xml'))

    # first & last moment

    def test_computes_first_moment_into_prior_month(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        expected = datetime.datetime(2009, 07, 26)
        self.assertEqual(presenter.first_moment, expected)

    def test_computes_last_moment_into_next_month(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        expected = datetime.datetime(2009, 9, 5, 23, 59, 59)
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
            'month.html?year=2009&month=8&day=26'
        ))

    def test_sets_navigation_prev_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.prev_href.endswith(
            'month.html?year=2009&month=7&day=1'
        ))

    def test_sets_navigation_next_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.next_href.endswith(
            'month.html?year=2009&month=9&day=1'
        ))

    # canvas

    def test_sets_day_headings_for_template_to_show_above_calendar(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(len(presenter.day_headings), 7)
        
        sunday = calendar.day_name[ calendar.firstweekday() ]
        self.assertEqual(presenter.day_headings[0], sunday)

    def test_has_weeks_where_each_week_is_a_list_of_days(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        
        weeks = presenter.weeks
        self.assertEqual(weeks[0][0].month,  7)  # sun jul 26
        self.assertEqual(weeks[0][0].day,   26)
        self.assertEqual(weeks[5][6].month,  9)  # sat sep 5
        self.assertEqual(weeks[5][6].day,    5)
    
    def test_each_day_of_the_week_is_initialized_to_no_events(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        
        for week in presenter.weeks:
            for day in week:
                self.assertEqual(day.events, [])

    def test_each_day_of_week_is_given_an_add_event_url(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        for week in presenter.weeks:
            for day in week:
                url = presenter.url_for('add_calendarevent.html')
                self.assertEqual(day.add_event_url, url)

    def test_each_day_of_week_is_given_a_show_day_url(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        for week in presenter.weeks:
            for day in week:
                format = '%s?year=%d&month=%d&day=%d'
                url = format % (presenter.url_for('day.html'),
                                day.year, day.month, day.day)   
                self.assertEqual(day.show_day_url, url)

    # _find_contiguous_slot_across_days
    
    def test__find_contiguous_slot_across_days_gets_first_available(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        days = [ DummyDayWithEvents(), DummyDayWithEvents() ]

        index = presenter._find_contiguous_slot_across_days(days)
        self.assertEqual(index, 0)
    
    def test__find_contiguous_slot_across_days_searches_top_down(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        days = [ DummyDayWithEvents(), DummyDayWithEvents() ]
        days[0].event_slots[0] = DummyCatalogEvent()
        days[1].event_slots[1] = DummyCatalogEvent()

        index = presenter._find_contiguous_slot_across_days(days)
        self.assertEqual(index, 2)
        
    def test__find_contiguous_slot_across_days_may_find_None(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        days = [DummyDayWithEvents]*2
        days[0].event_slots = [DummyCatalogEvent()]*5

        index = presenter._find_contiguous_slot_across_days(days)
        self.assert_(index is None)

    # _should_event_be_bubbled
    
    def test__should_event_be_bubbled_no_for_event_less_than_whole_day(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 14,  1,  0,  0),
                    endDate  =datetime.datetime(2009, 9, 14,  2,  0,  0)
                )        
        self.assertFalse(presenter._should_event_be_bubbled(event))
    
    def test__should_event_be_bubbled_yes_for_whole_single_day(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 14,  0,  0,  0),
                    endDate  =datetime.datetime(2009, 9, 14, 23, 59, 59)
                )        
        self.assertTrue(presenter._should_event_be_bubbled(event))

    def test__should_event_be_bubbled_yes_for_spans_of_multiple_days(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 14,  0,  0,  0),
                    endDate  =datetime.datetime(2009, 9, 16,  0,  0,  0)
                )        
        self.assertTrue(presenter._should_event_be_bubbled(event))

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.month import MonthViewPresenter
        return MonthViewPresenter(*args, **kargs)


class DayOnMonthViewTests(unittest.TestCase):

    # year, month, day

    def test_assigns_year_month_day(self):
        day = self._makeOne(2009, 9, 5)
        self.assertEqual(day.year,  2009)
        self.assertEqual(day.month, 9)
        self.assertEqual(day.day,   5)

    # current_month

    def test_current_month_defaults_to_True(self):
        day = self._makeOne(2009, 9, 5)
        self.assertTrue(day.current_month)

    def test_assigns_current_month(self):
        day = self._makeOne(2009, 9, 5, current_month=True)
        self.assertTrue(day.current_month)

    # current_day

    def test_current_day_defaults_to_True(self):
        day = self._makeOne(2009, 9, 5)
        self.assertFalse(day.current_day)

    def test_assigns_current_day(self):
        day = self._makeOne(2009, 9, 5, current_day=True)
        self.assertTrue(day.current_month)

    # add_event_url

    def test_add_event_url_defaults_to_pound(self):
        day = self._makeOne(2009, 9, 5)
        self.assertEqual(day.add_event_url, '#')

    def test_assigns_add_event_url(self):
        url = 'http://somewhere'
        day = self._makeOne(2009, 9, 5, add_event_url=url)
        self.assertEqual(day.add_event_url, url)

    # show_day_url

    def test_show_day_url_defaults_to_pound(self):
        day = self._makeOne(2009, 9, 5)
        self.assertEqual(day.show_day_url, '#')

    def test_assigns_show_day_url_url(self):
        url = 'http://somewhere'
        day = self._makeOne(2009, 9, 5, show_day_url=url)
        self.assertEqual(day.show_day_url, url)

    # events

    def test_assigns_events(self):
        dummy_event = self

        day = self._makeOne(2009, 9, 5)
        day.event_slots[0] = dummy_event
        day.event_slots[1] = dummy_event

        events = [dummy_event, dummy_event]
        self.assertEqual(day.events, events)
   
    # day_label_class
    
    def test_day_label_class_is_empty_for_current_month(self):
        day = self._makeOne(2009, 9, 5, current_month=True)
        self.assertEqual(day.day_label_class, '')

    def test_day_label_class_is_faded_for_other_months(self):
        day = self._makeOne(2009, 9, 5, current_month=False)
        self.assertEqual(day.day_label_class, 'faded')
   
    # today_class
    
    def test_today_class_is_today_for_current_day(self):
        day = self._makeOne(2009, 9, 5, current_day=True)
        self.assertEqual(day.today_class, 'today')
        
    def test_today_class_is_empty_for_other_days(self):
        day = self._makeOne(2009, 9, 5, current_day=False)
        self.assertEqual(day.today_class, '')

    # first and last moment
    
    def test_first_moment_is_beginning_of_day(self):
        day = self._makeOne(2009, 9, 5)         
        expected = datetime.datetime(2009, 9, 5, 0, 0, 0)
        self.assertEqual(day.first_moment, expected)

    def test_first_moment_is_ending_of_day(self):
        day = self._makeOne(2009, 9, 5)         
        expected = datetime.datetime(2009, 9, 5, 23, 59, 59)
        self.assertEqual(day.last_moment, expected)

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.month import DayOnMonthView
        return DayOnMonthView(*args, **kargs)
