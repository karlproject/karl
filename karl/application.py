import logging
import os
import sys
import transaction

from zope.component import queryUtility

from repoze.bfg.router import make_app as bfg_make_app
from repoze.who.plugins.zodb.users import Users
from repoze.zodbconn.finder import PersistentApplicationFinder

from karl.log import setup_log
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
    # paster app config callback
    zodb_uri = global_config.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')
    get_root = PersistentApplicationFinder(zodb_uri, appmaker)

    # Coerce a value out of the [app:karl] section in the INI file
    jquery_dev_mode = kw.get('jquery_dev_mode', False)
    kw['jquery_dev_mode'] = asbool(jquery_dev_mode)

    # Set up logging
    if 'syslog' in kw:
        syslog = kw.pop('syslog')
        if ':' in syslog:
            host, port = syslog.split(':')
            port = int(port)
            address = (host, port)
        elif '/' in syslog:
            address = syslog
        else:
            host, port = syslog, 514

        debug = kw.get('debug', global_config.get('debug', False))
        if debug:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO

        app_name = kw.pop('syslog_app_name', 'karl')
        setup_log(app_name, address, loglevel)

    # Set up logging admin view (coerce instances to list)
    if 'syslog_view' in kw:
        kw['syslog_view_instances'] = kw.get('syslog_view_instances',
                                             'karl').split()

    if 'logs_view' in kw:
        kw['logs_view'] = map(os.path.abspath, kw['logs_view'].split())

    # Make BFG app
    pkg_name = global_config.get('package', None)
    if pkg_name is not None:
        __import__(pkg_name)
        package = sys.modules[pkg_name]
        app = bfg_make_app(get_root, package, options=kw)
    else:
        filename = 'karl.includes:standalone.zcml'
        app = bfg_make_app(get_root, filename=filename, options=kw)

    return app

def find_users(root):
    # Called by repoze.who
    # XXX Should this really go here?
    if not 'site' in root:
        return Users()
    return root['site'].users

