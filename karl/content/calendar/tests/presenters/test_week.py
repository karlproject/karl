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

 
class WeekViewPresenterTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    def test_has_a_title_of_week_of_day_name_and_number(self):
        focus_at = datetime.datetime(2009, 9, 2)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.title, 'Week of Wednesday 9/2')

    def test_has_a_feed_url(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assert_(presenter.feed_url.startswith('http'))

    # first & last moment

    def test_computes_first_moment_at_first_day_of_week(self):
        focus_at = datetime.datetime(2009, 9, 2)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.first_moment.year,   2009)
        self.assertEqual(presenter.first_moment.month,  8)
        self.assertEqual(presenter.first_moment.day,    30)
        self.assertEqual(presenter.first_moment.hour,   0)
        self.assertEqual(presenter.first_moment.minute, 0)
        self.assertEqual(presenter.first_moment.second, 0)

    def test_computes_last_moment_at_last_day_of_week(self):
        focus_at = datetime.datetime(2009, 9, 2)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.last_moment.year,   2009)
        self.assertEqual(presenter.last_moment.month,  9)
        self.assertEqual(presenter.last_moment.day,    5)
        self.assertEqual(presenter.last_moment.hour,   23)
        self.assertEqual(presenter.last_moment.minute, 59)
        self.assertEqual(presenter.last_moment.second, 59)

    def test_computes_first_moment_properly_at_midweek(self):
        focus_at = datetime.datetime(2009, 9, 17)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.first_moment.year,   2009)
        self.assertEqual(presenter.first_moment.month,  9)
        self.assertEqual(presenter.first_moment.day,    13)
        self.assertEqual(presenter.first_moment.hour,   0)
        self.assertEqual(presenter.first_moment.minute, 0)
        self.assertEqual(presenter.first_moment.second, 0)

    def test_computes_last_moment_properly_at_midweek(self):
        focus_at = datetime.datetime(2009, 9, 17)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.last_moment.year,   2009)
        self.assertEqual(presenter.last_moment.month,  9)
        self.assertEqual(presenter.last_moment.day,    19)
        self.assertEqual(presenter.last_moment.hour,   23)
        self.assertEqual(presenter.last_moment.minute, 59)
        self.assertEqual(presenter.last_moment.second, 59)

    # css today_class used to highlight today's column
    
    def test_sets_today_class_for_css_when_focus_is_on_now(self):
        focus_at = datetime.datetime(2009, 9, 17)
        now_at   = datetime.datetime(2009, 9, 17)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.today_class, 'cal_today_thu')

    def test_sets_today_class_for_a_different_day_in_focus_week(self):
        focus_at = datetime.datetime(2009, 9, 17)
        now_at   = datetime.datetime(2009, 9, 14)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.today_class, 'cal_today_mon')

    def test_sets_today_class_to_empty_when_now_is_out_of_focus(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime(2009, 9, 14)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.today_class, '')

    # css auto_scroll_class used to trigger javascript scroll effect

    def test_auto_scroll_class_is_today_when_now_is_in_focus(self):
        focus_at = datetime.datetime(2009, 11, 2)
        now_at   = datetime.datetime(2009, 11, 5)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.auto_scroll_class, 'today')
        
    def test_auto_scroll_class_is_empty_when_now_is_not_in_focus(self):
        focus_at = datetime.datetime(2009, 11, 2)
        now_at   = datetime.datetime(2009, 10, 31)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.auto_scroll_class, '')

    # days in week
    
    def test_each_day_is_assigned_a_show_url(self):
        focus_at = datetime.datetime(2009, 11, 3)
        now_at   = datetime.datetime(2009, 11, 3)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
                                       
        sunday = presenter.week[0]
        self.assert_('day.html' in sunday.show_url)
        self.assert_('year=2009&month=11&day=1' in sunday.show_url)

        saturday = presenter.week[6]
        self.assert_('day.html' in saturday.show_url)
        self.assert_('year=2009&month=11&day=7' in saturday.show_url)

    def test_each_day_is_assigned_an_add_event_url_after_paint_events(self):
        focus_at = datetime.datetime(2009, 11, 3)
        now_at   = datetime.datetime(2009, 11, 3)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        presenter.paint_events([])
                                       
        sunday = presenter.week[0]
        self.assert_('add_calendarevent.html' in sunday.add_event_url)

        saturday = presenter.week[6]
        self.assert_('add_calendarevent.html' in saturday.add_event_url)
 
    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.week import WeekViewPresenter
        return WeekViewPresenter(*args, **kargs)


class DayOnWeekViewTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    # properties
    
    def test_has_a_heading_used_at_the_top_of_calendar_columns(self):
        day = self._makeOne(2009, 9, 4)
        self.assertEqual(day.heading, 'Fri 9/4')
     
    def test_has_a_css_day_abbr_purposely_not_localized(self):
        day = self._makeOne(2009, 9, 4)
        self.assertEqual(day.css_day_abbr, 'fri')

    def test_has_properties_for_year_month_day(self):
        day = self._makeOne(2009, 9, 4)
        self.assertEqual(day.year,  2009)
        self.assertEqual(day.month, 9)
        self.assertEqual(day.day,   4)

    def test_has_a_show_url_used_to_link_to_the_day_view(self):
        day = self._makeOne(2009, 9, 4, show_url='http://the-day')
        self.assertEqual(day.show_url, 'http://the-day')

    def test_has_an_add_event_url(self):
        day = self._makeOne(2009, 9, 4, add_event_url='http://add-event')
        self.assertEqual(day.add_event_url, 'http://add-event')

    # start_datetime & end_datetime
    
    def test_computes_start_datetime_at_beginning_of_day(self):
        day = self._makeOne(2009, 9, 4)
        self.assertEqual(day.start_datetime, 
                         datetime.datetime(2009, 9, 4, 0, 0, 0))

    def test_computes_end_datetime_at_ending_of_day(self):
        day = self._makeOne(2009, 9, 4)
        self.assertEqual(day.end_datetime, 
                         datetime.datetime(2009, 9, 4, 23, 59, 59))

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.week import DayOnWeekView
        return DayOnWeekView(*args, **kargs)
