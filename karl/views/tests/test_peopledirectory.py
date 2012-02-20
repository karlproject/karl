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
"""Tests of karl.views.peopledirectory
"""

import unittest

from pyramid import testing
from simplejson import JSONDecoder

import karl.testing

class Test_admin_contents(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import admin_contents
        return admin_contents(context, request)

    def test_GET(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        from karl.views.peopledirectory import _ADDABLES
        site = testing.DummyModel()
        site['profiles'] = testing.DummyModel()
        pd = site['people'] = testing.DummyModel(title='People')
        directlyProvides(pd, IPeopleDirectory)
        request = testing.DummyRequest()

        info = self._callFUT(pd, request)

        self.assertEqual(info['api'].context, pd)
        self.assertEqual(info['peopledir'], pd)
        actions = info['actions']
        self.assertEqual(len(actions), len(_ADDABLES[IPeopleDirectory]) + 1)
        self.assertEqual(actions[0][1], 'add_section.html')
        self.assertEqual(actions[1][1], 'http://example.com/profiles/add.html')


class Test_peopledirectory_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import peopledirectory_view
        return peopledirectory_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface
        registerCatalogSearch()
        karl.testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

    def test_empty(self):
        from pyramid.exceptions import Forbidden
        pd = testing.DummyModel()
        pd.order = ()
        request = testing.DummyRequest()
        self.assertRaises(Forbidden, self._callFUT, pd, request)

    def test_no_sections_allowed(self):
        from pyramid.exceptions import Forbidden
        karl.testing.registerDummySecurityPolicy(permissive=False)
        pd = testing.DummyModel()
        pd['s1'] = testing.DummyModel()
        pd.order = ('s1',)
        request = testing.DummyRequest()
        self.assertRaises(Forbidden, self._callFUT, pd, request)

    def test_one_section_allowed(self):
        from pyramid.httpexceptions import HTTPFound
        karl.testing.registerDummySecurityPolicy(permissive=True)
        site = testing.DummyModel()
        pd = site['people'] = testing.DummyModel()
        pd['s1'] = testing.DummyModel()
        pd.order = ('s1',)
        request = testing.DummyRequest()
        response = self._callFUT(pd, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/people/s1/')

    def test_first_section_not_allowed(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.threadlocal import get_current_registry
        from pyramid.httpexceptions import HTTPFound
        karl.testing.registerDummySecurityPolicy(permissive=True)
        reg = get_current_registry() # b/c
        authz_policy = reg.queryUtility(IAuthorizationPolicy)
        authz_policy.permits = (lambda context, prin, perm:
                                    context.__name__ != 's1')
        site = testing.DummyModel()
        pd = site['people'] = testing.DummyModel()
        pd['s1'] = testing.DummyModel()
        pd['s2'] = testing.DummyModel()
        pd['s3'] = testing.DummyModel()
        pd.order = ('s1', 's2', 's3')
        request = testing.DummyRequest()
        response = self._callFUT(pd, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/people/s2/')


class Test_download_peopledirectory_xml(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import download_peopledirectory_xml
        return download_peopledirectory_xml(context, request)

    def test_empty(self):
        # Actual XML emission tested in karl.utilities.tests.test_peopleconf
        from lxml import etree
        pd = testing.DummyModel(order=())
        pd['categories'] = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(pd, request)
        self.assertEqual(response.headers['Content-Type'],
                         'application/xml; charset=UTF-8')
        tree = etree.fromstring(response.body)
        self.failUnless(tree.xpath('/peopledirectory/categories'))
        self.failIf(tree.xpath('/peopledirectory/categories/*'))
        self.failUnless(tree.xpath('/peopledirectory/sections'))
        self.failIf(tree.xpath('/peopledirectory/sections/*'))


class Test_upload_peopledirectory_xml(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import upload_peopledirectory_xml
        return upload_peopledirectory_xml(context, request)

    def test_no_submit(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        site = testing.DummyModel()
        pd = site['people'] = testing.DummyModel(title='People')
        directlyProvides(pd, IPeopleDirectory)
        request = testing.DummyRequest()

        info = self._callFUT(pd, request)

        self.assertEqual(info['api'].context, pd)
        self.assertEqual(info['peopledir'], pd)

    def test_w_submit_empty_clears_existing(self):
        from StringIO import StringIO
        from pyramid.httpexceptions import HTTPFound
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        XML = """<?xml version="1.0"?>
        <peopledirectory>
         <categories>
         </categories>
         <sections>
         </sections>
        </peopledirectory>
        """
        site = testing.DummyModel(list_aliases={})
        site['profiles'] = testing.DummyModel()
        pd = site['people'] = testing.DummyModel(title='People')
        def _set_order(value):
            pd._order = value
        def _update_indexes():
            pd._indexes_updated = True
        pd.set_order = _set_order
        pd.update_indexes = _update_indexes
        pd.catalog = testing.DummyModel(document_map=testing.DummyModel())
        directlyProvides(pd, IPeopleDirectory)
        categories = pd['categories'] = testing.DummyModel()
        categories['bogus'] = testing.DummyModel()
        pd['nonesuch'] = testing.DummyModel()
        class DummyFile:
            pass
        xml = DummyFile()
        xml.file = StringIO(XML)
        request = testing.DummyRequest(post={'form.submit': '1',
                                             'xml':  xml,
                                            })

        response = self._callFUT(pd, request)

        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/people/')

        self.failUnless(pd._indexes_updated)
        self.assertEqual(list(pd.order), [])
        self.assertEqual(list(pd.keys()), ['categories'])
        self.assertEqual(list(pd['categories'].keys()), [])


class Test_get_tabs(unittest.TestCase):

    def _callFUT(self, peopledir, request, current_sectionid):
        from karl.views.peopledirectory import get_tabs
        return get_tabs(peopledir, request, current_sectionid)

    def test_empty(self):
        pd = testing.DummyModel(order=[])
        request = testing.DummyRequest()
        tabs = self._callFUT(pd, request, 's2')
        self.assertEqual(len(tabs), 0)

    def test_one_tab(self):
        pd = testing.DummyModel(order=['s1'])
        pd['s1'] = testing.DummyModel(tab_title='Section 1')
        request = testing.DummyRequest()
        tabs = self._callFUT(pd, request, 's1')
        self.assertEqual(len(tabs), 1)
        tab = tabs[0]
        self.assertEqual(tab['href'], 'http://example.com/s1/')
        self.assertEqual(tab['title'], 'Section 1')
        self.failUnless(tab['selected'])

    def test_multiple_tabs(self):
        pd = testing.DummyModel(order=['s1', 's2'])
        pd['s1'] = testing.DummyModel(tab_title='Section 1')
        pd['s2'] = testing.DummyModel(tab_title='Section 2')
        request = testing.DummyRequest()
        tabs = self._callFUT(pd, request, 's2')
        self.assertEqual(len(tabs), 2)
        tab = tabs[0]
        self.assertEqual(tab['href'], 'http://example.com/s1/')
        self.assertEqual(tab['title'], 'Section 1')
        self.failIf(tab['selected'])
        tab = tabs[1]
        self.assertEqual(tab['href'], 'http://example.com/s2/')
        self.assertEqual(tab['title'], 'Section 2')
        self.failUnless(tab['selected'])

    def test_skip_unauthorized(self):
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.threadlocal import get_current_registry
        karl.testing.registerDummySecurityPolicy(permissive=True)
        reg = get_current_registry() # b/c
        authz_policy = reg.queryUtility(IAuthorizationPolicy)
        authz_policy.permits = (lambda context, prin, perm:
                                    context.__name__ != 's1')
        pd = testing.DummyModel(order=['s1', 's2', 's3'])
        pd['s1'] = testing.DummyModel(tab_title='Section 1')
        pd['s2'] = testing.DummyModel(tab_title='Section 2')
        pd['s3'] = testing.DummyModel(tab_title='Section 3')
        request = testing.DummyRequest()
        tabs = self._callFUT(pd, request, 's2')
        self.assertEqual(len(tabs), 2)
        tab = tabs[0]
        self.assertEqual(tab['href'], 'http://example.com/s2/')
        self.assertEqual(tab['title'], 'Section 2')
        self.failUnless(tab['selected'])
        tab = tabs[1]
        self.assertEqual(tab['href'], 'http://example.com/s3/')
        self.assertEqual(tab['title'], 'Section 3')
        self.failIf(tab['selected'])


class Test_render_report_group(unittest.TestCase):

    def _callFUT(self, group, request, css_class=''):
        from karl.views.peopledirectory import render_report_group
        return render_report_group(group, request, css_class)

    def _makeSectionColumn(self, **kw):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleSectionColumn
        column = testing.DummyModel(**kw)
        directlyProvides(column, IPeopleSectionColumn)
        return column

    def _makeGroup(self, **kw):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportGroup
        group = testing.DummyModel(**kw)
        directlyProvides(group, IPeopleReportGroup)
        return group

    def _makeReport(self, **kw):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        report = testing.DummyModel(**kw)
        directlyProvides(report, IPeopleReport)
        return report

    def test_empty(self):
        group = self._makeGroup(title='')
        request = testing.DummyRequest()
        html = self._callFUT(group, request)
        self.assertEqual(html, '<ul>\n</ul>')

    def test_empty_no_title(self):
        group = self._makeGroup()
        request = testing.DummyRequest()
        html = self._callFUT(group, request)
        self.assertEqual(html, '<ul>\n</ul>')

    def test_empty_w_title(self):
        group = self._makeGroup(title='Testing')
        request = testing.DummyRequest()
        html = self._callFUT(group, request)
        self.assertEqual(html, '<h3>Testing</h3>\n<ul>\n</ul>')

    def test_structure(self):

        group = self._makeGroup(title='Group 1')

        report = group['r11'] = self._makeReport(
            link_title='Report 1.1', css_class='priority')

        group2 = group['g12'] = self._makeGroup(title='Group 1.2')

        report2 = group2['r121'] = self._makeReport(
            link_title='Report 1.2.1', css_class='general')

        request = testing.DummyRequest()
        html = self._callFUT(group, request, 'toplevel')

        self.failUnless('<h3>Group 1</h3>' in html)
        self.failUnless('>Report 1.1</a>' in html)
        self.failUnless('<h3>Group 1.2</h3>' in html)
        self.failUnless('>Report 1.2.1</a>' in html)

        self.failUnless('class="priority"' in html)
        self.failUnless('class="general"' in html)


class Test_get_admin_actions(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import get_admin_actions
        return get_admin_actions(context, request)

    def _makeContext(self):
        site = testing.DummyModel()
        site['profiles'] = testing.DummyModel()
        pd = site['people'] = testing.DummyModel()
        return pd

    def test_not_admin(self):
        karl.testing.registerDummySecurityPolicy(permissive=False)
        context = self._makeContext()
        request = testing.DummyRequest()
        actions = self._callFUT(context, request)
        self.assertEqual(len(actions), 0)

    def test_w_admin_no_marker(self):
        karl.testing.registerDummySecurityPolicy(permissive=True)
        context = self._makeContext()
        request = testing.DummyRequest()
        actions = self._callFUT(context, request)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action[0], 'Edit')
        self.assertEqual(action[1], 'edit.html')

    def test_w_admin_w_marker(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        karl.testing.registerDummySecurityPolicy(permissive=True)
        context = self._makeContext()
        directlyProvides(context, IPeopleReport)
        request = testing.DummyRequest()
        actions = self._callFUT(context, request)
        self.assertEqual(len(actions), 5)
        action = actions[0]
        self.assertEqual(action[0], 'Edit')
        self.assertEqual(action[1], 'edit.html')
        action = actions[1]
        self.assertEqual(action[0], 'Add CategoryFilter')
        self.assertEqual(action[1], 'add_category_report_filter.html')
        action = actions[2]
        self.assertEqual(action[0], 'Add GroupFilter')
        self.assertEqual(action[1], 'add_group_report_filter.html')
        action = actions[3]
        self.assertEqual(action[0], 'Add IsStaffFilter')
        self.assertEqual(action[1], 'add_is_staff_report_filter.html')
        action = actions[4]
        self.assertEqual(action[0], 'Add MailingList')
        self.assertEqual(action[1], 'add_mailing_list.html')

    def test_w_admin_w_marker_already_mailinglist(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        karl.testing.registerDummySecurityPolicy(permissive=True)
        context = self._makeContext()
        context['mailinglist'] = testing.DummyModel()
        directlyProvides(context, IPeopleReport)
        request = testing.DummyRequest()
        actions = self._callFUT(context, request)
        self.assertEqual(len(actions), 4)
        action = actions[0]
        self.assertEqual(action[0], 'Edit')
        self.assertEqual(action[1], 'edit.html')
        action = actions[1]
        self.assertEqual(action[0], 'Add CategoryFilter')
        self.assertEqual(action[1], 'add_category_report_filter.html')
        action = actions[2]
        self.assertEqual(action[0], 'Add GroupFilter')
        self.assertEqual(action[1], 'add_group_report_filter.html')
        action = actions[3]
        self.assertEqual(action[0], 'Add IsStaffFilter')
        self.assertEqual(action[1], 'add_is_staff_report_filter.html')


class Test_get_actions(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import get_actions
        return get_actions(context, request)

    def _makeContext(self):
        site = testing.DummyModel()
        site['profiles'] = testing.DummyModel()
        pd = site['people'] = testing.DummyModel()
        return pd

    def test_not_admin(self):
        karl.testing.registerDummySecurityPolicy(permissive=False)
        context = self._makeContext()
        request = testing.DummyRequest()
        actions = self._callFUT(context, request)
        self.assertEqual(len(actions), 0)

    def test_w_admin_not_admin_html_view(self):
        karl.testing.registerDummySecurityPolicy(permissive=True)
        context = self._makeContext()
        request = testing.DummyRequest()
        actions = self._callFUT(context, request)
        #self.assertEqual(len(actions), 2) # see LP #668489
        self.assertEqual(len(actions), 1)
        action = actions[0]
        #self.assertEqual(action[0], 'Admin')
        #self.assertEqual(action[1], 'admin.html')
        #action = actions[1]
        self.assertEqual(action[0], 'Add User')
        self.assertEqual(action[1], 'http://example.com/profiles/add.html')

    def test_w_admin_and_admin_html_view(self):
        karl.testing.registerDummySecurityPolicy(permissive=True)
        context = self._makeContext()
        request = testing.DummyRequest()
        request.view_name = 'admin.html'
        actions = self._callFUT(context, request)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action[0], 'Add User')
        self.assertEqual(action[1], 'http://example.com/profiles/add.html')


class Test_section_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import section_view
        return section_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface
        registerCatalogSearch()
        karl.testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

    def test_empty_column(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        from karl.models.interfaces import IPeopleSectionColumn
        site = testing.DummyModel()
        pd = site['people'] = testing.DummyModel(order=('s1',))
        directlyProvides(pd, IPeopleDirectory)
        section = pd['s1'] = testing.DummyModel(title='A', tab_title='B')
        column = section['c1'] = testing.DummyModel(title='', width=40)
        directlyProvides(column, IPeopleSectionColumn)

        request = testing.DummyRequest()
        info = self._callFUT(section, request)

        self.assertEqual(info['api'].context, section)
        self.assertEqual(info['peopledir'], pd)
        self.assertEqual(info['peopledir_tabs'], [{
            'href': 'http://example.com/people/s1/',
            'url': 'http://example.com/people/s1/',
            'selected': 'selected',
            'title': 'B',
            }])
        c_info = info['columns']
        self.assertEqual(len(c_info), 1)
        self.assertEqual(c_info[0]['html'], '<ul class="column">\n</ul>')
        self.assertEqual(c_info[0]['width'], 40)

    def test_non_empty_column(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleSectionColumn
        pd, section, report = _makeReport()
        del section[report.__name__]
        directlyProvides(report, IPeopleReport)
        report.css_class = ''
        column = section['c1'] = testing.DummyModel(title='')
        directlyProvides(column, IPeopleSectionColumn)
        column[report.__name__] = report

        request = testing.DummyRequest()
        info = self._callFUT(section, request)

        c_info = info['columns']
        self.assertEqual(len(c_info), 1)
        html = c_info[0]['html']
        self.assertEqual(html.split('\n'), [
                         '<ul class="column">',
                         '<li><a href="http://example.com/people/s1/c1/r1/"'
                                    ' class="">A</a></li>',
                         '</ul>'])

    def test_multiple_columns(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleSectionColumn
        pd, section, report = _makeReport()
        del section[report.__name__]
        directlyProvides(report, IPeopleReport)
        report.css_class = ''
        column = section['c1'] = testing.DummyModel(title='')
        directlyProvides(column, IPeopleSectionColumn)
        column['r1'] = report

        column2 = section['c2'] = testing.DummyModel(title='')
        directlyProvides(column2, IPeopleSectionColumn)
        r2 = column2['r2'] = testing.DummyModel(link_title='B',
                                                css_class='red')
        directlyProvides(r2, IPeopleReport)

        section.values = lambda: [x[1] for x in sorted(section.items())]

        request = testing.DummyRequest()
        info = self._callFUT(section, request)

        c_info = info['columns']
        self.assertEqual(len(c_info), 2)
        html = c_info[0]['html']
        self.assertEqual(html.split('\n'), [
                         '<ul class="column">',
                         '<li><a href="http://example.com/people/s1/c1/r1/"'
                                    ' class="">A</a></li>',
                         '</ul>'])
        html = c_info[1]['html']
        self.assertEqual(html.split('\n'), [
                         '<ul class="column">',
                         '<li><a href="http://example.com/people/s1/c2/r2/"'
                                    ' class="red">B</a></li>',
                         '</ul>'])

    def test_single_allowed_report(self):
        # when a section contains only a single report, redirect to that report
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from pyramid.httpexceptions import HTTPFound
        self._register()
        pd, section, report = _makeReport()
        directlyProvides(report, IPeopleReport)

        request = testing.DummyRequest()
        response = self._callFUT(section, request)

        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/people/s1/r1/')


class Test_report_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import report_view
        return report_view(context, request)

    def _register(self, **kw):
        from zope.interface import Interface
        from karl.testing import registerCatalogSearch
        from karl.testing import registerSettings
        from karl.models.interfaces import ILetterManager
        registerSettings(**kw)
        registerCatalogSearch()
        karl.testing.registerAdapter(DummyLetterManager, Interface, ILetterManager)

    def test_unqualified_report_no_mailinglist(self):
        self._register()
        pd, section, report = _makeReport()
        request = testing.DummyRequest()

        info = self._callFUT(report, request)

        self.assertEqual(info['api'].context, report)
        self.assertEqual(info['peopledir'], pd)
        self.failUnless('grid_data' in info['head_data'])
        self.assertEqual(info['print_url'],
            'http://example.com/people/s1/r1/print.html')
        self.assertEqual(info['csv_url'],
            'http://example.com/people/s1/r1/csv')
        self.assertEqual(info['pictures_url'],
            'http://example.com/people/s1/r1/picture_view.html')
        self.assertEqual(info['qualifiers'], [])
        self.assertEqual(info['mailto'], None)

    def test_report_with_mailinglist_wo_subdomain(self):
        self._register()
        pd, section, report = _makeReport()
        report['mailinglist'] = testing.DummyModel(short_address='alias')
        request = testing.DummyRequest()

        info = self._callFUT(report, request)

        self.assertEqual(info['mailto'],
                         'mailto:alias@karl3.example.com')

    def test_report_with_mailinglist_w_subdomain(self):
        self._register(system_list_subdomain='lists.example.com')
        pd, section, report = _makeReport()
        report['mailinglist'] = testing.DummyModel(short_address='alias')
        request = testing.DummyRequest()

        info = self._callFUT(report, request)

        self.assertEqual(info['mailto'],
                         'mailto:alias@lists.example.com')

    def test_qualified_report(self):
        self._register()
        pd, section, report = _makeReport()
        request = testing.DummyRequest({'body': 'spock'})

        info = self._callFUT(report, request)

        self.assertEqual(info['peopledir'], pd)
        self.assertEqual(info['api'].context, report)
        self.failUnless('grid_data' in info['head_data'])
        self.assertEqual(info['print_url'],
            'http://example.com/people/s1/r1/print.html?body=spock')
        self.assertEqual(info['csv_url'],
            'http://example.com/people/s1/r1/csv?body=spock')
        self.assertEqual(info['pictures_url'],
            'http://example.com/people/s1/r1/picture_view.html?body=spock')
        self.assertEqual(info['qualifiers'], ['Search for "spock"'])


class Test_jquery_grid_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import jquery_grid_view
        return jquery_grid_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()

    def test_view(self):
        self._register()
        report = DummyReport()
        report.title = 'Report A'
        report.columns = ['name']
        request = testing.DummyRequest({'start': 0, 'limit': 10})

        response = self._callFUT(report, request)

        self.assertEqual(response.content_type, 'application/x-json')
        payload = JSONDecoder().decode(response.body)
        self.assertEqual(payload['records'], [])
        self.assertEqual(payload['batchSize'], 10)
        self.failUnless(payload.get('columns'))
        self.assertEqual(payload['columns'][0]['id'], 'name')


class Test_get_column_jsdata(unittest.TestCase):

    def _callFUT(self, columns, max_width):
        from karl.views.peopledirectory import get_column_jsdata
        return get_column_jsdata(columns, max_width)

    def test_equal_weights(self):
        columns = [
            testing.DummyModel(id='name', title='Name', weight=1.0),
            testing.DummyModel(id='email', title='Email', weight=1.0),
        ]
        jsdata = self._callFUT(columns, 100)
        self.assertEqual(jsdata, [
            {'width': 50, 'id': 'name', 'label': 'Name'},
            {'width': 50, 'id': 'email', 'label': 'Email'}
            ])

    def test_unequal_weights(self):
        columns = [
            testing.DummyModel(id='name', title='Name', weight=1.2),
            testing.DummyModel(id='email', title='Email', weight=1.0),
        ]
        jsdata = self._callFUT(columns, 100)
        self.assertEqual(jsdata, [
            {'width': 54, 'id': 'name', 'label': 'Name'},
            {'width': 45, 'id': 'email', 'label': 'Email'}
            ])


class Test_profile_photo_rows(unittest.TestCase):

    def _callFUT(self, entries, request, api):
        from karl.views.peopledirectory import profile_photo_rows
        return profile_photo_rows(entries, request, api)

    def test_it(self):
        entries = []
        for i in range(4):
            entries.append(_makeProfile())
        del entries[0]['photo']

        class DummyAPI:
            static_url = 'http://example.com/static'

        request = testing.DummyRequest()
        iterator = self._callFUT(entries, request, DummyAPI())

        row = iterator.next()
        self.assertEqual(len(row), 3)
        self.assertEqual(row[0], {
            'profile': entries[0],
            'url': 'http://example.com/',
            'photo_url': 'http://example.com/static/images/defaultUser.gif',
            })
        self.assertEqual(row[1], {
            'profile': entries[1],
            'url': 'http://example.com/',
            'photo_url': 'http://example.com/photo/thumb/75x100.jpg',
            })

        row = iterator.next()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0]['profile'], entries[3])

        # no more rows
        self.assertEqual(len(list(iterator)), 0)


class Test_picture_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import picture_view
        return picture_view(context, request)

    def _register(self, **kw):
        from zope.interface import Interface
        from karl.models.interfaces import ILetterManager
        from karl.testing import registerCatalogSearch
        from karl.testing import registerSettings
        registerSettings(**kw)
        registerCatalogSearch()
        karl.testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)


    def test_unqualified_report(self):
        self._register()

        pd, section, report = _makeReport()
        request = testing.DummyRequest()

        info = self._callFUT(report, request)

        self.assertEqual(info['peopledir'], pd)
        self.assertEqual(info['api'].context, report)
        self.assertEqual(len(list(info['rows'])), 0)
        self.assertEqual(info['print_url'],
            'http://example.com/people/s1/r1/print.html')
        self.assertEqual(info['csv_url'],
            'http://example.com/people/s1/r1/csv')
        self.assertEqual(info['tabular_url'],
            'http://example.com/people/s1/r1/')
        self.assertEqual(info['qualifiers'], [])
        self.assertEqual(info['mailto'], None)

    def test_qualified_report(self):
        self._register()

        pd, section, report = _makeReport()
        request = testing.DummyRequest({'body': "spock's brain"})

        info = self._callFUT(report, request)

        self.assertEqual(len(list(info['rows'])), 0)
        self.assertEqual(info['print_url'],
            'http://example.com/people/s1/r1/print.html?body=spock%27s+brain')
        self.assertEqual(info['csv_url'],
            'http://example.com/people/s1/r1/csv?body=spock%27s+brain')
        self.assertEqual(info['tabular_url'],
            'http://example.com/people/s1/r1/?body=spock%27s+brain')
        self.assertEqual(info['qualifiers'], ['Search for "spock\'s brain"'])
        self.assertEqual(info['mailto'], None)

    def test_bad_search_text(self):
        from zope.index.text.parsetree import ParseError
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface

        def search(*args, **kw):
            raise ParseError
        karl.testing.registerAdapter(search, (Interface, Interface),
            ICatalogSearch)
        karl.testing.registerAdapter(search, (Interface,), ICatalogSearch)
        karl.testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        info = self._callFUT(report, request)
        self.assertEqual(len(list(info['rows'])), 0)
        self.assertEqual(info['mailto'], None)

    def test_report_with_mailinglist_wo_subdomain(self):
        self._register()
        pd, section, report = _makeReport()
        report['mailinglist'] = testing.DummyModel(short_address='alias')
        request = testing.DummyRequest()

        info = self._callFUT(report, request)

        self.assertEqual(info['mailto'],
                         'mailto:alias@karl3.example.com')

    def test_report_with_mailinglist_w_subdomain(self):
        self._register(system_list_subdomain='lists.example.com')
        pd, section, report = _makeReport()
        report['mailinglist'] = testing.DummyModel(short_address='alias')
        request = testing.DummyRequest()

        info = self._callFUT(report, request)

        self.assertEqual(info['mailto'],
                         'mailto:alias@lists.example.com')


class Test_get_search_qualifiers(unittest.TestCase):

    def _callFUT(self, request):
        from karl.views.peopledirectory import get_search_qualifiers
        return get_search_qualifiers(request)

    def test_no_qualifiers(self):
        request = testing.DummyRequest()
        kw, qualifiers = self._callFUT(request)
        self.assertEqual(kw, {})
        self.assertEqual(qualifiers, [])

    def test_letter_qualifier(self):
        request = testing.DummyRequest({'lastnamestartswith': 'L'})
        kw, qualifiers = self._callFUT(request)
        self.assertEqual(kw, {'query': {'lastnamestartswith': 'L'}})
        self.assertEqual(qualifiers, ["Last names that begin with 'L'"])

    def test_body_qualifier(self):
        request = testing.DummyRequest({'body': 'a b*'})
        kw, qualifiers = self._callFUT(request)
        self.assertEqual(kw, {'query': {'body': 'a b*'}})
        self.assertEqual(qualifiers, ['Search for "a b*"'])


class Test_get_report_query(unittest.TestCase):

    def _callFUT(self, report, request):
        from karl.views.peopledirectory import get_report_query
        return get_report_query(report, request)

    def test_uses_underlying_reports_query(self):
        report = DummyReport()
        report._query = {'category_office': {'query': ['nyc'],
                                             'operator': 'or'}}
        request = testing.DummyRequest({
            'lastnamestartswith': 'L',
            'body': 'a b*',
            })
        kw = self._callFUT(report, request)
        self.assertEqual(kw, {
            'allowed': {'operator': 'or', 'query': []},
            'category_office': {'operator': 'or', 'query': ['nyc']},
            'lastnamestartswith': 'L',
            'texts': 'a b**',
            })



class Test_get_grid_data(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request, **kw):
        from karl.views.peopledirectory import get_grid_data
        return get_grid_data(context, request, **kw)

    def test_empty(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        grid_data = self._callFUT(report, request, limit=10, width=100)
        batch = {'reverse': False, 'next_batch': None, 'entries': [],
            'batch_size': 10, 'sort_index': 'lastfirst',
            'previous_batch': None, 'batch_end': 0,
            'batching_required': False, 'total': 0, 'batch_start': 0}
        self.assertEqual(grid_data, {
            'fetch_url': 'http://example.com/people/s1/r1/jquery_grid',
            'sortColumn': 'name',
            'records': [],
            'sortDirection': 'asc',
            'width': 100,
            'batch': batch,
            'batchSize': 10,
            'totalRecords': 0,
            'scrollbarWidth': 15,
            'allocateWidthForScrollbar': True,
            'columns': [{'width': 85, 'id': 'name', 'label': 'Name'}],
            })

    def test_non_empty(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        def searcher(context, request=None):
            def resolve(docid):
                return testing.DummyModel(title='Profile %d' % docid)
            def search(**kw):
                return (25, range(25), resolve)
            return search
        karl.testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        karl.testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        grid_data = self._callFUT(report, request, start=21, limit=10)
        self.assertEqual(len(grid_data['records']), 4)
        self.assertEqual(grid_data['totalRecords'], 25)

    def test_letter_and_text_search(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        def searcher(context, request=None):
            def resolve(docid):
                return testing.DummyModel(title='Profile %d' % docid)
            def search(**kw):
                return (25, range(25), resolve)
            return search
        karl.testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        karl.testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        pd, section, report = _makeReport()
        request = testing.DummyRequest({
            'lastnamestartswith': 'A',
            'body': 'stuff',
            })
        grid_data = self._callFUT(report, request, start=21, limit=10)
        self.assertEqual(grid_data['fetch_url'],
            'http://example.com/people/s1/r1/jquery_grid?'
            'body=stuff&lastnamestartswith=A')

    def test_bad_text_search(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        from zope.index.text.parsetree import ParseError
        def searcher(context, request=None):
            def search(**kw):
                raise ParseError()
            return search
        karl.testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        karl.testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        grid_data = self._callFUT(report, request)
        self.assertEqual(len(grid_data['records']), 0)
        self.assertEqual(grid_data['totalRecords'], 0)


class Test_get_report_descriptions(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, report):
        from karl.views.peopledirectory import get_report_descriptions
        return get_report_descriptions(report)

    def test_no_matching_category(self):
        pd, section, report = _makeReport()
        report['office'] = testing.DummyModel(values=['nyc'])
        res = self._callFUT(report)
        self.assertEqual(res, [])

    def test_no_matching_description(self):
        pd, section, report = _makeReport()
        report['office'] = testing.DummyModel(values=['nyc'])
        office = pd['categories']['office'] = testing.DummyModel()
        res = self._callFUT(report)
        self.assertEqual(res, [])

    def test_one_description(self):
        pd, section, report = _makeReport()
        report['office'] = testing.DummyModel(values=['nyc'])
        office = pd['categories']['office'] = testing.DummyModel()
        office['nyc'] = testing.DummyModel(title='New York',
                                           description='I<b>heart</b>NY',
                                          )
        res = self._callFUT(report)
        self.assertEqual(res, ['I<b>heart</b>NY'])


class Test_text_dump(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, report, request):
        from karl.views.peopledirectory import text_dump
        return text_dump(report, request)

    def test_empty(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        dumper = self._callFUT(report, request)
        rows = list(dumper)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], ['Name'])

    def test_non_empty(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        def searcher(context, request=None):
            def resolve(docid):
                return testing.DummyModel(title='Profile %d' % docid)
            def search(**kw):
                return (2, range(2), resolve)
            return search
        karl.testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        karl.testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        dumper = self._callFUT(report, request)
        rows = list(dumper)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], ['Name'])
        self.assertEqual(rows[1], ['Profile 0'])
        self.assertEqual(rows[2], ['Profile 1'])


class Test_csv_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import csv_view
        return csv_view(context, request)

    def test_empty(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        response = self._callFUT(report, request)
        self.assertEqual(response.content_type, 'application/x-csv')
        self.assertEqual(response.headers['Content-Disposition'],
            'attachment;filename=r1.csv')
        self.assertEqual(response.body, 'Name\r\n')

    def test_non_empty(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        def searcher(context, request=None):
            def resolve(docid):
                return testing.DummyModel(title=u'Profile "%d" \u30b7' % docid)
            def search(**kw):
                return (2, range(2), resolve)
            return search
        karl.testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        karl.testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        response = self._callFUT(report, request)
        self.assertEqual(response.content_type, 'application/x-csv')
        self.assertEqual(response.headers['Content-Disposition'],
            'attachment;filename=r1.csv')
        self.assertEqual(response.body,
            'Name\r\n'
            '"Profile ""0"" \xe3\x82\xb7"\r\n'
            '"Profile ""1"" \xe3\x82\xb7"\r\n'
            )


class Test_print_view(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, response):
        from karl.views.peopledirectory import print_view
        return print_view(context, response)

    def test_it(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        pd, section, report = _makeReport()
        request = testing.DummyRequest()
        info = self._callFUT(report, request)
        self.assertEqual(info['header'], ['Name'])
        self.assertEqual(list(info['rows']), [])


class Test_open_search_view(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import opensearch_view
        return opensearch_view(context, request)

    def test_it(self):
        context = testing.DummyModel()
        context.title = 'Test Report'
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['report'], context)
        self.assertEqual(info['url'], 'http://example.com/')


class Test_redirector_view(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import redirector_view
        return redirector_view(context, request)

    def test_w_absolute_url(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyModel()
        context.target_url = 'http://other.example.com/'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://other.example.com/')

    def test_w_site_relative_url(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyModel()
        context.target_url = '/somewhere/over/the/rainbow'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                         'http://example.com/somewhere/over/the/rainbow')

    def test_w_relative_url(self):
        from pyramid.httpexceptions import HTTPFound
        grandparent = testing.DummyModel()
        parent = grandparent['parent'] = testing.DummyModel()
        context = parent['context'] = testing.DummyModel()
        context.target_url = 'somewhere/over/the/rainbow'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                         'http://example.com/parent/somewhere/over/the/rainbow')


class Test_redirector_admin_view(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import redirector_admin_view
        return redirector_admin_view(context, request)

    def test_it(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location, 'http://example.com/edit.html')


class ReportColumnTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.views.peopledirectory import ReportColumn
        return ReportColumn

    def _makeOne(self, id='col1', title='Column One', **kw):
        return self._getTargetClass()(id, title, **kw)

    def test_ctor(self):
        col = self._makeOne()
        self.assertEqual(col.id, 'col1')
        self.assertEqual(col.title, 'Column One')
        self.assertEqual(col.sort_index, 'col1')
        self.assertEqual(col.weight, 1.0)

    def test_render_text_exists(self):
        col = self._makeOne()
        profile = testing.DummyModel(col1='xyz')
        self.assertEqual(col.render_text(profile), 'xyz')

    def test_render_text_missing(self):
        col = self._makeOne()
        profile = testing.DummyModel()
        self.assertEqual(col.render_text(profile), '')

    def test_render_html_exists(self):
        col = self._makeOne()
        profile = testing.DummyModel(col1='<xyz>')
        request = testing.DummyRequest()
        self.assertEqual(col.render_html(profile, request), '&lt;xyz&gt;')

    def test_render_html_missing(self):
        col = self._makeOne()
        profile = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertEqual(col.render_html(profile, request), '&nbsp;')

    def test_render_text_none(self):
        col = self._makeOne()
        profile = testing.DummyModel(col1=None)
        self.assertEqual(col.render_text(profile), '')


class NameColumnTests(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from karl.views.peopledirectory import NameColumn
        return NameColumn

    def _makeOne(self, id='col1', title='Name Column', **kw):
        return self._getTargetClass()(id, title, **kw)

    def test_render_text(self):
        col = self._makeOne()
        profile = testing.DummyModel(title='Profile 1')
        self.assertEqual(col.render_text(profile), 'Profile 1')

    def test_render_html(self):
        col = self._makeOne()
        profile = testing.DummyModel(title='Odd"Name')
        request = testing.DummyRequest()
        self.assertEqual(col.render_html(profile, request),
            'Odd"Name<a href="http://example.com/" style="display: none;"/>')


class PhoneColumnTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.views.peopledirectory import PhoneColumn
        return PhoneColumn

    def _makeOne(self, id='phone', title='Phone'):
        return self._getTargetClass()(id, title)

    def test_render_text_with_extension(self):
        col = self._makeOne()
        profile = testing.DummyModel(phone='123-4567', extension='89')
        self.assertEqual(col.render_text(profile), '123-4567 x 89')

    def test_render_text_no_extension(self):
        col = self._makeOne()
        profile = testing.DummyModel(phone='123-4567')
        self.assertEqual(col.render_text(profile), '123-4567')

    def test_render_text_no_phone(self):
        col = self._makeOne()
        profile = testing.DummyModel()
        self.assertEqual(col.render_text(profile), '')

    def test_render_text_none(self):
        col = self._makeOne()
        profile = testing.DummyModel(phone=None)
        self.assertEqual(col.render_text(profile), '')

    def test_render_html_no_phone(self):
        col = self._makeOne()
        profile = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertEqual(col.render_html(profile, request), '&nbsp;')


class DummyLetterManager:
    def __init__(self, context):
        self.context = context

    def get_info(self, request):
        return {}


def _makeReport():
    from zope.interface import directlyProvides
    from karl.models.interfaces import IPeopleDirectory
    site = testing.DummyModel()
    pd = site['people'] = testing.DummyModel(order=[])
    directlyProvides(pd, IPeopleDirectory)
    pd['categories'] = testing.DummyModel()

    section = pd['s1'] = testing.DummyModel(tab_title='A', title='Section A')
    pd.order = ('s1',)
    report = DummyReport()
    section['r1'] = report
    return pd, section, report


class DummyReport(testing.DummyModel):
    _query = None
    def __init__(self):
        testing.DummyModel.__init__(self,
            title='Report A',
            link_title='A',
            columns=['name'],
            )

    def getQuery(self):
        return self._query or {}


def _makeProfile():
    from karl.content.interfaces import IImage
    from zope.interface import implements

    class DummyImageFile(object):
        implements(IImage)
        is_image = True

        def __init__(self):
            self.title = None
            self.data = ONE_PIXEL_JPEG
            self.size = len(self.data)
            self.mimetype = None
            self.filename= None
            self.creator = None

    class DummyProfile(testing.DummyModel):
        def __init__(self):
            testing.DummyModel.__init__(self)
            self['photo'] = DummyImageFile()

        def get_photo(self):
            return self.get('photo')

    return DummyProfile()


ONE_PIXEL_JPEG = [
0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01,
0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xff, 0xdb, 0x00, 0x43, 0x00, 0x05,
0x03, 0x04, 0x04, 0x04, 0x03, 0x05, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x06,
0x07, 0x0c, 0x08, 0x07, 0x07, 0x07, 0x07, 0x0f, 0x0b, 0x0b, 0x09, 0x0c, 0x11,
0x0f, 0x12, 0x12, 0x11, 0x0f, 0x11, 0x11, 0x13, 0x16, 0x1c, 0x17, 0x13, 0x14,
0x1a, 0x15, 0x11, 0x11, 0x18, 0x21, 0x18, 0x1a, 0x1d, 0x1d, 0x1f, 0x1f, 0x1f,
0x13, 0x17, 0x22, 0x24, 0x22, 0x1e, 0x24, 0x1c, 0x1e, 0x1f, 0x1e, 0xff, 0xdb,
0x00, 0x43, 0x01, 0x05, 0x05, 0x05, 0x07, 0x06, 0x07, 0x0e, 0x08, 0x08, 0x0e,
0x1e, 0x14, 0x11, 0x14, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0xff, 0xc0, 0x00, 0x11, 0x08, 0x00, 0x01, 0x00, 0x01, 0x03, 0x01,
0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01, 0xff, 0xc4, 0x00, 0x15, 0x00,
0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x08, 0xff, 0xc4, 0x00, 0x14, 0x10, 0x01, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0xff, 0xc4, 0x00, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xc4, 0x00,
0x14, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xda, 0x00, 0x0c, 0x03, 0x01, 0x00,
0x02, 0x11, 0x03, 0x11, 0x00, 0x3f, 0x00, 0xb2, 0xc0, 0x07, 0xff, 0xd9
]

ONE_PIXEL_JPEG = ''.join([chr(x) for x in ONE_PIXEL_JPEG])
