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
from pyramid import testing


class Test_peopledir_item_info(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.utilities.peopleconf import peopledir_item_info
        return peopledir_item_info(context, request)

    def test_w_section_empty(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL
        from pyramid.security import Everyone
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleSection
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    title='TITLE',
                    tab_title='TAB_TITLE',
                    __acl__=[(Allow, Everyone, ['view']), DENY_ALL]
                  )
        directlyProvides(context, IPeopleSection)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'section',
             'title': 'TITLE',
             'tab_title': 'TAB_TITLE',
             'acl': {'aces': [('allow', 'system.Everyone', ['view'])],
                     'inherit': False,
                    },
             'items': [],
            })

    def test_w_section_non_empty(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL
        from pyramid.security import Everyone
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        from karl.models.interfaces import IPeopleSection
        TARGET_URL_1 = 'http://example.com/target1'
        TARGET_URL_2 = 'http://example.com/target2'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    title='TITLE',
                    tab_title='TAB_TITLE',
                    __acl__=[(Allow, Everyone, ['view']), DENY_ALL]
                  )
        directlyProvides(context, IPeopleSection)
        sub2 = context['sub2'] = testing.DummyModel(
                    target_url=TARGET_URL_2)
        directlyProvides(sub2, IPeopleRedirector)
        sub1 = context['sub1'] = testing.DummyModel(
                    target_url=TARGET_URL_1)
        directlyProvides(sub1, IPeopleRedirector)
        request = testing.DummyRequest()
        context.order = ('sub1', 'sub2')
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'section',
             'title': 'TITLE',
             'tab_title': 'TAB_TITLE',
             'acl': {'aces': [('allow', 'system.Everyone', ['view'])],
                     'inherit': False,
                    },
             'items': [
                 {'name': 'sub1',
                  'url': 'http://example.com/testing/sub1/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_1,
                 },
                 {'name': 'sub2',
                  'url': 'http://example.com/testing/sub2/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_2,
                 },
             ],
            })

    def test_w_column_empty(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleSectionColumn
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel()
        directlyProvides(context, IPeopleSectionColumn)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'column',
             'items': [],
            })

    def test_w_column_non_empty(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        from karl.models.interfaces import IPeopleSectionColumn
        TARGET_URL_1 = 'http://example.com/target1'
        TARGET_URL_2 = 'http://example.com/target2'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel()
        directlyProvides(context, IPeopleSectionColumn)
        sub2 = context['sub2'] = testing.DummyModel(
                    target_url=TARGET_URL_2)
        directlyProvides(sub2, IPeopleRedirector)
        sub1 = context['sub1'] = testing.DummyModel(
                    target_url=TARGET_URL_1)
        directlyProvides(sub1, IPeopleRedirector)
        request = testing.DummyRequest()
        context.order = ('sub1', 'sub2')
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'column',
             'items': [
                 {'name': 'sub1',
                  'url': 'http://example.com/testing/sub1/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_1,
                 },
                 {'name': 'sub2',
                  'url': 'http://example.com/testing/sub2/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_2,
                 },
             ],
            })

    def test_w_group_empty(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportGroup
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            title='TITLE')
        directlyProvides(context, IPeopleReportGroup)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'title': 'TITLE',
             'type': 'report-group',
             'items': [],
            })

    def test_w_group_non_empty(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        from karl.models.interfaces import IPeopleReportGroup
        TARGET_URL_1 = 'http://example.com/target1'
        TARGET_URL_2 = 'http://example.com/target2'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            title='TITLE')
        directlyProvides(context, IPeopleReportGroup)
        sub2 = context['sub2'] = testing.DummyModel(
                    target_url=TARGET_URL_2)
        directlyProvides(sub2, IPeopleRedirector)
        sub1 = context['sub1'] = testing.DummyModel(
                    target_url=TARGET_URL_1)
        directlyProvides(sub1, IPeopleRedirector)
        request = testing.DummyRequest()
        context.order = ('sub1', 'sub2')
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'title': 'TITLE',
             'type': 'report-group',
             'items': [
                 {'name': 'sub1',
                  'url': 'http://example.com/testing/sub1/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_1,
                 },
                 {'name': 'sub2',
                  'url': 'http://example.com/testing/sub2/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_2,
                 },
             ],
            })

    def test_w_report_empty(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    title='TITLE',
                    link_title='LINK_TITLE',
                    css_class='',
                    columns=(),
                  )
        directlyProvides(context, IPeopleReport)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'report',
             'title': 'TITLE',
             'link_title': 'LINK_TITLE',
             'css_class': '',
             'columns': [],
             'items': [],
            })

    def test_w_report_non_empty(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        from karl.models.interfaces import IPeopleReport
        TARGET_URL_1 = 'http://example.com/target1'
        TARGET_URL_2 = 'http://example.com/target2'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    title='TITLE',
                    link_title='LINK_TITLE',
                    css_class='',
                    columns=('a', 'b'),
                  )
        directlyProvides(context, IPeopleReport)
        sub2 = context['sub2'] = testing.DummyModel(
                    target_url=TARGET_URL_2)
        directlyProvides(sub2, IPeopleRedirector)
        sub1 = context['sub1'] = testing.DummyModel(
                    target_url=TARGET_URL_1)
        directlyProvides(sub1, IPeopleRedirector)
        request = testing.DummyRequest()
        context.order = ('sub1', 'sub2')
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'report',
             'title': 'TITLE',
             'link_title': 'LINK_TITLE',
             'css_class': '',
             'columns': ['a', 'b'],
             'items': [
                 {'name': 'sub1',
                  'url': 'http://example.com/testing/sub1/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_1,
                 },
                 {'name': 'sub2',
                  'url': 'http://example.com/testing/sub2/',
                  'type': 'redirector',
                  'target_url': TARGET_URL_2,
                 },
             ],
            })

    def test_w_category_filter(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportCategoryFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    values=('a', 'b'))
        directlyProvides(context, IPeopleReportCategoryFilter)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'filter-category',
             'values': ['a', 'b'],
            })

    def test_w_group_filter(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportGroupFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    values=('a', 'b'))
        directlyProvides(context, IPeopleReportGroupFilter)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'filter-group',
             'values': ['a', 'b'],
            })

    def test_w_isstaff_filter(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    include_staff=True)
        directlyProvides(context, IPeopleReportIsStaffFilter)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'filter-isstaff',
             'values': ['True'],
            })

    def test_w_mailinglist(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportMailingList
        SHORT_ADDRESS = 'short-address'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    short_address=SHORT_ADDRESS)
        directlyProvides(context, IPeopleReportMailingList)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'mailinglist',
             'short_address': SHORT_ADDRESS,
            })

    def test_w_redirector(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        TARGET_URL = 'http://example.com/target'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    target_url=TARGET_URL)
        directlyProvides(context, IPeopleRedirector)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'name': 'testing',
             'url': 'http://example.com/testing/',
             'type': 'redirector',
             'target_url': TARGET_URL,
            })


