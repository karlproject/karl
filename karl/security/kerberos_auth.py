import logging
import sys

from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.util import DottedNameResolver

from karl.utils import find_users

try:
    import kerberos
    kerberos # stfu pyflakes
except ImportError:
    # Kerberos is an optional component. This module won't work if Kerberos
    # isn't available, but is still testable via unittests using mock.
    kerberos = None

log = logging.getLogger(__name__)

SERVICE = 'HTTP'
SCHEME = 'Negotiate'

resolve_dotted_name = DottedNameResolver(sys.modules[__name__]).resolve


def get_kerberos_userid(request):
    if not request.authorization or request.authorization[0] != 'Negotiate':
        if 'challenge' in request.params:
            raise HTTPUnauthorized(headers={'WWW-Authenticate': 'Negotiate'})
        return None

    ticket = request.authorization[1]
    log.debug("Kerberos ticket received: %s" % ticket)

    result, context = kerberos.authGSSServerInit(SERVICE)
    if result != 1:
        log.error("Could not initialize Kerberos GSS service.")
        return None

    try:
        if not kerberos.authGSSServerStep(context,ticket) == 1:
            return None
    except kerberos.GSSError, e:
        log.error("%s: GSSError %s" % (request.remote_addr, e))
        return None

    principal = kerberos.authGSSServerUserName(context)
    kerberos.authGSSServerClean(context)

    settings = request.registry.settings

    # Get domain and realm from principal
    realm = domain = None
    userid = principal
    if '@' in principal:
        userid, realm = userid.split('@')
    if '\\' in userid:
        userid, domain = userid.split('\\')

    # Do domain and realm checking
    allowed_realms = settings.get('kerberos.allowed_realms')
    if allowed_realms:
        allowed_realms = allowed_realms.split()
        if realm not in allowed_realms:
            return None
    allowed_domains = settings.get('kerberos.allowed_domains')
    if allowed_domains:
        allowed_domains = allowed_domains.split()
        if domain not in allowed_domains:
            return None

    # Look up Karl user based on kerberos principal
    credentials = {
        'principal': principal,
        'userid': userid,
        'realm': realm,
        'domain': domain}
    dotted_name = settings.get('kerberos.user_finder')
    if dotted_name:
        user_finder = resolve_dotted_name(dotted_name)
    else:
        user_finder = mapping_user_finder # default

    user = user_finder(request, credentials)
    if user:
        return user['id']


def login_user_finder(request, credentials):
    users = find_users(request.context)
    return users.get(login=credentials['userid'])


def mapping_user_finder(request, credentials):
    users = find_users(request.context)
    if hasattr(users, 'sso_map'):
        userid = users.sso_map.get(credentials['principal'])
        if userid:
            return users.get(userid=userid)
