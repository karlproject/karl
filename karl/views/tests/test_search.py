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

import mock
import unittest

from pyramid import testing
from zope.interface import implements
from zope.interface import Interface
from zope.interface import taggedValue
from pyramid.testing import cleanUp

import karl.testing as karltesting

class JQueryLivesearchViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.search import jquery_livesearch_view
        return jquery_livesearch_view(context, request)

    def test_no_parameter(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        context = testing.DummyModel()
        request = testing.DummyRequest()
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '400 Bad Request')

    def test_with_parameter_noresults(self):
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        def dummy_factory(context, request, term):
            def results():
                return 0, [], None
            return results
        dummy_factory.livesearch = True
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            }
        results = self._callFUT(context, request)
        self.assertEqual(len(results), 0)

    def test_with_parameter_withresults(self):
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        from karl.views.interfaces import ILiveSearchEntry
        def dummy_factory1(context, request, term):
            pass
        def dummy_factory2(context, request, term):
            def results():
                return 1, [1], lambda x: testing.DummyModel(title='yo')
            return results
        dummy_factory1.livesearch = dummy_factory2.livesearch = True

        registerListItem(IGroupSearchFactory, dummy_factory1, 'dummy1',
                         title='Dummy1', sort_key=1)
        registerListItem(IGroupSearchFactory, dummy_factory2, 'dummy2',
                         title='Dummy2', sort_key=2)
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            }
        def dummy_adapter(context, request):
            return dict(title=context.title)
        karltesting.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        results = self._callFUT(context, request)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'yo')

    def test_with_parameter_withresults_withkind(self):
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        from karl.views.interfaces import ILiveSearchEntry
        def dummy_factory(context, request, term):
            def results():
                return 1, [1], lambda x: testing.DummyModel(title='yo')
            return results
        registerListItem(IGroupSearchFactory, dummy_factory,
                         'foo_kind', title='Dummy')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            'kind': 'foo_kind',
            }
        def dummy_adapter(context, request):
            return dict(title=context.title)
        karltesting.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        results = self._callFUT(context, request)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'yo')

    def test_with_parameter_withresults_withbadkind(self):
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        def dummy_factory(context, request, term):
            def results():
                return 1, [1], lambda x: testing.DummyModel(title='yo')
            return results
        registerListItem(IGroupSearchFactory, dummy_factory,
                         'foo_kind', title='Dummy')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            'kind': 'bad_kind',
            }
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '400 Bad Request')

    def test_numresults_nokind(self):
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        from karl.views.interfaces import ILiveSearchEntry
        def dummy_factory(context, request, term):
            return DummyGroupSearchFactory(
                lambda x: testing.DummyModel(title='yo'))
        dummy_factory.livesearch = True
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy',
                         title='Dummy')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            }
        def dummy_adapter(context, request):
            return dict(title=context.title)
        karltesting.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        results = self._callFUT(context, request)
        self.assertEqual(len(results), 5)

    def test_numresults_withkind(self):
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        from karl.views.interfaces import ILiveSearchEntry
        def dummy_factory(context, request, term):
            return DummyGroupSearchFactory(
                lambda x: testing.DummyModel(title='yo'))
        registerListItem(IGroupSearchFactory, dummy_factory,
                         'foo_kind', title='Dummy')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            'kind': 'foo_kind',
            }
        def dummy_adapter(context, request):
            return dict(title=context.title)
        karltesting.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        results = self._callFUT(context, request)
        self.assertEqual(len(results), 20)


