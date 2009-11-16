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

from repoze.bfg import testing

class StatsTest(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def test_stats_page(self):
        from karl.views import stats
        context = testing.DummyModel()
        request = testing.DummyRequest()
        result = stats.stats(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        self.failUnless('Community Counts' in body)
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(result.headerlist[0],
                         ('Content-Type', 'text/html; charset=UTF-8'))
        self.assertEqual(result.headerlist[1], ('Content-Length',
                                                str(len(body))))
        