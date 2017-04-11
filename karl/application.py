import datetime
import json
import os
import sys
import time

from ZODB.POSException import ReadOnlyError

from zope.component import queryUtility

from repoze.depinj import lookup

import transaction

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import RepozeWho1AuthenticationPolicy
from pyramid.events import NewRequest
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.httpexceptions import HTTPNotFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig as Session
from pyramid.util import DottedNameResolver

from pyramid_multiauth import MultiAuthenticationPolicy
from pyramid_jwtauth import JWTAuthenticationPolicy
from pyramid_zodbconn import get_connection

from karl.authorization import RestrictedACLAuthorizationPolicy
from karl.bootstrap.interfaces import IBootstrapper
from karl.debugload import RootCreated
from karl.models.site import get_weighted_textrepr
from karl.security.basicauth import BasicAuthenticationPolicy
from karl.textindex import KarlPGTextIndex
from karl.utils import find_users
from karl.utils import asbool

try:
    import pyramid_debugtoolbar
    pyramid_debugtoolbar  # pyflakes stfu
except ImportError:
    pyramid_debugtoolbar = None


try:
    import perfmetrics
    perfmetrics  # ode to pyflakes
except ImportError:
    perfmetrics = None


try:
    import slowlog
    slowlog  # ode to pyflakes
except ImportError:
    slowlog = None


def configure_karl(config, load_zcml=True):
    # Authorization/Authentication policies
    settings = config.registry.settings
    authentication_policy = MultiAuthenticationPolicy([
        JWTAuthenticationPolicy.from_settings(settings),
        AuthTktAuthenticationPolicy(
            settings['who_secret'],
            callback=group_finder,
            cookie_name=settings['who_cookie']),
        # for b/w compat with bootstrapper
        RepozeWho1AuthenticationPolicy(callback=group_finder),
        BasicAuthenticationPolicy(),
        ])
    config.set_authorization_policy(RestrictedACLAuthorizationPolicy())
    config.set_authentication_policy(authentication_policy)

    # Static tree revisions routing
    static_rev = settings.get('static_rev')
    if not static_rev:
        static_rev = _guess_static_rev()
        settings['static_rev'] = static_rev
    config.add_static_view('/static/%s' % static_rev, 'karl.views:static',
        cache_max_age=60 * 60 * 24 * 365)
    # Add a redirecting static view to all _other_ revisions.
    def _expired_static_predicate(info, request):
        # We add a redirecting route to all static/*,
        # _except_ if it starts with the active revision segment.
        path = info['match']['path']
        return path and path[0] != static_rev
    config.add_route('expired-static', '/static/*path',
        custom_predicates=(_expired_static_predicate, ))

    # Need a session if using Velruse
    config.set_session_factory(Session(settings['who_secret']))

    config.include('karl.debugload')
    config.include('karl.underprofile')

    if load_zcml:
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml('standalone.zcml')

    debug = asbool(settings.get('debug', 'false'))
    if not debug:
        config.add_view('karl.errorpage.errorpage', context=Exception,
                        renderer="karl.views:templates/errorpage.pt")
        config.add_view('karl.errorpage.errorpage', context=HTTPNotFound,
                        renderer="karl.views:templates/errorpage.pt")
        config.add_view('karl.errorpage.errorpage', context=NotFound,
                        renderer="karl.views:templates/errorpage.pt")
        config.add_view('karl.errorpage.errorpage', context=ReadOnlyError,
                        renderer="karl.views:templates/errorpage.pt")

    debugtoolbar = asbool(settings.get('debugtoolbar', 'false'))
    if debugtoolbar and pyramid_debugtoolbar:
        config.include(pyramid_debugtoolbar)

    config.add_subscriber(block_webdav, NewRequest)

    # override renderer for jwtauth requests
    config.add_renderer(name='karl_json', factory=karl_json_renderer_factory)
    config.add_subscriber(jwtauth_override, NewRequest)

    if slowlog is not None:
        config.include(slowlog)

    if perfmetrics is not None:
        config.include(perfmetrics)

    if 'intranet_search_paths' in settings:
        settings['intranet_search_paths'] = settings[
            'intranet_search_paths'].split()
    else:
        settings['intranet_search_paths'] = ('/profiles', '/offices')

    # admin5 Admin UI
    config.include('admin5')
    config.include('karl.box')

    # SSO
    config.include('karl.saml')

    # Login tracking
    config.include('karl.login_tracker')


