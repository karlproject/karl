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
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp
from karl.content.newcalendar.tests.presenters.test_base import dummy_url_for
 

class CalendarNavigationTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    # left navigation

    def test_sets_today_button_img_disabled_when_day_shown(self):
        focus_at = datetime.datetime(2009, 8, 1)
        now_at   = datetime.datetime(2009, 8, 26)

        presenter  = self._makePresenter(focus_at, now_at, dummy_url_for)
        navigation = self._makeNavigation(presenter)

        self.assertTrue(navigation._is_today_shown())
        self.assertEqual(navigation.today_button_img, 'today_disabled.png')

    def test_sets_today_button_img_enabled_when_day_is_not_shown(self):
        focus_at = datetime.datetime(2009, 7, 26)
        now_at   = datetime.datetime(2009, 8, 26)

        presenter  = self._makePresenter(focus_at, now_at, dummy_url_for)
        navigation = self._makeNavigation(presenter)

        self.assertFalse(navigation._is_today_shown())
        self.assertEqual(navigation.today_button_img, 'today.png')

    # helpers

    def _makePresenter(self, *args, **kargs):
        from karl.content.newcalendar.presenters.month import MonthViewPresenter
        return MonthViewPresenter(*args, **kargs)

    def _makeNavigation(self, *args, **kargs):
        from karl.content.newcalendar.navigation import Navigation
        return Navigation(*args, **kargs)


