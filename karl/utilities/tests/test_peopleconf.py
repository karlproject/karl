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
"""Tests of karl.utilities.peopleconf"""

import unittest
from repoze.bfg import testing


class Test_dump_peopledir(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _callFUT(self, elem):
        from karl.utilities.peopleconf import dump_peopledir
        return dump_peopledir(elem)

    def _makeContext(self, order=()):
        pd = testing.DummyModel(order=order)
        pd['categories'] = testing.DummyModel()
        return pd

    def _xpath(self, xml, xpath):
        from lxml import etree
        tree = etree.fromstring(xml.encode('UTF8'))
        return tree.xpath(xpath)

    def test_empty(self):
        pd = self._makeContext()
        xml = self._callFUT(pd)
        self.failUnless(self._xpath(xml, '/peopledirectory'))
        self.failUnless(self._xpath(xml, '/peopledirectory/categories'))
        self.failIf(self._xpath(xml, '/peopledirectory/categories/*'))
        self.failUnless(self._xpath(xml, '/peopledirectory/sections'))
        self.failIf(self._xpath(xml, '/peopledirectory/sections/*'))

    def test_with_old_style_category_and_values(self):
        pd = self._makeContext()
        # Old-style has 'categories' as an attribute, ...
        cat = pd.categories = testing.DummyModel()
        # and each category has a '_container' attribute.
        offices = cat['offices'] = testing.DummyModel(title='Offices',
                                                      _container={})
        nyc = testing.DummyModel(title='New York', description='On Broadway')
        offices._container['nyc'] = nyc
        xml = self._callFUT(pd)
        o_nodes = self._xpath(xml, '/peopledirectory/categories/category')
        self.assertEqual(len(o_nodes), 1)
        self.assertEqual(o_nodes[0].get('title'), 'Offices')
        n_nodes = self._xpath(xml, '/peopledirectory/categories/category/value')
        self.assertEqual(len(n_nodes), 1)
        self.assertEqual(n_nodes[0].get('title'), 'New York')
        self.assertEqual(n_nodes[0].text, 'On Broadway')

    def test_with_new_style_category_and_values(self):
        pd = self._makeContext()
        # New-style has 'categories' as an item:
        # 'data' signals that categories is a new-style repoze.folder.Folder.
        offices = pd['categories']['offices'] = testing.DummyModel(
                                                            title='Offices',
                                                            data={})
        offices['nyc'] = testing.DummyModel(title='New York',
                                            description='On Broadway')
        xml = self._callFUT(pd)
        o_nodes = self._xpath(xml, '/peopledirectory/categories/category')
        self.assertEqual(len(o_nodes), 1)
        self.assertEqual(o_nodes[0].get('title'), 'Offices')
        n_nodes = self._xpath(xml, '/peopledirectory/categories/category/value')
        self.assertEqual(len(n_nodes), 1)
        self.assertEqual(n_nodes[0].get('title'), 'New York')
        self.assertEqual(n_nodes[0].text, 'On Broadway')

    def test_section_acl_w_inherit(self):
        pd = self._makeContext(order=('testing',))
        pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',
                                                                   'edit'))])
        xml = self._callFUT(pd)
        s_nodes = self._xpath(xml, '/peopledirectory/sections/section')
        self.assertEqual(len(s_nodes), 1)
        self.assertEqual(s_nodes[0].get('name'), 'testing')
        self.assertEqual(s_nodes[0].get('title'), 'Testing')
        self.assertEqual(s_nodes[0].get('tab-title'), 'Testing (TAB)')
        a_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]/acl/*')
        self.assertEqual(len(a_nodes), 1)
        self.assertEqual(a_nodes[0].tag, 'allow')
        self.assertEqual(a_nodes[0].get('principal'), 'system.Everyone')
        p_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]'
                                    '/acl/allow/permission')
        self.assertEqual(len(p_nodes), 2)
        self.assertEqual(p_nodes[0].text, 'view')
        self.assertEqual(p_nodes[1].text, 'edit')
        self.failIf(
            self._xpath(xml,
                        '/peopledirectory/sections/testing/acl/no-inherit'))

    def test_section_acl_wo_inherit(self):
        from repoze.bfg.security import DENY_ALL
        pd = self._makeContext(order=('testing',))
        pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',)),
                                     DENY_ALL,
                                    ])
        xml = self._callFUT(pd)
        a_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]/acl/*')
        self.assertEqual(len(a_nodes), 2)
        self.assertEqual(a_nodes[0].tag, 'allow')
        self.assertEqual(a_nodes[1].tag, 'no-inherit')

    def test_section_no_acl(self):
        pd = self._makeContext(order=('testing',))
        pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                        )
        xml = self._callFUT(pd)
        a_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]/acl/*')
        self.assertEqual(len(a_nodes), 0)

    def test_section_w_no_columns(self):
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', 'view')])
        report = section['report'] = testing.DummyModel(title='Report',
                                    link_title='Report (Link)',
                                    css_class='CSS',
                                    columns=('name', 'phone'),
                                    filters={'offices': ['nyc', 'london']})
        xml = self._callFUT(pd)
        r_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report')
        self.assertEqual(len(r_nodes), 1)
        self.assertEqual(r_nodes[0].tag, 'report')
        self.assertEqual(r_nodes[0].get('name'), 'report')
        self.assertEqual(r_nodes[0].get('title'), 'Report')
        self.assertEqual(r_nodes[0].get('link-title'), 'Report (Link)')
        self.assertEqual(r_nodes[0].get('class'), 'CSS')
        f_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report/filter')
        self.assertEqual(len(f_nodes), 1)
        self.assertEqual(f_nodes[0].get('category'), 'offices')
        self.assertEqual(f_nodes[0].get('values'), 'nyc london')
        x_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report/columns')
        self.assertEqual(len(x_nodes), 1)
        self.assertEqual(x_nodes[0].get('names'), 'name phone')

    def test_section_w_oldstyle_columns(self):
        pd = self._makeContext(order=('testing',))
        report = testing.DummyModel(title='Report',
                                    link_title='Report (Link)',
                                    css_class='CSS',
                                    columns=('name', 'phone'),
                                    filters={'offices': ['nyc', 'london']})
        column = testing.DummyModel(reports=(report,))
        pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            columns=(column,),
                            __acl__=[('Allow', 'system.Everyone', 'view')])
        xml = self._callFUT(pd)
        c_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]/column')
        self.assertEqual(len(c_nodes), 1)
        self.assertEqual(c_nodes[0].get('name'), 'column_000000001')
        r_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/*')
        self.assertEqual(len(r_nodes), 1)
        self.assertEqual(r_nodes[0].tag, 'report')
        self.assertEqual(r_nodes[0].get('name'), 'item_000000001')
        self.assertEqual(r_nodes[0].get('title'), 'Report')
        self.assertEqual(r_nodes[0].get('link-title'), 'Report (Link)')
        self.assertEqual(r_nodes[0].get('class'), 'CSS')
        f_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/report/filter')
        self.assertEqual(len(f_nodes), 1)
        self.assertEqual(f_nodes[0].get('category'), 'offices')
        self.assertEqual(f_nodes[0].get('values'), 'nyc london')
        x_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/report/columns')
        self.assertEqual(len(x_nodes), 1)
        self.assertEqual(x_nodes[0].get('names'), 'name phone')

    def test_section_w_newstyle_columns(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleSectionColumn
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                                title='Testing',
                                tab_title='Testing (TAB)',
                                __acl__=[('Allow', 'system.Everyone', 'view')])
        column = section['c1'] = testing.DummyModel(order=('report',))
        directlyProvides(column, IPeopleSectionColumn)
        report = column['report'] = testing.DummyModel(title='Report',
                                        link_title='Report (Link)',
                                        css_class='CSS',
                                        columns=('name', 'phone'))
        report['offices'] = testing.DummyModel(values=['nyc', 'london'])
        xml = self._callFUT(pd)
        c_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]/column')
        self.assertEqual(len(c_nodes), 1)
        self.assertEqual(c_nodes[0].get('name'), 'c1')
        r_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/*')
        self.assertEqual(len(r_nodes), 1)
        self.assertEqual(r_nodes[0].tag, 'report')
        self.assertEqual(r_nodes[0].get('name'), 'report')
        self.assertEqual(r_nodes[0].get('title'), 'Report')
        self.assertEqual(r_nodes[0].get('link-title'), 'Report (Link)')
        self.assertEqual(r_nodes[0].get('class'), 'CSS')
        f_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/report/filter')
        self.assertEqual(len(f_nodes), 1)
        self.assertEqual(f_nodes[0].get('category'), 'offices')
        self.assertEqual(f_nodes[0].get('values'), 'nyc london')
        x_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/report/columns')
        self.assertEqual(len(x_nodes), 1)
        self.assertEqual(x_nodes[0].get('names'), 'name phone')

    def test_section_w_report_group(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportGroup
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', 'view')])
        group = section['rg1'] = testing.DummyModel(title='Group')
        directlyProvides(group, IPeopleReportGroup)
        report = group['report'] = testing.DummyModel(title='Report',
                                    link_title='Report (Link)',
                                    css_class='CSS',
                                    columns=('name', 'phone'),
                                    filters={'offices': ['nyc', 'london']})
        xml = self._callFUT(pd)
        g_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report-group')
        self.assertEqual(len(g_nodes), 1)
        self.assertEqual(g_nodes[0].get('name'), 'rg1')
        self.assertEqual(g_nodes[0].get('title'), 'Group')
        r_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report-group/report')
        self.assertEqual(len(r_nodes), 1)
        self.assertEqual(r_nodes[0].get('name'), 'report')
        self.assertEqual(r_nodes[0].get('title'), 'Report')
        self.assertEqual(r_nodes[0].get('link-title'), 'Report (Link)')
        self.assertEqual(r_nodes[0].get('class'), 'CSS')
        f_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report-group/report/filter')
        self.assertEqual(len(f_nodes), 1)
        self.assertEqual(f_nodes[0].get('category'), 'offices')
        self.assertEqual(f_nodes[0].get('values'), 'nyc london')
        x_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/report-group/report/columns')
        self.assertEqual(len(x_nodes), 1)
        self.assertEqual(x_nodes[0].get('names'), 'name phone')

class ParseErrorTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.utilities.peopleconf import ParseError
        return ParseError

    def _makeOne(self, msg, elem):
        return self._getTargetClass()(msg, elem)

    def test_no_document(self):
        elem = DummyElement()
        obj = self._makeOne("test", elem)
        self.assertEqual(obj.msg, "test")
        self.assertEqual(obj.sourceline, 10)
        self.assertEqual(obj.url, None)
        self.assertEqual(str(obj), 'test on line 10')

    def test_with_document(self):
        elem = DummyElement(docinfo=DummyDocInfo())
        obj = self._makeOne("test", elem)
        self.assertEqual(obj.msg, "test")
        self.assertEqual(obj.sourceline, 10)
        self.assertEqual(obj.url, '/tmp/file')
        self.assertEqual(str(obj), 'test on line 10 of /tmp/file')


class Test_name_and_title(unittest.TestCase):

    def _callFUT(self, elem):
        from karl.utilities.peopleconf import name_and_title
        return name_and_title(elem)

    def test_minimal(self):
        from lxml.etree import Element
        elem = Element('report', name='r1')
        name, title = self._callFUT(elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(title, 'r1')

    def test_wo_name_but_w_id(self):
        from lxml.etree import Element
        elem = Element('report', id='r1')
        name, title = self._callFUT(elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(title, 'r1')

    def test_with_title(self):
        from lxml.etree import Element
        elem = Element('report', name='r1', title='Report One')
        name, title = self._callFUT(elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(title, 'Report One')

    def test_wo_name_or_id(self):
        from lxml.etree import Element
        from karl.utilities.peopleconf import ParseError
        elem = Element('report')
        self.assertRaises(ParseError, self._callFUT, elem)


class Test_set_acl(unittest.TestCase):

    def _callFUT(self, obj, elem):
        from karl.utilities.peopleconf import set_acl
        return set_acl(obj, elem)

    def test_success(self):
        from karl.security.policy import NO_INHERIT
        xml = """
        <any-object>
            <acl>
                <allow principal="alice">
                 <permission>view</permission>
                 <permission>edit</permission>
                </allow>
                <deny principal="bob">
                 <permission>edit</permission>
                </deny>
                <no-inherit/>
            </acl>
        </any-object>
        """
        elem = parse_xml(xml)
        obj = testing.DummyModel()
        self._callFUT(obj, elem)
        self.assertEqual(obj.__acl__, [
            ('Allow', 'alice', ('view', 'edit')),
            ('Deny', 'bob', ('edit',)),
            NO_INHERIT,
            ])

    def test_missing_principal(self):
        xml = """
        <any-object>
            <acl>
                <allow>
                 <permission>view</permission>
                </allow>
            </acl>
        </any-object>
        """
        elem = parse_xml(xml)
        obj = testing.DummyModel()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, obj, elem)

    def test_missing_permissions(self):
        xml = """
        <any-object>
            <acl>
                <allow principal="alice"/>
            </acl>
        </any-object>
        """
        elem = parse_xml(xml)
        obj = testing.DummyModel()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, obj, elem)

    def test_unrecognized(self):
        xml = """
        <any-object>
            <acl>
                <xml/>
            </acl>
        </any-object>
        """
        elem = parse_xml(xml)
        obj = testing.DummyModel()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, obj, elem)


class Test_parse_report(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _callFUT(self, peopledir, elem):
        from karl.utilities.peopleconf import parse_report
        return parse_report(peopledir, elem)

    def test_minimal(self):
        xml = """
        <report name="r1">
            <columns names="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        name, report = self._callFUT(peopledir, elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(report.title, 'r1')
        self.assertEqual(report.link_title, 'r1')
        self.assertEqual(len(report), 0)
        self.assertEqual(report.columns, ('name',))

    def test_complete(self):
        from karl.models.peopledirectory import PeopleReportCategoryFilter
        xml = """
        <report name="r1" title="Report One" link-title="One">
            <filter category="office" values="nyc la"/>
            <filter category="department" values="toys"/>
            <columns names="name email"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC', 'la': 'LA'}
        peopledir['categories']['department'] = {'toys': 'Toys'}
        name, report = self._callFUT(peopledir, elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(report.title, 'Report One')
        self.assertEqual(report.link_title, 'One')
        self.assertEqual(len(report), 2)
        self.failUnless(isinstance(report['department'],
                        PeopleReportCategoryFilter))
        self.assertEqual(report['department'].values, ('toys',))
        self.failUnless(isinstance(report['office'],
                        PeopleReportCategoryFilter))
        self.assertEqual(report['office'].values, ('nyc', 'la'))
        self.assertEqual(report.columns, ('name', 'email'))

    def test_no_such_category(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <filter category="office" values="nyc"/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_no_category_values(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <filter category="office" values=""/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC'}
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_invalid_category_value(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <filter category="office" values="la"/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC'}
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_group_value(self):
        from karl.models.peopledirectory import PeopleReportGroupFilter
        xml = """
        <report name="r1">
            <filter values="g1"/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        name, report = self._callFUT(peopledir, elem)
        self.assertEqual(len(report), 1)
        self.failUnless(isinstance(report['groups'], PeopleReportGroupFilter))
        self.assertEqual(report['groups'].values, ('g1',))
        self.assertEqual(report.columns, ('name',))

    def test_no_columns(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <filter category="office" values="nyc"/>
            <columns names=""/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC'}
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_bad_column(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <filter category="office" values="nyc"/>
            <columns names="name zodiac"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC'}
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)


class Test_parse_report_group(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _callFUT(self, peopledir, elem):
        from karl.utilities.peopleconf import parse_report_group
        return parse_report_group(peopledir, elem)

    def test_no_subelements(self):
        xml = """
        <report-group name="test">
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        name, group = self._callFUT(peopledir, elem)
        self.assertEqual(name, 'test')
        self.assertEqual(len(group), 0)


class Test_parse_reports(unittest.TestCase):

    def _callFUT(self, peopledir, parent_elem):
        from karl.utilities.peopleconf import parse_reports
        return parse_reports(peopledir, parent_elem)

    def test_no_reports(self):
        xml = """
        <report-group name="test">
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        contents = self._callFUT(peopledir, elem)
        self.assertEqual(contents, [])

    def test_complete(self):
        xml = """
        <report-group name="test">
            <report name="r1">
                <columns names="name"/>
            </report>
            <!-- Reports for the musically inclined -->
            <report-group name="musicians" title="Musicians">
                <report name="r2">
                    <columns names="name"/>
                </report>
            </report-group>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        items = self._callFUT(peopledir, elem)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0][0], 'r1')
        self.assertEqual(items[0][1].title, 'r1')
        self.assertEqual(items[1][1].title, 'Musicians')
        self.assertEqual(items[1][1]['r2'].title, 'r2')

    def test_non_unique_report(self):
        xml = """
        <report-group name="test">
            <report name="r1">
                <columns names="name"/>
            </report>
            <report name="r1">
                <columns names="name"/>
            </report>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_non_unique_report_group(self):
        xml = """
        <column name="c1">
            <report-group name="rg1">
              <report name="r1">
                  <columns names="name"/>
              </report>
            </report-group>
            <report-group name="rg1">
              <report name="r2">
                  <columns names="name"/>
              </report>
            </report-group>
        </column>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_unrecognized(self):
        xml = """
        <report-group name="test">
            <xml/>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)


class Test_parse_section(unittest.TestCase):

    def _callFUT(self, peopledir, elem):
        from karl.utilities.peopleconf import parse_section
        return parse_section(peopledir, elem)

    def test_minimal(self):
        xml = """
        <section>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        columns = self._callFUT(peopledir, elem)
        self.assertEqual(list(columns), [])

    def test_column(self):
        xml = """
        <section>
            <column name="column_001">
                <report name="r1">
                    <columns names="name"/>
                </report>
            </column>
            <column name="column_002">
            </column>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        items = self._callFUT(peopledir, elem)
        self.assertEqual(len(items), 2)
        name, column = items[0]
        self.assertEqual(name, 'column_001')
        self.assertEqual(len(column), 1)
        self.assertEqual(list(column), ['r1'])
        name, column = items[1]
        self.assertEqual(name, 'column_002')
        self.assertEqual(len(column), 0)

    def test_single_report(self):
        xml = """
        <section>
            <report name="r1">
                <columns names="name"/>
            </report>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        items = self._callFUT(peopledir, elem)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][0], 'r1')
        report = items[0][1]
        self.assertEqual(list(report.columns), ['name'])

    def test_single_report_group(self):
        xml = """
        <section>
          <report-group name="rg1">
            <report name="r1">
                <columns names="name"/>
            </report>
          </report-group>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        items = self._callFUT(peopledir, elem)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][0], 'rg1')
        group = items[0][1]
        report = group['r1']
        self.assertEqual(list(report.columns), ['name'])

    def test_unrecognized(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <section>
            <xml/>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)


class Test_peopleconf(unittest.TestCase):

    def setUp(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from repoze.bfg.testing import cleanUp
        cleanUp()

    def _callFUT(self, peopledir, elem, **kw):
        from karl.utilities.peopleconf import peopleconf
        return peopleconf(peopledir, elem, **kw)

    def test_all(self):
        from karl.models.peopledirectory import PeopleCategories
        xml = """
        <peopledirectory>
            <categories>
                <category name="offices" title="Offices">
                    <value name="nyc" title="NYC">
                        <description>I<b>heart</b>NY</description>
                    </value>
                </category>
            </categories>
            <sections>
                <section name="everyone" title="Everyone" tab-title="All">
                    <acl>
                        <allow principal="bob">
                         <permission>view</permission>
                        </allow>
                    </acl>
                    <column name="c1">
                        <report-group name="cities" title="Cities">
                            <report name="ny" title="NYC Office"
                                    link-title="NYC">
                                <filter category="offices" values="nyc"/>
                                <columns names="name email"/>
                            </report>
                        </report-group>
                    </column>
                </section>
            </sections>
        </peopledirectory>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['existing'] = testing.DummyModel()

        self._callFUT(peopledir, elem)

        self.failIf('existing' in peopledir)
        self.failUnless(isinstance(peopledir['categories'], PeopleCategories))

        EXPECTED = ['everyone']
        self.assertEqual(peopledir.order, EXPECTED)
        self.assertEqual(len(peopledir.keys()), len(EXPECTED) + 1)
        for name in EXPECTED:
            self.failUnless(name in peopledir)
        self.assertEqual(peopledir['everyone'].__acl__,
            [('Allow', 'bob', ('view',))])
        self.assertEqual(list(peopledir['everyone'].keys()), ['c1'])
        self.assertEqual(list(peopledir['everyone']['c1'].keys()), ['cities'])
        self.assertEqual(list(peopledir['everyone']['c1']['cities'].keys()),
                         ['ny'])

        categories = peopledir['categories']
        self.assertEqual(list(categories.keys()), ['offices'])
        self.assertEqual(categories['offices'].title, 'Offices')
        self.assertEqual(list(categories['offices'].keys()), ['nyc'])
        self.assertEqual(categories['offices']['nyc'].description,
                         'I<b>heart</b>NY')

    def test_nested_category_description(self):
        from karl.models.peopledirectory import PeopleCategories
        xml = """
        <peopledirectory>
            <categories>
                <category name="offices" title="Offices">
                    <value name="nyc" title="NYC">
                      <description>
                        <nested>Nested description here.</nested>
                      </description>
                    </value>
                </category>
            </categories>
        </peopledirectory>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        # old-style
        del peopledir['categories']
        peopledir.categories = object()

        self._callFUT(peopledir, elem)

        self.failIf('categories' in peopledir.__dict__)
        self.failUnless(isinstance(peopledir['categories'], PeopleCategories))

        category = peopledir['categories']['offices']['nyc']
        self.failUnless('<nested>Nested description here.</nested>'
                            in category.description)

    def test_empty_category_description(self):
        xml = """
        <peopledirectory>
            <categories>
                <category name="offices" title="Offices">
                    <value name="nyc" title="NYC">
                    </value>
                </category>
            </categories>
        </peopledirectory>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir['categories']['bogus'] = object()

        self._callFUT(peopledir, elem)

        self.failIf('bogus' in peopledir['categories'])

        category = peopledir['categories']['offices']['nyc']
        self.assertEqual(category.description, '')

    def test_force_reindex(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IProfile
        from karl.testing import DummyCatalog
        xml = """
        <peopledirectory>
            <sections>
                <section name="everyone" title="Everyone">
                    <report name="everyone" title="Everyone">
                        <columns names="name email"/>
                    </report>
                </section>
            </sections>
        </peopledirectory>
        """
        elem = parse_xml(xml)
        site = testing.DummyModel()
        peopledir = DummyPeopleDirectory()
        peopledir.catalog = DummyCatalog()
        site['people'] = peopledir
        profiles = testing.DummyModel()
        site['profiles'] = profiles
        profile = profiles['dummy'] = testing.DummyModel()
        directlyProvides(profile, IProfile)
        self._callFUT(peopledir, elem, force_reindex=True)
        self.assertEqual(len(peopledir.catalog.indexed), 1)
        self.failUnless(peopledir.catalog.indexed[0] is profile)


class DummyElement:
    sourceline = 10
    def __init__(self, docinfo=None):
        self.docinfo = docinfo
    def getroottree(self):
        return self

class DummyDocInfo:
    URL = '/tmp/file'

class DummyPeopleDirectory(dict):
    __parent__ = None

    def __init__(self):
        self['categories'] = {}

    def set_order(self, order):
        self.order = order

    def update_indexes(self):
        return False

def parse_xml(xml):
    from lxml.etree import parse
    from StringIO import StringIO
    return parse(StringIO(xml)).getroot()
