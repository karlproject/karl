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

from repoze.bfg import testing
from karl import testing as karltesting

class EditProfileTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        karltesting.registerCatalogSearch()
        karltesting.registerSettings()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import edit_profile_view
        return edit_profile_view(context, request)

    def test_not_submitted(self):
        context = DummyProfile(email='ed3@example.com')
        context.title = "Eddie"
        site = karltesting.DummyRoot()
        site['profiles']['ed'] = context
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/edit_profile.pt')

        response = self._callFUT(context, request)

        self.failIf(response.location)
        self.failIf(renderer.fielderrors)
        self.assertEqual(renderer.staff_change_password_url,
            'http://pw.example.com?username=ed&email=ed3%40example.com'
            '&came_from=http%3A%2F%2Fexample.com%2Fprofiles%2Fed%2F')

    def test_submitted_invalid(self):
        renderer = testing.registerDummyRenderer('templates/edit_profile.pt')
        request = testing.DummyRequest({'form.submitted':1})
        context = DummyProfile(email='me@example.com')
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        testing.registerDummySecurityPolicy('userid')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                           IObjectWillBeModifiedEvent))
        params = profile_data.copy()
        params['form.submitted'] = '1'
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Profile%20edited')
        for k, v in profile_data.items():
            if k == 'photo':
                continue
            self.assertEqual(getattr(context, k), v)
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)

    def test_upload_photo(self):
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        testing.registerDummySecurityPolicy('userid')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from zope.interface import Interface
        from karl.testing import DummyUpload
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                           IObjectWillBeModifiedEvent))
        from repoze.lemonade.interfaces import IContentFactory
        from karl.models.interfaces import IImageFile
        from karl.views.tests.test_file import DummyImageFile
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)

        params = profile_data.copy()
        params['form.submitted'] = '1'
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo)
        params['photo.static'] = ''
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        
        response = self._callFUT(context, request)

        self.assertTrue(len(context["photo.jpg"].stream.read()) > 0)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Profile%20edited')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)

    def test_reupload_photo(self):
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        testing.registerDummySecurityPolicy('userid')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from zope.interface import Interface
        from karl.testing import DummyUpload
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                           IObjectWillBeModifiedEvent))
        from repoze.lemonade.interfaces import IContentFactory
        from karl.models.interfaces import IImageFile
        from karl.views.tests.test_file import DummyImageFile
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)

        params = profile_data.copy()
        params['form.submitted'] = '1'
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo)
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        response = self._callFUT(context, request)

        self.assertTrue(len(context["photo.jpg"].stream.read()) > 0)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Profile%20edited')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)

        prev_len = len(dummy_photo)
        dummy_photo2 = dummy_photo * 2
        self.assertEqual(len(dummy_photo) * 2, len(dummy_photo2))
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo2)
        request = testing.DummyRequest(params)
        response = self._callFUT(context, request)
        self.assertTrue(len(context["photo.jpg"].stream.read()) > 0)

    def test_delete_photo(self):
        testing.registerDummySecurityPolicy('userid')
        params = profile_data.copy()
        params['form.submitted'] = '1'
        params['photo_delete'] = '1'
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context["photo.jpg"] = testing.DummyModel()
        context.title = "Eddie"
        response = self._callFUT(context, request)

        self.assertRaises(KeyError, context.__getitem__, "photo.jpg")

class GetGroupFieldsTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self):
        from karl.views.people import get_group_fields
        return get_group_fields(None)

    def test_it(self):
        karltesting.registerSettings()
        gf = self._callFUT()
        self.assertEqual(gf, [
            {
                'fieldname': 'groupfield-group-KarlAdmin',
                'group': 'group.KarlAdmin',
                'title': 'KarlAdmin',
            },
            {
                'fieldname': 'groupfield-group-KarlLovers',
                'group': 'group.KarlLovers',
                'title': 'KarlLovers',
            },
            ])

class AdminEditProfileTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        karltesting.registerCatalogSearch()
        karltesting.registerSettings()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import admin_edit_profile_view
        return admin_edit_profile_view(context, request)

    def test_not_submitted(self):
        context = DummyProfile(email='ed3@example.com')
        context.title = "Eddie"
        site = karltesting.DummyRoot()
        site['profiles']['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/admin_edit_profile.pt')

        response = self._callFUT(context, request)

        self.failIf(response.location)
        self.failIf(renderer.fielderrors)

    def test_form_group_fields(self):
        context = DummyProfile(email='ed3@example.com')
        context.title = "Eddie"
        site = karltesting.DummyRoot()
        site['profiles']['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", ['group.KarlAdmin'])
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/admin_edit_profile.pt')

        self._callFUT(context, request)

        self.assertEqual(renderer.group_fields, [
            {
                'fieldname': 'groupfield-group-KarlAdmin',
                'group': 'group.KarlAdmin',
                'title': 'KarlAdmin',
            },
            {
                'fieldname': 'groupfield-group-KarlLovers',
                'group': 'group.KarlLovers',
                'title': 'KarlLovers',
            },
            ])

    def test_submitted_invalid(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin_edit_profile.pt')
        request = testing.DummyRequest({'form.submitted':1})
        context = DummyProfile(email='me@example.com')
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        testing.registerDummySecurityPolicy('userid')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from zope.interface import Interface
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                           IObjectWillBeModifiedEvent))
        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '',
            'password': '',
            'password_confirm': '',
            })
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
                         'http://example.com/ed/?status_message=User%20edited')
        for k, v in profile_data.items():
            if k == 'photo':
                continue
            self.assertEqual(getattr(context, k), v)
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)

    def test_upload_photo(self):
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        testing.registerDummySecurityPolicy('userid')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from zope.interface import Interface
        from karl.testing import DummyUpload
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                           IObjectWillBeModifiedEvent))
        from repoze.lemonade.interfaces import IContentFactory
        from karl.models.interfaces import IImageFile
        from karl.views.tests.test_file import DummyImageFile
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)

        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '',
            'password': '',
            'password_confirm': '',
            })
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo)
        params['photo.static'] = ''
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)

        self.assertTrue(len(context["photo.jpg"].stream.read()) > 0)
        self.assertEqual(response.location,
            'http://example.com/ed/?status_message=User%20edited')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)

    def test_reupload_photo(self):
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        testing.registerDummySecurityPolicy('userid')
        from karl.models.interfaces import IObjectModifiedEvent
        from karl.models.interfaces import IObjectWillBeModifiedEvent
        from zope.interface import Interface
        from karl.testing import DummyUpload
        L = testing.registerEventListener((Interface, IObjectModifiedEvent))
        L2 = testing.registerEventListener((Interface,
                                           IObjectWillBeModifiedEvent))
        from repoze.lemonade.interfaces import IContentFactory
        from karl.models.interfaces import IImageFile
        from karl.views.tests.test_file import DummyImageFile
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)

        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '',
            'password': '',
            'password_confirm': '',
            })
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo)
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)

        self.assertTrue(len(context["photo.jpg"].stream.read()) > 0)
        self.assertEqual(response.location,
            'http://example.com/ed/?status_message=User%20edited')
        self.assertEqual(len(L), 2)
        self.assertEqual(len(L2), 2)

        prev_len = len(dummy_photo)
        dummy_photo2 = dummy_photo * 2
        self.assertEqual(len(dummy_photo) * 2, len(dummy_photo2))
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo2)
        request = testing.DummyRequest(params)
        response = self._callFUT(context, request)
        self.assertTrue(len(context["photo.jpg"].stream.read()) > 0)

    def test_delete_photo(self):
        testing.registerDummySecurityPolicy('userid')
        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '',
            'password': '',
            'password_confirm': '',
            })
        params['photo_delete'] = '1'
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context["photo.jpg"] = testing.DummyModel()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)

        self.assertRaises(KeyError, context.__getitem__, "photo.jpg")

    def test_change_login(self):
        testing.registerDummySecurityPolicy('userid')
        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'zed',
            'home_path': '',
            'password': '',
            'password_confirm': '',
            })
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)

        self.assertEqual(users.get_by_id('ed')['login'], 'zed')

    def test_change_groups(self):
        testing.registerDummySecurityPolicy('userid')
        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'zed',
            'home_path': '',
            'groupfield-group-KarlLovers': 'on',
            'password': '',
            'password_confirm': '',
            })
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", ['group.KarlAdmin'])
        response = self._callFUT(context, request)

        self.assertEqual(users.added_groups, [('ed', 'group.KarlLovers')])
        self.assertEqual(users.removed_groups, [('ed', 'group.KarlAdmin')])

    def test_change_home_path(self):
        testing.registerDummySecurityPolicy('userid')
        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '/zzz',
            'password': '',
            'password_confirm': '',
            })
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)

        self.assertEqual(context.home_path, '/zzz')

    def test_change_password(self):
        testing.registerDummySecurityPolicy('userid')
        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '',
            'password': 'abcdefgh',
            'password_confirm': 'abcdefgh',
            })
        request = testing.DummyRequest(params)
        context = DummyProfile()
        context.title = "Eddie"
        site = testing.DummyModel()
        site['ed'] = context
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        response = self._callFUT(context, request)

        from repoze.who.plugins.zodb.users import get_sha_password
        pw = get_sha_password('abcdefgh')
        self.assertEqual(users.get_by_id('ed')['password'], pw)


class ShowProfileTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import show_profile_view
        return show_profile_view(context, request)

    def _registerTagbox(self):
        from karl.testing import registerTagbox
        registerTagbox()

    def _registerCatalogSearch(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()

    def test_editable(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        testing.registerDummySecurityPolicy('userid')
        renderer = testing.registerDummyRenderer('templates/profile.pt')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'userid'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 3)
        self.assertEqual(renderer.actions[0][1], 'admin_edit_profile.html')
        self.assertEqual(renderer.actions[1][1], 'manage_communities.html')
        self.assertEqual(renderer.actions[2][1], 'manage_tags.html')

    def test_not_editable(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        testing.registerDummySecurityPolicy('userid')
        renderer = testing.registerDummyRenderer('templates/profile.pt')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'chris'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context.users.add("chris", "chrislogin", "password", [])
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 1)
        self.assertEqual(renderer.actions[0][1], 'admin_edit_profile.html')
        #self.assertEqual(renderer.actions[1][1], 'delete.html')

    def test_communities(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from repoze.bfg.testing import DummyModel
        from karl.testing import DummyCommunity
        from karl.testing import DummyUsers
        renderer = testing.registerDummyRenderer('templates/profile.pt')
        request = testing.DummyRequest()
        context = DummyProfile()
        users = DummyUsers()

        community1 = DummyCommunity()
        community1.title = "Community 1"

        communities = community1.__parent__
        communities["community2"] = community2 = DummyCommunity()
        community2.title = "Community 2"
        users.add("userid", "userid", "password",
                  ["group.community:community:members",
                   "group.community:community2:moderators"])

        site = communities.__parent__
        site.users = users
        site["profiles"] = profiles = DummyModel()
        profiles["userid"] = context

        self._callFUT(context, request)
        self.assertEqual(renderer.communities, [
            {"title": "Community 1",
             "moderator": False,
             "url": "http://example.com/communities/community/",},
            {"title": "Community 2",
             "moderator": True,
             "url": "http://example.com/communities/community2/",},
        ])

    def test_communities_nonviewable_filtered(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from repoze.bfg.testing import DummyModel
        from repoze.bfg.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy(permissive=False)
        from karl.testing import DummyCommunity
        from karl.testing import DummyUsers
        renderer = testing.registerDummyRenderer('templates/profile.pt')
        request = testing.DummyRequest()
        context = DummyProfile()
        users = DummyUsers()

        community1 = DummyCommunity()
        community1.title = "Community 1"

        communities = community1.__parent__
        communities["community2"] = community2 = DummyCommunity()
        community2.title = "Community 2"
        users.add("userid", "userid", "password",
                  ["group.community:community:members",
                   "group.community:community2:moderators"])

        site = communities.__parent__
        site.users = users
        site["profiles"] = profiles = DummyModel()
        profiles["userid"] = context

        self._callFUT(context, request)
        self.assertEqual(renderer.communities, [])

    def test_tags(self):
        from karl.testing import DummyUsers
        self._registerTagbox()
        self._registerCatalogSearch()
        testing.registerDummySecurityPolicy('eddie')
        TAGS = {'beaver': 1, 'wally': 3}
        context = DummyProfile()
        context.title = "Eddie"
        context.__name__ = "eddie"
        users = context.users = DummyUsers()
        users.add("eddie", "eddie", "password", [])
        tags = context.tags = testing.DummyModel()
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['eddie']
            assert community is None
            return TAGS.keys()
        tags.getTags = _getTags
        def _getFrequency(tags=None, community=None, user=None):
            assert community is None
            assert tags is not None
            assert user == 'eddie'
            return TAGS.items()
        tags.getFrequency = _getFrequency
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/profile.pt')

        response = self._callFUT(context, request)

        self.assertEqual(len(renderer.tags), 2)
        self.failUnless(renderer.tags[0], {'name': 'wally', 'count': 3})
        self.failUnless(renderer.tags[1], {'name': 'beaver', 'count': 1})

    def test_tags_capped_at_ten(self):
        from karl.testing import DummyUsers
        self._registerTagbox()
        self._registerCatalogSearch()
        testing.registerDummySecurityPolicy('eddie')
        TAGS = {'alpha': 1,
                'bravo': 2,
                'charlie': 3,
                'delta': 4,
                'echo': 5,
                'foxtrot': 6,
                'golf': 7,
                'hotel': 8,
                'india': 9,
                'juliet': 10,
                'kilo': 11,
               }
        context = DummyProfile()
        context.title = "Eddie"
        context.__name__ = "eddie"
        users = context.users = DummyUsers()
        users.add("eddie", "eddie", "password", [])
        tags = context.tags = testing.DummyModel()
        def _getTags(items=None, users=None, community=None):
            assert items is None
            assert list(users) == ['eddie']
            assert community is None
            return TAGS.keys()
        tags.getTags = _getTags
        def _getFrequency(tags=None, community=None, user=None):
            assert community is None
            assert tags is not None
            assert user == 'eddie'
            return TAGS.items()
        tags.getFrequency = _getFrequency
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/profile.pt')

        response = self._callFUT(context, request)

        self.assertEqual(len(renderer.tags), 10)
        self.failUnless(renderer.tags[0], {'name': 'kilo', 'count': 11})
        self.failUnless(renderer.tags[1], {'name': 'juliet', 'count': 10})
        self.failUnless(renderer.tags[9], {'name': 'bravo', 'count': 2})

    def test_show_recently_added(self):
        self._registerTagbox()

        search_args = {}
        def searcher(context):
            def search(**args):
                search_args.update(args)
                doc1 = testing.DummyModel(title='doc1')
                doc2 = testing.DummyModel(title='doc2')
                docids = [doc1, None, doc2]
                return len(docids), docids, lambda docid: docid
            return search
        from karl.models.interfaces import ICatalogSearch
        from repoze.bfg.testing import registerAdapter
        from zope.interface import Interface
        registerAdapter(searcher, (Interface,), ICatalogSearch)
        from karl.models.interfaces import IGridEntryInfo
        testing.registerAdapter(DummyGridEntryAdapter, (Interface, Interface),
                                IGridEntryInfo)

        from karl.testing import DummyUsers
        testing.registerDummySecurityPolicy('userid')
        renderer = testing.registerDummyRenderer('templates/profile.pt')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'chris'
        context.users = DummyUsers()
        context.users.add("userid", "userid", "password", [])
        context.users.add("chris", "chris", "password", [])
        self._callFUT(context, request)
        self.assertEqual(search_args['limit'], 5)
        self.assertEqual(search_args['creator'], 'chris')
        self.assertEqual(search_args['sort_index'], 'creation_date')
        self.assertEqual(search_args['reverse'], True)
        self.assertEqual(len(renderer.recent_items), 2)
        self.assertEqual(renderer.recent_items[0].context.title, 'doc1')
        self.assertEqual(renderer.recent_items[1].context.title, 'doc2')

class RecentContentTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import recent_content_view
        return recent_content_view(context, request)

    def test_without_content(self):
        context = DummyProfile()
        context.title = 'Z'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/profile_recent_content.pt')
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEquals(len(renderer.recent_items), 0)
        self.assertFalse(renderer.batch_info['batching_required'])

    def test_with_content(self):
        search_args = {}
        def searcher(context):
            def search(**args):
                search_args.update(args)
                doc1 = testing.DummyModel(title='doc1')
                doc2 = testing.DummyModel(title='doc2')
                docids = [doc1, None, doc2]
                return len(docids), docids, lambda docid: docid
            return search
        from karl.models.interfaces import ICatalogSearch
        from repoze.bfg.testing import registerAdapter
        from zope.interface import Interface
        registerAdapter(searcher, (Interface), ICatalogSearch)
        from karl.models.interfaces import IGridEntryInfo
        testing.registerAdapter(DummyGridEntryAdapter, (Interface, Interface),
                                IGridEntryInfo)

        context = DummyProfile()
        context.title = 'Z'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/profile_recent_content.pt')
        self._callFUT(context, request)
        self.assert_(renderer.api is not None)
        self.assertEquals(len(renderer.recent_items), 2)
        self.assertEquals(renderer.recent_items[0].context.title, 'doc1')
        self.assertEquals(renderer.recent_items[1].context.title, 'doc2')
        self.assertFalse(renderer.batch_info['batching_required'])

class ManageCommunitiesTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from karl.testing import DummyUsers

        # Set up dummy skel
        site = testing.DummyModel()
        self.users = site.users = DummyUsers()
        communities = site["communities"] = testing.DummyModel()
        community1 = communities["community1"] = testing.DummyModel()
        community1.title = "Test Community 1"
        community1.member_names = set(['a', 'c'])
        community1.moderator_names = set(['b'])
        community1.members_group_name = "community1_members"
        community1.moderators_group_name = "community1_moderators"
        self.community1 = community1

        community2 = communities["community2"] = testing.DummyModel()
        community2.title = "Test Community 2"
        community2.member_names = set(['b'])
        community2.moderator_names = set(['a', 'c'])
        community2.members_group_name = "community2_members"
        community2.moderators_group_name = "community2_moderators"
        self.community2 = community2

        community3 = communities["community3"] = testing.DummyModel()
        community3.title = "Test Community 3"
        community3.member_names = set(['b'])
        community3.moderator_names = set(['c'])
        community3.members_group_name = "community3_members"
        community3.moderators_group_name = "community3_moderators"
        self.community3 = community3

        from karl.testing import DummyProfile
        profiles = site["profiles"] = testing.DummyModel()
        self.profile = profiles["a"] = DummyProfile()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import manage_communities_view
        return manage_communities_view(context, request)

    def test_show_form(self):
        renderer = testing.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")
        self.profile.set_alerts_preference("community2", 1)
        self._callFUT(self.profile, request)

        self.assertEqual(renderer.post_url,
            "http://example.com/profiles/a/manage_communities.html")
        self.assertEqual(2, len(renderer.communities))

        community1 = renderer.communities.pop(0)
        self.assertEqual("community1", community1["name"])
        self.assertEqual("Test Community 1", community1["title"])
        self.assertTrue(community1["alerts_pref"][0]["selected"])
        self.assertFalse(community1["alerts_pref"][1]["selected"])
        self.assertFalse(community1["alerts_pref"][2]["selected"])
        self.assertTrue(community1["may_leave"])

        community2 = renderer.communities.pop(0)
        self.assertEqual("community2", community2["name"])
        self.assertEqual("Test Community 2", community2["title"])
        self.assertFalse(community2["alerts_pref"][0]["selected"])
        self.assertTrue(community2["alerts_pref"][1]["selected"])
        self.assertFalse(community2["alerts_pref"][2]["selected"])
        self.assertFalse(community2["may_leave"])

    def test_cancel(self):
        renderer = testing.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")

        request.params["form.cancel"] = "cancel"
        response = self._callFUT(self.profile, request)
        self.assertEqual("http://example.com/profiles/a/", response.location)

    def test_submit_alert_prefs(self):
        renderer = testing.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")

        from karl.models.interfaces import IProfile
        request.params["form.submitted"] = "submit"
        request.params["alerts_pref_community1"] = str(IProfile.ALERT_NEVER)
        request.params["alerts_pref_community2"] = str(IProfile.ALERT_DIGEST)

        self.assertEqual(IProfile.ALERT_IMMEDIATELY,
                         self.profile.get_alerts_preference("community1"))
        self.assertEqual(IProfile.ALERT_IMMEDIATELY,
                         self.profile.get_alerts_preference("community2"))
        response = self._callFUT(self.profile, request)

        self.assertEqual(IProfile.ALERT_NEVER,
                         self.profile.get_alerts_preference("community1"))
        self.assertEqual(IProfile.ALERT_DIGEST,
                         self.profile.get_alerts_preference("community2"))
        self.assertEqual(
            "http://example.com/profiles/a/?status_message=Community+preferences+updated.",
            response.location)

    def test_leave_community(self):
        renderer = testing.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")

        request.params["form.submitted"] = "submit"
        request.params["leave_community1"] = "True"

        self.failUnless("a" in self.community1.member_names)
        response = self._callFUT(self.profile, request)
        self.assertEqual( [("a", "community1_members")],
                          self.users.removed_groups)
        self.assertEqual(
            "http://example.com/profiles/a/?status_message=Community+preferences+updated.",
            response.location)

    def test_leave_community_sole_moderator(self):
        renderer = testing.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")

        request.params["form.submitted"] = "submit"
        request.params["leave_community2"] = "True"

        self.assertRaises(AssertionError, self._callFUT, self.profile, request)

class ShowProfilesViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import show_profiles_view
        return show_profiles_view(context, request)

    def test_it(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from karl.models.adapters import CatalogSearch
        catalog = karltesting.DummyCatalog({1:'/foo', 2:'/bar'})
        testing.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        testing.registerAdapter(DummyLetterManager, Interface,
                                ILetterManager)
        context = testing.DummyModel()
        context.catalog = catalog
        foo = testing.DummyModel()
        testing.registerModels({'/foo':foo})
        request = testing.DummyRequest(
            params={'titlestartswith':'A'})
        renderer = testing.registerDummyRenderer('templates/profiles.pt')
        self._callFUT(context, request)
        profiles = list(renderer.profiles)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0], foo)


class ChangePasswordViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        karltesting.registerSettings()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import change_password_view
        return change_password_view(context, request)

    def _old_password(self):
        from repoze.who.plugins.zodb.users import get_sha_password
        return get_sha_password('oldoldold')

    def test_show_form(self):
        context = DummyProfile()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/change_password.pt')
        response = self._callFUT(context, request)
        self.failIf(response.location)
        self.failIf(renderer.fielderrors)

    def test_submitted_incomplete(self):
        context = DummyProfile()
        request = testing.DummyRequest({
            'form.submitted':1
            })
        renderer = testing.registerDummyRenderer('templates/change_password.pt')
        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_wrong_old_password(self):
        from karl.testing import DummyUsers
        context = DummyProfile()
        context.__name__ = 'me'
        context.users = DummyUsers()
        context.users.add('me', 'me', self._old_password(), [])

        request = testing.DummyRequest({
            'form.submitted': 1,
            'old_password': 'idontknow',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        renderer = testing.registerDummyRenderer('templates/change_password.pt')

        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_new_password_mismatch(self):
        from karl.testing import DummyUsers
        context = DummyProfile()
        context.__name__ = 'me'
        context.users = DummyUsers()
        context.users.add('me', 'me', self._old_password(), [])

        request = testing.DummyRequest({
            'form.submitted': 1,
            'old_password': 'oldoldold',
            'password': 'newnewnew',
            'password_confirm': 'winwinwin',
            })
        renderer = testing.registerDummyRenderer('templates/change_password.pt')

        self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_success(self):
        from karl.testing import DummyUsers
        context = DummyProfile()
        context.__name__ = 'me'
        parent = testing.DummyModel()
        parent.__name__ = ''
        parent.__parent__ = None
        context.__parent__ = parent
        context.title = 'Me'
        context.email = 'me@example.com'
        parent.users = DummyUsers()
        parent.users.add('me', 'me', self._old_password(), [])

        request = testing.DummyRequest({
            'form.submitted': 1,
            'old_password': 'oldoldold',
            'password': 'newnewnew',
            'password_confirm': 'newnewnew',
            })
        renderer = testing.registerDummyRenderer(
            'templates/change_password.pt')

        from repoze.sendmail.interfaces import IMailDelivery
        from karl.testing import DummyMailer
        mailer = DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        response = self._callFUT(context, request)

        from repoze.who.plugins.zodb.users import get_sha_password
        new_enc = get_sha_password('newnewnew')
        self.assertEqual(parent.users.get_by_id('me')['password'], new_enc)

        self.assertEqual(response.location,
            'http://example.com/me/?status_message=Password%20changed')

        self.assertEqual(len(mailer), 1)
        msg = mailer.pop()
        self.assertEqual(msg.mto, ['me@example.com'])
        self.assertEqual(msg.mfrom, "admin@example.com")


class TestDeleteProfileView(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.people import delete_profile_view
        return delete_profile_view(context, request)

    def test_noconfirm(self):
        context = DummyProfile(firstname='Mori', lastname='Turi')
        context.title = 'Context'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/delete_profile.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')

    def test_confirm_not_deleting_own_profile(self):
        from karl.testing import DummyUsers
        parent = testing.DummyModel()
        users = parent.users = DummyUsers()
        context = DummyProfile()
        parent['userid'] = context
        testing.registerDummySecurityPolicy('admin')
        request = testing.DummyRequest(params={'confirm':'1'})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location,
                         'http://example.com/?status_message='
                         'Deleted+profile%3A+userid')
        self.failIf('userid' in parent)
        self.assertEqual(users.removed_users, ['userid'])

    def test_confirm_deleting_own_profile(self):
        from karl.testing import DummyUsers
        parent = testing.DummyModel()
        users = parent.users = DummyUsers()
        context = DummyProfile()
        parent['userid'] = context
        testing.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest(params={'confirm':'1'})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '401 Unauthorized')
        self.failIf('userid' in parent)
        self.assertEqual(users.removed_users, ['userid'])

class AddUserTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        karltesting.registerSettings()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import add_user_view
        return add_user_view(context, request)

    def test_not_submitted(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/add_user.pt')
        response = self._callFUT(context, request)
        self.failIf(response.location)
        self.failIf(renderer.fielderrors)

    def test_submitted_invalid(self):
        context = testing.DummyModel()
        request = testing.DummyRequest({'form.submitted': True})
        renderer = testing.registerDummyRenderer(
            'templates/add_user.pt')
        response = self._callFUT(context, request)
        self.failUnless(renderer.fielderrors)

    def test_submitted_valid(self):
        testing.registerDummySecurityPolicy('userid')
        karltesting.registerCatalogSearch()
        karltesting.registerSecurityWorkflow()
        from karl.models.profile import Profile
        from karl.models.interfaces import IProfile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Profile, IProfile)

        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '/path/for/ed',
            'password': 'abcdefgh',
            'password_confirm': 'abcdefgh',
            'groupfield-group-KarlLovers': 'on',
            })
        request = testing.DummyRequest(params)
        site = testing.DummyModel()
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        response = self._callFUT(site, request)
        self.assertEqual(response.location, 'http://example.com/ed/')
        user = users.get_by_id('ed')
        self.assert_(user is not None)
        self.assert_(site['ed'] is not None)
        self.assertEqual(user['groups'], ['group.KarlLovers'])

    def test_submitted_with_photo(self):
        testing.registerDummySecurityPolicy('userid')
        karltesting.registerCatalogSearch()
        karltesting.registerSecurityWorkflow()
        from karl.models.profile import Profile
        from karl.models.interfaces import IProfile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Profile, IProfile)

        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from repoze.lemonade.interfaces import IContentFactory
        from karl.models.interfaces import IImageFile
        from karl.views.tests.test_file import DummyImageFile
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)

        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '/path/for/ed',
            'password': 'abcdefgh',
            'password_confirm': 'abcdefgh',
            })
        from karl.testing import DummyUpload
        params['photo'] = DummyUpload(
            filename="test.jpg",
            mimetype="image/jpeg",
            data=dummy_photo)
        params['photo.static'] = ''
        request = testing.DummyRequest(params)
        site = testing.DummyModel()
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        response = self._callFUT(site, request)

        self.assertEqual(response.location, 'http://example.com/ed/')
        profile = site['ed']
        self.assertTrue(len(profile["photo.jpg"].stream.read()) > 0)

    def test_submitted_conflicting_userid(self):
        testing.registerDummySecurityPolicy('userid')
        karltesting.registerCatalogSearch()
        karltesting.registerSecurityWorkflow()
        from karl.models.profile import Profile
        from karl.models.interfaces import IProfile
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Profile, IProfile)

        params = profile_data.copy()
        params.update({
            'form.submitted': '1',
            'login': 'ed',
            'home_path': '/path/for/ed',
            'password': 'abcdefgh',
            'password_confirm': 'abcdefgh',
            'groupfield-group-KarlLovers': 'on',
            })
        request = testing.DummyRequest(params)
        site = testing.DummyModel()
        from karl.testing import DummyUsers
        users = site.users = DummyUsers()
        users.add("ed", "ed", "password", [])
        renderer = testing.registerDummyRenderer(
            'templates/add_user.pt')
        response = self._callFUT(site, request)

        self.assertEqual(renderer.fielderrors,
            {'login': u"User ID 'ed' already exists"})

profile_data = {
    'firstname':'firstname',
    'lastname':'lastname',
    'email':'email@example.com',
    'phone':'phone',
    'extension':'extension',
    'department': 'department1',
    'position':'position',
    'organization':'organization',
    'location':'location',
    'country':'CH',
    'website':'http://example.com',
    'languages': 'englishy',
    'photo': None,
    'biography': 'Interesting Person',
    }

class DummyProfile(testing.DummyModel):
    def __setitem__(self, name, value):
        """Simulate Folder behavior"""
        if self.get(name, None) is not None:
            raise KeyError(u"An object named %s already exists" % name)
        testing.DummyModel.__setitem__(self, name, value)

    def get_photo(self):
        for name in self.keys():
            if name.startswith("photo"):
                return self[name]
        return None

class DummyLetterManager:
    def __init__(self, context):
        self.context = context

    def get_info(self, request):
        return {}

class DummyGridEntryAdapter(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
