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
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

class TestGetCatalogBatch(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, **kw):
        from karl.views.batch import get_catalog_batch
        return get_catalog_batch(context, request, **kw)

    def _register(self, batch):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        searchkw = {}
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                searchkw.update(kw)
                return len(batch), batch, resolver
            return search
        testing.registerAdapter(dummy_catalog_search, (Interface),
                                ICatalogSearch)
        return searchkw


    def test_defaults(self):
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['entries'], [1,2,3])
        self.assertEqual(info['batch_start'], 0)
        self.assertEqual(info['batch_size'], 20)
        self.assertEqual(info['batch_end'], 3)
        self.assertEqual(info['total'], 3)
        self.assertEqual(info['sort_index'], 'modified_date')
        self.assertEqual(info['reverse'], False)
        self.assertEqual(len(searchkw), 2)
        self.assertEqual(searchkw['reverse'], False)
        self.assertEqual(searchkw['sort_index'], 'modified_date')

    def test_with_texts_and_no_sort_index_adds_index_query_order(self):
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request, texts='abc', other2='hello',
                             other1='yo')
        self.assertEqual(len(searchkw), 4)
        self.assertEqual(searchkw['texts'], 'abc')
        self.assertEqual(searchkw['other1'], 'yo')
        self.assertEqual(searchkw['other2'], 'hello')
        index_query_order = searchkw['index_query_order']
        self.assertEqual(len(index_query_order), 3)
        self.assertEqual(index_query_order[-1], 'texts')
        self.assertEqual(info['sort_index'], None)

    def test_with_texts_and_index_query_order(self):
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest()
        order = ['texts', 'other2', 'other1']
        info = self._callFUT(context, request, texts='abc', other2='hello',
                             other1='yo',
                             index_query_order=order)
        self.assertEqual(len(searchkw), 6)
        self.assertEqual(searchkw['texts'], 'abc')
        self.assertEqual(searchkw['other1'], 'yo')
        self.assertEqual(searchkw['other2'], 'hello')
        self.assertEqual(searchkw['sort_index'], 'modified_date')
        self.assertEqual(searchkw['reverse'], False)
        self.assertEqual(searchkw['index_query_order'], order)

    def test_with_texts_and_sort_index(self):
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest()
        order = ['texts', 'other2', 'other1']
        info = self._callFUT(context, request, texts='abc', other2='hello',
                             other1='yo', sort_index='hello', reverse=True)
        self.assertEqual(len(searchkw), 5)
        self.assertEqual(searchkw['texts'], 'abc')
        self.assertEqual(searchkw['other1'], 'yo')
        self.assertEqual(searchkw['other2'], 'hello')
        self.assertEqual(searchkw['sort_index'], 'hello')
        self.assertEqual(searchkw['reverse'], True)

    def test_overridden(self):
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=dict(batch_start='1', batch_size='10', sort_index='other',
                        reverse='1')
            )
        info = self._callFUT(context, request)
        self.assertEqual(info['entries'], [2,3])
        self.assertEqual(info['batch_start'], 1)
        self.assertEqual(info['batch_size'], 10)
        self.assertEqual(info['batch_end'], 3)
        self.assertEqual(info['total'], 3)
        self.assertEqual(info['sort_index'], 'other')
        self.assertEqual(info['reverse'], True)
        self.assertEqual(len(searchkw), 2)
        self.assertEqual(searchkw['reverse'], True)
        self.assertEqual(searchkw['sort_index'], 'other')

    def test_missing_model(self):
        searchkw = self._register([1,2,3,None])
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=dict(batch_start='1', batch_size='10', sort_index='other',
                        reverse='1')
            )
        info = self._callFUT(context, request)
        self.assertEqual(info['entries'], [2,3])
        self.assertEqual(info['batch_start'], 1)
        self.assertEqual(info['batch_size'], 10)
        self.assertEqual(info['batch_end'], 3)
        self.assertEqual(info['total'], 4)
        self.assertEqual(info['sort_index'], 'other')
        self.assertEqual(info['reverse'], True)
        self.assertEqual(len(searchkw), 2)
        self.assertEqual(searchkw['reverse'], True)
        self.assertEqual(searchkw['sort_index'], 'other')

    def test_overflows_batch(self):
        searchkw = self._register([1,2,3,4,5,6,7])
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=dict(batch_start='0', batch_size='3', sort_index='other',
                        reverse='1')
            )
        info = self._callFUT(context, request)
        self.assertEqual(info['entries'], [1, 2,3])
        self.assertEqual(info['batch_start'], 0)
        self.assertEqual(info['batch_size'], 3)
        self.assertEqual(info['batch_end'], 3)
        self.assertEqual(info['total'], 7)
        self.assertEqual(info['sort_index'], 'other')
        self.assertEqual(info['reverse'], True)
        self.assertEqual(len(searchkw), 2)
        self.assertEqual(searchkw['reverse'], True)
        self.assertEqual(searchkw['sort_index'], 'other')

    def test_batching_urls_next_and_prev(self):
        import urlparse
        from cgi import parse_qs
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest(
            params=dict(batch_start='0', batch_size='2', reverse='1',
                        sort_index='1')
            )
        info = self._callFUT(context, request)
        next_url = info['next_batch']['url']
        next_query = urlparse.urlparse(next_url).query
        next_query = parse_qs(next_query)

        self.assertEqual(next_query['batch_start'], ['2'])
        self.assertEqual(next_query['batch_size'], ['2'])
        self.assertEqual(next_query['sort_index'], ['1'])
        self.assertEqual(next_query['reverse'], ['1'])

        self.assertEqual(info['next_batch']['name'],
                         'Next 1 entries (3 - 3 of about 3)')
        self.assertEqual(info['previous_batch'], None)

        request = testing.DummyRequest(
            params=dict(batch_start='2', batch_size='2', reverse='1',
                        sort_index='1')
            )

        info = self._callFUT(context, request)
        self.assertEqual(info['next_batch'], None)

        previous_url = info['previous_batch']['url']
        previous_query = urlparse.urlparse(previous_url).query
        previous_query = parse_qs(previous_query)

        self.assertEqual(previous_query['batch_start'], ['0'])
        self.assertEqual(previous_query['batch_size'], ['2'])
        self.assertEqual(previous_query['sort_index'], ['1'])
        self.assertEqual(previous_query['reverse'], ['1'])

        self.assertEqual(info['previous_batch']['name'],
                 'Previous 2 entries (1 - 2)')

        request = testing.DummyRequest(
            params=dict(batch_start='1', batch_size='3', reverse='1',
                        sort_index='1')
            )
        info = self._callFUT(context, request)
        self.assertEqual(info['next_batch'], None)
        self.assertEqual(info['previous_batch'], None)
        self.assertEqual(info['batching_required'], False)

        request = testing.DummyRequest(
            params=dict(batch_start='10', batch_size='3', reverse='1',
                        sort_index='1')
            )
        info = self._callFUT(context, request)
        self.assertEqual(info['next_batch'], None)
        previous_url = info['previous_batch']['url']
        previous_query = urlparse.urlparse(previous_url).query
        previous_query = parse_qs(previous_query)

        self.assertEqual(previous_query['batch_start'], ['0'])
        self.assertEqual(previous_query['batch_size'], ['3'])
        self.assertEqual(previous_query['sort_index'], ['1'])
        self.assertEqual(previous_query['reverse'], ['1'])

        self.assertEqual(info['previous_batch']['name'],
                 'Previous 3 entries (1 - 3)')
        self.assertEqual(info['batching_required'], True)


