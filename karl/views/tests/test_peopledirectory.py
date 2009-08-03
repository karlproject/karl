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
"""Tests of karl.views.peopledirectory"""

import unittest
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing


class PeopleDirectoryViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import peopledirectory_view
        return peopledirectory_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

    def test_index_page(self):
        self._register()

        report = DummyReport()
        section = report.__parent__
        section.columns.append(testing.DummyModel(title='', reports=[]))
        pd = section.__parent__

        # expect it to show the first section
        renderer = testing.registerDummyRenderer(
            'templates/people_section.pt')
        request = testing.DummyRequest()
        self._callFUT(pd, request)

        self.assertEqual(renderer.peopledir, pd)
        self.assertEqual(renderer.api.context, section)


class FindPeopleDirectoryTests(unittest.TestCase):

    def _callFUT(self, context):
        from karl.views.peopledirectory import find_peopledirectory
        return find_peopledirectory(context)

    def test_it(self):
        pd = testing.DummyModel()
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        directlyProvides(pd, IPeopleDirectory)
        context = testing.DummyModel()
        pd['obj'] = context
        self.assertEqual(self._callFUT(context), pd)


class GetTabsTests(unittest.TestCase):

    def _callFUT(self, peopledir, request, current_sectionid):
        from karl.views.peopledirectory import get_tabs
        return get_tabs(peopledir, request, current_sectionid)

    def test_it(self):
        pd = testing.DummyModel(order=[])
        for sectionid in ('s1', 's2'):
            section = testing.DummyModel(tab_title=sectionid.title())
            pd[sectionid] = section
            pd.order.append(sectionid)
        request = testing.DummyRequest()
        tabs = self._callFUT(pd, request, 's2')
        self.assertEqual(tabs, [
            {'href': 'http://example.com/s1/',
                'selected': False, 'title': 'S1'},
            {'href': 'http://example.com/s2/',
                'selected': True,'title': 'S2'},
            ])


