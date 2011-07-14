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

from zope.interface import Interface

from repoze.bfg import testing
from repoze.bfg.testing import cleanUp


class LiveSearchEntryAdapterTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_generic_adapter(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import generic_livesearch_result
        result = generic_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('http://example.com/foo/', result['url'])

    def test_profile_adapter_defaultimg(self):
        context = testing.DummyModel(title='foo',
                                     extension='x1234',
                                     email='foo@example.com',
                                     department='science',
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import profile_livesearch_result
        result = profile_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('x1234', result['extension'])
        self.assertEqual('foo@example.com', result['email'])
        self.failUnless(result['thumbnail'].endswith('/images/defaultUser.gif'))
        self.assertEqual('science', result['department'])
        self.assertEqual('profile', result['type'])
        self.assertEqual('profile', result['category'])

    def test_profile_adapter_customimg(self):
        from karl.content.interfaces import IImage
        from zope.interface import alsoProvides
        context = testing.DummyModel(title='foo',
                                     extension='x1234',
                                     email='foo@example.com',
                                     department='science',
                                     )
        dummyphoto = testing.DummyModel(title='photo')
        alsoProvides(dummyphoto, IImage)
        context['photo'] = dummyphoto
        request = testing.DummyRequest()
        from karl.views.adapters import profile_livesearch_result
        result = profile_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('x1234', result['extension'])
        self.assertEqual('foo@example.com', result['email'])
        self.assertEqual('http://example.com/photo/thumb/85x85.jpg',
                         result['thumbnail'])
        self.assertEqual('science', result['department'])
        self.assertEqual('profile', result['type'])
        self.assertEqual('profile', result['category'])

    def test_page_adapter_withnocommunity(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     modified_by='johnny',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import page_livesearch_result
        result = page_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('johnny', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual(None, result['community'])
        self.assertEqual('page', result['type'])
        self.assertEqual('page', result['category'])

    def test_page_adapter_withcommunity(self):
        from datetime import datetime
        from karl.models.interfaces import ICommunity
        from zope.interface import alsoProvides
        root = testing.DummyModel(title='nice community')
        alsoProvides(root, ICommunity)
        context = testing.DummyModel(__name__='foo',
                                     __parent__=root,
                                     title='foo',
                                     modified_by='johnny',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import page_livesearch_result
        result = page_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('johnny', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual('nice community', result['community'])
        self.assertEqual('page', result['type'])
        self.assertEqual('page', result['category'])

    def test_page_adapter_withoffice(self):
        from datetime import datetime
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IIntranets
        from zope.interface import alsoProvides
        root = testing.DummyModel(title='nice office')
        alsoProvides(root, ICommunity)
        alsoProvides(root, IIntranets)
        context = testing.DummyModel(__name__='foo',
                                     __parent__=root,
                                     title='foo',
                                     modified_by='johnny',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import page_livesearch_result
        result = page_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('johnny', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual(None, result['community'])
        self.assertEqual('page', result['type'])
        self.assertEqual('page', result['category'])

    def test_reference_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     modified_by='biff',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import reference_livesearch_result
        result = reference_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('biff', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual('page', result['type'])
        self.assertEqual('reference', result['category'])

    def test_blogentry_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     modified_by='marty',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import blogentry_livesearch_result
        result = blogentry_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('marty', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual(None, result['community'])
        self.assertEqual('post', result['type'])
        self.assertEqual('blogentry', result['category'])

    def test_comment_adapter_noparents(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     creator='michael',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import comment_livesearch_result
        result = comment_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('michael', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual(None, result['community'])
        self.assertEqual(None, result['forum'])
        self.assertEqual(None, result['blog'])
        self.assertEqual('post', result['type'])
        self.assertEqual('comment', result['category'])

    def test_comment_adapter_withparents(self):
        from zope.interface import alsoProvides
        from datetime import datetime
        from karl.content.interfaces import IForum
        from karl.content.interfaces import IBlogEntry
        from karl.models.interfaces import ICommunity
        root = testing.DummyModel(title='object title')
        # cheat here and have the object implement all the interfaces we expect
        alsoProvides(root, IForum)
        alsoProvides(root, ICommunity)
        alsoProvides(root, IBlogEntry)
        context = testing.DummyModel(__parent__=root,
                                     title='foo',
                                     creator='michael',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import comment_livesearch_result
        result = comment_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('michael', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual('object title', result['community'])
        self.assertEqual('object title', result['forum'])
        self.assertEqual('object title', result['blog'])
        self.assertEqual('post', result['type'])
        self.assertEqual('comment', result['category'])

    def test_forum_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     creator='sarah',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import forum_livesearch_result
        result = forum_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('sarah', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual('post', result['type'])
        self.assertEqual('forum', result['category'])

    def test_forumtopic_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     creator='sarah',
                                     created=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import forumtopic_livesearch_result
        result = forumtopic_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('sarah', result['creator'])
        self.assertEqual('1985-01-01T00:00:00', result['created'])
        self.assertEqual(None, result['forum'])
        self.assertEqual('post', result['type'])
        self.assertEqual('forumtopic', result['category'])

    def test_file_adapter(self):
        from datetime import datetime
        from karl.content.views.interfaces import IFileInfo
        context = testing.DummyModel(title='foo',
                                     modified_by='susan',
                                     modified=datetime(1985, 1, 1),
                                     )
        request = testing.DummyRequest()
        testing.registerAdapter(DummyFileAdapter,
                                (testing.DummyModel, testing.DummyRequest),
                                IFileInfo)

        from karl.views.adapters import file_livesearch_result
        result = file_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('susan', result['modified_by'])
        self.assertEqual('1985-01-01T00:00:00', result['modified'])
        self.assertEqual('file', result['type'])
        self.assertEqual('file', result['category'])
        self.assertEqual(None, result['community'])
        self.failUnless(result['icon'].endswith('/imgpath.png'))

    def test_community_adapter(self):
        from zope.interface import alsoProvides
        from karl.models.interfaces import ICommunityInfo
        context = testing.DummyModel(title='foo',
                                     number_of_members=7,
                                     )
        def dummy_communityinfo_adapter(context, request):
            return context
        testing.registerAdapter(dummy_communityinfo_adapter,
                                (testing.DummyModel, testing.DummyRequest),
                                ICommunityInfo)
        request = testing.DummyRequest()
        from karl.views.adapters import community_livesearch_result
        result = community_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual(7, result['num_members'])
        self.assertEqual('community', result['type'])
        self.assertEqual('community', result['category'])

    def test_calendar_adapter(self):
        from datetime import datetime
        context = testing.DummyModel(title='foo',
                                     startDate=datetime(1985, 1, 1),
                                     endDate=datetime(1985, 2, 1),
                                     location='mars',
                                     )
        request = testing.DummyRequest()
        from karl.views.adapters import calendar_livesearch_result
        result = calendar_livesearch_result(context, request)
        self.assertEqual('foo', result['title'])
        self.assertEqual('1985-01-01T00:00:00', result['start'])
        self.assertEqual('1985-02-01T00:00:00', result['end'])
        self.assertEqual('mars', result['location'])
        self.assertEqual(None, result['community'])
        self.assertEqual('calendarevent', result['type'])
        self.assertEqual('calendarevent', result['category'])


class AdvancedSearchResultsDisplayTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_generic(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import BaseAdvancedSearchResultsDisplay
        adapter = BaseAdvancedSearchResultsDisplay(context, request)
        self.assertEqual('searchresults_generic', adapter.macro)
        self.assertEqual({}, adapter.display_data)

    def test_office(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import AdvancedSearchResultsDisplayOffice
        adapter = AdvancedSearchResultsDisplayOffice(context, request)
        self.assertEqual('searchresults_office', adapter.macro)
        self.assertEqual({}, adapter.display_data)

    def test_people(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import AdvancedSearchResultsDisplayPeople
        context.extension = '1234'
        context.room_no = '101'
        context.email = 'foo@example.com'
        context.photo = None
        adapter = AdvancedSearchResultsDisplayPeople(context, request)
        self.assertEqual('searchresults_people', adapter.macro)
        self.failUnless('1234' in adapter.display_data['contact_html'])
        self.failUnless('101' in adapter.display_data['contact_html'])
        self.failUnless('foo@example.com'
                        in adapter.display_data['contact_html'])
        thumb = adapter.display_data['thumbnail']
        self.failUnless(thumb.endswith('/defaultUser.gif'))

    def test_event(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import AdvancedSearchResultsDisplayEvent
        from karl.utilities.interfaces import IKarlDates
        testing.registerUtility(lambda x,y: "custom date string",
                                IKarlDates)
        from datetime import datetime
        context.startDate = datetime(1900, 1, 1, 1, 1)
        context.endDate = datetime(1900, 1, 1, 2, 2)
        context.location = 'earth'
        adapter = AdvancedSearchResultsDisplayEvent(context, request)
        self.assertEqual('searchresults_event', adapter.macro)
        self.assertEqual('custom date string',
                         adapter.display_data['startDate'])
        self.assertEqual('custom date string',
                         adapter.display_data['endDate'])
        self.assertEqual('earth',
                         adapter.display_data['location'])

    def test_file(self):
        root = testing.DummyModel()
        context = testing.DummyModel(__name__='foo', __parent__=root,
                                     title='foo')
        request = testing.DummyRequest()
        from karl.views.adapters import AdvancedSearchResultsDisplayFile
        from karl.content.views.interfaces import IFileInfo
        testing.registerAdapter(DummyFileAdapter,
                                (Interface, Interface),
                                IFileInfo)
        adapter = AdvancedSearchResultsDisplayFile(context, request)
        self.assertEqual('searchresults_file', adapter.macro)
        self.assertEqual('DummyFileAdapter',
                         type(adapter.display_data['fileinfo']).__name__)
        self.failUnless(adapter.display_data['icon'].endswith('/imgpath.png'))


class DummyFileAdapter(object):
    def __init__(self, context, request):
        pass
    mimeinfo = dict(small_icon_name='imgpath.png')