class TestGetCatalogBatchGrid(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.batch import get_catalog_batch_grid
        return get_catalog_batch_grid(context, request)

    def _register(self, batch):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        searchkw = {}
        def dummy_catalog_search(context):
            def resolver(x):
                return x
            def search(**kw):
                searchkw.update(kw)
                return len(batch), batch, resolver
            return search
        testing.registerAdapter(dummy_catalog_search, (Interface),
                                ICatalogSearch)
        return searchkw

    def test_defaults(self):
        searchkw = self._register([1,2,3])
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['entries'], [1,2,3])
        self.assertEqual(info['batch_start'], 0)
        self.assertEqual(info['batch_size'], 20)
        self.assertEqual(info['batch_end'], 3)
        self.assertEqual(info['total'], 3)
        self.assertEqual(info['sort_index'], 'modified_date')
        self.assertEqual(info['reverse'], False)
        self.assertEqual(info['current_page'], 1)
        self.assertEqual(info['last_page'], 1)
        s = info['gridbatch_snippet']
        self.assertTrue('ui-state-default' in s)
        self.assertTrue('ui-state-disabled' in s)

    def test_many_pages(self):
        searchkw = self._register(range(1, 1002))
        context = testing.DummyModel()
        request = testing.DummyRequest({'batch_start': '500'})
        info = self._callFUT(context, request)
        self.assertEqual(info['entries'], range(501, 521))
        self.assertEqual(info['batch_start'], 500)
        self.assertEqual(info['batch_size'], 20)
        self.assertEqual(info['batch_end'], 520)
        self.assertEqual(info['total'], 1001)
        self.assertEqual(info['sort_index'], 'modified_date')
        self.assertEqual(info['reverse'], False)
        self.assertEqual(info['current_page'], 26)
        self.assertEqual(info['last_page'], 51)
        s = info['gridbatch_snippet']
        self.assertTrue('>1<' in s)
        self.assertFalse('>2<' in s)
        self.assertFalse('>22<' in s)
        self.assertTrue('>23<' in s)
        self.assertTrue('>24<' in s)
        self.assertTrue('>25<' in s)
        self.assertTrue('>26<' in s)
        self.assertTrue('>27<' in s)
        self.assertTrue('>28<' in s)
        self.assertTrue('>29<' in s)
        self.assertFalse('>30<' in s)
        self.assertFalse('>50<' in s)
        self.assertTrue('>51<' in s)
        self.assertTrue('>...<' in s)

    def test_unicode(self):
        searchkw = self._register(range(100))
        context = testing.DummyModel()
        request = testing.DummyRequest()
        request.params = {'text': u'smile! \u30b7'}
        info = self._callFUT(context, request)
        s = info['gridbatch_snippet']
        # expect utf-8 and "+" encoding
        self.assertTrue('&text=smile%21+%E3%82%B7' in s)


