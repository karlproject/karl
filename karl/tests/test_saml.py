import mock
import unittest

from pyramid import testing


class TestIdentityProvider(unittest.TestCase):

    def make_one(self):
        from karl.saml import IdentityProvider
        idp = IdentityProvider({
            'name': 'Testing',
            'metadata': {'foo': 'bar'},
        })
        return idp

    @mock.patch('karl.saml.Saml2Config')
    @mock.patch('karl.saml.Saml2Client')
    def test_username_from_callback(self, Client, Config):
        client = Client.return_value
        authn_response = client.parse_authn_request_response.return_value
        authn_response.get_subject.return_value.text = 'Mr. Fred'
        idp = self.make_one()
        request = mock.Mock(params={'SAMLResponse': 'He is Mr. Fred'})
        request.route_url.return_value = 'https://example.com/saml/whatever'
        self.assertEqual(idp.username_from_callback(request), 'Mr. Fred')

    @mock.patch('karl.saml.Saml2Config')
    @mock.patch('karl.saml.Saml2Client')
    def test_username_from_callback_no_saml_response(self, Client, Config):
        from pyramid.httpexceptions import HTTPBadRequest
        client = Client.return_value
        authn_response = client.parse_authn_request_response.return_value
        authn_response.get_subject.return_value.text = 'Mr. Fred'
        idp = self.make_one()
        request = mock.Mock(params={})
        request.route_url.return_value = 'https://example.com/saml/whatever'
        with self.assertRaises(HTTPBadRequest):
            idp.username_from_callback(request)


class TestCallback(unittest.TestCase):

    def call_fut(self, context, request):
        from karl.saml import callback
        return callback(context, request)

    @mock.patch('repoze.folder.objectEventNotify', mock.Mock())
    @mock.patch('karl.saml.login_user')
    def test_it(self, login_user):
        from karl.models.profile import ProfilesFolder, Profile
        root = testing.DummyResource()
        root['profiles'] = profiles = ProfilesFolder()
        profiles['bob'] = profile = Profile()
        profile.sso_id = 'bobs your uncle'

        idp = mock.Mock()
        idp.username_from_callback.return_value = 'bobs your uncle'
        request = mock.Mock(matchdict={'idp': 'nsa'})
        request.registry.identity_providers = {'nsa': idp}
        response = self.call_fut(root, request)
        assert response is login_user.return_value
        login_user.assert_called_once_with(
            request, profile, 'bobs your uncle', 'bob')

    @mock.patch('repoze.folder.objectEventNotify', mock.Mock())
    @mock.patch('karl.saml.login_user')
    def test_it_no_match(self, login_user):
        from karl.models.profile import ProfilesFolder, Profile
        root = testing.DummyResource()
        root['profiles'] = profiles = ProfilesFolder()
        profiles['bob'] = profile = Profile()
        profile.sso_id = 'bobs your uncle'

        idp = mock.Mock()
        idp.username_from_callback.return_value = 'bobs your auant'
        request = mock.Mock(matchdict={'idp': 'nsa'})
        request.registry.identity_providers = {'nsa': idp}
        response = self.call_fut(root, request)
        assert response.status_int == 302
        login_user.assert_not_called()
