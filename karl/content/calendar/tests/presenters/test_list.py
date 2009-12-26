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
    
    def test_sets_navigation_today_url(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.today_url.endswith(
            'list.html?year=2009&month=8&day=26'
        ))

    def test_sets_navigation_prev_url(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.prev_url.endswith(
            'list.html?year=2009&month=7&day=1'
        ))

    def test_sets_navigation_next_url(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assertTrue(presenter.navigation.next_url.endswith(
            'list.html?year=2009&month=9&day=1'
        ))

       
    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.list import ListViewPresenter
        return ListViewPresenter(*args, **kargs)