class RenderReportGroupTests(unittest.TestCase):

    def _callFUT(self, group, request, css_class=''):
        from karl.views.peopledirectory import render_report_group
        return render_report_group(group, request, css_class)

    def test_structure(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup

        group = testing.DummyModel(title='Group 1', reports=[])

        report = testing.DummyModel(
            link_title='Report 1.1', css_class='priority')
        directlyProvides(report, IPeopleReport)
        group.reports.append(report)

        group2 = testing.DummyModel(title='Group 1.2', reports=[])
        directlyProvides(group2, IPeopleReportGroup)
        group.reports.append(group2)

        report2 = testing.DummyModel(
            link_title='Report 1.2.1', css_class='general')
        directlyProvides(report2, IPeopleReport)
        group2.reports.append(report2)

        request = testing.DummyRequest()
        html = self._callFUT(group, request, 'toplevel')

        self.assert_('<h3>Group 1</h3>' in html)
        self.assert_('>Report 1.1</a>' in html)
        self.assert_('<h3>Group 1.2</h3>' in html)
        self.assert_('>Report 1.2.1</a>' in html)

        self.assert_('class="priority"' in html)
        self.assert_('class="general"' in html)

    def test_empty(self):
        group = testing.DummyModel(title='', reports=[])
        request = testing.DummyRequest()
        html = self._callFUT(group, request)
        self.assertEqual(html, '<ul>\n</ul>')


class SectionViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import section_view
        return section_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

    def test_index_page(self):
        report = DummyReport()
        section = report.__parent__
        section.columns.append(testing.DummyModel(title='', reports=[]))
        pd = section.__parent__

        renderer = testing.registerDummyRenderer(
            'templates/people_section.pt')
        request = testing.DummyRequest()
        self._callFUT(section, request)

        self.assertEqual(renderer.peopledir, pd)
        self.assertEqual(renderer.peopledir_tabs, [{
            'href': 'http://example.com/s1/',
            'selected': True,
            'title': 'A',
            }])
        self.assertEqual(renderer.column_html, ['<ul class="column">\n</ul>'])
        self.assertEqual(renderer.api.context, section)

    def test_single_report(self):
        # when a section contains only a single report, show that report
        self._register()

        report = DummyReport()
        section = report.__parent__
        pd = section.__parent__

        renderer = testing.registerDummyRenderer(
            'templates/people_report.pt')
        request = testing.DummyRequest()
        self._callFUT(section, request)

        self.assertEqual(renderer.peopledir, pd)
        self.assertEqual(renderer.api.context, report)


class ReportViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import report_view
        return report_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

    def test_unqualified_report(self):
        self._register()

        report = DummyReport()
        section = report.__parent__
        pd = section.__parent__

        renderer = testing.registerDummyRenderer(
            'templates/people_report.pt')
        request = testing.DummyRequest()
        self._callFUT(report, request)

        self.assertEqual(renderer.peopledir, pd)
        self.assertEqual(renderer.api.context, report)
        self.assert_('grid_data' in renderer.head_data)
        self.assertEqual(renderer.print_url,
            'http://example.com/s1/r1/print.html')
        self.assertEqual(renderer.csv_url,
            'http://example.com/s1/r1/csv')
        self.assertEqual(renderer.pictures_url,
            'http://example.com/s1/r1/picture_view.html')
        self.assertEqual(renderer.qualifiers, [])

    def test_qualified_report(self):
        self._register()

        report = DummyReport()
        section = report.__parent__
        pd = section.__parent__

        renderer = testing.registerDummyRenderer(
            'templates/people_report.pt')
        request = testing.DummyRequest({'body': 'spock'})
        self._callFUT(report, request)

        self.assertEqual(renderer.peopledir, pd)
        self.assertEqual(renderer.api.context, report)
        self.assert_('grid_data' in renderer.head_data)
        self.assertEqual(renderer.print_url,
            'http://example.com/s1/r1/print.html?body=spock')
        self.assertEqual(renderer.csv_url,
            'http://example.com/s1/r1/csv?body=spock')
        self.assertEqual(renderer.pictures_url,
            'http://example.com/s1/r1/picture_view.html?body=spock')
        self.assertEqual(renderer.qualifiers, ['Search for "spock"'])


class JqueryGridViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import jquery_grid_view
        return jquery_grid_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()

    def test_it(self):
        self._register()
        report = testing.DummyModel(
            title='Report A',
            columns=['name'],
            query=None,
            filters={}
            )
        request = testing.DummyRequest({'start': 0, 'limit': 10})
        res = self._callFUT(report, request)
        self.assertEqual(res.content_type, 'application/x-json')
        payload = eval(res.body)
        self.assertEqual(payload['records'], [])
        self.assertEqual(payload['batchSize'], 10)
        self.assert_(payload.get('columns'))
        self.assertEqual(payload['columns'][0]['id'], 'name')


class GetColumnJsdataTests(unittest.TestCase):

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


class ProfilePhotoRowsTests(unittest.TestCase):

    def _callFUT(self, entries, request, api):
        from karl.views.peopledirectory import profile_photo_rows
        return profile_photo_rows(entries, request, api)

    def test_it(self):
        entries = []
        for i in range(4):
            entries.append(DummyProfile())
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
            'photo_url': 'http://example.com/photo/',
            })
        row = iterator.next()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0]['profile'], entries[3])

        # no more rows
        for row in iterator:
            self.fail()

class PictureViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import picture_view
        return picture_view(context, request)

    def _register(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

    def test_unqualified_report(self):
        self._register()

        report = DummyReport()
        section = report.__parent__
        pd = section.__parent__
        renderer = testing.registerDummyRenderer(
            'templates/people_pictures.pt')
        request = testing.DummyRequest()
        self._callFUT(report, request)

        self.assertEqual(renderer.peopledir, pd)
        self.assertEqual(renderer.api.context, report)
        self.assertEqual(len(list(renderer.rows)), 0)
        self.assertEqual(renderer.print_url,
            'http://example.com/s1/r1/print.html')
        self.assertEqual(renderer.csv_url,
            'http://example.com/s1/r1/csv')
        self.assertEqual(renderer.tabular_url,
            'http://example.com/s1/r1/')
        self.assertEqual(renderer.qualifiers, [])

    def test_qualified_report(self):
        self._register()

        report = DummyReport()
        renderer = testing.registerDummyRenderer(
            'templates/people_pictures.pt')
        request = testing.DummyRequest({'body': "spock's brain"})
        self._callFUT(report, request)

        self.assertEqual(len(list(renderer.rows)), 0)
        self.assertEqual(renderer.print_url,
            'http://example.com/s1/r1/print.html?body=spock%27s+brain')
        self.assertEqual(renderer.csv_url,
            'http://example.com/s1/r1/csv?body=spock%27s+brain')
        self.assertEqual(renderer.tabular_url,
            'http://example.com/s1/r1/?body=spock%27s+brain')
        self.assertEqual(renderer.qualifiers, ['Search for "spock\'s brain"'])

    def test_bad_search_text(self):
        from zope.index.text.parsetree import ParseError
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from zope.interface import Interface

        def search(*args, **kw):
            raise ParseError
        testing.registerAdapter(search, (Interface, Interface),
            ICatalogSearch)
        testing.registerAdapter(search, (Interface,), ICatalogSearch)
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)

        report = DummyReport()
        renderer = testing.registerDummyRenderer(
            'templates/people_pictures.pt')
        request = testing.DummyRequest()
        self._callFUT(report, request)
        self.assertEqual(len(list(renderer.rows)), 0)


