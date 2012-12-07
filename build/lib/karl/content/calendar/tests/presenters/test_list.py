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

    def test_has_a_feed_url(self):
        focus_at = datetime.datetime(2009, 8, 1)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)

        self.assert_(presenter.feed_url.startswith('http'))

    def test_title_is_month_name_and_year(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.title, 'Upcoming Events')

    # paint_events

    def test_paints_event_of_one_hour(self):
        focus_at = datetime.datetime(2010, 2, 15)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        event = DummyCatalogEvent(
                    title="Meeting",
                    startDate=datetime.datetime(2010, 2, 15,  13,  0,  0),
                    endDate  =datetime.datetime(2010, 2, 15,  14,  0,  0),
                )
        presenter.paint_events([event])

        # presenters.list.Event
        painted_event = presenter.events[0]

        self.assertEqual(painted_event.title,
                         event.title)                           # Meeting
        self.assertEqual(painted_event.first_line_day,
                         event.startDate.strftime("%m/%d/%Y")) # Mon, Feb 15
        self.assertEqual(painted_event.second_line_day, '')

        starts = painted_event._format_time_of_day(event.startDate)
        ends   = painted_event._format_time_of_day(event.endDate)
        desc   = "%s - %s" % (starts, ends)
        self.assertEqual(painted_event.first_line_time, desc)   # 1pm - 2pm
        self.assertEqual(painted_event.second_line_time, '')

    def test_paints_event_of_one_full_day(self):
        focus_at = datetime.datetime(2010, 2, 15)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        event = DummyCatalogEvent(
                    title="Vacation",
                    startDate=datetime.datetime(2010, 2, 15,  0,  0,  0),
                    endDate  =datetime.datetime(2010, 2, 16,  0,  0,  0)
                )
        presenter.paint_events([event])

        # presenters.list.Event
        painted_event = presenter.events[0]
        self.assertEqual(painted_event.title,
                         event.title)                           # Vacation

        self.assertEqual(painted_event.first_line_day,
                         event.startDate.strftime("%m/%d/%Y")) # Mon, Feb 15
        self.assertEqual(painted_event.first_line_time, 'all-day')

        self.assertEqual(painted_event.second_line_day, '')     # empty second line
        self.assertEqual(painted_event.second_line_time, '')

    def test_paints_event_of_three_full_days(self):
        focus_at = datetime.datetime(2010, 2, 15)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        event = DummyCatalogEvent(
                    title="Vacation",
                    startDate=datetime.datetime(2010, 2, 15,  0,  0,  0),
                    endDate  =datetime.datetime(2010, 2, 18,  0,  0,  0)
                )
        presenter.paint_events([event])

        # presenters.list.Event
        painted_event = presenter.events[0]
        self.assertEqual(painted_event.title,
                         event.title)                           # Vacation

        self.assertEqual(painted_event.first_line_day,
                         event.startDate.strftime("%m/%d/%Y")) # Mon, Feb 15
        self.assertEqual(painted_event.first_line_time, 'all-day')

        ends_at = event.endDate - datetime.timedelta(days=1)
        self.assertEqual(painted_event.second_line_day,
                        '') # all day events: no second line.
        self.assertEqual(painted_event.second_line_time, '')


    def test_paints_event_sameday_suppresses_label(self):
        focus_at = datetime.datetime(2010, 2, 15)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        event = DummyCatalogEvent(
                    title="Vacation",
                    startDate=datetime.datetime(2010, 2, 15,  0,  0,  0),
                    endDate  =datetime.datetime(2010, 2, 18,  0,  0,  0)
                )
        import copy
        event2 = copy.copy(event)
        event2.prev_start_date = event.startDate
        presenter.paint_events([event, event2])

        # presenters.list.Event
        painted_events = presenter.events
        self.assertEqual(len(painted_events), 2)
        for i, _e in enumerate(painted_events):
            if i == 0:
                # first one has the date
                self.assertEqual(_e.first_line_day,
                    event.startDate.strftime("%m/%d/%Y")) # Mon, Feb 15
            else:
                # Consequtive lines that have the same date,
                # have the day-label missing.
                self.assertEqual(_e.first_line_day, '')
            self.assertEqual(_e.first_line_time, 'all-day')
            self.assertEqual(_e.second_line_day,
                            '') # all day events: no second line.
            self.assertEqual(painted_events[0].second_line_time, '')


    def test_paints_event_of_three_days_with_partial_days(self):
        focus_at = datetime.datetime(2010, 2, 17)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        event = DummyCatalogEvent(
                    title="Travel",
                    startDate=datetime.datetime(2010, 2, 15, 13,  0,  0),
                    endDate  =datetime.datetime(2010, 2, 17, 16,  0,  0)
                )
        presenter.paint_events([event])

        # presenters.list.Event
        painted_event = presenter.events[0]
        self.assertEqual(painted_event.title,
                         event.title)                           # Travel

        self.assertEqual(painted_event.first_line_day,
                         event.startDate.strftime("%m/%d/%Y")) # Mon, Feb 15
        starts = painted_event._format_time_of_day(event.startDate)
        desc   = "%s - " % (starts)
        self.assertEqual(painted_event.first_line_time, desc)   # 1pm -

        self.assertEqual(painted_event.second_line_day, '')
        self.assertEqual(painted_event.second_line_time, '')

    def test_navigation_without_nav_params(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        presenter.page = 2
        presenter.has_more = True

        presenter._init_navigation()
        nav = presenter.navigation
        self.assertEqual(nav.prev_url,
            'http://example.com/list.html?year=2009&month=8&day=26'
            '&per_page=20&page=1')
        self.assertEqual(nav.next_url,
            'http://example.com/list.html?year=2009&month=8&day=26'
            '&per_page=20&page=3')

    def test_navigation_with_nav_params(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for,
            nav_params={'filter': 'X Y'})
        presenter.page = 2
        presenter.has_more = True

        presenter._init_navigation()
        nav = presenter.navigation
        self.assertEqual(nav.prev_url,
            'http://example.com/list.html?year=2009&month=8&day=26'
            '&per_page=20&filter=X+Y&page=1')
        self.assertEqual(nav.next_url,
            'http://example.com/list.html?year=2009&month=8&day=26'
            '&per_page=20&filter=X+Y&page=3')

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.list import ListViewPresenter
        return ListViewPresenter(*args, **kargs)
