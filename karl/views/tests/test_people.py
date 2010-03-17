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
from karl.testing import DummySessions

class DummyForm(object):
    pass

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

class TestEditProfileFormController(unittest.TestCase):
    simple_used = ['firstname',
                   'lastname',
                   'email',
                   'phone',
                   'extension',
                   'department',
                   'position',
                   'organization',
                   'location',
                   'country',
                   'website',
                   'languages',
                   'biography']

    def setUp(self):
        cleanUp()
        sessions = DummySessions()
        context = DummyProfile(sessions=sessions)
        context.title = 'title'
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.views.people import EditProfileFormController
        return EditProfileFormController(context, request)

    def test_make_one_with_photo(self):
        context = self.context
        from karl.views.tests.test_file import DummyImageFile
        context['photo'] = DummyImageFile()
        controller = self._makeOne(context, self.request)
        self.failUnless(controller.photo is not None)
        self.assertEqual(controller.photo.filename, 'photo')

    def test_form_defaults(self):
        context = self.context
        request = self.request
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            setattr(context, fieldname, value)
        controller = self._makeOne(context, request)
        defaults = controller.form_defaults()
        for fieldname, value in profile_data.items():
            self.assertEqual(defaults[fieldname], value)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = controller.form_fields()
        fields = dict(fields)
        for fieldname in profile_data:
            self.failUnless(fieldname in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        for fieldname in profile_data:
            self.failUnless(fieldname in widgets)
        
    def test___call__(self):
        self.request.form = DummyForm()
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')
        self.assertEqual(response.get('form_title'), 'Edit Profile')
        self.assertEqual(response.get('include_blurb'), True)

        # one more time faking user as staff to improve coverage
        controller = self._makeOne(self.context, self.request)
        controller.api._isStaff = True
        response = controller()
        self.failUnless(response['api'].user_is_staff)        

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')
        
    def test_handle_submit(self):
        controller = self._makeOne(self.context, self.request)
        converted = {}
        # first set up the simple fields to submit
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            converted[fieldname] = value
        # then set up with the photo
        from karl.models.interfaces import IImageFile
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        from karl.views.tests.test_file import DummyImageFile
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)
        converted['photo'] = DummyUpload(filename='test.jpg',
                                         mimetype='image/jpeg',
                                         data=dummy_photo)
        # finally submit
        controller.handle_submit(converted)
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            self.assertEqual(getattr(self.context, fieldname), value)
        self.failUnless('photo.jpg' in self.context)
        self.failUnless(len(self.context['photo.jpg'].stream.read()) > 1)