class GetSearchQualifiersTests(unittest.TestCase):

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


class GetReportQueryTests(unittest.TestCase):

    def _callFUT(self, report, request):
        from karl.views.peopledirectory import get_report_query
        return get_report_query(report, request)

    def test_it(self):
        report = testing.DummyModel(
            query={'groups': ['group.KarlStaff']},
            filters={'office': ['nyc']},
            )
        request = testing.DummyRequest({
            'lastnamestartswith': 'L',
            'body': 'a b*',
            })
        kw = self._callFUT(report, request)
        self.assertEqual(kw, {
            'allowed': {'operator': 'or', 'query': []},
            'groups': ['group.KarlStaff'],
            'category_office': {'operator': 'or', 'query': ['nyc']},
            'lastnamestartswith': 'L',
            'texts': 'a b**',
            })


class GetGridDataTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request, **kw):
        from karl.views.peopledirectory import get_grid_data
        return get_grid_data(context, request, **kw)

    def test_empty(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        report = DummyReport()
        request = testing.DummyRequest()
        grid_data = self._callFUT(report, request, limit=10, width=100)
        self.assertEqual(grid_data, {
            'fetch_url': 'http://example.com/s1/r1/jquery_grid',
            'sortColumn': 'name',
            'records': [],
            'sortDirection': 'asc',
            'width': 100,
            'batchSize': 10,
            'totalRecords': 0,
            'columns': [{'width': 100, 'id': 'name', 'label': 'Name'}],
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
        testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        report = DummyReport()
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
        testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        report = DummyReport()
        request = testing.DummyRequest({
            'lastnamestartswith': 'A',
            'body': 'stuff',
            })
        grid_data = self._callFUT(report, request, start=21, limit=10)
        self.assertEqual(grid_data['fetch_url'],
            'http://example.com/s1/r1/jquery_grid?'
            'body=stuff&lastnamestartswith=A')

    def test_bad_text_search(self):
        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        from zope.index.text.parsetree import ParseError
        def searcher(context, request=None):
            def search(**kw):
                raise ParseError()
            return search
        testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        report = DummyReport()
        request = testing.DummyRequest()
        grid_data = self._callFUT(report, request)
        self.assertEqual(len(grid_data['records']), 0)
        self.assertEqual(grid_data['totalRecords'], 0)


class TextDumpTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, report, request):
        from karl.views.peopledirectory import text_dump
        return text_dump(report, request)

    def test_empty(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        report = DummyReport()
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
        testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        report = DummyReport()
        request = testing.DummyRequest()
        dumper = self._callFUT(report, request)
        rows = list(dumper)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], ['Name'])
        self.assertEqual(rows[1], ['Profile 0'])
        self.assertEqual(rows[2], ['Profile 1'])


class CSVViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.peopledirectory import csv_view
        return csv_view(context, request)

    def test_empty(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        report = DummyReport()
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
        testing.registerAdapter(searcher, (Interface, Interface),
            ICatalogSearch)
        testing.registerAdapter(searcher, (Interface,), ICatalogSearch)

        report = DummyReport()
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


class PrintViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, response):
        from karl.views.peopledirectory import print_view
        return print_view(context, response)

    def test_it(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        report = DummyReport()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/people_print.pt')
        self._callFUT(report, request)
        self.assertEqual(renderer.header, ['Name'])
        self.assertEqual(list(renderer.rows), [])


class AddUserViewTests(unittest.TestCase):

    def _callFUT(self, context, response):
        from karl.views.peopledirectory import add_user_view
        return add_user_view(context, response)

    def test_it(self):
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
            'http://example.com/profiles/add.html')


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


class NameColumnTests(unittest.TestCase):

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


class DummyProfile(testing.DummyModel):
    def __init__(self):
        testing.DummyModel.__init__(self)
        self['photo'] = testing.DummyModel()

    def get_photo(self):
        return self.get('photo')


class DummyReport(testing.DummyModel):
    def __init__(self):
        testing.DummyModel.__init__(self,
            title='Report A',
            link_title='A',
            columns=['name'],
            query=None,
            filters={}
            )

        pd = testing.DummyModel(order=[])
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        directlyProvides(pd, IPeopleDirectory)

        section = testing.DummyModel(
            columns=[], tab_title='A', title='Section A')
        pd['s1'] = section
        pd.order.append('s1')
        section['r1'] = self
