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

from zope.interface import Interface
from zope.testing.cleanup import cleanUp

from repoze.bfg.testing import DummyModel
from repoze.bfg.testing import DummyRequest
from repoze.bfg.testing import registerDummyRenderer
from repoze.bfg.testing import registerAdapter
from repoze.bfg.testing import registerUtility

from karl.testing import DummyCatalog
from karl.testing import DummyLayoutProvider
from karl.testing import DummySearchAdapter
from karl.testing import DummyTagQuery
from karl.testing import DummyFolderAddables
from karl.testing import DummyUsers

class TestShowNetworkEventsView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        self.template_fn = 'templates/custom_folder.pt'

        self.parent = DummyModel(title='dummyparent')
        self.context = DummyModel(title='dummytitle', text='dummytext')
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()
        self.parent["profiles"] = DummyModel()
        users = self.parent.users = DummyUsers()
        users.add("userid", "userid", "password", [])

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.custom_folderviews import network_events_view
        return network_events_view(context, request)

    def _registerAddables(self):
        from karl.views.interfaces import IFolderAddables
        registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerKarlDates(self):
        d1 = 'Wednesday, January 28, 2009 08:32 AM'
        def dummy(date, flavor):
            return d1
        from karl.utilities.interfaces import IKarlDates
        registerUtility(dummy, IKarlDates)

    def _registerCatalogSearch(self):
        from karl.models.interfaces import ICatalogSearch
        registerAdapter(DummySearchAdapter, (Interface), ICatalogSearch)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider

        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _registerSecurityPolicy(self):
        from repoze.bfg.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy("userid")

    def _register(self):
        self._registerAddables()
        self._registerKarlDates()
        self._registerCatalogSearch()
        self._registerTagbox()
        self._registerLayoutProvider()
        self._registerSecurityPolicy()

    def test_first_request(self):
        self._register()

        context = self.context
        request = DummyRequest()

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 5)
        self.assertEqual(renderer.backto,
                         {'href': 'http://example.com/',
                          'title': 'Home'})
        self.assertEqual(renderer.entries, [])
        self.assertEqual(renderer.fb_years[:3], ['2007', '2008', '2009'])
        self.assertEqual(len(renderer.fb_months), 12)
        self.assertEqual(renderer.searchterm, None)
        self.assertEqual(renderer.selected_year, None)
        self.assertEqual(renderer.selected_month, None)
        self.assertEqual(renderer.past_events_url,
                         "http://example.com/child/?past_events=True")

    def test_with_searchterm(self):
        self._register()

        context = self.context
        request = DummyRequest({'searchterm':'someword'})

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.searchterm, 'someword')
        self.assertEqual(renderer.selected_year, None)
        self.assertEqual(renderer.selected_month, None)

    def test_with_unparseable_searchterm(self):
        self._register()

        context = self.context
        request = DummyRequest({'searchterm':'the'})

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.searchterm, 'the')
        self.assertEqual(renderer.selected_year, None)
        self.assertEqual(renderer.selected_month, None)

    def test_with_year_and_month(self):
        self._register()

        context = self.context
        request = DummyRequest({
                'year':'2007',
                'month':'3',
                })

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.searchterm, None)
        self.assertEqual(renderer.selected_year, '2007')
        self.assertEqual(renderer.selected_month, '3')

    def test_past_events(self):
        self._register()

        context = self.context
        request = DummyRequest({
            'past_events': 'True',
        })

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.future_events_url,
                         "http://example.com/child/?past_events=False")
        self.assertEqual(renderer.past_events_url, None)

    def test_future_events(self):
        self._register()

        context = self.context
        request = DummyRequest({
            'past_events': 'False',
        })

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.past_events_url,
                         "http://example.com/child/?past_events=True")
        self.assertEqual(renderer.future_events_url, None)

class TestShowNetworkNewsView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        self.template_fn = 'templates/custom_folder.pt'

        self.parent = DummyModel(title='dummyparent')
        self.context = DummyModel(title='dummytitle', text='dummytext')
        self.context['attachments'] = DummyModel()
        self.parent['child'] = self.context
        self.parent.catalog = DummyCatalog()
        self.parent["profiles"] = DummyModel()
        users = self.parent.users = DummyUsers()
        users.add("userid", "userid", "password", [])

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.custom_folderviews import network_news_view
        return network_news_view(context, request)

    def _registerAddables(self):
        from karl.views.interfaces import IFolderAddables
        registerAdapter(DummyFolderAddables, (Interface, Interface),
                                IFolderAddables)

    def _registerTagbox(self):
        from karl.models.interfaces import ITagQuery
        registerAdapter(DummyTagQuery, (Interface, Interface),
                                ITagQuery)

    def _registerKarlDates(self):
        d1 = 'Wednesday, January 28, 2009 08:32 AM'
        def dummy(date, flavor):
            return d1
        from karl.utilities.interfaces import IKarlDates
        registerUtility(dummy, IKarlDates)

    def _registerCatalogSearch(self):
        from karl.models.interfaces import ICatalogSearch
        registerAdapter(DummySearchAdapter, (Interface), ICatalogSearch)

    def _registerLayoutProvider(self):
        from karl.views.interfaces import ILayoutProvider

        ad = registerAdapter(DummyLayoutProvider,
                             (Interface, Interface),
                             ILayoutProvider)

    def _registerSecurityPolicy(self):
        from repoze.bfg.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy("userid")

    def _register(self):
        self._registerAddables()
        self._registerKarlDates()
        self._registerCatalogSearch()
        self._registerTagbox()
        self._registerLayoutProvider()
        self._registerSecurityPolicy()

    def test_first_request(self):
        self._register()

        context = self.context
        request = DummyRequest()

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 5)
        self.assertEqual(renderer.backto,
                         {'href': 'http://example.com/',
                          'title': 'Home'})
        self.assertEqual(renderer.entries, [])
        self.assertEqual(renderer.fb_years[:3], ['2007', '2008', '2009'])
        self.assertEqual(len(renderer.fb_months), 12)
        self.assertEqual(renderer.searchterm, None)
        self.assertEqual(renderer.selected_year, None)
        self.assertEqual(renderer.selected_month, None)
        self.assertEqual(renderer.past_events_url, None)

    def test_with_searchterm(self):
        self._register()

        context = self.context
        request = DummyRequest({'searchterm':'someword'})

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.searchterm, 'someword')
        self.assertEqual(renderer.selected_year, None)
        self.assertEqual(renderer.selected_month, None)

    def test_with_year_and_month(self):
        self._register()

        context = self.context
        request = DummyRequest({
                'year':'2007',
                'month':'3',
                })

        renderer = registerDummyRenderer(self.template_fn)
        response = self._callFUT(context, request)

        self.assertEqual(renderer.searchterm, None)
