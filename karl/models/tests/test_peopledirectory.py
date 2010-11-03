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


def _makeProfile(**kw):
    from zope.interface import implements
    from karl.models.interfaces import IProfile

    class DummyProfile(testing.DummyModel):
        implements(IProfile)

    return DummyProfile(**kw)


class TestDiscriminatorFunctions(unittest.TestCase):

    def test_get_lastname_firstletter_on_profile(self):
        from karl.models.peopledirectory import get_lastname_firstletter
        obj = _makeProfile(lastname='Smith')
        self.assertEqual(get_lastname_firstletter(obj, 0), 'S')

    def test_get_lastname_firstletter_on_other(self):
        from karl.models.peopledirectory import get_lastname_firstletter
        obj = testing.DummyModel(lastname='Smith')
        self.assertEqual(get_lastname_firstletter(obj, 0), 0)

    def test_get_department(self):
        from karl.models.peopledirectory import get_department
        obj = _makeProfile(department='Redundant')
        self.assertEqual(get_department(obj, 0), 'redundant')
        obj.department = None
        self.assertEqual(get_department(obj, 0), 0)

    def test_get_email(self):
        from karl.models.peopledirectory import get_email
        obj = _makeProfile(email='xyz@Example.com')
        self.assertEqual(get_email(obj, 0), 'xyz@example.com')
        obj.email = None
        self.assertEqual(get_email(obj, 0), 0)

    def test_get_location(self):
        from karl.models.peopledirectory import get_location
        obj = _makeProfile(location='SLC')
        self.assertEqual(get_location(obj, 0), 'slc')
        obj.location = None
        self.assertEqual(get_location(obj, 0), 0)

    def test_get_organization(self):
        from karl.models.peopledirectory import get_organization
        obj = _makeProfile(organization='Fun')
        self.assertEqual(get_organization(obj, 0), 'fun')
        obj.organization = None
        self.assertEqual(get_organization(obj, 0), 0)

    def test_get_phone(self):
        from karl.models.peopledirectory import get_phone
        obj = _makeProfile(phone='(123) 456-0')
        self.assertEqual(get_phone(obj, 0), '(123) 456-0')
        obj.phone = None
        self.assertEqual(get_phone(obj, 0), 0)

    def test_get_phone_with_extension(self):
        from karl.models.peopledirectory import get_phone
        obj = _makeProfile(phone='(123) 456-0', extension='42')
        self.assertEqual(get_phone(obj, 0), '(123) 456-0 x 42')

    def test_get_position(self):
        from karl.models.peopledirectory import get_position
        obj = _makeProfile(position='Head Boss')
        self.assertEqual(get_position(obj, 0), 'head boss')
        obj.position = None
        self.assertEqual(get_position(obj, 0), 0)

    def test_get_groups_for_profile(self):
        from karl.models.peopledirectory import get_groups
        from karl.testing import DummyUsers
        obj = _makeProfile()
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
        obj = _makeProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        self.assertEqual(get_groups(obj, 0), 0)

    def test_is_staff_for_staff(self):
        from karl.models.peopledirectory import is_staff
        from karl.testing import DummyUsers
        obj = _makeProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        site.users.add('testuser', 'testuser', '', ['group.KarlStaff'])
        self.assertEqual(is_staff(obj, ()), True)

    def test_is_staff_for_non_staff(self):
        from karl.models.peopledirectory import is_staff
        from karl.testing import DummyUsers
        obj = _makeProfile()
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
        obj = _makeProfile()
        site = testing.DummyModel()
        site['testuser'] = obj
        site.users = DummyUsers()
        self.assertEqual(is_staff(obj, ()), ())


