import mock
import unittest


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
