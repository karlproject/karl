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
from repoze.bfg.testing import cleanUp

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
        request.params = {
            'val': 'somesearch',
            }
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(len(results), 0)

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
        request.params = {
            'val': 'somesearch',
            }
        def dummy_adapter(context, request):
            return dict(title=context.title)
        from karl.views.interfaces import ILiveSearchEntry
        testing.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'yo')
        self.assertEqual(response.content_type, 'application/json')

    def test_with_parameter_withresults_withkind(self):
        def dummy_factory(context, request, term):
            def results():
                return 1, [1], lambda x: testing.DummyModel(title='yo')
            return results
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
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
        from karl.views.interfaces import ILiveSearchEntry
        testing.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'yo')
        self.assertEqual(response.content_type, 'application/json')

    def test_with_parameter_withresults_withbadkind(self):
        def dummy_factory(context, request, term):
            def results():
                return 1, [1], lambda x: testing.DummyModel(title='yo')
            return results
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
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
        def dummy_factory(context, request, term):
            return DummyGroupSearchFactory(
                lambda x: testing.DummyModel(title='yo'))
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
        registerListItem(IGroupSearchFactory, dummy_factory, 'dummy',
                         title='Dummy')
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {
            'val': 'somesearch',
            }
        def dummy_adapter(context, request):
            return dict(title=context.title)
        from karl.views.interfaces import ILiveSearchEntry
        testing.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(results), 5)

    def test_numresults_withkind(self):
        def dummy_factory(context, request, term):
            return DummyGroupSearchFactory(
                lambda x: testing.DummyModel(title='yo'))
        from repoze.lemonade.testing import registerListItem
        from karl.models.interfaces import IGroupSearchFactory
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
        from karl.views.interfaces import ILiveSearchEntry
        testing.registerAdapter(dummy_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ILiveSearchEntry)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        from simplejson import loads
        results = loads(response.body)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(results), 10)


class LiveSearchEntryAdapterTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_generic_adapter(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import generic_livesearch_result
        result = generic_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('http://example.com/foo/', result['url'])

    def test_profile_adapter_defaultimg(self):
        context = testing.DummyModel(title='foo',
                                     extension='x1234',
                                     email='foo@example.com',
                                     department='science',
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import profile_livesearch_result
        result = profile_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('x1234', result['extension'])
        self.assertEqual('foo@example.com', result['email'])
        self.failUnless(result['thumbnail'].endswith('/images/defaultUser.gif'))
        self.assertEqual('science', result['department'])
        self.assertEqual('profile', result['type'])
        self.assertEqual('profile', result['category'])

    def test_profile_adapter_customimg(self):
        from karl.content.interfaces import IImage
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='foo',
                                     extension='x1234',
                                     email='foo@example.com',
                                     department='science',
                                     )
        dummyphoto = testing.DummyModel(title='photo')
        alsoProvides(dummyphoto, IImage)
        context['photo'] = dummyphoto
        request = testing.DummyRequest()
        from karl.views.adapters import profile_livesearch_result
        result = profile_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('x1234', result['extension'])
        self.assertEqual('foo@example.com', result['email'])
        self.assertEqual('http://example.com/photo/thumb/85x85.jpg',
                         result['thumbnail'])
        self.assertEqual('science', result['department'])
        self.assertEqual('profile', result['type'])
        self.assertEqual('profile', result['category'])

    def test_page_adapter_withnocommunity(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     modified_by='johnny',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import page_livesearch_result
        result = page_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('johnny', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual(None, result['community'])
        self.assertEqual('page', result['type'])
        self.assertEqual('page', result['category'])

    def test_page_adapter_withcommunity(self):
        from datetime import datetime
        from karl.models.interfaces import ICommunity
        from zope.interface import alsoProvides
        root = testing.DummyModel(title='nice community')
        alsoProvides(root, ICommunity)
        context = testing.DummyModel(__name__='foo',
                                     __parent__=root,
                                     title='foo',
                                     modified_by='johnny',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import page_livesearch_result
        result = page_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('johnny', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual('nice community', result['community'])
        self.assertEqual('page', result['type'])
        self.assertEqual('page', result['category'])

    def test_page_adapter_withoffice(self):
        from datetime import datetime
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IIntranets
        from zope.interface import alsoProvides
        root = testing.DummyModel(title='nice office')
        alsoProvides(root, ICommunity)
        alsoProvides(root, IIntranets)
        context = testing.DummyModel(__name__='foo',
                                     __parent__=root,
                                     title='foo',
                                     modified_by='johnny',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import page_livesearch_result
        result = page_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('johnny', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual(None, result['community'])
        self.assertEqual('page', result['type'])
        self.assertEqual('page', result['category'])

    def test_reference_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     modified_by='biff',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import reference_livesearch_result
        result = reference_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('biff', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual('page', result['type'])
        self.assertEqual('reference', result['category'])

    def test_blogentry_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     modified_by='marty',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import blogentry_livesearch_result
        result = blogentry_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('marty', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual(None, result['community'])
        self.assertEqual('post', result['type'])
        self.assertEqual('blogentry', result['category'])

    def test_comment_adapter_noparents(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     creator='michael',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import comment_livesearch_result
        result = comment_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('michael', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual(None, result['community'])
        self.assertEqual(None, result['forum'])
        self.assertEqual(None, result['blog'])
        self.assertEqual('post', result['type'])
        self.assertEqual('comment', result['category'])

    def test_comment_adapter_withparents(self):
        from zope.interface import alsoProvides
        from datetime import datetime
        from karl.content.interfaces import IForum
        from karl.content.interfaces import IBlogEntry
        from karl.models.interfaces import ICommunity
        root = testing.DummyModel(title='object title')
        # cheat here and have the object implement all the interfaces we expect
        alsoProvides(root, IForum)
        alsoProvides(root, ICommunity)
        alsoProvides(root, IBlogEntry)
        context = testing.DummyModel(__parent__=root,
                                     title='foo',
                                     creator='michael',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import comment_livesearch_result
        result = comment_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('michael', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual('object title', result['community'])
        self.assertEqual('object title', result['forum'])
        self.assertEqual('object title', result['blog'])
        self.assertEqual('post', result['type'])
        self.assertEqual('comment', result['category'])

    def test_forum_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     creator='sarah',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import forum_livesearch_result
        result = forum_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('sarah', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual('post', result['type'])
        self.assertEqual('forum', result['category'])

    def test_forumtopic_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     creator='sarah',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import forumtopic_livesearch_result
        result = forumtopic_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('sarah', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual(None, result['forum'])
        self.assertEqual('post', result['type'])
        self.assertEqual('forumtopic', result['category'])

    def test_file_adapter(self):
        from datetime import datetime
        from karl.content.views.interfaces import IFileInfo
        context = testing.DummyModel(title='foo',
                                     modified_by='susan',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        class FileDummyAdapter(object):
            def __init__(self, context, request):
                pass
            mimeinfo = dict(small_icon_name='imgpath.png')

        testing.registerAdapter(FileDummyAdapter,
                                (testing.DummyModel, testing.DummyRequest),
                                IFileInfo)

        from karl.views.adapters import file_livesearch_result
        result = file_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('susan', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual('file', result['type'])
        self.assertEqual('file', result['category'])
        self.assertEqual(None, result['community'])
        self.failUnless(result['icon'].endswith('/imgpath.png'))

    def test_community_adapter(self):
        from zope.interface import alsoProvides
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel(title='foo',
                                     number_of_members=7,
                                     )
        def dummy_communityinfo_adapter(context, request):
            return context
        testing.registerAdapter(dummy_communityinfo_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ICommunityInfo)
        request = testing.DummyRequest()
        from karl.views.adapters import community_livesearch_result
        result = community_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual(7, result['num_members'])
        self.assertEqual('community', result['type'])
        self.assertEqual('community', result['category'])

    def test_calendar_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     startDate=datetime(1985, 1, 1),
                                     endDate=datetime(1985, 2, 1),
                                     location='mars',
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import calendar_livesearch_result
        result = calendar_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('1985-01-01T00:00:00', result['start'])
        self.assertEqual('1985-02-01T00:00:00', result['end'])
        self.assertEqual('mars', result['location'])
        self.assertEqual(None, result['community'])
        self.assertEqual('calendarevent', result['type'])
        self.assertEqual('calendarevent', result['category'])


class SearchResultsViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        testing.registerDummyRenderer('karl.views:templates/generic_layout.pt')
        testing.registerDummyRenderer(
            'karl.views:templates/community_layout.pt')

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.search import searchresults_view
        return searchresults_view(context, request)

    def test_no_searchterm(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict())
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(DummyEmptySearch, (Interface),
                                ICatalogSearch)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], [])

    def test_bad_kind(self):
        from webob.multidict import MultiDict
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
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'yo'}))
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo'])
        self.assertEqual(len(result['results']), 1)

    def test_known_kind(self):
        from webob.multidict import MultiDict
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
        result = self._callFUT(context, request)
        self.assertEqual(result['terms'], ['yo', 'People'])
        self.assertEqual(len(result['results']), 1)

    def test_community_search(self):
        context = testing.DummyModel()
        context.title = 'Citizens'
        from webob.multidict import MultiDict
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
        result = self._callFUT(context, request)
        self.assertEqual(result['community'], 'Citizens')
        self.assertEqual(result['terms'], ['yo'])
        self.assertEqual(len(result['results']), 1)

    def test_parse_error(self):
        from webob.multidict import MultiDict
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict({'body':'the'}))
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)
        testing.registerAdapter(ParseErrorSearch, (Interface),
                                ICatalogSearch)
        result = self._callFUT(context, request)
        self.assertEqual(len(result['terms']), 0)
        self.assertEqual(len(result['results']), 0)
        self.assertEqual(result['error'], "Error: 'the' is nonsense")

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
        testing.registerAdapter(DummySearch, (Interface),
                                ICatalogSearch)
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo'}))
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result[0]['total'], 1)

    def test_without_kind_without_terms(self):
        from webob.multidict import MultiDict
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
        from webob.multidict import MultiDict
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
        from webob.multidict import MultiDict
        from webob.exc import HTTPBadRequest
        request = testing.DummyRequest(
            params=MultiDict({'body':'yo', 'kind':'doesntexist'}))
        context = testing.DummyModel()
        self.assertRaises(HTTPBadRequest, self._callFUT, context, request)

    def test_with_kind_without_body(self):
        from karl.models.interfaces import IGroupSearchFactory
        from repoze.lemonade.testing import registerListItem
        from webob.multidict import MultiDict
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
        from webob.multidict import MultiDict
        from karl.views.search import make_query
        context = testing.DummyModel()
        request = testing.DummyRequest(params=MultiDict(params))
        return make_query(context, request)

    def test_body_field(self):
        from repoze.lemonade.interfaces import IContent
        query, terms = self._callFUT({'body': 'yo'})
        self.assertEqual(query, {
            'texts': 'yo',
            'interfaces': [IContent],
            'sort_index': 'texts',
            })
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
        from karl.views.search import advancedsearch_view
        result = advancedsearch_view(context, request)
        self.assertEqual(
            result['post_url'], 'http://example.com/searchresults.html')
        self.assertEqual(result['type_choices'], [
            ('Comment', 'karl_models_interfaces_IComment'),
            ])
        self.assertFalse('2006' in result['year_choices'])
        self.assertTrue('2007' in result['year_choices'])


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

class DummyGroupSearchFactory:
    limit = 5
    def __init__(self, resolver):
        self.resolver = resolver
    def __call__(self):
        return self.limit, range(self.limit), self.resolver

class IDummyContent(Interface):
    taggedValue('name', 'dummy')

class DummyContent(testing.DummyModel):
    implements(IDummyContent)

dummycontent = DummyContent()