class Test_update_peopledir_item(unittest.TestCase):

    def _callFUT(self, context, info):
        from karl.utilities.peopleconf import update_peopledir_item
        return update_peopledir_item(context, info)

    def test_w_section_deleting_wo_deny_all(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL
        from pyramid.security import Everyone
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleSection
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    title='BEFORE_TITLE',
                    tab_title='BEFORE_TAB_TITLE',
                    __acl__=[DENY_ALL],
                  )
        directlyProvides(context, IPeopleSection)
        doomed = context['doomed'] = testing.DummyModel()
        directlyProvides(doomed, IPeopleReport)
        context.order = ('doomed',)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'section',
                       'title': 'AFTER_TITLE',
                       'tab_title': 'AFTER_TAB_TITLE',
                       'acl': {'aces': [('allow', 'system.Everyone', ['view'])],
                               'inherit': True,
                              },
                       'items': [],
                      })
        self.assertEqual(context.title, 'AFTER_TITLE')
        self.assertEqual(context.tab_title, 'AFTER_TAB_TITLE')
        self.assertEqual(context.__acl__, [(Allow, Everyone, ['view'])])
        self.assertEqual(list(context.order), [])

    def test_w_section_adding_w_deny_all(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL
        from pyramid.security import Everyone
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        from karl.models.interfaces import IPeopleSection
        from karl.models.interfaces import IPeopleSectionColumn
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    title='BEFORE_TITLE',
                    tab_title='BEFORE_TAB_TITLE',
                    __acl__=[],
                  )
        directlyProvides(context, IPeopleSection)
        context.order = ()
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'section',
                       'title': 'AFTER_TITLE',
                       'tab_title': 'AFTER_TAB_TITLE',
                       'acl': {'aces': [('allow', 'system.Everyone', ['view'])],
                               'inherit': False,
                              },
                       'items': [
                            {'name': 'eee',
                             'type': 'column',
                             'items': [],
                            },
                            {'name': 'bbb',
                             'type': 'report-group',
                             'title': 'BBB_TITLE',
                             'link_title': 'BBB_LINK_TITLE',
                             'css_class': 'BBB_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ddd',
                                 'type': 'report',
                                 'title': 'DDD_TITLE',
                                 'link_title': 'DDD_LINK_TITLE',
                                 'css_class': 'DDD_CSS_CLASS',
                                 'columns': ['e', 'f'],
                                 'items': [],
                                },
                             ],
                            },
                            {'name': 'aaa',
                             'type': 'report',
                             'title': 'AAA_TITLE',
                             'link_title': 'AAA_LINK_TITLE',
                             'css_class': 'AAA_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ccc',
                                 'type': 'filter-isstaff',
                                 'values': ['True'],
                                },
                             ],
                            },
                       ],
                      })
        self.assertEqual(context.title, 'AFTER_TITLE')
        self.assertEqual(context.tab_title, 'AFTER_TAB_TITLE')
        self.assertEqual(context.__acl__,
                         [(Allow, Everyone, ['view']), DENY_ALL])
        self.assertEqual(list(context.order), ['eee', 'bbb', 'aaa'])
        self.assertTrue(IPeopleSectionColumn.providedBy(context['eee']))
        self.assertTrue(IPeopleReportGroup.providedBy(context['bbb']))
        self.assertEqual(context['bbb'].title, 'BBB_TITLE')
        self.assertTrue(IPeopleReport.providedBy(context['bbb']['ddd']))
        self.assertEqual(context['bbb']['ddd'].title, 'DDD_TITLE')
        self.assertTrue(IPeopleReport.providedBy(context['aaa']))
        self.assertEqual(context['aaa'].title, 'AAA_TITLE')
        self.assertTrue(IPeopleReportIsStaffFilter.providedBy(
                                context['aaa']['ccc']))
        self.assertEqual(context['aaa']['ccc'].include_staff, True)

    def test_w_column_deleting(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleSectionColumn
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            )
        directlyProvides(context, IPeopleSectionColumn)
        doomed = context['doomed'] = testing.DummyModel()
        directlyProvides(doomed, IPeopleReport)
        context.order = ('doomed',)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'column',
                       'items': [],
                      })
        self.assertEqual(list(context.order), [])

    def test_w_column_adding(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        from karl.models.interfaces import IPeopleSectionColumn
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            )
        directlyProvides(context, IPeopleSectionColumn)
        doomed = context['doomed'] = testing.DummyModel()
        directlyProvides(doomed, IPeopleReport)
        context.order = ('doomed',)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'column',
                       'items': [
                            {'name': 'bbb',
                             'type': 'report-group',
                             'title': 'BBB_TITLE',
                             'link_title': 'BBB_LINK_TITLE',
                             'css_class': 'BBB_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ddd',
                                 'type': 'report',
                                 'title': 'DDD_TITLE',
                                 'link_title': 'DDD_LINK_TITLE',
                                 'css_class': 'DDD_CSS_CLASS',
                                 'columns': ['e', 'f'],
                                 'items': [],
                                },
                             ],
                            },
                            {'name': 'aaa',
                             'type': 'report',
                             'title': 'AAA_TITLE',
                             'link_title': 'AAA_LINK_TITLE',
                             'css_class': 'AAA_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ccc',
                                 'type': 'filter-isstaff',
                                 'values': ['True'],
                                },
                             ],
                            },
                       ],
                      })
        self.assertEqual(list(context.order), ['bbb', 'aaa'])
        self.assertTrue(IPeopleReportGroup.providedBy(context['bbb']))
        self.assertEqual(context['bbb'].title, 'BBB_TITLE')
        self.assertTrue(IPeopleReport.providedBy(context['bbb']['ddd']))
        self.assertEqual(context['bbb']['ddd'].title, 'DDD_TITLE')
        self.assertTrue(IPeopleReport.providedBy(context['aaa']))
        self.assertEqual(context['aaa'].title, 'AAA_TITLE')
        self.assertTrue(IPeopleReportIsStaffFilter.providedBy(
                                context['aaa']['ccc']))
        self.assertEqual(context['aaa']['ccc'].include_staff, True)

    def test_w_reportgroup_deleting(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            title='BEFORE_TITLE',
            )
        directlyProvides(context, IPeopleReportGroup)
        doomed = context['doomed'] = testing.DummyModel()
        directlyProvides(doomed, IPeopleReport)
        context.order = ('doomed',)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'report-group',
                       'title': 'AFTER_TITLE',
                       'items': [],
                      })
        self.assertEqual(context.title, 'AFTER_TITLE')
        self.assertEqual(list(context.order), [])

    def test_w_reportgroup_adding(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            title='BEFORE_TITLE',
            )
        directlyProvides(context, IPeopleReportGroup)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'report-group',
                       'title': 'AFTER_TITLE',
                       'items': [
                            {'name': 'bbb',
                             'type': 'report',
                             'title': 'BBB_TITLE',
                             'link_title': 'BBB_LINK_TITLE',
                             'css_class': 'BBB_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [],
                            },
                            {'name': 'aaa',
                             'type': 'report',
                             'title': 'AAA_TITLE',
                             'link_title': 'AAA_LINK_TITLE',
                             'css_class': 'AAA_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ccc',
                                 'type': 'filter-isstaff',
                                 'values': ['True'],
                                },
                             ],
                            },
                       ],
                      })
        self.assertEqual(context.title, 'AFTER_TITLE')
        self.assertEqual(list(context.order), ['bbb', 'aaa'])
        self.assertTrue(IPeopleReport.providedBy(context['bbb']))
        self.assertEqual(context['bbb'].title, 'BBB_TITLE')
        self.assertTrue(IPeopleReport.providedBy(context['aaa']))
        self.assertEqual(context['aaa'].title, 'AAA_TITLE')
        self.assertTrue(IPeopleReportIsStaffFilter.providedBy(
                                context['aaa']['ccc']))
        self.assertEqual(context['aaa']['ccc'].include_staff, True)

    def test_w_report_deleting(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleRedirector
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            title='BEFORE_TITLE',
            link_title='BEFORE_LINK_TITLE',
            css_class='BEFORE_CSS_CLASS',
            columns=('a', 'b'),
            )
        directlyProvides(context, IPeopleReport)
        doomed = context['doomed'] = testing.DummyModel()
        directlyProvides(doomed, IPeopleRedirector)
        context.order = ('doomed',)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'report',
                       'title': 'AFTER_TITLE',
                       'link_title': 'AFTER_LINK_TITLE',
                       'css_class': 'AFTER_CSS_CLASS',
                       'columns': ['c', 'd'],
                       'items': [],
                      })
        self.assertEqual(context.title, 'AFTER_TITLE')
        self.assertEqual(context.link_title, 'AFTER_LINK_TITLE')
        self.assertEqual(context.css_class, 'AFTER_CSS_CLASS')
        self.assertEqual(context.columns, ('c', 'd'))
        self.assertEqual(list(context.order), [])

    def test_w_report_adding(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportCategoryFilter
        from karl.models.interfaces import IPeopleReportGroupFilter
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        from karl.models.interfaces import IPeopleReportMailingList
        from karl.models.interfaces import IPeopleRedirector
        TARGET_URL = 'http://example.com/target/'
        SHORT_ADDRESS = 'short-address'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
            title='BEFORE_TITLE',
            link_title='BEFORE_LINK_TITLE',
            css_class='BEFORE_CSS_CLASS',
            columns=('a', 'b'),
            )
        directlyProvides(context, IPeopleReport)
        context.order = ()
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'report',
                       'title': 'AFTER_TITLE',
                       'link_title': 'AFTER_LINK_TITLE',
                       'css_class': 'AFTER_CSS_CLASS',
                       'columns': ['c', 'd'],
                       'items': [
                            {'name': 'bbb',
                             'type': 'filter-category',
                             'values': ['a', 'b'],
                            },
                            {'name': 'aaa',
                             'type': 'filter-group',
                             'values': ['c', 'd'],
                            },
                            {'name': 'ccc',
                             'type': 'filter-isstaff',
                             'values': ['True'],
                            },
                            {'name': 'eee',
                             'type': 'mailinglist',
                             'short_address': SHORT_ADDRESS,
                            },
                            {'name': 'ddd',
                             'type': 'redirector',
                             'target_url': TARGET_URL,
                            },
                       ],
                      })
        self.assertEqual(context.title, 'AFTER_TITLE')
        self.assertEqual(context.link_title, 'AFTER_LINK_TITLE')
        self.assertEqual(context.css_class, 'AFTER_CSS_CLASS')
        self.assertEqual(context.columns, ('c', 'd'))
        self.assertEqual(list(context.order),
                         ['bbb', 'aaa', 'ccc', 'eee', 'ddd'])
        self.assertTrue(IPeopleReportCategoryFilter.providedBy(context['bbb']))
        self.assertEqual(context['bbb'].values, ('a', 'b'))
        self.assertTrue(IPeopleReportGroupFilter.providedBy(context['aaa']))
        self.assertEqual(context['aaa'].values, ('c', 'd'))
        self.assertTrue(IPeopleReportIsStaffFilter.providedBy(context['ccc']))
        self.assertEqual(context['ccc'].include_staff, True)
        self.assertTrue(IPeopleReportMailingList.providedBy(context['eee']))
        self.assertEqual(context['eee'].short_address, SHORT_ADDRESS)
        self.assertTrue(IPeopleRedirector.providedBy(context['ddd']))
        self.assertEqual(context['ddd'].target_url, TARGET_URL)

    def test_w_category_filter(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportCategoryFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    values=('a', 'b'))
        directlyProvides(context, IPeopleReportCategoryFilter)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'filter-group',
                       'values': ['c', 'd'],
                      })
        self.assertEqual(context.values, ('c', 'd'))

    def test_w_group_filter(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportGroupFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    values=('a', 'b'))
        directlyProvides(context, IPeopleReportGroupFilter)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'filter-group',
                       'values': ['c', 'd'],
                      })
        self.assertEqual(context.values, ('c', 'd'))

    def test_w_isstaff_filter(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    include_staff=False)
        directlyProvides(context, IPeopleReportIsStaffFilter)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'filter-isstaff',
                       'values': ['True'],
                      })
        self.assertEqual(context.include_staff, True)

    def test_w_mailinglist(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportMailingList
        BEFORE_SHORT_ADDRESS = 'before-short-address'
        AFTER_SHORT_ADDRESS = 'after-short-address'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    short_address=BEFORE_SHORT_ADDRESS)
        directlyProvides(context, IPeopleReportMailingList)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'mailinglist',
                       'short_address': AFTER_SHORT_ADDRESS,
                      })
        self.assertEqual(context.short_address, AFTER_SHORT_ADDRESS)

    def test_w_redirector(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        BEFORE_TARGET_URL = 'http://example.com/before'
        AFTER_TARGET_URL = 'http://example.com/after'
        parent = testing.DummyModel()
        context = parent['testing'] = testing.DummyModel(
                    target_url=BEFORE_TARGET_URL)
        directlyProvides(context, IPeopleRedirector)
        self._callFUT(context, 
                      {'name': 'testing',
                       'url': 'http://example.com/testing/',
                       'type': 'redirector',
                       'target_url': AFTER_TARGET_URL,
                      })
        self.assertEqual(context.target_url, AFTER_TARGET_URL)


class Test_peopledir_info(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.utilities.peopleconf import peopledir_info
        return peopledir_info(context, request)

    def test_w_empty(self):
        context = testing.DummyModel(order=())
        context['categories'] = testing.DummyModel()
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data,
            {'sections': [],
             'categories': [],
            })

    def test_w_categories(self):
        context = testing.DummyModel(order=())
        categories = context['categories'] = testing.DummyModel()
        cat1 = categories['cat1'] = testing.DummyModel(title='Cat One')
        # Note unescapte amper!
        val1_1 = cat1['val1_1'] = testing.DummyModel(title='Val One One',
                                                     description='One & One')
        val1_2 = cat1['val1_2'] = testing.DummyModel(title='Val One Two',
                                                     description='One & Two')
        cat2 = categories['cat2'] = testing.DummyModel(title='Cat Two')
        val2_1 = cat2['val2_1'] = testing.DummyModel(title='Val Two One',
                                                     description='Two & One')
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data['sections'], [])
        self.assertEqual(data['categories'],
                         [{'name': 'cat1',
                           'url': 'http://example.com/categories/cat1/',
                           'title': 'Cat One',
                           'values': 
                                [{'name': 'val1_1',
                                  'url': 'http://example.com/categories/' +
                                            'cat1/val1_1/',
                                  'title': 'Val One One',
                                  'description': 'One & One',
                                  },
                                 {'name': 'val1_2',
                                  'url': 'http://example.com/categories/' +
                                            'cat1/val1_2/',
                                  'title': 'Val One Two',
                                  'description': 'One & Two',
                                  }
                                ],
                          },
                          {'name': 'cat2',
                           'url': 'http://example.com/categories/cat2/',
                           'title': 'Cat Two',
                           'values': 
                                [{'name': 'val2_1',
                                  'url': 'http://example.com/categories/' +
                                            'cat2/val2_1/',
                                  'title': 'Val Two One',
                                  'description': 'Two & One',
                                 }
                                ],
                          },
                         ])

    def test_w_section_w_acl_wo_items(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleSection
        context = testing.DummyModel(order=('test_section',))
        context['categories'] = testing.DummyModel()
        section = context['test_section'] = testing.DummyModel(
            title='TITLE', tab_title='TAB-TITLE', order=())
        section.__acl__ = [(Allow, 'phred', 'edit'), DENY_ALL]
        directlyProvides(section, IPeopleSection)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data['categories'], [])
        self.assertEqual(data['sections'],
                         [{'name': 'test_section',
                           'url': 'http://example.com/test_section/',
                           'type': 'section',
                           'title': 'TITLE',
                           'tab_title': 'TAB-TITLE',
                           'acl': {'aces': [('allow', 'phred', 'edit')],
                                   'inherit': False,
                                  },
                           'items': [],
                          },
                         ])

    def test_w_section_w_items(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        from karl.models.interfaces import IPeopleReportCategoryFilter
        from karl.models.interfaces import IPeopleReportGroupFilter
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        from karl.models.interfaces import IPeopleReportMailingList
        from karl.models.interfaces import IPeopleSection
        from karl.models.interfaces import IPeopleSectionColumn
        context = testing.DummyModel(order=('test_section',))
        context['categories'] = testing.DummyModel()
        section = context['test_section'] = testing.DummyModel(
            title='TITLE', tab_title='TAB-TITLE',
            order=('rd1', 'r1', 'rg1', 'col1'))
        directlyProvides(section, IPeopleSection)
        rd1 = section['rd1'] = testing.DummyModel(
                                        target_url='http://example.com/',
                                        )
        directlyProvides(rd1, IPeopleRedirector)
        r1 = section['r1'] = testing.DummyModel(
                                        title='R1',
                                        link_title='R1',
                                        css_class='report',
                                        columns=('a', 'b', 'c'),
                                        )
        directlyProvides(r1, IPeopleReport)
        entities1 = r1['entities'] = testing.DummyModel(values=('foo', 'bar'))
        directlyProvides(entities1, IPeopleReportCategoryFilter)
        mailinglist = r1['mailinglist'] = testing.DummyModel(
                                                    short_address='short')
        directlyProvides(mailinglist, IPeopleReportMailingList)
        rg1 = section['rg1'] = testing.DummyModel(title='RG1')
        directlyProvides(rg1, IPeopleReportGroup)
        r2 = rg1['r2'] = testing.DummyModel(
                                        title='R2',
                                        link_title='R2',
                                        css_class='report-extra',
                                        columns=('b', 'd', 'c'),
                                        )
        directlyProvides(r2, IPeopleReport)
        entities2 = r2['entities'] = testing.DummyModel(values=('baz', 'qux'))
        directlyProvides(entities2, IPeopleReportGroupFilter)
        # no mailing list
        col1 = section['col1'] = testing.DummyModel()
        directlyProvides(col1, IPeopleSectionColumn)
        r3 = col1['r3'] = testing.DummyModel(
                                        title='R3',
                                        link_title='R3',
                                        css_class='report',
                                        columns=('b', 'e'),
                                        )
        directlyProvides(r3, IPeopleReport)
        entities3 = r3['entities'] = testing.DummyModel(include_staff=True)
        directlyProvides(entities3, IPeopleReportIsStaffFilter)
        request = testing.DummyRequest()
        data = self._callFUT(context, request)
        self.assertEqual(data['categories'], [])
        self.assertEqual(data['sections'],
                         [{'name': 'test_section',
                           'url': 'http://example.com/test_section/',
                           'type': 'section',
                           'title': 'TITLE',
                           'tab_title': 'TAB-TITLE',
                           'acl': {'aces': [],
                                   'inherit': True,
                                  },
                           'items': [
                             {'name': 'rd1',
                              'url': 'http://example.com/test_section/rd1/',
                              'type': 'redirector',
                              'target_url': 'http://example.com/',
                             },
                             {'name': 'r1',
                              'url': 'http://example.com/test_section/r1/',
                              'type': 'report',
                              'title': 'R1',
                              'link_title': 'R1',
                              'css_class': 'report',
                              'columns': ['a', 'b', 'c'],
                              'items': [
                               {'name': 'entities',
                                'url':
                                 'http://example.com/test_section/r1/entities/',
                                'type': 'filter-category',
                                'values':  ['foo', 'bar'],
                               },
                               {'name': 'mailinglist',
                                'url':
                                 'http://example.com/test_section/r1/' +
                                        'mailinglist/',
                                'type': 'mailinglist',
                                'short_address':  'short',
                               },
                              ],
                             },
                             {'name': 'rg1',
                              'url': 'http://example.com/test_section/rg1/',
                              'type': 'report-group',
                              'title': 'RG1',
                              'items': [
                                {'name': 'r2',
                                 'url':
                                     'http://example.com/test_section/rg1/r2/',
                                 'type': 'report',
                                 'title': 'R2',
                                 'link_title': 'R2',
                                 'css_class': 'report-extra',
                                 'columns': ['b', 'd', 'c'],
                                 'items': [
                                  {'name': 'entities',
                                   'url':
                                     'http://example.com/test_section/rg1/' +
                                        'r2/entities/',
                                   'type': 'filter-group',
                                   'values':  ['baz', 'qux'],
                                  },
                                 ],
                                },
                               ],
                             },
                             {'name': 'col1',
                              'url': 'http://example.com/test_section/col1/',
                              'type': 'column',
                              'items': [
                                {'name': 'r3',
                                 'url': 'http://example.com/test_section/' +
                                                'col1/r3/',
                                 'type': 'report',
                                 'title': 'R3',
                                 'link_title': 'R3',
                                 'css_class': 'report',
                                 'columns': ['b', 'e'],
                                 'items': [
                                  {'name': 'entities',
                                   'url': 'http://example.com/test_section/' +
                                                'col1/r3/entities/',
                                   'type': 'filter-isstaff',
                                   'values':  ['True'],
                                  },
                                 ],
                                },
                               ],
                             },
                           ],
                          },
                         ])


class Test_update_peopledir(unittest.TestCase):

    def _callFUT(self, context, info):
        from karl.utilities.peopleconf import update_peopledir
        return update_peopledir(context, info)

    def test_updating_categories(self):
        from karl.models.interfaces import IPeopleCategory
        from karl.models.interfaces import IPeopleCategoryItem
        context = testing.DummyModel(order=())
        categories = context['categories'] = testing.DummyModel()
        doomed_cat = categories['doomed'] = testing.DummyModel()
        doomed_sec = context['doomed'] = testing.DummyModel()
        context.order = ('doomed',)
        info = {'sections': [],
                'categories':
                         [{'name': 'cat1',
                           'title': 'Cat One',
                           'values': 
                                [{'name': 'val1_1',
                                  'title': 'Val One One',
                                  'description': 'One & One',
                                  },
                                 {'name': 'val1_2',
                                  'title': 'Val One Two',
                                  'description': 'One & Two',
                                  }
                                ],
                          },
                          {'name': 'cat2',
                           'title': 'Cat Two',
                           'values': 
                                [{'name': 'val2_1',
                                  'title': 'Val Two One',
                                  'description': 'Two & One',
                                 }
                                ],
                          },
                         ],
               }
        self._callFUT(context, info)
        self.assertEqual(list(context.order), [])
        self.assertEqual(sorted(categories.keys()), ['cat1', 'cat2'])
        self.assertTrue(IPeopleCategory.providedBy(categories['cat1']))
        self.assertEqual(categories['cat1'].title, 'Cat One')
        self.assertTrue(IPeopleCategoryItem.providedBy(
                                categories['cat1']['val1_1']))
        self.assertEqual(categories['cat1']['val1_1'].title, 'Val One One')
        self.assertEqual(categories['cat1']['val1_1'].description, 'One & One')
        self.assertTrue(IPeopleCategoryItem.providedBy(
                                categories['cat1']['val1_2']))
        self.assertEqual(categories['cat1']['val1_2'].title, 'Val One Two')
        self.assertEqual(categories['cat1']['val1_2'].description, 'One & Two')
        self.assertTrue(IPeopleCategory.providedBy(categories['cat2']))
        self.assertEqual(categories['cat2'].title, 'Cat Two')
        self.assertTrue(IPeopleCategoryItem.providedBy(
                                categories['cat2']['val2_1']))
        self.assertEqual(categories['cat2']['val2_1'].title, 'Val Two One')
        self.assertEqual(categories['cat2']['val2_1'].description, 'Two & One')

    def test_updating_sections(self):
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        from karl.models.interfaces import IPeopleSection
        from karl.models.interfaces import IPeopleSectionColumn
        context = testing.DummyModel(order=())
        categories = context['categories'] = testing.DummyModel()
        doomed_cat = categories['doomed'] = testing.DummyModel()
        context.order = ()
        info = {'categories': [],
                'sections': [
                    {'name': 'bbb',
                     'type': 'section',
                     'title': 'BBB_TITLE',
                     'tab_title': 'BBB_TAB_TITLE',
                     'acl': {'aces': [('allow', 'system.Everyone', ['view'])],
                             'inherit': True,
                            },
                     'items': [],
                    },
                    {'name': 'aaa',
                     'type': 'section',
                     'title': 'AAA_TITLE',
                     'tab_title': 'AAA_TAB_TITLE',
                     'acl': {'aces': [('allow', 'system.Everyone', ['view'])],
                             'inherit': False,
                            },
                     'items': [
                            {'name': 'eee',
                             'type': 'column',
                             'items': [],
                            },
                            {'name': 'ddd',
                             'type': 'report-group',
                             'title': 'DDD_TITLE',
                             'link_title': 'DDD_LINK_TITLE',
                             'css_class': 'DDD_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ggg',
                                 'type': 'report',
                                 'title': 'GGG_TITLE',
                                 'link_title': 'GGG_LINK_TITLE',
                                 'css_class': 'GGG_CSS_CLASS',
                                 'columns': ['e', 'f'],
                                 'items': [],
                                },
                             ],
                            },
                            {'name': 'fff',
                             'type': 'report',
                             'title': 'FFF_TITLE',
                             'link_title': 'FFF_LINK_TITLE',
                             'css_class': 'FFF_CSS_CLASS',
                             'columns': ['c', 'd'],
                             'items': [
                                {'name': 'ccc',
                                 'type': 'filter-isstaff',
                                 'values': ['True'],
                                },
                             ],
                            },
                     ],
                    },
                ]
               }
        self._callFUT(context, info)
        self.assertEqual(sorted(categories.keys()), [])
        self.assertEqual(list(context.order), ['bbb', 'aaa'])
        self.assertTrue(IPeopleSection.providedBy(context['bbb']))
        self.assertEqual(context['bbb'].title, 'BBB_TITLE')
        self.assertTrue(IPeopleSection.providedBy(context['aaa']))
        self.assertEqual(context['aaa'].title, 'AAA_TITLE')
        self.assertTrue(IPeopleSectionColumn.providedBy(
                                            context['aaa']['eee']))
        self.assertTrue(IPeopleReportGroup.providedBy(
                                            context['aaa']['ddd']))
        self.assertEqual(context['aaa']['ddd'].title, 'DDD_TITLE')
        self.assertTrue(IPeopleReport.providedBy(
                                            context['aaa']['ddd']['ggg']))
        self.assertEqual(context['aaa']['ddd']['ggg'].title, 'GGG_TITLE')
        self.assertTrue(IPeopleReport.providedBy(context['aaa']['fff']))
        self.assertEqual(context['aaa']['fff'].title, 'FFF_TITLE')
        self.assertTrue(IPeopleReportIsStaffFilter.providedBy(
                                context['aaa']['fff']['ccc']))
        self.assertEqual(context['aaa']['fff']['ccc'].include_staff, True)


