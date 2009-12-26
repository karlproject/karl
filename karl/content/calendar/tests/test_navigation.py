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
from karl.content.calendar.tests.presenters.test_base import dummy_url_for
 

class CalendarNavigationTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    # left navigation

    def test_left_navigation_urls_are_initialized_to_None(self):
        focus_at = datetime.datetime(2009, 8, 1)
        now_at   = datetime.datetime(2009, 8, 26)

        presenter  = self._makePresenter(focus_at, now_at, dummy_url_for)
        navigation = self._makeNavigation(presenter)

        self.assert_(navigation.today_url is None)
        self.assert_(navigation.next_url is None)
        self.assert_(navigation.prev_url is None)
        
    # helpers

    def _makePresenter(self, *args, **kargs):
        from karl.content.calendar.presenters.month import MonthViewPresenter
        return MonthViewPresenter(*args, **kargs)

    def _makeNavigation(self, *args, **kargs):
        from karl.content.calendar.navigation import Navigation
        return Navigation(*args, **kargs)