def block_webdav(event):
    """
    Microsoft Office will now cause Internet Explorer to attempt to open Word
    Docs using WebDAV when viewing Word Docs in the browser.  It is imperative
    that we disavow any knowledge of WebDAV to prevent IE from doing insane
    things.

    http://serverfault.com/questions/301955/
    """
    if event.request.method in ('PROPFIND', 'OPTIONS'):
        raise HTTPMethodNotAllowed(event.request.method)


def jwtauth_override(event):
    request = event.request
    if ('authorization' in request.headers and
            'JWT token' in request.headers['authorization']):
        request.override_renderer = 'karl_json'
        return True


def karl_json_renderer_factory(info):
    def _render(value, system):

        def _to_json(obj):
            try:
                result = obj.__to_json__()
            except AttributeError:
                result = {'__class__': obj.__class__.__name__}
            return result

        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'application/json'
        return json.dumps(value, default=_to_json)
    return _render


def group_finder(identity, request):
    # Might be repoze.who policy which uses an identity dict
    if isinstance(identity, dict):
        return identity['groups']

    # Might be cached
    user = request.environ.get('karl.identity')
    if user is None:
        users = find_users(request.context)
        user = users.get(identity)
    if user is None:
        return None
    request.environ['karl.identity'] = user # cache for later
    return user['groups']


def _guess_static_rev():
    """Guess an appropriate static revision number.

    This is only used when no deployment tool set the static_rev
    for us.  Deployment tools should set static_rev because
    karl can only guess what static revisions are appropriate,
    while deployment tools can set a system-wide revision number
    that encompasses all relevant system changes.
    """
    # If Karl is installed as an egg, we can try to get the Karl version
    # number from the egg and use that.
    _static_rev = _get_egg_rev()

    if _static_rev is not None:
        return _static_rev

    # Fallback to just using a timestamp.  This is guaranteed not to fail
    # but will create different revisions for each process, resulting in
    # some extra static resource downloads
    _static_rev = 'r%d' % int(time.time())

    return _static_rev


def _get_egg_rev():
    # Find folder that this module is contained in
    module = sys.modules[__name__]
    path = os.path.dirname(os.path.abspath(module.__file__))

    # Walk up the tree until we find the parent folder of an EGG-INFO folder.
    while path != '/':
        egg_info = os.path.join(path, 'EGG-INFO')
        if os.path.exists(egg_info):
            rev = os.path.split(path)[1]
            return 'r%d' % hash(rev)
        path = os.path.dirname(path)


