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
import datetime
import time
import calendar
from karl.content.calendar.presenters.month import MonthViewPresenter
from karl.content.calendar.tests.presenters.test_base import dummy_url_for
from karl.content.calendar.tests.presenters.test_base import DummyCatalogEvent
from karl.content.calendar.tests.presenters.test_base import DummyDayWithEvents


class MonthSkeletonTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    def test_assigns_year_and_month_properties(self):
        skeleton = self._makeOne(2009, 8)

        self.assertEqual(skeleton.year,  2009)
        self.assertEqual(skeleton.month, 8)

    def test_sets_day_names_to_show_above_calendar(self):
        skeleton = self._makeOne(2009, 8)

        self.assertEqual(len(skeleton.day_names), 7)
        
        sunday = calendar.day_name[ calendar.firstweekday() ]
        self.assertEqual(skeleton.day_names[0], sunday)

    def test_sets_day_abbreviations_to_show_above_calendar(self):
        skeleton = self._makeOne(2009, 8)

        self.assertEqual(len(skeleton.day_abbrs), 7)
        
        sunday = calendar.day_abbr[ calendar.firstweekday() ]
        self.assertEqual(skeleton.day_abbrs[0], sunday)
    
    def test_builds_weeks_where_each_week_is_a_list_of_days(self):
        skeleton = self._makeOne(2009, 8)
        
        self.assertEqual(skeleton.weeks[0][0].month,  7)  # sun jul 26
        self.assertEqual(skeleton.weeks[0][0].day,   26)
        self.assertEqual(skeleton.weeks[0][6].month,  8)  # sat aug 1 
        self.assertEqual(skeleton.weeks[0][6].day,    1)

        self.assertEqual(skeleton.weeks[1][0].month,  8)  # sun aug 2
        self.assertEqual(skeleton.weeks[1][0].day,    2)
        self.assertEqual(skeleton.weeks[1][6].month,  8)  # sat aug 8
        self.assertEqual(skeleton.weeks[1][6].day,    8)

        self.assertEqual(skeleton.weeks[2][0].month,  8)  # sun aug 9
        self.assertEqual(skeleton.weeks[2][0].day,    9)
        self.assertEqual(skeleton.weeks[2][6].month,  8)  # sat aug 15
        self.assertEqual(skeleton.weeks[2][6].day,   15)

        self.assertEqual(skeleton.weeks[3][0].month,  8)  # sun aug 16
        self.assertEqual(skeleton.weeks[3][0].day,   16)
        self.assertEqual(skeleton.weeks[3][6].month,  8)  # sat aug 22
        self.assertEqual(skeleton.weeks[3][6].day,   22)
        
        self.assertEqual(skeleton.weeks[4][0].month,  8)  # sun aug 23
        self.assertEqual(skeleton.weeks[4][0].day,   23)
        self.assertEqual(skeleton.weeks[4][6].month,  8)  # sat aug 29
        self.assertEqual(skeleton.weeks[4][6].day,   29)

        self.assertEqual(skeleton.weeks[5][0].month,  8)  # sun aug 30
        self.assertEqual(skeleton.weeks[5][0].day,   30)
        self.assertEqual(skeleton.weeks[5][6].month,  9)  # sat sep 5
        self.assertEqual(skeleton.weeks[5][6].day,    5)
        
    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.utils import MonthSkeleton
        return MonthSkeleton(*args, **kargs)


class BubblePainterTests(unittest.TestCase):

    # _find_contiguous_slot_across_days
    
    def test__find_contiguous_slot_across_days_gets_first_available(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        days = [ DummyDayWithEvents(), DummyDayWithEvents() ]

        index = bubble_painter._find_contiguous_slot_across_days(days)
        self.assertEqual(index, 0)
    
    def test__find_contiguous_slot_across_days_searches_top_down(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        days = [ DummyDayWithEvents(), DummyDayWithEvents() ]
        days[0].event_slots[0] = DummyCatalogEvent()
        days[1].event_slots[1] = DummyCatalogEvent()

        index = bubble_painter._find_contiguous_slot_across_days(days)
        self.assertEqual(index, 2)
        
    def test__find_contiguous_slot_across_days_may_find_None(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        days = [DummyDayWithEvents]*2
        days[0].event_slots = [DummyCatalogEvent()]*5

        index = bubble_painter._find_contiguous_slot_across_days(days)
        self.assert_(index is None)

    def test__find_contiguous_slot_across_days_is_None_for_empty_list(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        days = []

        index = bubble_painter._find_contiguous_slot_across_days(days)
        self.assert_(index is None)

    # should_paint_event
    
    def test_should_paint_event_no_for_event_less_than_whole_day(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 14,  1,  0,  0),
                    endDate  =datetime.datetime(2009, 9, 14,  2,  0,  0)
                )        

        self.assertFalse(bubble_painter.should_paint_event(event))
    
    def test_should_paint_event_yes_for_whole_single_day(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 14,  0,  0,  0),
                    endDate  =datetime.datetime(2009, 9, 14, 23, 59, 59)
                )        

        self.assertTrue(bubble_painter.should_paint_event(event))

    def test_should_paint_event_yes_for_spans_of_multiple_days(self):
        presenter = self._makePresenter()
        bubble_painter = self._makeOne(presenter)

        event = DummyCatalogEvent(
                    startDate=datetime.datetime(2009, 9, 14,  0,  0,  0),
                    endDate  =datetime.datetime(2009, 9, 16,  0,  0,  0)
                )        

        self.assertTrue(bubble_painter.should_paint_event(event))

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.utils import BubblePainter
        return BubblePainter(*args, **kargs)
    
    def _makePresenter(self):
        focus_at = datetime.datetime(2009, 8, 1) 
        now_at   = datetime.datetime(2009, 8, 26)
        return MonthViewPresenter(focus_at, now_at, dummy_url_for)