class TestAdminEditProfileFormController(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self.sessions = sessions = DummySessions()
        context = DummyProfile(sessions=sessions)
        context.title = 'title'
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        # this initializes the available groups
        karltesting.registerSettings()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        # create the site and the users infrastructure first
        site = self.site = testing.DummyModel(sessions=self.sessions)
        site['profile'] = context
        from karl.testing import DummyUsers
        users = self.users = site.users = DummyUsers()
        users.add('profile', 'profile', 'password', ['group.KarlLovers'])
        from karl.views.people import AdminEditProfileFormController
        return AdminEditProfileFormController(context, request)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('login' in fields)
        self.failUnless('groups' in fields)
        self.failUnless('home_path' in fields)
        self.failUnless('password' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('login' in widgets)
        self.failUnless('groups' in widgets)
        self.failUnless('home_path' in widgets)
        self.failUnless('password' in widgets)

    def test_form_defaults(self):
        controller = self._makeOne(self.context, self.request)
        for fieldname, value in profile_data.items():
            setattr(self.context, fieldname, value)
        context = self.context
        context.home_path = '/home_path'
        self.site.users.change_password('profile', 'password')
        self.site.users.add_user_to_group('profile', 'group.KarlLovers')
        defaults = controller.form_defaults()
        self.assertEqual(defaults['password'], '')
        self.assertEqual(defaults['home_path'], '/home_path')
        self.assertEqual(defaults['login'], 'profile')
        self.assertEqual(defaults['groups'], set(['group.KarlLovers']))

    def test___call__(self):
        self.request.form = DummyForm()
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')
        self.assertEqual(response.get('form_title'),
                         'Edit User and Profile Information')
        self.assertEqual(response.get('include_blurb'), False)
        self.assertEqual(response.get('admin_edit'), True)

    def test_handle_submit(self):
        from repoze.who.plugins.zodb.users import get_sha_password
        controller = self._makeOne(self.context, self.request)
        converted = {}
        converted['home_path'] = '/home_path'
        converted['password'] = 'secret'
        converted['login'] = 'newlogin'
        converted['groups'] = ['group.KarlAdmin']
        response = controller.handle_submit(converted)
        context = self.context
        self.assertEqual(context.home_path, '/home_path')
        user = self.users.get_by_id('profile')
        self.assertEqual(user['password'], get_sha_password('secret'))
        self.assertEqual(user['login'], 'newlogin')
        self.assertEqual(self.users.added_groups,
                         [('profile', 'group.KarlAdmin')])
        self.assertEqual(self.users.removed_groups,
                         [('profile', 'group.KarlLovers')])
        self.assertEqual(response.location,
                         'http://example.com/profile/'
                         '?status_message=User%20edited')

        # try again w/ a login already in use
        context['inuse'] = testing.DummyModel()
        converted['login'] = 'inuse'
        from repoze.bfg.formish import ValidationError
        self.assertRaises(ValidationError, controller.handle_submit,
                          converted)

        # try again w/ special login value that will trigger ValueError
        converted['login'] = 'raise_value_error'
        self.assertRaises(ValidationError, controller.handle_submit,
                          converted)

class AddUserFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        sessions = self.sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        context.title = 'profiles'
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        karltesting.registerSettings()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        site = self.site = testing.DummyModel(sessions=self.sessions)
        site['profile'] = context
        from karl.testing import DummyUsers
        self.users = site.users = DummyUsers()
        from karl.views.people import AddUserFormController
        return AddUserFormController(context, request)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('login' in fields)
        self.failUnless('groups' in fields)
        self.failUnless('home_path' in fields)
        self.failUnless('password' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('login' in widgets)
        self.failUnless('groups' in widgets)
        self.failUnless('home_path' in widgets)
        self.failUnless('password' in widgets)

    def test_form_defaults(self):
        controller = self._makeOne(self.context, self.request)
        self.failUnless(controller.form_defaults() is None)

    def test___call__(self):
        self.request.form = DummyForm()
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title , 'Add User')
        self.assertEqual(response.get('form_title'), 'Add User')
        self.assertEqual(response.get('include_blurb'), False)

    def test_handle_submit(self):
        controller = self._makeOne(self.context, self.request)
        # first set up the easier fields
        converted = {'login': 'login',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path'}
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            converted[fieldname] = value
        # then set up the photo
        from karl.models.interfaces import IImageFile
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        from karl.views.tests.test_file import DummyImageFile
        from repoze.lemonade.interfaces import IContentFactory
        from repoze.lemonade.testing import registerContentFactory
        testing.registerAdapter(lambda *arg: DummyImageFile, (IImageFile,),
                                IContentFactory)
        converted['photo'] = DummyUpload(filename='test.jpg',
                                         mimetype='image/jpeg',
                                         data=dummy_photo)
        # next the workflow
        from repoze.workflow.testing import registerDummyWorkflow
        workflow = registerDummyWorkflow('security')
        # and the profile content factory
        from karl.models.profile import Profile
        from karl.models.interfaces import IProfile
        registerContentFactory(Profile, IProfile)
        # finally submit our constructed form
        response = controller.handle_submit(converted)
        self.assertEqual('http://example.com/profile/login/', response.location)
        user = self.users.get_by_id('login')
        self.failIf(user is None)
        self.assertEqual(user['groups'], ['group.KarlLovers'])
        self.assertEqual(len(workflow.initialized), 1)
        self.failUnless('login' in self.context)
        profile = self.context['login']
        self.failUnless('photo.jpg' in profile)
        self.failUnless(len(profile['photo.jpg'].stream.read()) > 0)

        # try again and make sure it fails
        converted['firstname'] = 'different'
        from repoze.bfg.formish import ValidationError
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        profile = self.context['login']
        self.failIf(profile.firstname != 'firstname')

class GetGroupOptionsTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self):
        from karl.views.people import get_group_options
        return get_group_options(None)

    def test_it(self):
        karltesting.registerSettings()
        gf = self._callFUT()
        self.assertEqual(gf, [
            ('group.KarlAdmin', 'KarlAdmin'),
            ('group.KarlLovers', 'KarlLovers')
            ])

class FilestorePhotoViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        sessions = DummySessions()
        context = self.context = testing.DummyModel(sessions=sessions)
        request = self.request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        request.subpath = ('sub', 'path', 'parts')

    def tearDown(self):
        cleanUp()

    def test_edit_profile_filestore_photo_view(self):
        from karl.views.forms.filestore import get_filestore
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        context = self.context
        request = self.request
        filestore = get_filestore(context, request, 'edit-profile')
        key = request.subpath[-1]
        upload = DummyUpload(filename='test.jpg',
                             mimetype='image/jpeg',
                             data=dummy_photo)
        filestore.put(key, upload.file, 'cache_tag', [])
        from karl.views.people import edit_profile_filestore_photo_view
        response = edit_profile_filestore_photo_view(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, dummy_photo)

    def test_add_user_filestore_photo_view(self):
        from karl.views.forms.filestore import get_filestore
        from karl.models.tests.test_image import one_pixel_jpeg as dummy_photo
        from karl.testing import DummyUpload
        context = self.context
        request = self.request
        filestore = get_filestore(context, request, 'add-user')
        key = request.subpath[-1]
        upload = DummyUpload(filename='test.jpg',
                             mimetype='image/jpeg',
                             data=dummy_photo)
        filestore.put(key, upload.file, 'cache_tag', [])
        from karl.views.people import add_user_filestore_photo_view
        response = add_user_filestore_photo_view(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.body, dummy_photo)

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

    def test_system_user(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        testing.registerDummySecurityPolicy('userid')
        renderer = testing.registerDummyRenderer('templates/profile.pt')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'admin'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context.users.add("chris", "chrislogin", "password", [])
        response = self._callFUT(context, request)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(len(renderer.actions), 1)
        self.assertEqual(renderer.actions[0][1], 'admin_edit_profile.html')


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
        self.profile.alert_attachments = 'link'

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

    def test_set_alert_attachments_attach(self):
        request = testing.DummyRequest()
        request.params["form.submitted"] = "submit"
        request.params["attachments"] = "attach"

        self.assertEqual(self.profile.alert_attachments, "link")
        self._callFUT(self.profile, request)
        self.assertEqual(self.profile.alert_attachments, "attach")

    def test_set_alert_attachments_link(self):
        request = testing.DummyRequest()
        request.params["form.submitted"] = "submit"
        request.params["attachments"] = "link"

        self.profile.alert_attachments = "attach"
        self._callFUT(self.profile, request)
        self.assertEqual(self.profile.alert_attachments, "link")

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
