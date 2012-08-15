import binascii

from zope.interface import implements

from paste.httpheaders import AUTHORIZATION
from paste.httpheaders import WWW_AUTHENTICATE

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Everyone
from pyramid.security import Authenticated

from repoze.who.plugins.zodb.users import get_sha_password
from karl.utils import find_users


def _get_basicauth_credentials(request):
    if 'HTTP_AUTHORIZATION' not in request.environ:
        return None

    authorization = AUTHORIZATION(request.environ)
    try:
        authmeth, auth = authorization.split(' ', 1)
    except ValueError: # not enough values to unpack
        return None
    if authmeth.lower() == 'basic':
        try:
            auth = auth.strip().decode('base64')
        except binascii.Error: # can't decode
            return None
        try:
            login, password = auth.split(':', 1)
        except ValueError: # not enough values to unpack
            return None
        return {'login':login, 'password':password}

    return None


def _check(credentials, request):
    login, password = credentials['login'], credentials['password']
    users = find_users(request.context)
    user = users.get(login=login)
    if user is None or user['password'] != get_sha_password(password):
        return None
    return [user['id']] + list(user['groups'])


class BasicAuthenticationPolicy(object):
    """ A :app:`Pyramid` :term:`authentication policy` which
    obtains data from basic authentication headers.

    Constructor Arguments

    ``check``

        A callback passed the credentials and the request,
        expected to return None if the userid doesn't exist or a sequence
        of group identifiers (possibly empty) if the user does exist.
        Required.

    ``realm``

        Default: ``Realm``.  The Basic Auth realm string.

    """
    implements(IAuthenticationPolicy)

    def __init__(self, check=_check, realm='Realm'):
        self.check = check
        self.realm = realm

    def authenticated_userid(self, request):
        credentials = _get_basicauth_credentials(request)
        if credentials is None:
            return None
        principals = self.check(credentials, request)
        if principals is not None: # is not None!
            return principals[0]

    def effective_principals(self, request):
        effective_principals = [Everyone]
        credentials = _get_basicauth_credentials(request)
        if credentials is None:
            return effective_principals
        principals = self.check(credentials, request)
        if principals is None: # is None!
            return effective_principals
        effective_principals.append(Authenticated)
        effective_principals.extend(principals)
        return effective_principals

    def unauthenticated_userid(self, request):
        creds = _get_basicauth_credentials(request)
        if creds is not None:
            return creds['login']
        return None

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
        return head
