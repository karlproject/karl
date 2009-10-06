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

class TestDiscriminatorFunctions(unittest.TestCase):

    def test_get_lastname_firstletter_on_profile(self):
        from karl.models.peopledirectory import get_lastname_firstletter
        obj = DummyProfile(lastname='Smith')
        self.assertEqual(get_lastname_firstletter(obj, 0), 'S')

    def test_get_lastname_firstletter_on_other(self):
        from karl.models.peopledirectory import get_lastname_firstletter
        obj = testing.DummyModel(lastname='Smith')
        self.assertEqual(get_lastname_firstletter(obj, 0), 0)

    def test_get_department(self):
        from karl.models.peopledirectory import get_department
        obj = DummyProfile(department='Redundant')
        self.assertEqual(get_department(obj, 0), 'redundant')
        obj.department = None
        self.assertEqual(get_department(obj, 0), 0)

    def test_get_email(self):
        from karl.models.peopledirectory import get_email
        obj = DummyProfile(email='xyz@Example.com')
        self.assertEqual(get_email(obj, 0), 'xyz@example.com')
        obj.email = None
        self.assertEqual(get_email(obj, 0), 0)

    def test_get_location(self):
        from karl.models.peopledirectory import get_location
        obj = DummyProfile(location='SLC')
        self.assertEqual(get_location(obj, 0), 'slc')
        obj.location = None
        self.assertEqual(get_location(obj, 0), 0)

    def test_get_organization(self):
        from karl.models.peopledirectory import get_organization
        obj = DummyProfile(organization='Fun')
        self.assertEqual(get_organization(obj, 0), 'fun')
        obj.organization = None
        self.assertEqual(get_organization(obj, 0), 0)

    def test_get_phone(self):
        from karl.models.peopledirectory import get_phone
        obj = DummyProfile(phone='(123) 456-0')
        self.assertEqual(get_phone(obj, 0), '(123) 456-0')
        obj.phone = None
        self.assertEqual(get_phone(obj, 0), 0)

    def test_get_phone_with_extension(self):
        from karl.models.peopledirectory import get_phone
        obj = DummyProfile(phone='(123) 456-0', extension='42')
        self.assertEqual(get_phone(obj, 0), '(123) 456-0 x 42')

    def test_get_position(self):
        from karl.models.peopledirectory import get_position
        obj = DummyProfile(position='Head Boss')
        self.assertEqual(get_position(obj, 0), 'head boss')
        obj.position = None
        self.assertEqual(get_position(obj, 0), 0)

    def test_get_groups_for_profile(self):
        from karl.models.peopledirectory import get_groups
        from karl.testing import DummyUsers
        obj = DummyProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        site.users.add('testuser', 'testuser', '', ['group1'])
        self.assertEqual(get_groups(obj, 0), ['group1'])

    def test_get_groups_for_non_profile(self):
        from karl.models.peopledirectory import get_groups
        from karl.testing import DummyUsers
        obj = testing.DummyModel()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        site.users.add('testuser', 'testuser', '', ['group1'])
        self.assertEqual(get_groups(obj, 0), 0)

    def test_get_groups_for_nonexistent_user(self):
        from karl.models.peopledirectory import get_groups
        from karl.testing import DummyUsers
        obj = DummyProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        self.assertEqual(get_groups(obj, 0), 0)

    def test_is_staff_for_staff(self):
        from karl.models.peopledirectory import is_staff
        from karl.testing import DummyUsers
        obj = DummyProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        site.users.add('testuser', 'testuser', '', ['group.KarlStaff'])
        self.assertEqual(is_staff(obj, ()), True)

    def test_is_staff_for_non_staff(self):
        from karl.models.peopledirectory import is_staff
        from karl.testing import DummyUsers
        obj = DummyProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        site.users.add('testuser', 'testuser', '', [])
        self.assertEqual(is_staff(obj, ()), False)

    def test_is_staff_for_non_profile(self):
        from karl.models.peopledirectory import is_staff
        from karl.testing import DummyUsers
        obj = testing.DummyModel()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        site.users.add('testuser', 'testuser', '', [])
        self.assertEqual(is_staff(obj, ()), ())

    def test_is_staff_for_nonexistent_user(self):
        from karl.models.peopledirectory import is_staff
        from karl.testing import DummyUsers
        obj = DummyProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        self.assertEqual(is_staff(obj, ()), ())

