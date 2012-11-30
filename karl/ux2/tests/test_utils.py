# Copyright (C) 2008-2012 Open Society Institute
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
#from karl import testing as karltesting

class JsonDictTests(unittest.TestCase):

    def Class(self, *arg, **kw):
        from karl.ux2.utils import JsonDict
        return JsonDict(*arg, **kw)

    def test_it(self):
        d = self.Class({
            'a': 'anything',
            'b': 1,
            'c': True,
            'd': None,
            })
        self.assertEqual(d['a'], 'anything')
        self.assertEqual(d['b'], 1)
        self.assertEqual(d['c'], True)
        self.assertEqual(d['d'], None)
        self.assertEqual(str(d),
            '{"a": "anything", "c": true, "b": 1, "d": null}')

    def test_deeper(self):
        d = self.Class({
            'a': {'b': 1, 'c': True, 'd': None},
            })
        self.assertEqual(d['a'], {'b': 1, 'c': True, 'd': None})
        self.assertEqual(str(d),
            '{"a": {"c": true, "b": 1, "d": null}}')


class JsonListTests(unittest.TestCase):

    def Class(self, *arg, **kw):
        from karl.ux2.utils import JsonList
        return JsonList(*arg, **kw)

    def test_it(self):
        l = self.Class([
            'anything',
            1,
            True,
            None,
            ])
        self.assertEqual(l[0], 'anything')
        self.assertEqual(l[1], 1)
        self.assertEqual(l[2], True)
        self.assertEqual(l[3], None)
        self.assertEqual(str(l),
            '["anything", 1, true, null]')

    def test_deeper(self):
        l = self.Class([
            {'b': 1, 'c': True, 'd': None},
            ])
        self.assertEqual(l[0], {'b': 1, 'c': True, 'd': None})
        self.assertEqual(str(l),
            '[{"c": true, "b": 1, "d": null}]')


class MyProfilePushdownTests(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import cleanUp
        cleanUp()
        from karl.models.interfaces import ICommunity
        self.site = testing.DummyModel()
        self.communities = self.site["communities"] = testing.DummyModel()
        self.community1 = self.communities["community1"] = testing.DummyModel(
            __provides__=(ICommunity, )
        )
        self.community1.title = "Test Community 1"

    def tearDown(self):
        from pyramid.testing import cleanUp
        cleanUp()

    def call_FUT(self, context, request):
        from karl.ux2.utils import searchbox_scope_options
        return searchbox_scope_options(context, request)

    def test_in_root(self):
        request = testing.DummyRequest()
        result = self.call_FUT(self.site, request)
        self.assertEqual(result, [{
            'path': '',
            'selected': True,
            'name': 'all KARL',
            'label': 'all KARL',
        }])

    def test_in_community(self):
        request = testing.DummyRequest()
        result = self.call_FUT(self.community1, request)
        self.assertEqual(result, [{
            'path': '',
            'selected': True,
            'name': 'all KARL',
            'label': 'all KARL',
        }, {
            'path': '/communities/community1',
            'name': 'this community',
            'label': 'Test Community 1',
        }])
