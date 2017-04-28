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
from karl.testing import DummySessions

class DummyForm(object):
    allfields = ()
    def __init__(self):
        self.errors = {}

profile_data = {
    'firstname': 'firstname',
    'lastname': 'lastname',
    'email': 'email@example.com',
    'phone': 'phone',
    'extension': 'extension',
    'fax': 'fax',
    'department': 'department1',
    'position': 'position',
    'organization': 'organization',
    'location': 'location',
    'country': 'CH',
    'date_format': None,
    'websites': ['http://example.com'],
    'languages': 'englishy',
    'photo': None,
    'biography': 'Interesting Person',
    }

class DummyProfile(testing.DummyModel):
    websites = ()
    title = 'firstname lastname'
    date_format = None
    last_passwords = []
    def __setitem__(self, name, value):
        """Simulate Folder behavior"""
        if self.get(name, None) is not None:
            raise KeyError(u"An object named %s already exists" % name)
        testing.DummyModel.__setitem__(self, name, value)


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
                   'fax',
                   'department',
                   'position',
                   'organization',
                   'location',
                   'country',
                   'website',
                   'languages',
                   'biography']

    def setUp(self):
        testing.cleanUp()
        sessions = DummySessions()
        context = DummyProfile(sessions=sessions)
        context.title = 'title'
        context['profiles'] = testing.DummyModel()
        context['profiles']['userid'] = DummyProfile()
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, context, request):
        from karl.views.people import EditProfileFormController
        return EditProfileFormController(context, request)

    def test_make_one_with_photo(self):
        context = self.context
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
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')
        self.assertEqual(response.get('form_title'), 'Edit Profile')
        self.assertEqual(response.get('include_blurb'), True)

    def test___call__user_is_staff(self):
        self.request.form = DummyForm()
        karltesting.registerDummySecurityPolicy('user', ('group.KarlStaff',))
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        response = controller()
        self.failUnless(response['api'].user_is_staff)

    def test__call__websites_error(self):
        self.request.form = form = DummyForm()
        form.errors['websites'] = Exception("You're doing it wrong.")
        form.errors['websites.0'] = Exception("You made a boo boo.")
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        controller()
        self.failUnless('websites.0' in form.errors)
        self.assertEqual(
            str(form.errors['websites']), "You're doing it wrong.")

    def test__call__websites_suberror(self):
        self.request.form = form = DummyForm()
        form.errors['websites.0'] = Exception("You made a boo boo.")
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        controller()
        self.failIf('websites.0' in form.errors)
        self.assertEqual(
            form.errors['websites'].message, 'You made a boo boo.')

    def test_admin_redirected(self):
        from pyramid.httpexceptions import HTTPFound
        self.request.form = DummyForm()
        controller = self._makeOne(self.context, self.request)
        karltesting.registerDummySecurityPolicy('user', ('group.KarlAdmin',))
        response = controller()
        self.failUnless(isinstance(response, HTTPFound))
        self.assertEqual(response.location,
                'http://example.com/admin_edit_profile.html')

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit_normal_defaults(self):
        from karl.content.interfaces import ICommunityFile
        from karl.testing import DummyUpload
        from repoze.lemonade.interfaces import IContentFactory
        karltesting.registerAdapter(
            lambda *arg: DummyImageFile, (ICommunityFile,),
            IContentFactory)
        controller = self._makeOne(self.context, self.request)
        converted = {'photo': DummyUpload(filename='test.jpg',
                                         mimetype='image/jpeg',
                                         data=one_pixel_jpeg)}
        # first set up the simple fields to submit
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            converted[fieldname] = value

        controller.handle_submit(converted)

        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            self.assertEqual(getattr(self.context, fieldname), value)
        self.failUnless('photo' in self.context)
        self.assertEqual(self.context['photo'].data, one_pixel_jpeg)

    def test_handle_submit_bad_upload(self):
        from karl.content.interfaces import ICommunityFile
        from karl.testing import DummyUpload
        from repoze.lemonade.interfaces import IContentFactory
        karltesting.registerAdapter(
            lambda *arg: DummyImageFile, (ICommunityFile,),
            IContentFactory)
        controller = self._makeOne(self.context, self.request)
        converted = {'photo': DummyUpload(filename='test.jpg',
                                         mimetype='x-application/not a jpeg',
                                         data='not a jpeg')}
        # first set up the simple fields to submit
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            converted[fieldname] = value

        from pyramid_formish import ValidationError
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_w_websites_no_scheme(self):
        controller = self._makeOne(self.context, self.request)
        # make sure the www. URLs get prepended
        converted = {'websites': ['www.example.com'],
                     'photo': None,
                    }
        controller.handle_submit(converted)
        self.assertEqual(self.context.websites, ['http://www.example.com'])
        self.failIf('photo' in self.context)

    def test_handle_submit_w_websites_None(self):
        controller = self._makeOne(self.context, self.request)
        # Apparently, the formish / schemaish stuff has a bug which can give
        # us None for a sequence field.
        converted = {'websites': None}
        # first set up the simple fields to submit
        for fieldname, value in profile_data.items():
            if fieldname in ('websites', 'photo'):
                continue
            converted[fieldname] = value
        controller.handle_submit(converted)
        self.assertEqual(self.context.websites, [])
        for fieldname, value in profile_data.items():
            if fieldname in ('websites', 'photo'):
                continue
            self.assertEqual(getattr(self.context, fieldname), value)

    def test_handle_submit_dont_clobber_home_path(self):
        # LP #594127, bad class inheritance code caused
        # EditFormController.simple_field_names to be contaminated with field
        # names from subclasses, which was causing 'home_path' to get
        # overwritten even though it isn't shown on the form.
        controller = self._makeOne(self.context, self.request)
        # first set up the simple fields to submit
        converted = {}
        for fieldname, value in profile_data.items():
            converted[fieldname] = value
        self.context.home_path = 'foo/bar'
        controller.handle_submit(converted)
        self.assertEqual(self.context.home_path, 'foo/bar')