class SearchResultsViewBase(object):

    def setUp(self):
        cleanUp()
        karltesting.registerDummyRenderer(
            'karl.views:templates/generic_layout.pt')
        karltesting.registerDummyRenderer(
            'karl.views:templates/community_layout.pt')

    def tearDown(self):
        cleanUp()

    def test_no_searchterm(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict())
        request.layout_manager = mock.Mock()
        from karl.models.interfaces import ICatalogSearch
        karltesting.registerAdapter(DummyEmptySearch, (Interface),
                                ICatalogSearch)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], [])

    def test_bad_kind(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=MultiDict({'kind':'unknown', 'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from pyramid.httpexceptions import HTTPBadRequest
        karltesting.registerAdapter(DummyEmptySearch, (Interface),
                                ICatalogSearch)
        self.assertRaises(HTTPBadRequest, self._callFUT, context, request)

    def test_none_kind(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo'])
        self.assertEqual(len(result['results']), 1)

    def test_with_batch(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'batch_start': '20',
                              'batch_size': '20'})
        )
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        result = self._callFUT(context, request)
        self.failIf('batch' in result['kind_knob'][0]['url'])
        self.failIf('batch' in result['since_knob'][0]['url'])

    def test_creator_not_found(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo'])
        self.assertEqual(len(result['results']), 1)

    def test_no_creator(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        class LocalDummyContent(testing.DummyModel):
            implements(IDummyContent)
            import datetime
            title = 'Dummy Content'
            modified = datetime.datetime(2010, 5, 12, 2, 42)
        class LocalDummySearch(DummySearch):
            content = LocalDummyContent()
        karltesting.registerAdapter(LocalDummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo'])
        self.assertEqual(len(result['results']), 1)

    def test_known_kind(self):
        from webob.multidict import MultiDict
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        content = DummyCommunityContent()
        def search_factory(*arg, **kw):
            return DummySearchFactory(content)
        search_factory.icon = 'foo.jpg'
        search_factory.advanced_search = True
        karltesting.registerUtility(
            search_factory, IGroupSearchFactory, name='People')
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'People'}))
        request.layout_manager = mock.Mock()
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo', 'People'])
        self.assertEqual(len(result['results']), 1)

    def test_known_kind_no_text_term(self):
        from webob.multidict import MultiDict
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        content = DummyCommunityContent()
        def search_factory(*arg, **kw):
            return DummySearchFactory(content)
        search_factory.icon = 'foo.jpg'
        search_factory.advanced_search = True
        karltesting.registerUtility(
            search_factory, IGroupSearchFactory, name='People')
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        request = testing.DummyRequest(
            params=MultiDict({'kind':'People'}))
        request.layout_manager = mock.Mock()
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['People'])
        self.assertEqual(len(result['results']), 1)

    def test_community_search(self):
        context = testing.DummyModel()
        context.title = 'Citizens'
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        from webob.multidict import MultiDict
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['community'], 'Citizens')
        self.assertEqual(result['terms'], ['yo'])
        self.assertEqual(len(result['results']), 1)

    def test_parse_error(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'the'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(ParseErrorSearch, (Interface),
                                ICatalogSearch)
        result = self._callFUT(context, request)
        self.assertEqual(len(result['terms']), 0)
        self.assertEqual(len(result['results']), 0)
        self.assertEqual(result['error'], "Error: 'the' is nonsense")

    def test_known_since(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        context.catalog = {}
        context['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'since': 'week'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.content.interfaces import IBlogEntry
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        registerContentFactory(DummyContent, IBlogEntry)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo', 'Past week'])
        self.assertEqual(len(result['results']), 1)



class SearchResultsViewTests(SearchResultsViewBase, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.search import searchresults_view
        return searchresults_view(context, request)

    def test_community_search_layout(self):
        root = testing.DummyModel()
        root.catalog = {}
        root['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        from webob.multidict import MultiDict
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides

        root['communities'] = testing.DummyModel()
        community = root['communities']['default'] = testing.DummyModel(title='citizens')
        office = root['offices'] = testing.DummyModel(title='all rights')
        directlyProvides(community, ICommunity)
        directlyProvides(office, ICommunity)

        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)

        import karl.views.api
        save_community = karl.views.api.TemplateAPI.community_layout
        save_generic = karl.views.api.TemplateAPI.generic_layout
        try:
            karl.views.api.TemplateAPI.community_layout = 'COMMUNITY'
            karl.views.api.TemplateAPI.generic_layout = 'GENERIC'

            # not on community
            result = self._callFUT(root, request)
            self.assertEqual(result['community'], None)
            self.assertEqual(result['old_layout'], 'GENERIC')
            self.assertEqual(result['show_search_knobs'], True)

            # normal community
            result = self._callFUT(community, request)
            self.assertEqual(result['community'], 'citizens')
            self.assertEqual(result['old_layout'], 'COMMUNITY')
            self.assertEqual(result['show_search_knobs'], True)

            # office
            result = self._callFUT(office, request)
            self.assertEqual(result['community'], 'all rights')
            self.assertEqual(result['old_layout'], 'COMMUNITY')
            self.assertEqual(result['show_search_knobs'], True)

        finally:
            karl.views.api.TemplateAPI.community_layout = save_community
            karl.views.api.TemplateAPI.generic_layout = save_generic

class CalendarSearchResultsViewTests(SearchResultsViewBase, unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.search import calendar_searchresults_view
        return calendar_searchresults_view(context, request)

    def test_calendar_search_layout(self):
        root = testing.DummyModel()
        root.catalog = {}
        root['profiles'] = profiles = testing.DummyModel()
        profiles['tweedle dee'] = testing.DummyModel(title='Tweedle Dee')
        from webob.multidict import MultiDict
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides

        root['communities'] = testing.DummyModel()
        community = root['communities']['default'] = testing.DummyModel(title='citizens')
        office = root['offices'] = testing.DummyModel(title='all rights')
        directlyProvides(community, ICommunity)
        directlyProvides(office, ICommunity)

        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        request.layout_manager = mock.Mock()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.views.interfaces import IAdvancedSearchResultsDisplay
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        karltesting.registerAdapter(DummySearchResultsDisplay,
                                (Interface, Interface),
                                IAdvancedSearchResultsDisplay)

        import karl.views.api
        save_community = karl.views.api.TemplateAPI.community_layout
        save_generic = karl.views.api.TemplateAPI.generic_layout
        try:
            karl.views.api.TemplateAPI.community_layout = 'COMMUNITY'
            karl.views.api.TemplateAPI.generic_layout = 'GENERIC'

            # not on community
            result = self._callFUT(root, request)
            self.assertEqual(result['community'], None)
            self.assertEqual(result['old_layout'], 'GENERIC')
            self.assertEqual(result['show_search_knobs'], False)

            # normal community
            result = self._callFUT(community, request)
            self.assertEqual(result['community'], 'citizens')
            self.assertEqual(result['old_layout'], 'COMMUNITY')
            self.assertEqual(result['show_search_knobs'], False)

            # office (generic layout, ie, wide here)
            result = self._callFUT(office, request)
            self.assertEqual(result['community'], 'all rights')
            self.assertEqual(result['old_layout'], 'GENERIC')
            self.assertEqual(result['show_search_knobs'], False)

        finally:
            karl.views.api.TemplateAPI.community_layout = save_community
            karl.views.api.TemplateAPI.generic_layout = save_generic




class GetBatchTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.search import get_batch
        return get_batch(context, request)

    def test_without_kind_with_terms(self):
        from webob.multidict import MultiDict
        from karl.models.interfaces import ICatalogSearch
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

    def test_without_kind_with_path(self):
        from webob.multidict import MultiDict
        from karl.models.interfaces import ICatalogSearch
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo'}))
        root = testing.DummyModel()
        context = testing.DummyModel()
        root['foo'] = context
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

    def test_without_kind_without_terms(self):
        from webob.multidict import MultiDict
        from karl.models.interfaces import ICatalogSearch
        karltesting.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        request = testing.DummyRequest(params=MultiDict({}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result, (None, []))

    def test_with_kind_with_body(self):
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerListItem
        from webob.multidict import MultiDict
        content = DummyContent()
        def search_factory(*arg, **kw):
            return DummySearchFactory(content)
        registerListItem(IGroupSearchFactory, search_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        karltesting.registerAdapter(DummySearch, (Interface), ICatalogSearch)
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'dummy1'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

    def test_bad_kind_with_body(self):
        from webob.multidict import MultiDict
        from pyramid.httpexceptions import HTTPBadRequest
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'doesntexist'}))
        context = testing.DummyModel()
        self.assertRaises(HTTPBadRequest, self._callFUT, context, request)

    def test_with_kind_without_body(self):
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerListItem
        from webob.multidict import MultiDict
        def dummy_factory(context, request, term):
            def results():
                return 0, [], None
            results.criteria = {'foo': 'bar'}
            return results
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        karltesting.registerAdapter(DummySearch, (Interface), ICatalogSearch)
        request = testing.DummyRequest(
            params=MultiDict({'kind':'dummy1'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

class MakeQueryTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, params):
        from webob.multidict import MultiDict
        from karl.views.search import make_query
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict(params))
        return make_query(context, request)

    def test_no_fields(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({})
        self.assertEqual(query, {
            'interfaces': {
                'operator': 'or',
                'query': [IContent]},
            'allowed': {'operator': 'or', 'query': []}})

    def test_body_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'body': 'yo'})
        self.assertEqual(query['texts'], 'yo')
        self.assertEqual(query['sort_index'], 'texts')
        self.assertEqual(terms, ['yo'])

    def test_creator_field(self):
        from zope.interface import Interface
        from zope.interface import implements
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import IProfile

        searched_for = {}

        class Profile:
            implements(IProfile)
        profile = Profile()
        profile.__name__ = 'admin'

        class ProfileSearch:
            def __init__(self, context):
                pass
            def __call__(self, **kw):
                searched_for.update(kw)
                return 1, [1], lambda x: profile

        karltesting.registerAdapter(ProfileSearch, (Interface),
                                ICatalogSearch)
        query, terms = self._callFUT({'creator': 'Ad'})
        self.assertEquals(searched_for,
            {'texts': 'Ad', 'interfaces': [IProfile]})
        from repoze.lemonade.interfaces import IContent
        self.assertEqual(query['creator'],
                         {'query': ['admin'], 'operator': 'or'})
        self.assertEqual(terms, ['Ad'])

    def test_tags_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'tags': 'a'})
        self.assertEqual(query['tags'], {'query': ['a'], 'operator': 'or'})
        self.assertEqual(terms, ['a'])

    def test_year_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'year': '1990'})
        self.assertEqual(query['creation_date'], (6311520, 6626483))
        self.assertEqual(terms, [1990])

