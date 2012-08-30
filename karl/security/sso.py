import logging
import sys

from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import HTTPFound
from pyramid.util import DottedNameResolver
from pyramid.view import view_config

from karl.models.interfaces import IProfile
from karl.models.interfaces import ICatalogSearch
from karl.utils import find_users
from karl.views.login import remember_login

resolve_dotted_name = DottedNameResolver(sys.modules[__name__]).resolve

log = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings
    sso = settings.get('sso', None)
    if not sso:
        return

    for name in sso.split():
        prefix = 'sso.%s.' % name
        provider = settings.get('%sprovider' % prefix)

        if provider == 'github':
            config.include('velruse.providers.github')
            config.add_github_login_from_settings(prefix=prefix)

        elif provider == 'google':
            config.include('velruse.providers.google')
            config.add_google_login(
                realm=settings['%srealm' % prefix],
                consumer_key=settings['%sconsumer_key' % prefix],
                consumer_secret=settings['%sconsumer_secret' % prefix])

        elif provider == 'yahoo':
            config.include('velruse.providers.yahoo')
            config.add_yahoo_login(
                realm=settings['%srealm' % prefix],
                consumer_key=settings['%sconsumer_key' % prefix],
                consumer_secret=settings['%sconsumer_secret' % prefix])

        elif provider == 'yasso':
            config.include('karl.security.sso_yasso')
            config.add_yasso_login_from_settings(prefix=prefix)

        else:
            raise ValueError("Unknown SSO provider: %s" % provider)

    config.scan('karl.security.sso')


@view_config(context='velruse.AuthenticationComplete')
def sso_login_success(context, request):
    # Velruse has replaced our root factory with something that returns a
    # context that isn't related at all to Karl content, so we have to get
    # back our root_factory and call it to talk to the ZODB.
    registry = request.registry
    root_factory = registry.queryUtility(IRootFactory)
    site = root_factory(request)
    settings = registry.settings
    dotted_name = settings.get('sso_user_finder')
    if dotted_name:
        user_finder = resolve_dotted_name(dotted_name)
    else:
        user_finder = mapping_user_finder
    user = user_finder(site, context)
    if user:
        max_age = None # XXX Interact with 'keep me logged in' in login form?
        came_from = request.application_url # XXX Use session to stash
        return remember_login(site, request, user['id'], max_age, came_from)

    return HTTPFound(request.resource_url(site, 'login.html', query={
        'reason': "Credentials from provider don't match credentials in %s" %
        settings.get('system_name', 'KARL')}))


@view_config(context='velruse.AuthenticationDenied')
def sso_login_failure(request):
    root_factory = request.registry.queryUtility(IRootFactory)
    site = root_factory(request)
    return HTTPFound(request.resource_url(site, 'login.html', query={
        'reason': "Authentication failed at external provider."}))


def verified_email_user_finder(site, context):
    email = context.profile.get('verifiedEmail')
    if not email:
        return None

    search = ICatalogSearch(site)
    count, docids, resolver = search(interfaces=[IProfile], email=email)
    if not count:
        return None
    if count > 1:
        log.warn('Unable to authenticate ambiguous email address: %s' % email)
        return None
    profile = resolver(docids[0])
    users = find_users(site)
    return users.get(profile.__name__)


def login_user_finder(site, context):
    users = find_users(site)
    return users.get(login=context.profile.get('userid'))


def mapping_user_finder(site, context):
    users = find_users(site)
    if hasattr(users, 'sso_map'):
        userid = users.sso_map.get(context.profile.get('userid'))
        if userid:
            return users.get(userid=userid)
