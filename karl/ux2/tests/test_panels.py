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
from pyramid import testing
from karl import testing as karltesting


class AdminMenuTests(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()
        import os
        from pyramid.interfaces import ISettings
        from karl.views.tests import test_admin
        # get the dir for existing test file for admin views
        test_dir = os.path.abspath(os.path.dirname(test_admin.__file__))
        settings = karltesting.DummySettings(
            statistics_folder=test_dir,
        )
        karltesting.registerUtility(settings, ISettings)

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.ux2.panels import admin_menu
        return admin_menu(context, request)

    def test_statistics_view_enabled(self):
        request = testing.DummyRequest()

        site = testing.DummyModel()
        request.context = context = site
        admin_settings = self._callFUT(context, request)

        self.assertEqual(admin_settings['statistics_view_enabled'], True)