class Test_dump_peopledir(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from pyramid.testing import cleanUp
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
        from pyramid.security import DENY_ALL
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

    def test_section_acl_w_redirector(self):
        from pyramid.security import DENY_ALL
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleRedirector
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',)),
                                     DENY_ALL,
                                    ])
        redirect = section['redirect'] = testing.DummyModel(
                                    target_url='http://example.com/')
        directlyProvides(redirect, IPeopleRedirector)
        xml = self._callFUT(pd)
        a_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section[@name="testing"]/acl/*')
        self.assertEqual(len(a_nodes), 2)
        self.assertEqual(a_nodes[0].tag, 'allow')
        self.assertEqual(a_nodes[1].tag, 'no-inherit')

    def test_section_w_no_columns(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',))])
        report = section['report'] = testing.DummyModel(title='Report',
                                    link_title='Report (Link)',
                                    css_class='CSS',
                                    columns=('name', 'phone'),
                                    filters={'offices': ['nyc', 'london']})
        directlyProvides(report, IPeopleReport)
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
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        pd = self._makeContext(order=('testing',))
        report = testing.DummyModel(title='Report',
                                    link_title='Report (Link)',
                                    css_class='CSS',
                                    columns=('name', 'phone'),
                                    filters={'offices': ['nyc', 'london']})
        directlyProvides(report, IPeopleReport)
        column = testing.DummyModel(reports=(report,))
        pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            columns=(column,),
                            __acl__=[('Allow', 'system.Everyone', ('view',))])
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
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportCategoryFilter
        from karl.models.interfaces import IPeopleReportGroupFilter
        from karl.models.interfaces import IPeopleReportIsStaffFilter
        from karl.models.interfaces import IPeopleSectionColumn
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',))])
        column = section['c1'] = testing.DummyModel(order=('report',))
        directlyProvides(column, IPeopleSectionColumn)
        report = column['report'] = testing.DummyModel(title='Report',
                                        link_title='Report (Link)',
                                        css_class='CSS',
                                        columns=('name', 'phone'))
        directlyProvides(report, IPeopleReport)
        offices = report['offices'] = testing.DummyModel(
                                            values=['nyc', 'london'])
        directlyProvides(offices, IPeopleReportCategoryFilter)
        groups = report['groups'] = testing.DummyModel(
                                            values=['group1', 'group2'])
        directlyProvides(groups, IPeopleReportGroupFilter)
        is_staff = report['is_staff'] = testing.DummyModel(
                                            include_staff=False)
        directlyProvides(is_staff, IPeopleReportIsStaffFilter)
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
        self.assertEqual(len(f_nodes), 3)
        self.assertEqual(f_nodes[0].get('name'), 'groups')
        self.assertEqual(f_nodes[0].get('type'), 'groups')
        self.assertEqual(f_nodes[0].get('values'), 'group1 group2')
        self.assertEqual(f_nodes[1].get('name'), 'is_staff')
        self.assertEqual(f_nodes[1].get('type'), 'is_staff')
        self.assertEqual(f_nodes[1].get('include_staff'), 'False')
        self.assertEqual(f_nodes[2].get('name'), 'offices')
        self.assertEqual(f_nodes[2].get('type'), 'category')
        self.assertEqual(f_nodes[2].get('category'), 'offices')
        self.assertEqual(f_nodes[2].get('values'), 'nyc london')
        x_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/report/columns')
        self.assertEqual(len(x_nodes), 1)
        self.assertEqual(x_nodes[0].get('names'), 'name phone')

    def test_section_w_mailinglist(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportCategoryFilter
        from karl.models.interfaces import IPeopleReportMailingList
        from karl.models.interfaces import IPeopleSectionColumn
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',))])
        column = section['c1'] = testing.DummyModel(order=('report',))
        directlyProvides(column, IPeopleSectionColumn)
        report = column['report'] = testing.DummyModel(title='Report',
                                        link_title='Report (Link)',
                                        css_class='CSS',
                                        columns=('name', 'phone'))
        directlyProvides(report, IPeopleReport)
        offices = report['offices'] = testing.DummyModel(
                                            values=['nyc', 'london'])
        directlyProvides(offices, IPeopleReportCategoryFilter)
        mlist = report['mailinglist'] = testing.DummyModel(
                                            short_address='alias')
        directlyProvides(mlist, IPeopleReportMailingList)
        xml = self._callFUT(pd)
        m_nodes = self._xpath(xml, '/peopledirectory/sections'
                                    '/section/column/report/mailinglist')
        self.assertEqual(len(m_nodes), 1)
        self.assertEqual(m_nodes[0].get('short_address'), 'alias')

    def test_section_w_report_group(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReport
        from karl.models.interfaces import IPeopleReportGroup
        pd = self._makeContext(order=('testing',))
        section = pd['testing'] = testing.DummyModel(
                            title='Testing',
                            tab_title='Testing (TAB)',
                            __acl__=[('Allow', 'system.Everyone', ('view',))])
        group = section['rg1'] = testing.DummyModel(title='Group')
        directlyProvides(group, IPeopleReportGroup)
        report = group['report'] = testing.DummyModel(title='Report',
                                    link_title='Report (Link)',
                                    css_class='CSS',
                                    columns=('name', 'phone'),
                                    filters={'offices': ['nyc', 'london']})
        directlyProvides(report, IPeopleReport)
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
        name, report = self._callFUT(peopledir, elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(report.title, 'r1')
        self.assertEqual(report.link_title, 'r1')
        self.assertEqual(len(report), 0)
        self.assertEqual(report.columns, ('name',))

    def test_complete(self):
        from karl.models.peopledirectory import PeopleReportCategoryFilter
        from karl.models.peopledirectory import PeopleReportGroupFilter
        from karl.models.peopledirectory import PeopleReportIsStaffFilter
        from karl.models.peopledirectory import PeopleReportMailingList
        xml = """
        <report name="r1" title="Report One" link-title="One">
            <filter name="offices" type="category" category="offices"
                    values="nyc la"/>
            <filter name="departments" type="category" category="departments"
                    values="toys"/>
            <filter name="groups" type="groups" values="g1 g2"/>
            <filter name="is_staff" type="is_staff" include_staff="False"/>
            <columns names="name email"/>
            <mailinglist short_address="alias"/>
        </report>
        """
        elem = parse_xml(xml)
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
        peopledir['categories']['offices'] = {'nyc': 'NYC', 'la': 'LA'}
        peopledir['categories']['departments'] = {'toys': 'Toys'}
        name, report = self._callFUT(peopledir, elem)
        self.assertEqual(name, 'r1')
        self.assertEqual(report.title, 'Report One')
        self.assertEqual(report.link_title, 'One')
        self.assertEqual(len(report), 5)
        self.failUnless(isinstance(report['departments'],
                        PeopleReportCategoryFilter))
        self.assertEqual(report['departments'].values, ('toys',))
        self.failUnless(isinstance(report['offices'],
                        PeopleReportCategoryFilter))
        self.assertEqual(report['offices'].values, ('nyc', 'la'))
        self.failUnless(isinstance(report['groups'],
                        PeopleReportGroupFilter))
        self.assertEqual(report['groups'].values, ('g1', 'g2'))
        self.failUnless(isinstance(report['is_staff'],
                        PeopleReportIsStaffFilter))
        self.failIf(report['is_staff'].include_staff)
        self.failUnless(isinstance(report['mailinglist'],
                        PeopleReportMailingList))
        self.assertEqual(report['mailinglist'].short_address, 'alias')
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC'}
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_group_value(self):
        from karl.models.peopledirectory import PeopleReportGroupFilter
        xml = """
        <report name="r1">
            <filter name="groups" type="groups" values="g1"/>
            <columns ids="name"/>
        </report>
        """
        elem = parse_xml(xml)
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        name, report = self._callFUT(peopledir, elem)
        self.assertEqual(len(report), 1)
        self.failUnless(isinstance(report['groups'], PeopleReportGroupFilter))
        self.assertEqual(report['groups'].values, ('g1',))
        self.assertEqual(report.columns, ('name',))

    def test_duplicate_short_address(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <columns names="name"/>
            <mailinglist short_address="duplicate"/>
        </report>
        """
        ALIASES = {'duplicate': '/somewhere/else'}
        elem = parse_xml(xml)
        site = testing.DummyModel(list_aliases=ALIASES)
        peopledir = site['people'] = DummyPeopleDirectory()
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_no_columns(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report name="r1">
            <filter category="office" values="nyc"/>
            <columns names=""/>
        </report>
        """
        elem = parse_xml(xml)
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
        peopledir['categories']['office'] = {'nyc': 'NYC'}
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)


class Test_parse_report_group(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from pyramid.testing import cleanUp
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
        from karl.utilities.peopleconf import ParseError
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
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_non_unique_report_group(self):
        from karl.utilities.peopleconf import ParseError
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
        self.assertRaises(ParseError, self._callFUT, peopledir, elem)

    def test_unrecognized(self):
        from karl.utilities.peopleconf import ParseError
        xml = """
        <report-group name="test">
            <xml/>
        </report-group>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
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

    def test_redirector(self):
        xml = """
        <section>
            <redirector name="old_name" target_url="path/to/new_name"/>
        </section>
        """
        elem = parse_xml(xml)
        peopledir = DummyPeopleDirectory()
        items = self._callFUT(peopledir, elem)
        self.assertEqual(len(items), 1)
        name, redirector = items[0]
        self.assertEqual(name, 'old_name')
        self.assertEqual(redirector.target_url, 'path/to/new_name')

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


class Test_clear_mailinglist_aliases(unittest.TestCase):

    def _callFUT(self, peopledir):
        from karl.utilities.peopleconf import clear_mailinglist_aliases
        return clear_mailinglist_aliases(peopledir)

    def test_clears_list_aliases_under_people(self):
        ALIASES = {'not_people': '/somewhere/else',
                   'under_people': '/people/path/to/resport',
                  }
        site = testing.DummyModel(list_aliases=ALIASES)
        peopledir = site['people'] = DummyPeopleDirectory()
        self._callFUT(peopledir)
        self.assertEqual(len(site.list_aliases), 1)
        self.failIf('under_people' in site.list_aliases)
        self.failUnless('not_people' in site.list_aliases)


class Test_find_mailinglist_aliases(unittest.TestCase):

    def _callFUT(self, peopledir):
        from karl.utilities.peopleconf import find_mailinglist_aliases
        return find_mailinglist_aliases(peopledir)

    def test_wo_conflicts(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportMailingList
        ALIASES = {'not_people': '/somewhere/else',
                  }
        site = testing.DummyModel(list_aliases=ALIASES)
        peopledir = site['people'] = testing.DummyModel()
        section = peopledir['section'] = testing.DummyModel()
        report1 = section['report1'] = testing.DummyModel()
        ml1 = report1['mailinglist'] = testing.DummyModel(short_address='one')
        directlyProvides(ml1, IPeopleReportMailingList)
        report2 = section['report2'] = testing.DummyModel()
        report3 = section['report3'] = testing.DummyModel()
        ml3 = report3['mailinglist'] = testing.DummyModel(short_address='three')
        directlyProvides(ml3, IPeopleReportMailingList)
        self._callFUT(peopledir)
        self.assertEqual(len(site.list_aliases), 3)
        self.assertEqual(site.list_aliases['not_people'], '/somewhere/else')
        self.assertEqual(site.list_aliases['one'], '/people/section/report1')
        self.assertEqual(site.list_aliases['three'], '/people/section/report3')

    def test_w_conflicts_inside_people(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportMailingList
        ALIASES = {'not_people': '/somewhere/else',
                  }
        site = testing.DummyModel(list_aliases=ALIASES)
        peopledir = site['people'] = testing.DummyModel()
        section = peopledir['section'] = testing.DummyModel()
        report1 = section['report1'] = testing.DummyModel()
        ml1 = report1['mailinglist'] = testing.DummyModel(
                                                short_address='conflict')
        directlyProvides(ml1, IPeopleReportMailingList)
        report2 = section['report2'] = testing.DummyModel()
        report3 = section['report3'] = testing.DummyModel()
        ml3 = report3['mailinglist'] = testing.DummyModel(
                                                short_address='conflict')
        directlyProvides(ml3, IPeopleReportMailingList)
        self.assertRaises(ValueError, self._callFUT, peopledir)

    def test_w_conflicts_outside_people(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleReportMailingList
        ALIASES = {'duplicate': '/somewhere/else',
                  }
        site = testing.DummyModel(list_aliases=ALIASES)
        peopledir = site['people'] = testing.DummyModel()
        section = peopledir['section'] = testing.DummyModel()
        report1 = section['report1'] = testing.DummyModel()
        ml1 = report1['mailinglist'] = testing.DummyModel(
                                            short_address='duplicate')
        directlyProvides(ml1, IPeopleReportMailingList)
        self.assertRaises(ValueError, self._callFUT, peopledir)


class Test_peopleconf(unittest.TestCase):

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
                        I<b>heart</b>NY
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
                                <filter type="category" category="offices"
                                        values="nyc"/>
                                <columns names="name email"/>
                            </report>
                        </report-group>
                    </column>
                </section>
            </sections>
        </peopledirectory>
        """
        elem = parse_xml(xml)
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
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
        site = testing.DummyModel(list_aliases={})
        peopledir = site['people'] = DummyPeopleDirectory()
        peopledir.catalog = DummyCatalog()
        profiles = site['profiles'] = testing.DummyModel()
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
