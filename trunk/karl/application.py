import logging
import os
import sys
import transaction
import webob

from zope.component import queryUtility

from repoze.bfg.router import make_app as bfg_make_app
from repoze.bfg.scripting import get_root
from repoze.bfg.traversal import model_path
from repoze.who.plugins.zodb.users import Users
from repoze.zodbconn.finder import PersistentApplicationFinder

from karl.log import configure_log
from karl.log import get_logger
from karl.log import set_subsystem
from karl.views.utils import get_user_home
from karl.utils import asbool
from karl.bootstrap.bootstrap import populate
from karl.bootstrap.interfaces import IBootstrapper

def appmaker(root):
    bootstrapper = queryUtility(IBootstrapper, default=populate)
    if not root.has_key('site'):
        bootstrapper(root)
        transaction.commit()
    return root['site']

def make_app(global_config, **kw):
    config = global_config.copy()
    config.update(kw)

    # paster app config callback
    zodb_uri = config.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')
    get_root = PersistentApplicationFinder(zodb_uri, appmaker)

    # Coerce a value out of the [app:karl] section in the INI file
    jquery_dev_mode = config.get('jquery_dev_mode', False)
    config['jquery_dev_mode'] = asbool(jquery_dev_mode)

    # Set up logging
    configure_log(**config)
    set_subsystem('karl')

    # Set up logging admin view (coerce instances to list)
    if 'logs_view' in config:
        config['logs_view'] = map(os.path.abspath, config['logs_view'].split())

    for key in ('syslog_view_instances', 'error_monitor_subsystems'):
        if key in config:
            config[key] = config[key].split()

    # Make BFG app
    pkg_name = config.get('package', None)
    if pkg_name is not None:
        __import__(pkg_name)
        package = sys.modules[pkg_name]
        app = bfg_make_app(get_root, package, options=config)
    else:
        filename = 'karl.includes:standalone.zcml'
        app = bfg_make_app(get_root, filename=filename, options=config)

    #exercise(app) # experimental
    return app

def exercise(app):
    """
    Simulate the first request to the application in order to prime the ZODB
    cache.

    Performing this operation during start up, it is hoped to delay user
    requests being handed off to this worker by mod_wsgi until after the cache
    is already primed.  Otherwise the first, slow, cache priming request would
    fall to an unlucky user.
    """
    # Need to be logged in as somebody.  Use the first user we find that is a
    # member of some group.
    root, closer = get_root(app)
    for profile in root['profiles'].values():
        user = root.users.get_by_id(profile.__name__)
        if user['groups']:
            break

    request = webob.Request.blank('/')
    request.environ['repoze.who.identity'] = user
    user['repoze.who.userid'] = user['id']
    home, extra_path = get_user_home(root, request)
    path = model_path(home, *extra_path)
    request.path_info = path
    response = request.get_response(app)
    if response.status_int != 200:
        logger = get_logger()
        logger.warn('Status of %s when priming cache.  Response body:\n%s' %
                    (response.status, response.body))

def find_users(root):
    # Called by repoze.who
    # XXX Should this really go here?
    if not 'site' in root:
        return Users()
    return root['site'].users

