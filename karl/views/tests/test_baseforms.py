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

class TestUsernameLookupValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_valid(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UsernameLookup
        val = UsernameLookup(not_empty=True, strip=True)
        state = AppState(profiles={})
        got = val.to_python("me", state)
        self.assertEqual(got, "me")

    def test_valid_with_trailing_spaces(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UsernameLookup
        val = UsernameLookup(not_empty=True, strip=True)
        state = AppState(profiles={})
        got = val.to_python("me \r\n ", state)
        self.assertEqual(got, "me")

    def test_no_spaces(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UsernameLookup
        from formencode.validators import Invalid
        val = UsernameLookup(not_empty=True, strip=True)
        state = AppState(profiles={})
        self.assertRaises(Invalid, val.to_python, "a b", state)

    def test_acceptable_characters(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UsernameLookup
        from formencode.validators import Invalid
        val = UsernameLookup(not_empty=True, strip=True)
        state = AppState(profiles={})
        self.assertRaises(Invalid, val.to_python, "a&b", state)

    def test_conflict(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UsernameLookup
        from formencode.validators import Invalid
        val = UsernameLookup(not_empty=True, strip=True)
        state = AppState(profiles={'me': 1})
        self.assertRaises(Invalid, val.to_python, "me", state)


class TestFieldsMatchValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_valid(self):
        from karl.views.baseforms import StartEndFields
        import datetime
        val = StartEndFields(start_field="start", end_field="end")
        val.to_python(dict(
            start = datetime.datetime(2008,1,1),
            end = datetime.datetime(2008,1,2),
            ))

    def test_invalid(self):
        from karl.views.baseforms import StartEndFields
        import datetime
        from formencode import validators
        val = StartEndFields(start_field="start", end_field="end")
        self.assertRaises(validators.Invalid, val.to_python, dict(
            start = datetime.datetime(2008,1,2),
            end = datetime.datetime(2008,1,1),
            ))

class TestUniqueEmailValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()
        
    def test_valid(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UniqueEmail
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerAdapter
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        registerAdapter(DummyCatalogSearch, Interface, ICatalogSearch)
        
        state = AppState(context=DummyModel(email="tres@example.org"))
        val = UniqueEmail()
        val.to_python("paul@example.org", state)
        
    def test_no_conflict_with_self(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UniqueEmail
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerAdapter
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        registerAdapter(DummyCatalogSearch, Interface, ICatalogSearch)
        
        state = AppState(context=DummyModel(email="tres@example.org"))
        val = UniqueEmail()
        val.to_python("tres@example.org", state)
        
    def test_invalid(self):
        from formencode.validators import Invalid
        from karl.views.baseforms import AppState
        from karl.views.baseforms import UniqueEmail
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerAdapter
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        registerAdapter(DummyCatalogSearch, Interface, ICatalogSearch)
        
        state = AppState(context=DummyModel(email="tres@example.org"))
        val = UniqueEmail()
        self.assertRaises(Invalid, val.to_python, "chris@example.org", state)
    
class TestHomePathValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_valid(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import HomePath
        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerModels
        registerModels({'item0': DummyModel()})
        state = AppState(context=DummyModel())
        val = HomePath()
        val.to_python("item0", state)

    def test_invalid_path(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import HomePath
        from repoze.bfg.testing import DummyModel
        from formencode.validators import Invalid
        from repoze.bfg.testing import registerModels
        registerModels({})
        state = AppState(context=DummyModel())
        val = HomePath()
        self.assertRaises(Invalid, val.to_python, "item0", state)

    def test_avoid_circular_redirect(self):
        from karl.views.baseforms import AppState
        from karl.views.baseforms import HomePath
        from repoze.bfg.testing import DummyModel
        from formencode.validators import Invalid
        from repoze.bfg.testing import registerModels
        site = DummyModel()
        registerModels({'//': site})
        state = AppState(context=site)
        val = HomePath()
        self.assertRaises(Invalid, val.to_python, "//", state)

class DummyCatalogSearch(object):
    def __init__(self, context):
        self.context = context
        self.searches = []
        
    def __call__(self, **kw):
        self.searches.append(kw)
        email = kw["email"][0]
        n = int(email == "chris@example.org" or email == "tres@example.org")
        return n, None, None
    