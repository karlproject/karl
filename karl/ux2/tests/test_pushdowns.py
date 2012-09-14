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
from pyramid import testing
from karl import testing as karltesting


class MyProfilePushdownTests(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import cleanUp
        config = cleanUp()
        config.add_static_view('static', 'karl.views:static')
        from zope.interface import Interface
        from karl.models.interfaces import ICommunityInfo
        from karl.models.interfaces import IGridEntryInfo
        karltesting.registerAdapter(DummyCommunityInfoAdapter,
                                (Interface, Interface),
                                ICommunityInfo)
        karltesting.registerAdapter(DummyGridInfoAdapter,
                                (Interface, Interface),
                                IGridEntryInfo)
        karltesting.registerDummySecurityPolicy('userid',
                                                ('group.community:community1:member',
                                                 'group.community:community2:member',
                                                 'group.community:community3:member'))

    def tearDown(self):
        from pyramid.testing import cleanUp
        cleanUp()


    def _callFUT(self, context, request):
        from karl.ux2.pushdowns import myprofile_ajax_view
        return myprofile_ajax_view(context, request)


    def test_it(self):
        from datetime import datetime
        from datetime import timedelta
        from pyramid.testing import DummyModel
        request = testing.DummyRequest()

        site = testing.DummyModel()
        communities = site["communities"] = testing.DummyModel()
        community1 = communities["community1"] = testing.DummyModel()
        community1.title = "Test Community 1"
        community1.last_activity_date = datetime.now()

        community2 = communities["community2"] = testing.DummyModel()
        community2.title = "Test Community 2"
        community2.last_activity_date = datetime.now() - timedelta(2)

        community3 = communities["community3"] = testing.DummyModel()
        community3.title = "Test Community 3"
        community3.last_activity_date = datetime.now() - timedelta(1)

        request.context = context = site
        site["profiles"] = profiles = DummyModel()
        profiles["userid"] = DummyProfile()

        item1 = DummyModel()
        item1.__name__ = 'doc1'
        item1.title = 'Doc 1'
        item1.modified = datetime.now()

        item2 = DummyModel()
        item2.__name__ = 'doc2'
        item2.title = 'Doc 2'
        item2.modified = datetime.now() - timedelta(1)

        registerCatalogSearch(results={'modified_by=userid': [item1, item2]})

        response = self._callFUT(context, request)
        data = response['data']
        communities = data['panels'][0]['communities']
        recent = data['panels'][1]['contexts']
        self.assertEqual(data['profile_name'], 'firstname lastname')
        self.assertEqual(data['profile_url'],
                'http://example.com/profiles/userid/')
        self.assertEqual(data['icon_url'],
                'http://example.com/static/images/defaultUser.gif')
        self.assertEqual(data['logout_url'], 'http://example.com/logout.html')
        self.assertEqual(data['department'], '4a')
        self.assertEqual(data['position'], 'halfback')
        self.assertEqual(data['email'], 'me@my.self')
        self.assertEqual(data['extension'], '911')
        self.assertEqual(data['phone'], '555-55555')
        self.assertEqual(len(communities), 3)
        self.assertEqual(len(recent), 2)
        self.assertEqual(communities[0]['title'], 'Test Community 1')
        self.assertEqual(communities[1]['title'], 'Test Community 3')
        self.assertEqual(communities[2]['title'], 'Test Community 2')
        self.assertEqual(recent[0]['title'], 'Doc 1')
        self.assertEqual(recent[1]['title'], 'Doc 2')


class DummyCommunityInfoAdapter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.last_activity_date = context.last_activity_date
        self.title = context.title
        self.description  = 'Description for %s' % self.title
        self.url = 'http://test/%s/' % context.__name__

class DummyGridInfoAdapter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.title = context.title
        self.creator_title = 'User Id'
        self.type = 'Blog Post'
        self.url = 'http://test/%s' % context.__name__

class DummyProfile(testing.DummyModel):
    websites = ()
    title = 'firstname lastname'
    date_format = None
    department = '4a'
    position = 'halfback'
    email = 'me@my.self'
    extension = '911'
    phone = '555-55555'

def dummy_search(results):
    class DummySearchAdapter:
        def __init__(self, context, request=None):
            self.context = context
            self.request = request

        def __call__(self, **kw):
            search = []
            for k,v in kw.items():
                key = '%s=%s' % (k,v)
                if key in results:
                    search.extend(results[key])

            return len(search), search, lambda x: x

    return DummySearchAdapter

def registerCatalogSearch(results={}):
    from zope.interface import Interface
    from karl.models.interfaces import ICatalogSearch
    karltesting.registerAdapter(
        dummy_search(results), (Interface,), ICatalogSearch)

