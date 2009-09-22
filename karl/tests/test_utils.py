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

class TestUtilFunctions(unittest.TestCase):
    def test_find_users(self):
        from karl.utils import find_users
        context = testing.DummyModel()
        self.assertEqual(find_users(context), None)
        context.users = '1'
        self.assertEqual(find_users(context), '1')

    def test_find_catalog(self):
        from karl.utils import find_catalog
        context = testing.DummyModel()
        self.assertEqual(find_catalog(context), None)
        context.catalog = '1'
        self.assertEqual(find_catalog(context), '1')
        
    def test_find_tags(self):
        from karl.utils import find_tags
        context = testing.DummyModel()
        self.assertEqual(find_tags(context), None)
        context.tags = '1'
        self.assertEqual(find_tags(context), '1')
        
    def test_find_profiles(self):
        from karl.utils import find_profiles
        context = testing.DummyModel()
        self.assertEqual(find_profiles(context), None)
        pf = context['profiles'] = testing.DummyModel()
        self.failUnless(find_profiles(context) is pf)
        
    def test_find_communities(self):
        from karl.utils import find_communities
        context = testing.DummyModel()
        self.assertEqual(find_communities(context), None)
        cf = context['communities'] = testing.DummyModel()
        self.failUnless(find_communities(context) is cf)

    def test_find_peopledirectory_catalog(self):
        from karl.utils import find_peopledirectory_catalog
        context = testing.DummyModel()
        self.assertEqual(find_peopledirectory_catalog(context), None)
        people = context['people'] = testing.DummyModel()
        people.catalog = testing.DummyModel()
        self.failUnless(
            find_peopledirectory_catalog(context) is people.catalog)

    def test_get_session(self):
        from karl.utils import get_session
        context = testing.DummyModel()
        session = testing.DummyModel()
        sessions = testing.DummyModel()
        sessions['abc'] = session
        context.sessions = sessions
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = 'abc'
        result = get_session(context, request)
        self.assertEqual(result, session)

    def test_docid_to_hex(self):
        from karl.utils import docid_to_hex
        from karl.utils import _MAX_32BIT_INT
        self.assertEqual(docid_to_hex(0), '7FFFFFFF')
        self.assertEqual(docid_to_hex(_MAX_32BIT_INT), 'FFFFFFFE')
        self.assertEqual(docid_to_hex(-_MAX_32BIT_INT), '00000000')

    def test_hex_to_docid(self):
        from karl.utils import hex_to_docid
        from karl.utils import _MAX_32BIT_INT
        self.assertEqual(hex_to_docid('7FFFFFFF'), 0)
        self.assertEqual(hex_to_docid('FFFFFFFE'), _MAX_32BIT_INT)
        self.assertEqual(hex_to_docid('00000000'), -_MAX_32BIT_INT)

    def test_coarse_datetime_repr(self):
        import datetime
        from karl.utils import coarse_datetime_repr
        self.assertEqual(coarse_datetime_repr(
            datetime.datetime(2009, 2, 13, 23, 31, 30)), 12345678)
        self.assertEqual(coarse_datetime_repr(
            datetime.datetime(2009, 2, 13, 23, 31, 31)), 12345678)
        self.assertEqual(coarse_datetime_repr(
            datetime.datetime(2009, 2, 13, 23, 31, 40)), 12345679)


class TestDebugSearch(unittest.TestCase):
    def _callFUT(self, context, **kw):
        from karl.utils import debugsearch
        return debugsearch(context, **kw)

    def test_it(self):
        from karl.models.interfaces import ICatalogSearch
        def searcher(context):
            def search(**kw):
                return 1, [1], lambda *arg: None
            return search
        testing.registerAdapter(searcher, provides=ICatalogSearch)
        context = testing.DummyModel()
        result = self._callFUT(context)
        self.assertEqual(result, (1, [None]))

class TestGetSession(unittest.TestCase):
    def _callFUT(self, context, request):
        from karl.utils import get_session
        return get_session(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        context.sessions = testing.DummyModel()
        foo = testing.DummyModel()
        context.sessions['foo'] = foo
        request.environ = {'repoze.browserid':'foo'}
        result = self._callFUT(context, request)
        self.assertEqual(result, foo)