def root_factory(request, name='site'):
    connstats_file = request.registry.settings.get(
        'connection_stats_filename')
    connstats_threshhold = float(request.registry.settings.get(
        'connection_stats_threshhold', 0))
    def finished(request):
        # closing the primary also closes any secondaries opened
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = time.time() - before
        if elapsed > connstats_threshhold:
            loads_after, stores_after = connection.getTransferCounts()
            loads = loads_after - loads_before
            stores = stores_after - stores_before
            with open(connstats_file, 'a', 0) as f:
                f.write('"%s", "%s", "%s", %f, %d, %d\n' %
                           (now,
                            request.method,
                            request.path_url,
                            elapsed,
                            loads,
                            stores,
                           )
                       )
                f.flush()

    # NB: Finished callbacks are executed in the order they've been added
    # to the request.  pyramid_zodbconn's ``get_connection`` registers a
    # finished callback which closes the ZODB database.  Because the
    # finished callback it registers closes the database, we need it to
    # execute after the "finished" function above.  As a result, the above
    # call to ``request.add_finished_callback`` *must* be executed before
    # we call ``get_connection`` below.

    # Rationale: we want the call to getTransferCounts() above to happen
    # before the ZODB database is closed, because closing the ZODB database
    # has the side effect of clearing the transfer counts (the ZODB
    # activity monitor clears the transfer counts when the database is
    # closed).  Having the finished callbacks called in the "wrong" order
    # will result in the transfer counts being cleared before the above
    # "finished" function has a chance to read their per-request values,
    # and they will appear to always be zero.

    if connstats_file is not None:
        request.add_finished_callback(finished)

    connection = get_connection(request)

    if connstats_file is not None:
        before = time.time()
        loads_before, stores_before = connection.getTransferCounts()

    folder = connection.root()
    if name not in folder:
        from karl.bootstrap.bootstrap import populate # avoid circdep
        bootstrapper = queryUtility(IBootstrapper, default=populate)
        bootstrapper(folder, name, request)

        # Use pgtextindex
        if 'pgtextindex.dsn' in request.registry.settings:
            site = folder.get(name)
            index = lookup(KarlPGTextIndex)(
                get_weighted_textrepr, drop_and_create=True)
            site.catalog['texts'] = index

        transaction.commit()

    request.registry.notify(RootCreated(request, folder))

    return folder[name]

def main(global_config, **settings):
    var = os.path.abspath(settings['var'])
    if 'mail_queue_path' not in settings:
        settings['mail_queue_path'] = os.path.join(var, 'mail_queue')
    if 'error_monitor_dir' not in settings:
        settings['error_monitor_dir'] = os.path.join(var, 'errors')
    if 'blob_cache' not in settings:
        settings['blob_cache'] = os.path.join(var, 'blob_cache')
    if 'var_instance' not in settings:
        settings['var_instance'] = os.path.join(var, 'instance')
    if 'var_tmp' not in settings:
        settings['var_tmp'] = os.path.join(var, 'tmp')

    # Configure timezone
    tz = settings.get('timezone')
    if tz is not None:
        os.environ['TZ'] = tz
        time.tzset()

    # Find package and configuration
    pkg_name = settings.get('package', None)
    if pkg_name is not None:
        __import__(pkg_name)
        package = sys.modules[pkg_name]
        configure_overrides = get_imperative_config(package)
        if configure_overrides is not None:
            filename = None
        else:
            filename = 'configure.zcml'
            # BBB Customization packages may be using ZCML style config but
            # need configuration done imperatively in core Karl.  These
            # customizaton packages have generally been written before the
            # introduction of imperative style config.
            configure_overrides = configure_karl
    else:
        import karl.includes
        package = karl.includes
        configure_overrides = configure_karl
        filename = None

    config = Configurator(
        package=package,
        settings=settings,
        root_factory=root_factory,
        autocommit=True
        )

    config.begin()
    config.include('pyramid_tm')
    config.include('pyramid_zodbconn')
    if filename is not None:
        if configure_overrides is not None: # BBB See above
            configure_overrides(config, load_zcml=False)
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml(filename)
    else:
        configure_karl(config)
    config.end()

    def closer():
        registry = config.registry
        dbs = getattr(registry, '_zodb_databases', None)
        if dbs:
            for db in dbs.values():
                db.close()
            del registry._zodb_databases

    app = config.make_wsgi_app()
    app.config = settings
    app.close = closer

    return app

def get_imperative_config(package):
    resolver = DottedNameResolver(package)
    try:
        return resolver.resolve('.application:configure_karl')
    except ImportError:
        return None

def is_normal_mode(registry):
    return registry.settings.get('mode', 'NORMAL').upper() == 'NORMAL'


def readonly(request, response):
    """
    This is a commit veto hook for use with pyramid_tm, which always vetos the
    commit (aborts the transaction).  It is intended to be used in conjunction
    with read-only mode to prevent ReadOnly errors--attempts to modify the
    database will be quietly ignored.  Use by setting `tm.commit_veto` to
    `karl.application.readonly` in `etc/karl.ini`.
    """
    return True
