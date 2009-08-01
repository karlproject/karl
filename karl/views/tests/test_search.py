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
from zope.interface import implements
from zope.interface import Interface
from zope.interface import taggedValue
from zope.testing.cleanup import cleanUp

class JQueryLivesearchViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.search import jquery_livesearch_view
        return jquery_livesearch_view(context, request)

    def test_no_parameter(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '400 Bad Request')


    def test_with_parameter_noresults(self):
        def dummy_factory(context, request, term):
            def results():
                return 0, [], None
            return results
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        context = testing.DummyModel()
        request = testing.DummyRequest()
        dummycontent = testing.DummyModel()
        request.params = {
            'val': 'somesearch',
            }
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['rowclass'], 'showall')
        self.assertEqual(results[0]['header'], '')
        self.assertEqual(results[0]['title'], 'Show All')
        self.assertEqual(results[1]['header'], 'Dummy1')
        self.assertEqual(results[1]['title'], 'No Result')

    def test_with_parameter_withresults(self):
        def dummy_factory1(context, request, term):
            pass
        def dummy_factory2(context, request, term):
            def results():
                return 1, [1], lambda x: testing.DummyModel(title='yo')
            return results
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        registerListItem(IGroupSearchFactory, dummy_factory1, 'dummy1',
                         title='Dummy1', sort_key=1)
        registerListItem(IGroupSearchFactory, dummy_factory2, 'dummy2',
                         title='Dummy2', sort_key=2)
        context = testing.DummyModel()
        request = testing.DummyRequest()
        dummycontent = testing.DummyModel()
        request.params = {
            'val': 'somesearch',
            }
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['rowclass'], 'showall')
        self.assertEqual(results[0]['header'], '')
        self.assertEqual(results[0]['title'], 'Show All')
        self.assertEqual(results[1]['header'], 'Dummy2')
        self.assertEqual(results[1]['title'], 'yo')
        self.assertEqual(response.content_type, 'application/x-json')

    def test_with_prefix_match(self):
        terms = []
        def dummy_factory(context, request, term):
            terms.append(term)
            def results():
                return 0, [], None
            return results
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        context = testing.DummyModel()
        request = testing.DummyRequest()
        dummycontent = testing.DummyModel()
        request.params = {
            'val': 'somesearch',
            }
        self._callFUT(context, request)
        self.assertEqual(terms, ['somesearch*'])

    def test_with_phrase_match(self):
        terms = []
        def dummy_factory(context, request, term):
            terms.append(term)
            def results():
                return 0, [], None
            return results
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        context = testing.DummyModel()
        request = testing.DummyRequest()
        dummycontent = testing.DummyModel()
        request.params = {
            'val': 'some search',
            }
        self._callFUT(context, request)
        self.assertEqual(terms, ['"some search"'])

class SearchResultsViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.search import searchresults_view
        return searchresults_view(context, request)

    def test_no_searchterm(self):
        from webob import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict())
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummyEmptySearch, (Interface),
                                ICatalogSearch)
        renderer = testing.registerDummyRenderer('templates/searchresults.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.terms, [])

    def test_bad_kind(self):
        from webob import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=MultiDict({'kind':'unknown', 'body':'yo'}))
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from webob.exc import HTTPBadRequest
        testing.registerAdapter(DummyEmptySearch, (Interface),
                                ICatalogSearch)
        self.assertRaises(HTTPBadRequest, self._callFUT, context, request)

    def test_none_kind(self):
        from webob import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        renderer = testing.registerDummyRenderer('templates/searchresults.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.terms, ['yo'])
        self.assertEqual(len(renderer.results), 1)

    def test_known_kind(self):
        from webob import MultiDict
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerContentFactory
        from zope.interface import Interface
        content = DummyContent()
        def search_factory(*arg, **kw):
            return DummySearchFactory(content)
        testing.registerUtility(
            search_factory, IGroupSearchFactory, name='People')
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'People'}))
        from karl.models.interfaces import ICatalogSearch
        registerContentFactory(DummyContent, IDummyContent)
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        renderer = testing.registerDummyRenderer('templates/searchresults.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.terms, ['yo', 'People'])
        self.assertEqual(len(renderer.results), 1)

    def test_community_search(self):
        context = testing.DummyModel()
        context.title = 'Citizens'
        from webob import MultiDict
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        renderer = testing.registerDummyRenderer('templates/searchresults.pt')
        response = self._callFUT(context, request)
        self.assertEqual(renderer.community, 'Citizens')
        self.assertEqual(renderer.terms, ['yo'])
        self.assertEqual(len(renderer.results), 1)

    def test_parse_error(self):
        from webob import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'the'}))
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        testing.registerAdapter(ParseErrorSearch, (Interface),
                                ICatalogSearch)
        renderer = testing.registerDummyRenderer('templates/searchresults.pt')
        response = self._callFUT(context, request)
        self.assertEqual(len(renderer.terms), 0)
        self.assertEqual(len(renderer.results), 0)
        self.assertEqual(renderer.error, "Error: 'the' is nonsense")

class GetBatchTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.search import get_batch
        return get_batch(context, request)

    def test_without_kind_with_terms(self):
        from webob import MultiDict
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

    def test_without_kind_without_terms(self):
        from webob import MultiDict
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        request = testing.DummyRequest(params=MultiDict({}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result, (None, []))

    def test_with_kind_with_body(self):
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerListItem
        from webob import MultiDict
        content = DummyContent()
        def search_factory(*arg, **kw):
            return DummySearchFactory(content)
        registerListItem(IGroupSearchFactory, search_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'dummy1'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

    def test_bad_kind_with_body(self):
        from webob import MultiDict
        from webob.exc import HTTPBadRequest
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'doesntexist'}))
        context = testing.DummyModel()
        self.assertRaises(HTTPBadRequest, self._callFUT, context, request)

    def test_with_kind_without_body(self):
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerListItem
        from webob import MultiDict
        def dummy_factory(context, request, term):
            def results():
                return 0, [], None
            return results
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy1',
                         title='Dummy1', sort_key=1)
        request = testing.DummyRequest(
            params=MultiDict({'kind':'dummy1'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result,  (None, ()))

class MakeQueryTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, params):
        from webob import MultiDict
        from karl.views.search import make_query
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict(params))
        return make_query(context, request)

    def test_body_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'body': 'yo'})
        self.assertEqual(query, {'texts': 'yo', 'interfaces': [IContent]})
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

        testing.registerAdapter(ProfileSearch, (Interface),
                                ICatalogSearch)
        query, terms = self._callFUT({'creator': 'Ad'})
        self.assertEquals(searched_for,
            {'texts': 'Ad', 'interfaces': [IProfile]})
        from repoze.lemonade.interfaces import IContent
        self.assertEqual(query, {
            'creator': {'query': ['admin'], 'operator': 'or'},
            'interfaces': [IContent],
            })
        self.assertEqual(terms, ['Ad'])

    def test_types_field(self):
        from karl.models.interfaces import IComment
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IComment)

        query, terms = self._callFUT(
            {'types': 'karl_models_interfaces_IComment'})
        self.assertEqual(query, {'interfaces':
            {'query': [IComment], 'operator': 'or'}})
        self.assertEqual(terms, ['Comment'])

    def test_tags_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'tags': 'a'})
        self.assertEqual(query, {
            'interfaces': [IContent],
            'tags': {'query': ['a'], 'operator': 'or'},
            })
        self.assertEqual(terms, ['a'])

    def test_year_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'year': '1990'})
        self.assertEqual(query,
            {'creation_date': (6311520, 6626483), 'interfaces': [IContent]})
        self.assertEqual(terms, [1990])


class AdvancedSearchViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_advancedsearch_view(self):
        from karl.models.interfaces import IComment
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IComment)

        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/advancedsearch.pt')
        from karl.views.search import advancedsearch_view
        result = advancedsearch_view(context, request)
        self.assertEqual(
            renderer.post_url, 'http://example.com/searchresults.html')
        self.assertEqual(renderer.type_choices, [
            ('Comment', 'karl_models_interfaces_IComment'),
            ])
        self.assertFalse('2006' in renderer.year_choices)
        self.assertTrue('2007' in renderer.year_choices)


class DummySearch:
    def __init__(self, context):
        pass
    def __call__(self, **kw):
        return 1, [1], lambda x: dummycontent

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
    def __init__(self, content):
        self.content = content
    def get_batch(self):
        return {'entries':[self.content], 'total':1}

class IDummyContent(Interface):
    taggedValue('name', 'dummy')

class DummyContent(testing.DummyModel):
    implements(IDummyContent)

dummycontent = DummyContent()

