import sys
import transaction

from zope.component import queryUtility

from repoze.bfg.router import make_app as bfg_make_app
from repoze.who.plugins.zodb.users import Users
from repoze.zodbconn.finder import PersistentApplicationFinder

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
    package = None
    filename = None

    pkg_name = global_config.get('package', None)
    if pkg_name is not None:
        __import__(pkg_name)
        package = sys.modules[pkg_name]
    else:
        filename = 'karl.includes:standalone.zcml'

    # paster app config callback
    zodb_uri = global_config.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')
    get_root = PersistentApplicationFinder(zodb_uri, appmaker)

    # Coerce a value out of the [app:karl] section in the INI file
    jquery_dev_mode = kw.get('jquery_dev_mode', False)
    kw['jquery_dev_mode'] = asbool(jquery_dev_mode)

    app = bfg_make_app(get_root, package, filename, options=kw)
    return app

def find_users(root):
    # Called by repoze.who
    # XXX Shouldthis really go here?
    if not 'site' in root:
        return Users()
    return root['site'].users
