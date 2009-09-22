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
from karl.content.newcalendar.tests.presenters.test_base import dummy_url_for


class DayViewPresenterTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    # title

    def test_title_is_day_name_with_numeric_month_and_day(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.title, 'Saturday 8/1')

    # first & last moment

    def test_computes_first_moment_as_beginning_of_same_day(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        expected = datetime.datetime(2009, 8, 26)
        self.assertEqual(presenter.first_moment, expected)

    def test_computes_last_moment_as_ending_of_same_day(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        expected = datetime.datetime(2009, 8, 26, 23, 59, 59)
        self.assertEqual(presenter.last_moment, expected)

    # prior_day & next_day
    
    def test_computes_next_day_within_the_same_month(self):
        focus_at = datetime.datetime(2009, 8, 30) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.next_day.year,  2009)
        self.assertEqual(presenter.next_day.month, 8)
        self.assertEqual(presenter.next_day.day,   31)

    def test_computes_next_day_into_the_next_month(self):
        focus_at = datetime.datetime(2009, 8, 31) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.next_day.year,  2009)
        self.assertEqual(presenter.next_day.month, 9)
        self.assertEqual(presenter.next_day.day,   1)

    def test_computes_prior_day_within_the_same_month(self):
        focus_at = datetime.datetime(2009, 8, 2) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.prior_day.year,  2009)
        self.assertEqual(presenter.prior_day.month, 8)
        self.assertEqual(presenter.prior_day.day,   1)

    def test_computes_prior_day_into_the_prior_month(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertEqual(presenter.prior_day.year,  2009)
        self.assertEqual(presenter.prior_day.month, 7)
        self.assertEqual(presenter.prior_day.day,   31)

    # left navigation
    
    def test_sets_navigation_today_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.today_href.endswith(
            'newday.html?year=2009&month=8&day=26'
        ))

    def test_sets_navigation_prev_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.prev_href.endswith(
            'newday.html?year=2009&month=7&day=31'
        ))

    def test_sets_navigation_next_href(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.next_href.endswith(
            'newday.html?year=2009&month=8&day=2'
        ))

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.newcalendar.presenters.day import DayViewPresenter
        return DayViewPresenter(*args, **kargs)