class TestProfileCategoryGetter(unittest.TestCase):

    def test_non_profile(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = testing.DummyModel(categories={'office': ['slc']})
        self.assertEqual(getter(obj, 0), 0)

    def test_success(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = DummyProfile(categories={'office': ['slc']})
        self.assertEqual(getter(obj, 0), ['slc'])

    def test_empty_category(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = DummyProfile(categories={'office': []})
        self.assertEqual(getter(obj, 0), 0)

    def test_no_categories(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = DummyProfile(categories={})
        self.assertEqual(getter(obj, 0), 0)

class TestPeopleDirectory(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleDirectory
        return PeopleDirectory

    def _makeOne(self):
        return self._getTargetClass()()

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleDirectory
        verifyClass(IPeopleDirectory, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleDirectory
        verifyObject(IPeopleDirectory, self._makeOne())

    def test_set_order(self):
        pd = self._makeOne()
        pd.set_order(['def', 'abc'])
        self.assertEqual(pd.order, ('def', 'abc'))

    def test_update_indexes_no_reindex(self):
        pd = self._makeOne()
        self.assertEqual(pd.update_indexes(), False)
        self.assertTrue('lastfirst' in pd.catalog)
        self.assertTrue('lastnamestartswith' in pd.catalog)
        self.assertTrue('texts' in pd.catalog)
        self.assertTrue('allowed' in pd.catalog)

    def test_update_indexes_after_new_category(self):
        pd = self._makeOne()
        pd.categories['office'] = 1
        self.assertFalse('category_office' in pd.catalog)
        self.assertEqual(pd.update_indexes(), True)
        self.assertTrue('category_office' in pd.catalog)

    def test_remove_category(self):
        pd = self._makeOne()
        pd.categories['office'] = 1
        pd.update_indexes()
        self.assertTrue('category_office' in pd.catalog)
        del pd.categories['office']
        self.assertEqual(pd.update_indexes(), False)
        self.assertFalse('category_office' in pd.catalog)


class TestPeopleCategory(unittest.TestCase):

    def test_it(self):
        from karl.models.peopledirectory import PeopleCategory
        pc = PeopleCategory('Offices')
        self.assertEqual(pc.title, 'Offices')


class TestPeopleCategoryItem(unittest.TestCase):

    def test_with_description(self):
        from karl.models.peopledirectory import PeopleCategoryItem
        pci = PeopleCategoryItem('Title', 'Description')
        self.assertEqual(pci.title, 'Title')
        self.assertEqual(pci.description, 'Description')

    def test_without_description(self):
        from karl.models.peopledirectory import PeopleCategoryItem
        pci = PeopleCategoryItem('Title')
        self.assertEqual(pci.title, 'Title')
        self.assertEqual(pci.description, '')


class TestPeopleSection(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleSection
        return PeopleSection

    def _makeOne(self, title='Organizations', tab_title='Orgs'):
        return self._getTargetClass()(title, tab_title)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleSection
        verifyClass(IPeopleSection, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleSection
        verifyObject(IPeopleSection, self._makeOne())

    def test_set_columns(self):
        obj = self._makeOne()
        a = testing.DummyModel()
        b = testing.DummyModel()
        obj.set_columns([a, b])
        self.assertEqual(obj.columns, (a, b))

class TestPeopleReportGroup(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReportGroup
        return PeopleReportGroup

    def _makeOne(self, title='G1'):
        return self._getTargetClass()(title)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportGroup
        verifyClass(IPeopleReportGroup, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportGroup
        verifyObject(IPeopleReportGroup, self._makeOne())

    def test_set_reports(self):
        obj = self._makeOne()
        a = testing.DummyModel()
        b = testing.DummyModel()
        obj.set_reports([a, b])
        self.assertEqual(obj.reports, (a, b))

class TestPeopleSectionColumn(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleSectionColumn
        return PeopleSectionColumn

    def _makeOne(self):
        return self._getTargetClass()()

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportGroup
        verifyClass(IPeopleReportGroup, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportGroup
        verifyObject(IPeopleReportGroup, self._makeOne())

class TestPeopleReport(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReport
        return PeopleReport

    def _makeOne(self, title='R1', link_title='Report One', css_class='normal'):
        return self._getTargetClass()(title, link_title, css_class)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReport
        verifyClass(IPeopleReport, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReport
        verifyObject(IPeopleReport, self._makeOne())

    def test_set_query(self):
        obj = self._makeOne()
        obj.set_query({'x': 'y'})
        self.assertEqual(obj.query, {'x': 'y'})

    def test_set_filter(self):
        obj = self._makeOne()
        obj.set_filter('office', ['nyc'])
        obj.set_filter('organization', ['fan-club'])
        self.assertEqual(obj.filters,
            {'office': ('nyc',), 'organization': ('fan-club',)})

    def test_set_columns(self):
        obj = self._makeOne()
        obj.set_columns(['name', 'email'])
        self.assertEqual(obj.columns, ('name', 'email'))

from zope.interface import implements
from karl.models.interfaces import IProfile

class DummyProfile(testing.DummyModel):
    implements(IProfile)