class TestProfileCategoryGetter(unittest.TestCase):

    def _makeFolder(self, mapping):
        class DummyFolder(dict):
            pass
        return DummyFolder(mapping)

    def test_non_profile(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = testing.DummyModel()
        obj.categories = {'office': ['slc']}
        self.assertEqual(getter(obj, 0), 0)

    def test_success(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = _makeProfile()
        obj.categories = {'office': ['slc']}
        self.assertEqual(getter(obj, 0), ['slc'])

    def test_empty_category(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = _makeProfile()
        obj.categories = {'office': []}
        self.assertEqual(getter(obj, 0), 0)

    def test_no_categories(self):
        from karl.models.peopledirectory import ProfileCategoryGetter
        getter = ProfileCategoryGetter('office')
        obj = _makeProfile()
        obj.categories = {}
        self.assertEqual(getter(obj, 0), 0)


class TestPeopleDirectory(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleDirectory
        return PeopleDirectory

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IPeopleDirectory(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleDirectory
        verifyClass(IPeopleDirectory, self._getTargetClass())

    def test_instance_conforms_to_IPeopleDirectory(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleDirectory
        verifyObject(IPeopleDirectory, self._makeOne())

    def test_update_indexes_no_reindex(self):
        pd = self._makeOne()
        self.assertEqual(pd.update_indexes(), False)
        self.failUnless('lastfirst' in pd.catalog)
        self.failUnless('lastnamestartswith' in pd.catalog)
        self.failUnless('texts' in pd.catalog)
        self.failUnless('allowed' in pd.catalog)

    def test_update_indexes_after_new_category(self):
        pd = self._makeOne()
        pd['categories']['office'] = testing.DummyModel()
        self.failIf('category_office' in pd.catalog)
        self.assertEqual(pd.update_indexes(), True)
        self.failUnless('category_office' in pd.catalog)

    def test_update_indexes_after_removing_category(self):
        pd = self._makeOne()
        pd['categories']['office'] = testing.DummyModel()
        pd.update_indexes()
        self.failUnless('category_office' in pd.catalog)
        del pd['categories']['office']
        self.assertEqual(pd.update_indexes(), False)
        self.failIf('category_office' in pd.catalog)


class TestPeopleCategories(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleCategories
        return PeopleCategories

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IPeopleCategories(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleCategories
        verifyClass(IPeopleCategories, self._getTargetClass())

    def test_instance_conforms_to_IPeopleCategories(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleCategories
        verifyObject(IPeopleCategories, self._makeOne())

    def test_it(self):
        from karl.models.peopledirectory import PeopleCategories
        pc = PeopleCategories()
        self.assertEqual(pc.title, 'People Categories')


class TestPeopleCategory(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleCategory
        return PeopleCategory

    def _makeOne(self, title='Testing'):
        return self._getTargetClass()(title)

    def test_class_conforms_to_IPeopleCategory(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleCategory
        verifyClass(IPeopleCategory, self._getTargetClass())

    def test_instance_conforms_to_IPeopleCategory(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleCategory
        verifyObject(IPeopleCategory, self._makeOne())

    def test_it(self):
        pc = self._makeOne('Offices')
        self.assertEqual(pc.title, 'Offices')


class TestPeopleCategoryItem(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleCategoryItem
        return PeopleCategoryItem

    def _makeOne(self, title='Testing', description=None):
        if description is not None:
            return self._getTargetClass()(title, description)
        return self._getTargetClass()(title)

    def test_class_conforms_to_IPeopleCategoryItem(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleCategoryItem
        verifyClass(IPeopleCategoryItem, self._getTargetClass())

    def test_instance_conforms_to_IPeopleCategory(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleCategoryItem
        verifyObject(IPeopleCategoryItem, self._makeOne())

    def test_with_description(self):
        pci = self._makeOne('Title', 'Description')
        self.assertEqual(pci.title, 'Title')
        self.assertEqual(pci.description, 'Description')

    def test_without_description(self):
        pci = self._makeOne('Title')
        self.assertEqual(pci.title, 'Title')
        self.assertEqual(pci.description, '')


class TestPeopleSection(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleSection
        return PeopleSection

    def _makeOne(self, title='Organizations', tab_title='Orgs'):
        return self._getTargetClass()(title, tab_title)

    def test_class_conforms_to_IPeopleSection(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleSection
        verifyClass(IPeopleSection, self._getTargetClass())

    def test_instance_conforms_to_IPeopleSection(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleSection
        verifyObject(IPeopleSection, self._makeOne())


class TestPeopleReportGroup(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReportGroup
        return PeopleReportGroup

    def _makeOne(self, title='G1'):
        return self._getTargetClass()(title)

    def test_class_conforms_to_IPeopleReportGroup(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportGroup
        verifyClass(IPeopleReportGroup, self._getTargetClass())

    def test_instance_conforms_to_IPeopleReportGroup(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportGroup
        verifyObject(IPeopleReportGroup, self._makeOne())


class TestPeopleSectionColumn(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleSectionColumn
        return PeopleSectionColumn

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IPeopleSectionColumn(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleSectionColumn
        verifyClass(IPeopleSectionColumn, self._getTargetClass())

    def test_instance_conforms_to_IPeopleSectionColumn(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleSectionColumn
        verifyObject(IPeopleSectionColumn, self._makeOne())


class _Conforms_to_IPeopleReportFilter(object):

    def test_class_conforms_to_IPeopleReportFilter(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportFilter
        verifyClass(IPeopleReportFilter, self._getTargetClass())

    def test_instance_conforms_to_IPeopleReportFilter(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportFilter
        verifyObject(IPeopleReportFilter, self._makeOne())


class TestPeopleReportCategoryFilter(unittest.TestCase,
                                     _Conforms_to_IPeopleReportFilter,
                                    ):
    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReportCategoryFilter
        return PeopleReportCategoryFilter

    def _makeOne(self, values=('a', 'b', 'c')):
        return self._getTargetClass()(values)

    def test_class_conforms_to_IPeopleReportCategoryFilter(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportCategoryFilter
        verifyClass(IPeopleReportCategoryFilter, self._getTargetClass())

    def test_instance_conforms_to_IPeopleReportCategoryFilter(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportCategoryFilter
        verifyObject(IPeopleReportCategoryFilter, self._makeOne())


class TestPeopleReportGroupFilter(unittest.TestCase,
                                  _Conforms_to_IPeopleReportFilter,
                                 ):
    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReportGroupFilter
        return PeopleReportGroupFilter

    def _makeOne(self, values=('a', 'b', 'c')):
        return self._getTargetClass()(values)

    def test_class_conforms_to_IPeopleReportGroupFilter(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportGroupFilter
        verifyClass(IPeopleReportGroupFilter, self._getTargetClass())

    def test_instance_conforms_to_IPeopleReportGroupFilter(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportGroupFilter
        verifyObject(IPeopleReportGroupFilter, self._makeOne())


class TestPeopleReportIsStaffFilter(unittest.TestCase,
                                    _Conforms_to_IPeopleReportFilter,
                                   ):
    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReportIsStaffFilter
        return PeopleReportIsStaffFilter

    def _makeOne(self, values=('a', 'b', 'c')):
        return self._getTargetClass()(values)

    def test_class_conforms_to_IPeopleReportIsStaffFilter(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        verifyClass(IPeopleReportIsStaffFilter, self._getTargetClass())

    def test_instance_conforms_to_IPeopleReportIsStaffFilter(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        verifyObject(IPeopleReportIsStaffFilter, self._makeOne())


class TestPeopleReport(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleReport
        return PeopleReport

    def _makeOne(self, title='R1', link_title='Report One', css_class='normal'):
        return self._getTargetClass()(title, link_title, css_class)

    def test_class_conforms_to_IPeopleReport(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleReport
        verifyClass(IPeopleReport, self._getTargetClass())

    def test_instance_conforms_to_IPeopleReport(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleReport
        verifyObject(IPeopleReport, self._makeOne())


class TestPeopleDirectorySchemaChanged(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.peopledirectory import PeopleDirectorySchemaChanged
        return PeopleDirectorySchemaChanged

    def _makeOne(self, peopledir=None):
        if peopledir is None:
            peopledir = testing.DummyModel()
        return self._getTargetClass()(peopledir)

    def test_class_conforms_to_IPeopleDirectorySchemaChanged(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IPeopleDirectorySchemaChanged
        verifyClass(IPeopleDirectorySchemaChanged, self._getTargetClass())

    def test_instance_conforms_to_IPeopleDirectorySchemaChanged(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IPeopleDirectorySchemaChanged
        verifyObject(IPeopleDirectorySchemaChanged, self._makeOne())


class Test_reindex_peopledirectory(unittest.TestCase):

    def _callFUT(self, peopledir):
        from karl.models.peopledirectory import reindex_peopledirectory
        reindex_peopledirectory(peopledir)

    def test_no_profiles(self):
        from karl.testing import DummyCatalog
        site = testing.DummyModel()
        peopledir = testing.DummyModel()
        peopledir.catalog = DummyCatalog()
        site['people'] = peopledir
        profiles = testing.DummyModel()
        site['profiles'] = profiles
        self._callFUT(peopledir)

    def test_with_new_profile(self):
        from karl.testing import DummyCatalog
        site = testing.DummyModel()
        peopledir = testing.DummyModel()
        peopledir.catalog = DummyCatalog()
        site['people'] = peopledir
        profiles = testing.DummyModel()
        site['profiles'] = profiles

        p1 = testing.DummyModel()
        from karl.models.interfaces import IProfile
        from zope.interface import directlyProvides
        directlyProvides(p1, IProfile)
        profiles['p1'] = p1

        self._callFUT(peopledir)
        self.assertEquals(peopledir.catalog.document_map.added,
            [(None, '/profiles/p1')])

    def test_with_existing_profile(self):
        from karl.testing import DummyCatalog
        site = testing.DummyModel()
        peopledir = testing.DummyModel()
        peopledir.catalog = DummyCatalog()
        site['people'] = peopledir
        profiles = testing.DummyModel()
        site['profiles'] = profiles

        p1 = testing.DummyModel()
        from karl.models.interfaces import IProfile
        from zope.interface import directlyProvides
        directlyProvides(p1, IProfile)
        profiles['p1'] = p1

        peopledir.catalog.document_map.add('/profiles/p1', 10)
        self._callFUT(peopledir)
        self.assertEquals(peopledir.catalog.document_map.added,
            [(10, '/profiles/p1')])

