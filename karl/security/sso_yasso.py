from urlparse import parse_qs

import requests

from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED

from velruse.api import (
    AuthenticationComplete,
    register_provider,
)
from velruse.settings import ProviderSettings

from base64 import urlsafe_b64encode
from pyramid.httpexceptions import HTTPBadRequest
from urllib import urlencode
import json
import os
import time


class YassoAuthenticationComplete(AuthenticationComplete):
    """
    Yasso auth complete
    """


def includeme(config):
    config.add_directive('add_yasso_login', add_yasso_login)
    config.add_directive('add_yasso_login_from_settings',
                         add_yasso_login_from_settings)


def add_yasso_login_from_settings(config, prefix):
    settings = config.registry.settings
    p = ProviderSettings(settings, prefix)
    p.update('authorize_url', required=True)
    p.update('token_url', required=True)
    p.update('userinfo_url', required=True)
    p.update('client_id', required=True)
    p.update('client_secret', required=True)
    p.update('login_path')
    p.update('callback_path')
    p.update('name')
    config.add_yasso_login(**p.kwargs)


def add_yasso_login(config,
                    authorize_url,
                    token_url,
                    userinfo_url,
                    client_id,
                    client_secret,
                    login_path='/login/yasso',
                    callback_path='/login/yasso/callback',
                    name='yasso'):
    """
    Add a Yasso login provider to the application.
    """
    provider = YassoProvider(name, authorize_url, token_url, userinfo_url,
                             client_id, client_secret)

    config.add_route(provider.login_route, login_path)
    config.add_view(provider, attr='login', route_name=provider.login_route,
                    permission=NO_PERMISSION_REQUIRED)

    config.add_route(provider.callback_route, callback_path,
                     use_global_views=True,
                     factory=provider.callback)

    register_provider(config, name, provider)


class YassoProvider(object):
    def __init__(self, name, authorize_url, token_url, userinfo_url, client_id,
                 client_secret):
        self.name = name
        self.type = 'yasso'
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url
        self.client_id = client_id
        self.client_secret = client_secret

        self.login_route = 'velruse.%s-login' % name
        self.callback_route = 'velruse.%s-callback' % name
        self.session_prefix = 'yasso_velruse.%s.' % name

    def login(self, request):
        """
        Redirect to the Yasso server for login.
        """
        authorize_url = self.authorize_url
        client_id = self.client_id
        redirect_uri = request.route_url(self.callback_route)
        state = urlsafe_b64encode(os.urandom(16))
        request.session[self.session_prefix + 'state'] = state

        q = urlencode([
            ('client_id', client_id),
            ('redirect_uri', redirect_uri),
            ('state', state),
            ('response_type', 'code'),
        ])
        location = '{0}?{1}'.format(authorize_url, q)
        headers = [('Cache-Control', 'no-cache')]
        return HTTPFound(location=location, headers=headers)

    def callback(self, request):
        """
        Receive an authorization code and return user credentials.
        """
        code = request.params.get('code')
        state = request.params.get('state')
        if not code or not state:
            return HTTPBadRequest("Missing code or state parameters")

        session = request.session
        session_state = session.get(self.session_prefix + 'state')
        if session_state != state:
            # CSRF protection
            return HTTPBadRequest(body="Incorrect state value")

        userinfo = self._get_userinfo(request, code)

        # Setup the "normalized" contact info
        profile = {'userid': userinfo['userid']}
        return YassoAuthenticationComplete(profile=profile,
                                           credentials={},
                                           provider_name=self.name,
                                           provider_type=self.type)

    def _get_userinfo(self, request, code):
        """
        Use an authorization code to get an access token.  Then use the access
        token to get user info.
        """
        token_url = self.token_url
        client_id = self.client_id
        client_secret = self.client_secret

        redirect_uri = request.route_url(self.callback_route)
        verify = token_url.startswith('https')
        r = requests.post(token_url, auth=(client_id, client_secret), data={
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code,
        }, verify=verify)
        r.raise_for_status()
        token_response = json.loads(r.content)
        access_token = token_response['access_token']

        userinfo_url = self.userinfo_url
        verify = userinfo_url.startswith('https')
        r = requests.post(userinfo_url, data={'access_token': access_token},
            verify=verify)
        r.raise_for_status()
        return json.loads(r.content)