class TestGetContainerBatch(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, **kw):
        from karl.views.batch import get_container_batch
        return get_container_batch(context, request, **kw)

    def test_no_items(self):
        container = testing.DummyModel()
        request = testing.DummyRequest()
        batch = self._callFUT(container, request)
        self.assertEqual(batch['entries'], [])
        self.assertEqual(batch['batch_start'], 0)
        self.assertEqual(batch['batch_size'], 20)
        self.assertEqual(batch['batch_end'], 0)
        self.assertEqual(batch['total'], 0)
        self.assertEqual(batch['previous_batch'], None)
        self.assertEqual(batch['next_batch'], None)
        self.assertEqual(batch['batching_required'], False)

    def test_few_items(self):
        container = testing.DummyModel()
        container['a'] = testing.DummyModel()
        container['b'] = testing.DummyModel()
        container['c'] = testing.DummyModel()
        request = testing.DummyRequest()
        batch = self._callFUT(container, request)
        self.assertEqual(len(batch['entries']), 3)
        self.assertEqual(batch['batch_start'], 0)
        self.assertEqual(batch['batch_size'], 20)
        self.assertEqual(batch['batch_end'], 3)
        self.assertEqual(batch['total'], 3)
        self.assertEqual(batch['previous_batch'], None)
        self.assertEqual(batch['next_batch'], None)
        self.assertEqual(batch['batching_required'], False)

    def test_many_items(self):
        container = testing.DummyModel()
        for i in range(100):
            container['i%02d' % i] = testing.DummyModel()
        request = testing.DummyRequest({
            'batch_size': 10,
            'batch_start': 60,
            })
        batch = self._callFUT(container, request)
        self.assertEqual(len(batch['entries']), 10)
        self.assertEqual(batch['batch_start'], 60)
        self.assertEqual(batch['batch_size'], 10)
        self.assertEqual(batch['batch_end'], 70)
        self.assertEqual(batch['total'], 100)
        self.assertEqual(batch['previous_batch'], {
            'url': 'http://example.com/?batch_size=10&batch_start=50',
            'name': 'Previous 10 entries (51 - 60)',
            })
        self.assertEqual(batch['next_batch'], {
            'url': 'http://example.com/?batch_size=10&batch_start=70',
            'name': 'Next 10 entries (71 - 80 of about 100)',
            })
        self.assertEqual(batch['batching_required'], True)

    def test_filter_by_interface(self):
        container = testing.DummyModel()
        container['a'] = testing.DummyModel()
        container['b'] = testing.DummyModel()
        from zope.interface import directlyProvides
        from karl.models.interfaces import IComment
        directlyProvides(container['b'], IComment)
        container['c'] = testing.DummyModel()
        request = testing.DummyRequest()
        batch = self._callFUT(container, request, interfaces=[IComment])
        self.assertEqual(len(batch['entries']), 1)
        self.assertEqual(batch['batch_start'], 0)
        self.assertEqual(batch['batch_size'], 20)
        self.assertEqual(batch['batch_end'], 1)
        self.assertEqual(batch['total'], 1)
        self.assertEqual(batch['previous_batch'], None)
        self.assertEqual(batch['next_batch'], None)
        self.assertEqual(batch['batching_required'], False)

    def test_filter_by_function(self):
        container = testing.DummyModel()
        container['a'] = testing.DummyModel()
        container['b'] = testing.DummyModel()
        container['c'] = testing.DummyModel()
        request = testing.DummyRequest()
        def filter_func(name, item):
            return name < 'c'
        batch = self._callFUT(container, request, filter_func=filter_func)
        self.assertEqual(len(batch['entries']), 2)
        self.assertEqual(batch['batch_start'], 0)
        self.assertEqual(batch['batch_size'], 20)
        self.assertEqual(batch['batch_end'], 2)
        self.assertEqual(batch['total'], 2)
        self.assertEqual(batch['previous_batch'], None)
        self.assertEqual(batch['next_batch'], None)
        self.assertEqual(batch['batching_required'], False)

    def test_sort(self):
        from datetime import datetime
        container = testing.DummyModel()
        container.catalog = {'creation_date': DummyCreationDateIndex()}
        container['a'] = testing.DummyModel(created=datetime(2007, 1, 1))
        container['b'] = testing.DummyModel(created=datetime(2008, 1, 1))
        container['c'] = testing.DummyModel(created=datetime(2009, 1, 1))
        request = testing.DummyRequest()
        batch = self._callFUT(
            container, request, sort_index='creation_date', reverse=True)
        self.assertEqual(len(batch['entries']), 3)
        self.assertEqual(
            [o.__name__ for o in batch['entries']], ['c', 'b', 'a'])


class DummyCreationDateIndex:
    def discriminator(self, obj, default):
        return obj.created
