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


class IdAndTitleTests(unittest.TestCase):

    def _callFUT(self, elem):
        from karl.utilities.peopleconf import id_and_title
        return id_and_title(elem)

    def test_minimal(self):
        from lxml.etree import Element
        elem = Element('report', id='r1')
        id, title = self._callFUT(elem)
        self.assertEqual(id, 'r1')
        self.assertEqual(title, 'r1')

    def test_with_title(self):
        from lxml.etree import Element
        elem = Element('report', id='r1', title='Report One')
        id, title = self._callFUT(elem)
        self.assertEqual(id, 'r1')
        self.assertEqual(title, 'Report One')

    def test_no_id(self):
        from lxml.etree import Element
        elem = Element('report')
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, elem)


class SetAclTests(unittest.TestCase):

    def _callFUT(self, obj, elem):
        from karl.utilities.peopleconf import set_acl
        return set_acl(obj, elem)

    def test_success(self):
        from karl.security.policy import NO_INHERIT
        xml = """
        <any-object>
            <acl>
                <allow principal="alice" permission="view"/>
                <deny principal="bob" permission="edit"/>
                <no-inherit/>
            </acl>
        </any-object>
        """
        elem = parse_xml(xml)
        obj = testing.DummyModel()
        self._callFUT(obj, elem)
        self.assertEqual(obj.__acl__, [
            ('Allow', 'alice', 'view'),
            ('Deny', 'bob', 'edit'),
            NO_INHERIT,
            ])

    def test_missing_principal(self):
        xml = """
        <any-object>
            <acl>
                <allow permission="view"/>
            </acl>
        </any-object>
        """
        elem = parse_xml(xml)
        obj = testing.DummyModel()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, obj, elem)

    def test_missing_permission(self):
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


