import logging
import kerberos

from pyramid.httpexceptions import HTTPUnauthorized

from karl.utils import find_users

log = logging.getLogger(__name__)

SERVICE = 'HTTP'
SCHEME = 'Negotiate'

def get_kerberos_userid(request):
    if not request.authorization:
        if 'challenge' in request.params:
            raise HTTPUnauthorized(headers={'WWW-Authenticate': 'Negotiate'})
        return None

    settings = request.registry.settings
    remove_realm = settings.get('kerberos.remove_realm', True)
    remove_domain = settings.get('kerberos.remove_domain', True)

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

    # strip off the realm and domain
    realm = domain = None
    working = principal
    if '@' in principal:
        working, realm = working.split('@')
        if remove_realm:
            principal = working
    if '//' in working:
        working, domain = working.split('\\')
        if remove_domain:
            principal = working

    # Require user to be in the system
    users = find_users(request.context)
    user = users.get(login=principal)
    if user:
        return user['id']
