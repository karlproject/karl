import mock
import StringIO
import unittest

from pyramid import testing


class UserSyncTests(unittest.TestCase):

    def setUp(self):
        self.context = context = testing.DummyResource()
        context.users = mock.Mock()
        context['profiles'] = testing.DummyResource()

    def make_one(self):
        from karl.utilities.usersync import UserSync as test_class
        return test_class(self.context)

    @mock.patch('karl.utilities.usersync.urllib2')
    def test_download_userdata(self, urllib2):
        urllib2.urlopen.return_value = StringIO.StringIO('"TEST"')
        testobj = self.make_one()
        self.assertEqual(testobj.download_userdata('URL'), 'TEST')
        urllib2.urlopen.assert_called_once_with('URL')

    @mock.patch('karl.utilities.usersync.urllib2')
    @mock.patch('karl.utilities.usersync.base64.encodestring',
                lambda s: 'base64:' + s)
    def test_download_userdata_with_credentials(self, urllib2):
        urllib2.urlopen.return_value = StringIO.StringIO('"TEST"')
        testobj = self.make_one()
        self.assertEqual(
            testobj.download_userdata('URL', 'user', 'password'),
            'TEST')
        urllib2.Request.assert_called_once_with('URL')
        request = urllib2.urlopen.call_args[0][0]
        request.add_header.assert_called_once_with(
            "Authorization", "Basic base64:user:password")

    def test_download_userdata_with_timestamp(self):
        pass

    @mock.patch('karl.utilities.usersync.create_content')
    def test_syncusers_create_user(self, create_content):
        from karl.models.interfaces import IProfile
        data = {'users': [
            {'username': 'fred',
             'firstname': 'Fred',
             'lastname': 'Flintstone',
             'email': 'fred@bedrock',
             'password': 'SHA1:gobbledygook',
             'login': 'mrfred',
             'groups': ['group.People', 'group.Prehistoric'],
             'phone': '919-555-1212',
             'extension': '23',
             'fax': '818-555-1212',
             'department': 'digging',
             'position': 'digger',
             'organization': 'Diggers',
             'location': 'Bedrock',
             'country': 'Pangea',
             'websites': ['http://bedrock.test'],
             'languages': ['human', 'dinosaur'],
             'office': '000',
             'room_no': '111',
             'biography': 'Born along time ago.',
             'date_format': 'en_OLD',
             'home_path': '/offices/bedrock'}
        ]}
        testobj = self.make_one()
        testobj.sync(data)
        self.context.users.add.assert_called_once_with(
            'fred', 'mrfred', 'SHA1:gobbledygook',
            ['group.People', 'group.Prehistoric'], encrypted=True)
        fred = self.context['profiles']['fred']
        self.assertEqual(fred.firstname, 'Fred')
        self.assertEqual(fred.lastname, 'Flintstone')
        self.assertEqual(fred.email, 'fred@bedrock')
        self.assertEqual(fred.phone, '919-555-1212')
        self.assertEqual(fred.extension, '23')
        self.assertEqual(fred.fax, '818-555-1212')
        self.assertEqual(fred.department, 'digging')
        self.assertEqual(fred.organization, 'Diggers')
        self.assertEqual(fred.location, 'Bedrock')
        self.assertEqual(fred.country, 'Pangea')
        self.assertEqual(fred.websites, ['http://bedrock.test'])
        self.assertEqual(fred.languages, ['human', 'dinosaur'])
        self.assertEqual(fred.office, '000')
        self.assertEqual(fred.room_no, '111')
        self.assertEqual(fred.biography, 'Born along time ago.')
        self.assertEqual(fred.date_format, 'en_OLD')
        self.assertEqual(fred.home_path, '/offices/bedrock')
        create_content.assert_called_once_with(IProfile)

    @mock.patch('karl.utilities.usersync.objectEventNotify')
    def test_sync_users_update(self, notify):
        data = {'users': [
            {'username': 'fred',
             'login': 'flintstone',
             'email': 'flintstone@bedrock'}
        ]}
        self.context['profiles']['fred'] = fred = mock.Mock(
            security_state='active')
        self.context.users.get.return_value = {
            'login': 'fred',
            'groups': [],
            'password': 'SHA1:gobbledygook'
        }
        testobj = self.make_one()
        testobj.sync(data)
        self.assertEqual(fred.email, 'flintstone@bedrock')
        self.context.users.get.assert_called_once_with('fred')
        self.context.users.add.assert_called_once_with(
            'fred', 'flintstone', 'SHA1:gobbledygook', [], encrypted=True)
        self.assertEquals(notify.call_count, 2)

    def test_sync_users_deactivate_user(self):
        pass

    def test_sync_users_reactivate_user(self):
        pass

    def test_sync_users_community_memberships(self):
        pass

    def test_sync_users_make_community_moderator(self):
        pass

    def test_sync_users_deactivate_missing(self):
        pass
