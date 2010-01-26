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

class TestFieldsMatchValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from karl.views.baseforms import StartEndFields
        validator = StartEndFields(start_field="start", 
                        end_field="end", 
                        all_day_field="allDay"
                    )
        return validator

    def test_valid(self):
        import datetime
        val = self._makeOne()
        val.to_python(dict(
            start = datetime.datetime(2008,1,1),
            end   = datetime.datetime(2008,1,2),
            allDay = False
            ))

    def test_invalid_when_end_date_is_before_start(self):
        import datetime
        from formencode import validators
        val = self._makeOne()
        self.assertRaises(validators.Invalid, val.to_python, dict(
            start = datetime.datetime(2008,1,2),
            end   = datetime.datetime(2008,1,1),
            allDay = False
            ))

    def test_invalid_when_duration_is_less_than_one_minute(self):
        import datetime
        from formencode import validators
        val = self._makeOne()
        self.assertRaises(validators.Invalid, val.to_python, dict(
            start = datetime.datetime(2008,1,1,0,0,0),
            end   = datetime.datetime(2008,1,1,0,0,0),
            allDay = False
            ))

    def test_adjusts_dates_when_all_day_flag_is_set(self):
        import datetime
        fields = dict(
            start = datetime.datetime(2008,1,1,1,2,3),
            end   = datetime.datetime(2008,1,2,4,5,6),
            allDay = True
        )
        val = self._makeOne()
        val.to_python(fields)
        self.assertEqual(fields['start'], 
                         datetime.datetime(2008,1,1,0,0,0))
        self.assertEqual(fields['end'],
                         datetime.datetime(2008,1,3,0,0,0))

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
    
