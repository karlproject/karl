import mock
import unittest

from zope.testing.cleanup import cleanUp

from pyramid import testing
from karl import testing as karltesting
from karl.testing import DummySessions

class DummyForm(object):
    errors = {}

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
    'websites': ['http://example.com'],
    'languages': 'englishy',
    'photo': None,
    'biography': 'Interesting Person',
    }

class DummyProfile(testing.DummyModel):
    websites = ()
    date_format = 'XY'
    def __setitem__(self, name, value):
        """Simulate Folder behavior"""
        if self.get(name, None) is not None:
            raise KeyError(u"An object named %s already exists" % name)
        testing.DummyModel.__setitem__(self, name, value)

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
