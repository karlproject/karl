import unittest


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
        var = os.path.join(tmp, 'var')
        os.mkdir(var)

        import pkg_resources
        import subprocess
        import sys
        initdb = pkg_resources.resource_filename(__name__, 'initdb.py')
        binpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        karlserve = os.path.join(binpath, 'karlserve')
        subprocess.check_call('%s -C %s debug -S %s test' % (
            karlserve, karlserve_ini, initdb), shell=True)

        from karlserve.application import make_app
        from webtest import TestApp
        self.app = TestApp(
            make_app({}, var=var, instances_config=instances_ini,
                     who_secret='wackadoo', who_cookie='macadamia'))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def login(self, login='admin', password='admin'):
        r = self.app.get('/')
        r = r.follow()
        self.assertTrue('Username' in r)
        form = r.form
        form['login'] = login
        form['password'] = password
        r = form.submit()
        r = r.follow()    # redirect to /
        r = r.follow()    # redirect to /communities/default
        r = r.follow()    # redirect to /communities/default/view.html
        self.assertTrue('Default Community' in r)
        return r


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