class TestAdminEditProfileFormController(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
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
        testing.cleanUp()

    def _makeOne(self, context, request, active=True):
        # create the site and the users infrastructure first
        site = self.site = testing.DummyModel(sessions=self.sessions)
        site['profile'] = context
        from karl.testing import DummyUsers
        users = self.users = site.users = DummyUsers()
        if active:
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

    def test_form_fields_inactive(self):
        controller = self._makeOne(self.context, self.request, False)
        fields = dict(controller.form_fields())
        self.failIf('login' in fields)
        self.failIf('groups' in fields)
        self.failUnless('home_path' in fields)
        self.failIf('password' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('login' in widgets)
        self.failUnless('groups' in widgets)
        self.failUnless('home_path' in widgets)
        self.failUnless('password' in widgets)

    def test_form_widgets_inactive(self):
        controller = self._makeOne(self.context, self.request, False)
        widgets = controller.form_widgets({})
        self.failIf('login' in widgets)
        self.failIf('groups' in widgets)
        self.failUnless('home_path' in widgets)
        self.failIf('password' in widgets)

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
        self.assertEqual(defaults['websites'], ['http://example.com'])

    def test_form_defaults_inactive(self):
        controller = self._makeOne(self.context, self.request, False)
        for fieldname, value in profile_data.items():
            setattr(self.context, fieldname, value)
        context = self.context
        context.home_path = '/home_path'
        defaults = controller.form_defaults()
        self.failIf('password' in defaults)
        self.assertEqual(defaults['home_path'], '/home_path')
        self.failIf('login' in defaults)
        self.failIf('groups' in defaults)
        self.assertEqual(defaults['websites'], ['http://example.com'])

    def test___call__(self):
        self.request.form = DummyForm()
        controller = self._makeOne(self.context, self.request)
        karltesting.registerLayoutProvider()
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')
        self.assertEqual(response.get('form_title'),
                         'Edit User and Profile Information')
        self.assertEqual(response.get('include_blurb'), False)
        self.assertEqual(response.get('admin_edit'), True)
        self.assertEqual(response.get('is_active'), True)

    def test__call__websites_error(self):
        self.request.form = form = DummyForm()
        form.errors['websites'] = Exception("You're doing it wrong.")
        form.errors['websites.0'] = Exception("You made a boo boo.")
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        controller()
        self.failUnless('websites.0' in form.errors)
        self.assertEqual(
            str(form.errors['websites']), "You're doing it wrong.")

    def test__call__websites_suberror(self):
        self.request.form = form = DummyForm()
        form.errors['websites.0'] = Exception("You made a boo boo.")
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        controller()
        self.failIf('websites.0' in form.errors)
        self.assertEqual(
            form.errors['websites'].message, 'You made a boo boo.')

    def test___call__inactive(self):
        self.request.form = DummyForm()
        controller = self._makeOne(self.context, self.request, False)
        karltesting.registerLayoutProvider()
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit title')
        self.assertEqual(response.get('form_title'),
                         'Edit User and Profile Information')
        self.assertEqual(response.get('include_blurb'), False)
        self.assertEqual(response.get('admin_edit'), True)
        self.assertEqual(response.get('is_active'), False)

    def test_handle_submit_normal(self):
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

    def test_handle_submit_w_websites_no_scheme(self):
        # make sure the www. URLs get prepended
        controller = self._makeOne(self.context, self.request)
        converted = {}
        converted['home_path'] = '/home_path'
        converted['login'] = 'newlogin'
        converted['password'] = 'secret2'
        converted['groups'] = ['group.KarlAdmin']
        converted['websites'] = ['www.example.com']
        controller.handle_submit(converted)
        self.assertEqual(self.context.websites, ['http://www.example.com'])

    def test_handle_submit_existing_login(self):
        # try w/ a login already in use
        from pyramid_formish import ValidationError
        controller = self._makeOne(self.context, self.request)
        converted = {}
        converted['home_path'] = '/home_path'
        converted['login'] = 'inuse'
        converted['password'] = 'secret3'
        converted['groups'] = ['group.KarlAdmin']
        converted['websites'] = ['www.example.com']
        context = self.context
        context['inuse'] = testing.DummyModel()
        self.assertRaises(ValidationError, controller.handle_submit,
                          converted)

    def test_handle_submit_w_login_raising_ValidationError(self):
        from pyramid_formish import ValidationError
        controller = self._makeOne(self.context, self.request)
        converted = {}
        converted['home_path'] = '/home_path'
        converted['login'] = 'raise_value_error'
        converted['password'] = 'secret4'
        converted['groups'] = ['group.KarlAdmin']
        converted['websites'] = ['www.example.com']
        # try again w/ special login value that will trigger ValueError
        self.assertRaises(ValidationError, controller.handle_submit,
                          converted)

    def test_handle_submit_w_websites_None(self):
        # Apparently, the formish / schemaish stuff has a bug which can give
        # us None for a sequence field.
        controller = self._makeOne(self.context, self.request)
        converted = {}
        converted['home_path'] = '/home_path'
        converted['login'] = 'newlogin'
        converted['password'] = 'secret5'
        converted['groups'] = ['group.KarlAdmin']
        converted['websites'] = None
        controller.handle_submit(converted)
        self.assertEqual(self.context.websites, [])

class AddUserFormControllerTests(unittest.TestCase):
    def setUp(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        testing.cleanUp()
        sessions = self.sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        context.title = 'profiles'
        self.context = context

        communities = context['communities'] = testing.DummyModel()
        self.community1 = communities['c1'] = testing.DummyModel()
        directlyProvides(self.community1, ICommunity)
        self.community2 = communities['c2'] = testing.DummyModel()
        directlyProvides(self.community2, ICommunity)

        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request
        karltesting.registerSettings()

        self.search_results = {}
        class DummySearch(object):
            def __init__(self, context):
                pass

            def __call__(myself, **kw):
                interfaces = kw.get('interfaces', None)
                if interfaces:
                    return self.search_results.get(
                        tuple(interfaces), (0, [], None)
                    )
                return 0, [], None

        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        karltesting.registerAdapter(DummySearch, (Interface,), ICatalogSearch)

    def tearDown(self):
        testing.cleanUp()

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
        karltesting.registerLayoutProvider()
        karltesting.registerDummyRenderer(
            'karl.views:forms/templates/snippets.pt')
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title , 'Add User')
        self.assertEqual(response.get('form_title'), 'Add User')
        self.assertEqual(response.get('include_blurb'), False)

    def test__call__websites_error(self):
        self.request.form = form = DummyForm()
        form.errors['websites'] = Exception("You're doing it wrong.")
        form.errors['websites.0'] = Exception("You made a boo boo.")
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        controller()
        self.failUnless('websites.0' in form.errors)
        self.assertEqual(
            str(form.errors['websites']), "You're doing it wrong.")

    def test__call__websites_suberror(self):
        self.request.form = form = DummyForm()
        form.errors['websites.0'] = Exception("You made a boo boo.")
        karltesting.registerLayoutProvider()
        controller = self._makeOne(self.context, self.request)
        controller()
        self.failIf('websites.0' in form.errors)
        self.assertEqual(
            form.errors['websites'].message, 'You made a boo boo.')

    def test_handle_submit(self):
        from repoze.lemonade.interfaces import IContentFactory
        from repoze.lemonade.testing import registerContentFactory
        from repoze.workflow.testing import registerDummyWorkflow
        from karl.content.interfaces import ICommunityFile
        from karl.models.interfaces import IProfile
        from karl.models.profile import Profile
        from karl.testing import DummyUpload
        # register defaults
        karltesting.registerAdapter(
            lambda *arg: DummyImageFile, (ICommunityFile,),
            IContentFactory)
        workflow = registerDummyWorkflow('security')
        registerContentFactory(Profile, IProfile)
        controller = self._makeOne(self.context, self.request)
        # first set up the easier fields
        converted = {'login': 'login',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                    }
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            converted[fieldname] = value
        # then set up the photo
        converted['photo'] = DummyUpload(filename='test.jpg',
                                         mimetype='image/jpeg',
                                         data=one_pixel_jpeg)
        # finally submit our constructed form
        response = controller.handle_submit(converted)

        self.assertEqual('http://example.com/profile/login/', response.location)
        user = self.users.get_by_id('login')
        self.failIf(user is None)
        self.assertEqual(user['groups'], ['group.KarlLovers'])
        self.assertEqual(len(workflow.initialized), 1)
        self.failUnless('login' in self.context)
        profile = self.context['login']
        self.failUnless('photo' in profile)
        self.assertEqual(profile['photo'].data, one_pixel_jpeg)

    def test_handle_submit_previously_invited(self):
        from repoze.lemonade.interfaces import IContentFactory
        from repoze.lemonade.testing import registerContentFactory
        from repoze.workflow.testing import registerDummyWorkflow
        from karl.content.interfaces import ICommunityFile
        from karl.models.interfaces import IInvitation
        from karl.models.interfaces import IProfile
        from karl.models.profile import Profile
        from karl.testing import DummyUpload

        # set up invitations
        self.community1['invite'] = invite1 = testing.DummyModel()
        self.community2['invite'] = invite2 = testing.DummyModel()
        self.search_results[(IInvitation,)] = (
            2, [invite1, invite2], lambda x: x)

        # register defaults
        karltesting.registerAdapter(
            lambda *arg: DummyImageFile, (ICommunityFile,),
            IContentFactory)
        registerDummyWorkflow('security')
        registerContentFactory(Profile, IProfile)
        controller = self._makeOne(self.context, self.request)
        # first set up the easier fields
        converted = {'login': 'login',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                    }
        for fieldname, value in profile_data.items():
            if fieldname == 'photo':
                continue
            converted[fieldname] = value
        # then set up the photo
        converted['photo'] = DummyUpload(filename='test.jpg',
                                         mimetype='image/jpeg',
                                         data=one_pixel_jpeg)
        # finally submit our constructed form
        controller.handle_submit(converted)

        self.failIf('invite' in self.community1)
        self.failIf('invite' in self.community2)

    def test_handle_submit_duplicate_id(self):
        from pyramid_formish import ValidationError
        # try again and make sure it fails
        controller = self._makeOne(self.context, self.request)
        self.context['existing'] = testing.DummyModel(
            firstname='firstname', security_state='active')
        converted = {'login': 'existing',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                     'firstname': 'different',
                    }
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        profile = self.context['existing']
        self.failIf(profile.firstname != 'firstname')
        self.assertEqual(controller.reactivate_user, None)

    def test_handle_submit_duplicate_id_inactive_user(self):
        from pyramid_formish import ValidationError
        # try again and make sure it fails
        controller = self._makeOne(self.context, self.request)
        self.context['existing'] = testing.DummyModel(
            firstname='firstname', security_state='inactive')
        converted = {'login': 'existing',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                     'firstname': 'different',
                    }
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        profile = self.context['existing']
        self.failIf(profile.firstname != 'firstname')
        self.assertEqual(controller.reactivate_user, {
            'url': 'http://example.com/profile/existing/reactivate.html',
            'userid': 'existing'})

    def test_handle_submit_duplicate_email(self):
        from karl.models.interfaces import IProfile
        from pyramid_formish import ValidationError
        # try again and make sure it fails
        controller = self._makeOne(self.context, self.request)
        self.context['existing'] = existing = testing.DummyModel(
            firstname='firstname', security_state='active')
        converted = {'login': 'newlogin',
                     'email': 'foo@example.org',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                     'firstname': 'different',
                    }
        self.search_results[(IProfile,)] = (1, [existing], lambda x: x)
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        profile = self.context['existing']
        self.failIf(profile.firstname != 'firstname')
        self.failIf('newlogin' in self.context)
        self.assertEqual(controller.reactivate_user, None)

    def test_handle_submit_duplicate_email_inactive_user(self):
        from karl.models.interfaces import IProfile
        from pyramid_formish import ValidationError
        # try again and make sure it fails
        controller = self._makeOne(self.context, self.request)
        self.context['existing'] = existing = testing.DummyModel(
            firstname='firstname', security_state='inactive')
        converted = {'login': 'newlogin',
                     'email': 'foo@example.org',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                     'firstname': 'different',
                    }
        self.search_results[(IProfile,)] = (1, [existing], lambda x: x)
        self.assertRaises(ValidationError, controller.handle_submit, converted)
        profile = self.context['existing']
        self.failIf(profile.firstname != 'firstname')
        self.failIf('newlogin' in self.context)
        self.assertEqual(controller.reactivate_user, {
            'url': 'http://example.com/profile/existing/reactivate.html',
            'userid': 'existing'})

    def test_handle_submit_w_websites_no_scheme(self):
        # once more, testing URL prepending
        from repoze.lemonade.testing import registerContentFactory
        from repoze.workflow.testing import registerDummyWorkflow
        from karl.models.interfaces import IProfile
        from karl.models.profile import Profile
        # register defaults
        registerDummyWorkflow('security')
        registerContentFactory(Profile, IProfile)
        controller = self._makeOne(self.context, self.request)
        # first set up the easier fields
        converted = {'login': 'login',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                     'photo': None,
                     'websites': ['www.example.com'],
                    }
        for fieldname, value in profile_data.items():
            if fieldname in ('websites', 'photo'):
                continue
            converted[fieldname] = value
        # then set up the photo
        controller.handle_submit(converted)
        profile = self.context['login']
        self.assertEqual(profile.websites, ['http://www.example.com'])

    def test_handle_submit_w_websites_None(self):
        # Apparently, the formish / schemaish stuff has a bug which can give
        # us None for a sequence field.
        from repoze.lemonade.testing import registerContentFactory
        from repoze.workflow.testing import registerDummyWorkflow
        from karl.models.interfaces import IProfile
        from karl.models.profile import Profile
        # register defaults
        registerDummyWorkflow('security')
        registerContentFactory(Profile, IProfile)
        controller = self._makeOne(self.context, self.request)
        # first set up the easier fields
        converted = {'login': 'login',
                     'password': 'password',
                     'groups': ['group.KarlLovers'],
                     'home_path': '/home_path',
                     'photo': None,
                     'websites': None,
                    }
        for fieldname, value in profile_data.items():
            if fieldname in ('websites', 'photo'):
                continue
            converted[fieldname] = value
        # then set up the photo
        controller.handle_submit(converted)
        profile = self.context['login']
        self.assertEqual(profile.websites, [])

class GetGroupOptionsTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        testing.cleanUp()
        sessions = DummySessions()
        self.context = testing.DummyModel(sessions=sessions)
        request = self.request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        request.subpath = ('sub', 'path', 'parts')

    def tearDown(self):
        testing.cleanUp()

    def test_edit_profile_filestore_photo_view(self):
        from karl.testing import DummyUpload
        from karl.views.forms.filestore import get_filestore
        from karl.views.people import edit_profile_filestore_photo_view
        context = self.context
        request = self.request
        filestore = get_filestore(context, request, 'edit-profile')
        key = request.subpath[-1]
        upload = DummyUpload(filename='test.jpg',
                             mimetype='image/jpeg',
                             data=one_pixel_jpeg)
        filestore.put(key, upload.file, 'cache_tag', [])
        try:
            response = edit_profile_filestore_photo_view(context, request)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.body, one_pixel_jpeg)
        finally:
            filestore.clear()

    def test_add_user_filestore_photo_view(self):
        from karl.testing import DummyUpload
        from karl.views.forms.filestore import get_filestore
        from karl.views.people import add_user_filestore_photo_view
        context = self.context
        request = self.request
        filestore = get_filestore(context, request, 'add-user')
        key = request.subpath[-1]
        upload = DummyUpload(filename='test.jpg',
                             mimetype='image/jpeg',
                             data=one_pixel_jpeg)
        filestore.put(key, upload.file, 'cache_tag', [])
        try:
            response = add_user_filestore_photo_view(context, request)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.body, one_pixel_jpeg)
        finally:
            filestore.clear()

class ShowProfileTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import show_profile_view
        return show_profile_view(context, request)

    def _registerTagbox(self):
        from karl.testing import registerTagbox
        registerTagbox()

    def _registerCatalogSearch(self):
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()

    def test_w_bad_photo(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        karltesting.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'userid'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context['communities'] = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        context['profiles']['userid'] = DummyProfile()
        dummyphoto = testing.DummyModel(title='photo')
        context['photo'] = dummyphoto # do *not* add IImage
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 4)
        self.failUnless(response['actions'][0][1].endswith(
                'userid/admin_edit_profile.html'))
        self.assertEqual(response['actions'][1][1], 'manage_communities.html')
        self.assertEqual(response['actions'][2][1], 'manage_tags.html')
        self.failUnless(response['profile']['photo']['url'].endswith(
                                                '/images/brokenImage.gif'))

    def test_editable(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        karltesting.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'userid'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context['communities'] = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        context['profiles']['userid'] = DummyProfile()
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 4)
        self.failUnless(response['actions'][0][1].endswith(
                'userid/admin_edit_profile.html'))
        self.assertEqual(response['actions'][1][1], 'manage_communities.html')
        self.assertEqual(response['actions'][2][1], 'manage_tags.html')

    def test_not_editable(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        karltesting.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'chris'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context.users.add("chris", "chrislogin", "password", [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['userid'] = DummyProfile()
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 2)
        self.failUnless(response['actions'][0][1].endswith(
                'chris/admin_edit_profile.html'))

    def test_communities(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from pyramid.testing import DummyModel
        from karl.testing import DummyCommunity
        from karl.testing import DummyUsers
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

        response = self._callFUT(context, request)
        self.assertEqual(response['communities'], [
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

        from pyramid.testing import DummyModel
        karltesting.registerDummySecurityPolicy(permissive=False)
        from karl.testing import DummyCommunity
        from karl.testing import DummyUsers
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

        response = self._callFUT(context, request)
        self.assertEqual(response['communities'], [])

    def test_tags(self):
        from karl.testing import DummyUsers
        self._registerTagbox()
        self._registerCatalogSearch()
        karltesting.registerDummySecurityPolicy('eddie')
        TAGS = {'beaver': 1, 'wally': 3}
        context = DummyProfile()
        context.title = "Eddie"
        context.__name__ = "eddie"
        context['communities'] = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        context['profiles']['eddie'] = DummyProfile()
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
        response = self._callFUT(context, request)

        self.assertEqual(len(response['tags']), 2)
        self.failUnless(response['tags'][0], {'name': 'wally', 'count': 3})
        self.failUnless(response['tags'][1], {'name': 'beaver', 'count': 1})

    def test_tags_capped_at_ten(self):
        from karl.testing import DummyUsers
        self._registerTagbox()
        self._registerCatalogSearch()
        karltesting.registerDummySecurityPolicy('eddie')
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
        context['communities'] = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        context['profiles']['eddie'] = DummyProfile()
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

        response = self._callFUT(context, request)
        self.assertEqual(len(response['tags']), 10)
        self.failUnless(response['tags'][0], {'name': 'kilo', 'count': 11})
        self.failUnless(response['tags'][1], {'name': 'juliet', 'count': 10})
        self.failUnless(response['tags'][9], {'name': 'bravo', 'count': 2})

    def test_show_recently_added(self):
        self._registerTagbox()

        search_args = {}
        def searcher(context):
            def search(**args):
                search_args.update(args)
                doc1 = testing.DummyModel(title='doc1')
                doc2 = testing.DummyModel(title='doc2')
                docids = [doc1, doc2]
                return len(docids), docids, lambda docid: docid
            return search
        from karl.models.interfaces import ISQLCatalogSearch
        from zope.interface import Interface
        karltesting.registerAdapter(searcher, (Interface,), ISQLCatalogSearch)
        from karl.models.interfaces import IGridEntryInfo
        karltesting.registerAdapter(
            DummyGridEntryAdapter, (Interface, Interface),
            IGridEntryInfo)

        from karl.testing import DummyUsers
        karltesting.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'chris'
        context.users = DummyUsers()
        context.users.add("userid", "userid", "password", [])
        context.users.add("chris", "chris", "password", [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['userid'] = DummyProfile()
        response = self._callFUT(context, request)
        self.assertEqual(search_args['limit'], 5)
        self.assertEqual(search_args['creator'], 'chris')
        self.assertEqual(search_args['sort_index'], 'creation_date')
        self.assertEqual(search_args['reverse'], True)
        self.assertEqual(len(response['recent_items']), 2)
        self.assertEqual(response['recent_items'][0].context.title, 'doc1')
        self.assertEqual(response['recent_items'][1].context.title, 'doc2')

    def test_system_user(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        karltesting.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'admin'
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context.users.add("chris", "chrislogin", "password", [])
        context['profiles'] = testing.DummyModel()
        context['profiles']['userid'] = DummyProfile()
        response = self._callFUT(context, request)
        self.assertEqual(len(response['actions']), 2)
        self.failUnless(response['actions'][0][1].endswith(
                'admin/admin_edit_profile.html'))

    def test_never_logged_in(self):
        self._registerTagbox()
        self._registerCatalogSearch()

        from karl.testing import DummyUsers
        request = testing.DummyRequest()
        context = DummyProfile()
        context.__name__ = 'userid'
        context.last_login_time = None
        context.users = DummyUsers()
        context.users.add("userid", "userlogin", "password", [])
        context['communities'] = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response['profile']['last_login_time'], None)


class ProfileThumbnailTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import profile_thumbnail
        return profile_thumbnail(context, request)

    def test_wo_photo(self):
        context = testing.DummyModel()
        rsp = self._callFUT(context, testing.DummyRequest())
        self.failUnless(rsp.location.startswith('http://example.com/static/'))
        self.failUnless(rsp.location.endswith('/images/defaultUser.gif'))

    def test_w_photo(self):
        from zope.interface import directlyProvides
        from karl.content.interfaces import IImage
        context = testing.DummyModel()
        photo = context['photo'] = testing.DummyModel()
        directlyProvides(photo, IImage)
        response = self._callFUT(context, testing.DummyRequest())
        self.assertEqual(response.location,
                         'http://example.com/photo/thumb/75x100.jpg')


class RecentContentTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import recent_content_view
        return recent_content_view(context, request)

    def test_without_content(self):
        context = DummyProfile()
        context.title = 'Z'
        request = testing.DummyRequest()
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()
        response = self._callFUT(context, request)
        self.assert_(response['api'] is not None)
        self.assertEquals(len(response['recent_items']), 0)
        self.assertFalse(response['batch_info']['batching_required'])

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
        from karl.models.interfaces import ISQLCatalogSearch
        from zope.interface import Interface
        karltesting.registerAdapter(searcher, (Interface), ISQLCatalogSearch)
        from karl.models.interfaces import IGridEntryInfo
        karltesting.registerAdapter(
            DummyGridEntryAdapter, (Interface, Interface),
            IGridEntryInfo)

        context = DummyProfile()
        context.title = 'Z'
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.assert_(response['api'] is not None)
        self.assertEquals(len(response['recent_items']), 2)
        self.assertEquals(response['recent_items'][0].context.title, 'doc1')
        self.assertEquals(response['recent_items'][1].context.title, 'doc2')
        self.assertFalse(response['batch_info']['batching_required'])

class ManageCommunitiesTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

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
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import manage_communities_view
        return manage_communities_view(context, request)

    def test_show_form(self):
        renderer = karltesting.registerDummyRenderer(
            'karl.views:templates/manage_communities.pt')
        karltesting.registerDummyRenderer(
            'karl.views:templates/formfields.pt')
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
        karltesting.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")

        request.params["form.cancel"] = "cancel"
        response = self._callFUT(self.profile, request)
        self.assertEqual("http://example.com/profiles/a/", response.location)

    def test_submit_alert_prefs(self):
        karltesting.registerDummyRenderer(
            'templates/manage_communities.pt')
        request = testing.DummyRequest(
            url="http://example.com/profiles/a/manage_communities.html")

        from karl.models.interfaces import IProfile
        request.params["form.submitted"] = "submit"
        request.params["alerts_pref_community1"] = str(IProfile.ALERT_NEVER)
        request.params["alerts_pref_community2"
                      ] = str(IProfile.ALERT_DAILY_DIGEST)
        request.params["alerts_pref_community3"
                      ] = str(IProfile.ALERT_WEEKLY_DIGEST)
        request.params["alerts_pref_community4"
                      ] = str(IProfile.ALERT_BIWEEKLY_DIGEST)

        self.assertEqual(IProfile.ALERT_IMMEDIATELY,
                         self.profile.get_alerts_preference("community1"))
        self.assertEqual(IProfile.ALERT_IMMEDIATELY,
                         self.profile.get_alerts_preference("community2"))
        self.assertEqual(IProfile.ALERT_IMMEDIATELY,
                         self.profile.get_alerts_preference("community3"))
        self.assertEqual(IProfile.ALERT_IMMEDIATELY,
                         self.profile.get_alerts_preference("community4"))

        response = self._callFUT(self.profile, request)

        self.assertEqual(IProfile.ALERT_NEVER,
                         self.profile.get_alerts_preference("community1"))
        self.assertEqual(IProfile.ALERT_DAILY_DIGEST,
                         self.profile.get_alerts_preference("community2"))
        self.assertEqual(IProfile.ALERT_WEEKLY_DIGEST,
                         self.profile.get_alerts_preference("community3"))
        self.assertEqual(IProfile.ALERT_BIWEEKLY_DIGEST,
                         self.profile.get_alerts_preference("community4"))
        self.assertEqual(
            "http://example.com/profiles/a/"
            "?status_message=Community+preferences+updated.",
            response.location)

    def test_leave_community(self):
        karltesting.registerDummyRenderer(
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
            "http://example.com/profiles/a/"
            "?status_message=Community+preferences+updated.",
            response.location)

    def test_leave_community_sole_moderator(self):
        karltesting.registerDummyRenderer(
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
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import show_profiles_view
        return show_profiles_view(context, request)

    def test_it(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ILetterManager
        from karl.models.adapters import CatalogSearch
        catalog = karltesting.DummyCatalog({1:'/foo', 2:'/bar'})
        karltesting.registerAdapter(CatalogSearch, (Interface), ICatalogSearch)
        karltesting.registerAdapter(DummyLetterManager, Interface,
                                    ILetterManager)
        context = testing.DummyModel()
        context.catalog = catalog
        foo = testing.DummyModel()
        karltesting.registerModels({'/foo':foo})
        request = testing.DummyRequest(
            params={'titlestartswith':'A'})
        renderer = karltesting.registerDummyRenderer('templates/profiles.pt')
        self._callFUT(context, request)
        profiles = list(renderer.profiles)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0], foo)

    def test_redirect(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = testing.DummyModel()
        context['people'] = testing.DummyModel()
        directlyProvides(context['people'], IPeopleDirectory)
        response = self._callFUT(context, testing.DummyRequest())
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location, 'http://example.com/people/')

class ChangePasswordFormControllerTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        karltesting.registerSettings()
        from karl.testing import DummyUsers
        # Set up dummy skel
        site = testing.DummyModel()
        site.users = DummyUsers()
        site['profiles'] = testing.DummyModel()
        self.site = site
        self.context = site['profiles']['profile'] = DummyProfile()
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self, context, request):
        from karl.views.people import ChangePasswordFormController
        return ChangePasswordFormController(context, request)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('old_password' in fields)
        self.failUnless('password' in fields)
        self.assertEqual(len(fields), 2)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('old_password' in widgets)
        self.failUnless('password' in widgets)
        self.assertEqual(len(widgets), 2)

    def test___call__(self):
        controller = self._makeOne(self.context, self.request)
        karltesting.registerLayoutProvider()
        karltesting.registerDummyRenderer(
            'karl.views:forms/templates/snippets.pt')
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Change Password')
        self.failUnless('layout' in response)
        self.failUnless('actions' in response)
        self.failIf(response['actions'])
        self.failUnless('blurb_macro' in response)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location,
                         'http://example.com/profiles/profile/')

    def test_handle_submit_normal(self):
        # first create the fake user
        users = self.site.users
        users.add('profile', 'profile', 'oldoldold', [])
        # now dress up the profile object a bit
        profile = self.site['profiles']['profile']
        profile.title = 'Pro File'
        profile.email = 'profile@example.com'
        converted = {'old_password': 'oldoldold',
                     'password': 'newnewnew',
                     }

        controller = self._makeOne(self.context, self.request)
        response = controller.handle_submit(converted)

        from repoze.who.plugins.zodb.users import get_sha_password
        new_enc = get_sha_password('newnewnew')
        self.assertEqual(users.get_by_id('profile')['password'], new_enc)
        self.assertEqual(response.location,
            'http://example.com/profiles/profile/'
            '?status_message=Password%20changed')


class TestDeactivateProfileView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.people import deactivate_profile_view
        return deactivate_profile_view(context, request)

    def test_noconfirm(self):
        context = DummyProfile(firstname='Mori', lastname='Turi')
        context.title = 'Context'
        request = testing.DummyRequest()
        karltesting.registerDummyRenderer(
            'templates/deactivate_profile.pt')
        response = self._callFUT(context, request)
        self.assertEqual(sorted(response.keys()), ['api', 'myself'])

    def test_confirm_no_user_matching_profile(self):
        from karl.testing import DummyUsers
        from repoze.workflow.testing import registerDummyWorkflow
        parent = testing.DummyModel()
        users = parent.users = DummyUsers()
        # Simulate a profile which has no corresponding user.
        def _raise_KeyError(name):
            users.removed_users.append(name)
            raise KeyError(name)
        users.remove = _raise_KeyError
        workflow = registerDummyWorkflow('security')
        context = DummyProfile(firstname='Mori', lastname='Turi')
        parent['profiles'] = testing.DummyModel()
        parent['profiles']['userid'] = context
        karltesting.registerDummySecurityPolicy('user', ('group.KarlAdmin',))
        request = testing.DummyRequest(params={'confirm':'1'})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location,
                         'http://example.com/profiles/?status_message='
                         'Deactivated+user+account%3A+userid')
        self.assertEqual(users.removed_users, ['userid'])
        self.assertEqual(workflow.transitioned, [{
            'to_state': 'inactive', 'content': context,
            'request': request, 'guards': (),
            'context': None, 'skip_same': True}])

    def test_confirm_not_deleting_own_profile(self):
        from karl.testing import DummyUsers
        from repoze.workflow.testing import registerDummyWorkflow
        parent = testing.DummyModel()
        users = parent.users = DummyUsers()
        workflow = registerDummyWorkflow('security')
        context = DummyProfile(firstname='Mori', lastname='Turi')
        parent['profiles'] = testing.DummyModel()
        parent['profiles']['userid'] = context
        karltesting.registerDummySecurityPolicy('user', ('group.KarlAdmin',))
        request = testing.DummyRequest(params={'confirm':'1'})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location,
                         'http://example.com/profiles/?status_message='
                         'Deactivated+user+account%3A+userid')
        self.assertEqual(users.removed_users, ['userid'])
        self.assertEqual(workflow.transitioned, [{
            'to_state': 'inactive', 'content': context,
            'request': request, 'guards': (),
            'context': None, 'skip_same': True}])

    def test_confirm_deleting_own_profile(self):
        from karl.testing import DummyUsers
        from repoze.workflow.testing import registerDummyWorkflow
        parent = testing.DummyModel()
        users = parent.users = DummyUsers()
        workflow = registerDummyWorkflow('security')
        context = DummyProfile(firstname='Mori', lastname='Turi')
        parent['profiles'] = testing.DummyModel()
        parent['profiles']['userid'] = context
        karltesting.registerDummySecurityPolicy('userid')
        request = testing.DummyRequest(params={'confirm':'1'})
        request.context = context

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location,
            'http://example.com/login.html?reason=User+removed')
        self.assertEqual(users.removed_users, ['userid'])
        self.assertEqual(workflow.transitioned, [{
            'to_state': 'inactive', 'content': context,
            'request': request, 'guards': (),
            'context': None, 'skip_same': True}])

class TestReactivateProfileView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        self.reset_password_calls = []

    def tearDown(self):
        testing.cleanUp()

    def _dummy_reset_password(self, user, profile, request):
        self.reset_password_calls.append((user, profile, request))

    def _callFUT(self, context, request):
        from karl.views.people import reactivate_profile_view as fut
        return fut(context, request, self._dummy_reset_password)

    def test_noconfirm(self):
        context = DummyProfile(firstname='Mori', lastname='Turi')
        context.title = 'Context'
        request = testing.DummyRequest()
        karltesting.registerDummyRenderer(
            'templates/reactivate_profile.pt')
        response = self._callFUT(context, request)
        self.assertEqual(sorted(response.keys()), ['api'])

    def test_confirm(self):
        from karl.testing import DummyUsers
        from repoze.workflow.testing import registerDummyWorkflow
        parent = testing.DummyModel()
        users = parent.users = DummyUsers()
        workflow = registerDummyWorkflow('security')
        context = DummyProfile()
        parent['userid'] = context
        karltesting.registerDummySecurityPolicy('admin')
        request = testing.DummyRequest(params={'confirm':'1'})

        response = self._callFUT(context, request)

        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location,
                         'http://example.com/userid/?status_message='
                         'Reactivated+user+account%3A+userid')
        self.assertEqual(users.added[0], 'userid')
        self.assertEqual(users.added[1], 'userid')
        self.assertEqual(users.added[3], [])
        self.assertEqual(workflow.transitioned, [{
            'to_state': 'active', 'content': context,
            'request': request, 'guards': (),
            'context': None, 'skip_same': True}])
        self.assertEqual(
            self.reset_password_calls,
            [(users.get_by_id('userid'), context, request)])

class DummyImageFile(object):
    def __init__(self, title=None, stream=None, mimetype=None, filename=None,
                 creator=None):
        self.title = title
        self.mimetype = mimetype
        if stream is not None:
            self.data = stream.read()
        else:
            self.data = one_pixel_jpeg
        self.size = len(self.data)
        self.filename= filename
        self.creator = creator
        self.is_image = mimetype != 'x-application/not a jpeg'

one_pixel_jpeg = [
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

one_pixel_jpeg = ''.join([chr(x) for x in one_pixel_jpeg])