class IDummyContent(Interface):
    taggedValue('name', 'dummy')
    taggedValue('icon', 'dummy.png')

class DummyContent(testing.DummyModel):
    implements(IDummyContent)
    import datetime
    title = 'Dummy Content'
    creator = 'tweedle dee'
    modified = datetime.datetime(2010, 5, 12, 2, 42)

class DummyCommunityContent(DummyContent):
    from karl.models.interfaces import ICommunity
    implements(ICommunity)

dummycontent = DummyCommunityContent()

class DummySearch:
    content = dummycontent
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        return 1, [1], lambda x: self.content

class DummySearchResultsDisplay:
    display_data = {}
    macro = 'searchresults_generic'
    def __init__(self, context, request):
        pass

class DummyEmptySearch:
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        return 0, [], lambda x: None

class ParseErrorSearch:
    def __init__(self, context):
        pass
    def __call__(self, texts, **kw):
        from zope.index.text.parsetree import ParseError
        raise ParseError("'%s' is nonsense" % texts)

class DummySearchFactory:
    criteria = {'foo': 'bar'}
    def __init__(self, content):
        self.content = content
    def get_batch(self):
        return {'entries':[self.content], 'total':1}

class DummyGroupSearchFactory:
    limit = 5
    def __init__(self, resolver):
        self.resolver = resolver
    def __call__(self):
        return self.limit, range(self.limit), self.resolver

class DummyFileAdapter(object):
    def __init__(self, context, request):
        pass
    mimeinfo = dict(small_icon_name='imgpath.png')