class ParseReportTests(unittest.TestCase):

    def _callFUT(self, peopledir, elem):
        from karl.utilities.peopleconf import parse_report
        return parse_report(peopledir, elem)

    def test_minimal(self):
        xml = """
        <report id="r1">
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        reportid, obj = self._callFUT(peopledir, elem)
        self.assertEqual(reportid, 'r1')
        self.assertEqual(obj.title, 'r1')
        self.assertEqual(obj.link_title, 'r1')
        self.assertEqual(obj.filters, {})
        self.assertEqual(obj.columns, ('name',))

    def test_complete(self):
        xml = """
        <report id="r1" title="Report One" link-title="One">
            <query>{'is_staff': True}</query>
            <filter category="office" values="nyc la"/>
            <filter category="department" values="toys"/>
            <columns ids="name email"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir.categories['office'] = {'nyc': 'NYC', 'la': 'LA'}
        peopledir.categories['department'] = {'toys': 'Toys'}
        reportid, obj = self._callFUT(peopledir, elem)
        self.assertEqual(reportid, 'r1')
        self.assertEqual(obj.title, 'Report One')
        self.assertEqual(obj.link_title, 'One')
        self.assertEqual(obj.query, {'is_staff': True})
        self.assertEqual(obj.filters, {
            'department': ('toys',),
            'office': ('nyc', 'la'),
            })
        self.assertEqual(obj.columns, ('name', 'email'))

    def test_no_such_category(self):
        xml = """
        <report id="r1">
            <filter category="office" values="nyc"/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_no_category_values(self):
        xml = """
        <report id="r1">
            <filter category="office" values=""/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir.categories['office'] = {'nyc': 'NYC'}
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_invalid_category_value(self):
        xml = """
        <report id="r1">
            <filter category="office" values="la"/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir.categories['office'] = {'nyc': 'NYC'}
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_no_columns(self):
        xml = """
        <report id="r1">
            <filter category="office" values="nyc"/>
            <columns ids=""/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir.categories['office'] = {'nyc': 'NYC'}
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_bad_column(self):
        xml = """
        <report id="r1">
            <filter category="office" values="nyc"/>
            <columns ids="name zodiac"/>
        </report>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        peopledir.categories['office'] = {'nyc': 'NYC'}
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)


class ParseReportsTests(unittest.TestCase):

    def _callFUT(self, peopledir, parent_elem, reportmap):
        from karl.utilities.peopleconf import parse_reports
        return parse_reports(peopledir, parent_elem, reportmap)

    def test_no_reports(self):
        xml = """
        <report-group>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        contents = self._callFUT(peopledir, elem, {})
        self.assertEqual(contents, [])

    def test_complete(self):
        xml = """
        <report-group>
            <report id="r1">
                <columns ids="name"/>
            </report>
            <report-group title="Musicians">
                <report id="r2">
                    <columns ids="name"/>
                </report>
            </report-group>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        reportmap = {}
        contents = self._callFUT(peopledir, elem, reportmap)
        self.assertEqual(len(contents), 2)
        self.assertEqual(contents[0].title, 'r1')
        self.assertEqual(contents[1].title, 'Musicians')
        self.assertEqual(contents[1].reports[0].title, 'r2')
        self.assertEqual(len(reportmap), 2)
        self.assert_('r1' in reportmap)
        self.assert_('r2' in reportmap)

    def test_non_unique_report(self):
        xml = """
        <report-group>
            <report id="r1">
                <columns ids="name"/>
            </report>
            <report id="r1">
                <columns ids="name"/>
            </report>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem, {})

    def test_unrecognized(self):
        xml = """
        <report-group>
            <xml/>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem, {})


class ParseSectionTests(unittest.TestCase):

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
        columns, reportmap = self._callFUT(peopledir, elem)
        self.assertEqual(columns, [])
        self.assertEqual(reportmap, {})

    def test_column(self):
        xml = """
        <section>
            <column>
                <report id="r1">
                    <columns ids="name"/>
                </report>
            </column>
            <column>
            </column>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        columns, reportmap = self._callFUT(peopledir, elem)
        self.assertEqual(len(columns), 2)
        self.assertEqual(len(columns[0].reports), 1)
        self.assertEqual(reportmap.keys(), ['r1'])

    def test_single_report(self):
        xml = """
        <section>
            <report id="r1">
                <columns ids="name"/>
            </report>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        columns, reportmap = self._callFUT(peopledir, elem)
        self.assertEqual(columns, [])
        self.assertEqual(reportmap.keys(), ['r1'])

    def test_no_mix_columns_and_single_report_1(self):
        xml = """
        <section>
            <report id="r1">
                <columns ids="name"/>
            </report>
            <column>
                <report id="r2">
                    <columns ids="name"/>
                </report>
            </column>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_no_mix_columns_and_single_report_2(self):
        xml = """
        <section>
            <column>
                <report id="r2">
                    <columns ids="name"/>
                </report>
            </column>
            <report id="r1">
                <columns ids="name"/>
            </report>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_multiple_reports_require_columns(self):
        xml = """
        <section>
            <report id="r1">
                <columns ids="name"/>
            </report>
            <report id="r2">
                <columns ids="name"/>
            </report>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_unrecognized(self):
        xml = """
        <section>
            <xml/>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        from karl.utilities.peopleconf import ParseError
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)


class PeopleConfTests(unittest.TestCase):

    def _callFUT(self, peopledir, elem, **kw):
        from karl.utilities.peopleconf import peopleconf
        return peopleconf(peopledir, elem, **kw)

    def test_all(self):
        xml = """
        <peopledirectory>
            <categories>
                <category id="offices" title="Offices">
                    <value id="nyc" title="NYC">
                        <description>I<b>heart</b>NY</description>
                    </value>
                </category>
            </categories>
            <sections>
                <section id="everyone" title="Everyone" tab-title="All">
                    <acl>
                        <allow principal="bob" permission="view"/>
                    </acl>
                    <column>
                        <report-group title="Cities">
                            <report id="ny" title="NYC Office"
                                    link-title="NYC">
                                <filter category="offices" values="nyc"/>
                                <columns ids="name email"/>
                            </report>
                        </report-group>
                    </column>
                </section>
            </sections>
        </peopledirectory>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        self._callFUT(peopledir, elem)
        self.assertEqual(peopledir.order, ['everyone'])
        self.assertEqual(peopledir.keys(), ['everyone'])
        self.assertEqual(peopledir['everyone'].__acl__,
            [('Allow', 'bob', 'view')])
        self.assertEqual(list(peopledir['everyone'].keys()), ['ny'])

        self.assertEqual(list(peopledir.categories.keys()), ['offices'])
        self.assertEqual(peopledir.categories['offices'].title, 'Offices')
        self.assertEqual(list(peopledir.categories['offices'].keys()), ['nyc'])
        self.assertEqual(peopledir.categories['offices']['nyc'].description,
            'I<b>heart</b>NY')

    def test_force_reindex(self):
        from karl.testing import DummyCatalog
        xml = """
        <peopledirectory>
            <sections>
                <section id="everyone" title="Everyone">
                    <report id="everyone" title="Everyone">
                        <columns ids="name email"/>
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
        self._callFUT(peopledir, elem, force_reindex=True)


class ReindexTests(unittest.TestCase):

    def _callFUT(self, peopledir):
        from karl.utilities.peopleconf import reindex
        reindex(peopledir)

    def test_no_profiles(self):
        from karl.testing import DummyCatalog
        site = testing.DummyModel()
        peopledir = DummyPeopleDirectory()
        peopledir.catalog = DummyCatalog()
        site['people'] = peopledir
        profiles = testing.DummyModel()
        site['profiles'] = profiles
        self._callFUT(peopledir)

    def test_with_new_profile(self):
        from karl.testing import DummyCatalog
        site = testing.DummyModel()
        peopledir = DummyPeopleDirectory()
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
        peopledir = DummyPeopleDirectory()
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
        self.categories = {}

    def set_order(self, order):
        self.order = order

    def update_indexes(self):
        return False

def parse_xml(xml):
    from lxml.etree import parse
    from StringIO import StringIO
    return parse(StringIO(xml)).getroot()
