import subprocess
try:
    import unittest2 as unittest
    unittest  # stfu pyflakes
except ImportError:
    import unittest


from repoze.browserid.middleware import make_middleware as browserid


class Base(unittest.TestCase):

    def setUp(self):
        from pyramid.threadlocal import manager
        manager.clear()

        import os
        import tempfile
        config = {
            'dbname': os.environ.get('KARLWEBTEST_PGDBNAME', 'karlwebtest'),
            'user': os.environ.get('KARLWEBTEST_PGUSER', 'karlwebtest'),
            'host': os.environ.get('KARLWEBTEST_PGHOST', 'localhost'),
            'password': os.environ.get('KARLWEBTEST_PGPASSWORD', 'test'),
            'port': os.environ.get('KARLWEBTEST_PGPORT', '5432'),
        }
        self.tmp = tmp = tempfile.mkdtemp('.karl-webtest')
        instances_ini = os.path.join(tmp, 'instances.ini')
        with open(instances_ini, 'w') as out:
            out.write(instances_ini_tmpl % config)
        karlserve_ini = os.path.join(tmp, 'karlserve.ini')
        with open(karlserve_ini, 'w') as out:
            out.write(karlserve_ini_tmpl)
        postoffice_ini = os.path.join(tmp, 'postoffice.ini')
        with open(postoffice_ini, 'w') as out:
            out.write(postoffice_ini_tmpl)
        var = os.path.join(tmp, 'var')
        os.mkdir(var)

        import pkg_resources
        import sys
        initdb = pkg_resources.resource_filename(__name__, 'initdb.py')
        binpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        karlserve = os.path.join(binpath, 'karlserve')
        shell('dropdb %s' % config['dbname'], check=False)
        shell('createdb -O %s %s' % (config['user'], config['dbname']))
        shell('%s -C %s debug -S %s test' % (karlserve, karlserve_ini, initdb))
        postoffice = os.path.join(binpath, 'postoffice')
        shell('%s -C %s' % (postoffice, postoffice_ini))

        from karlserve.application import make_app
        from webtest import TestApp
        settings = {
            'var': var, 'instances_config': instances_ini,
            'who_secret': 'wackadoo', 'who_cookie': 'macadamia',
            'postoffice.zodb_uri':
            'file://%s/po.db?blobstorage_dir=%s/poblobs' % (var, var)}

        from relstorage.adapters import postgresql
        self.Psycopg2Connection = postgresql.Psycopg2Connection
        import psycopg2
        self.connect = psycopg2.connect
        self.connections = []
        def sneaky_connect(connect):
            def wrapper(*args, **kw):
                c = connect(*args, **kw)
                self.connections.append(c)
                return c
            return wrapper
        postgresql.Psycopg2Connection = sneaky_connect(
            postgresql.Psycopg2Connection)
        psycopg2.connect = sneaky_connect(psycopg2.connect)

        self.app = TestApp(browserid(make_app(settings), None, 'sshwabbits'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)
        from relstorage.adapters import postgresql
        postgresql.Psycopg2Connection = self.Psycopg2Connection
        import psycopg2
        psycopg2.connect = self.connect
        while self.connections:
            c = self.connections.pop()
            if not c.closed:
                c.close()

    def login(self, login='admin', password='admin'):
        r = self.app.get('/')
        r = r.follow()
        self.assertTrue('Username' in r)
        form = r.form
        form['login'] = login
        form['password'] = password
        r = form.submit()
        return r


def shell(cmd, check=True):
    if check:
        call = subprocess.check_call
    else:
        call = subprocess.call
    return call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


instances_ini_tmpl = """\
[instance:test]
dsn = dbname='%(dbname)s' user='%(user)s' host='%(host)s' password='%(password)s' port='%(port)s'
repozitory_db_string = postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(dbname)s
root = true
"""


karlserve_ini_tmpl = """\
[app:karlserve]
use = egg:karlserve#application
instances_config = %(here)s/instances.ini
var = %(here)s/var
who_secret = wackadoo
who_cookie = macadamia
"""


postoffice_ini_tmpl = """\
[post office]
zodb_uri = file://%(here)s/var/po.db?blobstorage_dir=%(here)s/var/poblobs
maildir = %(here)s/var/po_mail

[queue:test]
filters = to_hostname:pg.example.com
"""
