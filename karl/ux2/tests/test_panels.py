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


class GlobalNavTests(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.ux2.panels import global_nav
        return global_nav(context, request)

    def _make_layout(self, site, request):
        layout = testing.DummyModel()
        layout.site = site
        layout.people_url = request.url + '/people'
        layout.profiles_url = None
        layout.should_show_calendar_tab = False
        layout.user_is_staff = False
        return layout

    def test_communities_selected(self):
        site = testing.DummyModel()
        site['communities'] = communities = testing.DummyModel()
        request = testing.DummyRequest()
        request.layout_manager = testing.DummyModel()
        request.url = request.url + '/communities'
        request.layout_manager.layout = self._make_layout(site, request)
        request.context = context = communities
        global_nav = self._callFUT(context, request)

        self.assertEqual(global_nav['nav_menu'][0]['id'], 'communities')
        self.assertEqual(global_nav['nav_menu'][0]['selected'], 'selected')

    def test_people_selected(self):
        site = testing.DummyModel()
        site['people'] = people = testing.DummyModel()
        request = testing.DummyRequest()
        request.layout_manager = testing.DummyModel()
        request.layout_manager.layout = self._make_layout(site, request)
        request.url = request.url + '/people'
        request.context = context = people
        global_nav = self._callFUT(context, request)

        self.assertEqual(global_nav['nav_menu'][1]['id'], 'people')
        self.assertEqual(global_nav['nav_menu'][1]['selected'], 'selected')

    def test_feeds_selected(self):
        site = testing.DummyModel()
        request = testing.DummyRequest()
        request.layout_manager = testing.DummyModel()
        request.url = request.url + '/contentfeeds.html'
        request.layout_manager.layout = self._make_layout(site, request)
        request.context = context = site
        global_nav = self._callFUT(context, request)

        self.assertEqual(global_nav['nav_menu'][2]['id'], 'feeds')
        self.assertEqual(global_nav['nav_menu'][2]['selected'], 'selected')

    def test_calendar_selected(self):
        site = testing.DummyModel()
        site['offices'] = testing.DummyModel()
        site['offices']['calendar'] = calendar = testing.DummyModel()
        request = testing.DummyRequest()
        request.layout_manager = testing.DummyModel()
        request.url = request.url + '/offices/calendar'
        request.layout_manager.layout = self._make_layout(site, request)
        request.layout_manager.layout.should_show_calendar_tab = True
        request.context = context = calendar
        global_nav = self._callFUT(context, request)

        self.assertEqual(global_nav['nav_menu'][3]['id'], 'calendar')
        self.assertEqual(global_nav['nav_menu'][3]['selected'], 'selected')

    def test_tags_selected(self):
        site = testing.DummyModel()
        request = testing.DummyRequest()
        request.layout_manager = testing.DummyModel()
        request.url = request.url + '/tagcloud.html'
        request.layout_manager.layout = self._make_layout(site, request)
        request.layout_manager.layout.user_is_staff = True
        request.context = context = site
        global_nav = self._callFUT(context, request)

        self.assertEqual(global_nav['nav_menu'][3]['id'], 'tagcloud')
        self.assertEqual(global_nav['nav_menu'][3]['selected'], 'selected')

    def test_chatter_selected(self):
        site = testing.DummyModel()
        site['chatter'] = chatter = testing.DummyModel()
        request = testing.DummyRequest()
        request.layout_manager = testing.DummyModel()
        request.url = request.url + '/chatter'
        request.layout_manager.layout = self._make_layout(site, request)
        request.context = context = chatter
        global_nav = self._callFUT(context, request)

        self.assertEqual(global_nav['nav_menu'][3]['id'], 'chatter')
        self.assertEqual(global_nav['nav_menu'][3]['selected'], 'selected')
