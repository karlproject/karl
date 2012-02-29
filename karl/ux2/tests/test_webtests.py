import os
import shutil
import tempfile
from unittest import TestCase
from webtest import TestApp

instances = """
[instance:fs]

"""

pre = 'file://%(var)s/'
zodbconn_uri = pre + 'karl.db?blobstorage_dir=%(var)s/blobs/'
po = pre + 'postoffice.db?blobstorage_dir=%(var)s/postoffice_blobs'

class FunctionalTests(TestCase):

    def setUp(self):
        self.tmp = tmp = tempfile.mkdtemp('.karlserve-testing')
        self.etc = etc = os.path.join(tmp, 'etc')
        os.mkdir(etc)
        self.var = var = os.path.join(tmp, 'var')
        os.mkdir(var)
        os.mkdir(os.path.join(var, 'blobs'))
        self.instances_ini = os.path.join(etc, 'instances.ini')

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def make_application(self):
        d = {'var': self.var, 'etc': self.etc}
        instances_ini = instances % d
        with open(self.instances_ini, 'w') as out:
            out.write(instances_ini)

        from karlserve.application import make_app
        settings = {
            'instances_config': self.instances_ini,
            'zodbconn.uri': zodbconn_uri % d,
            'postoffice.zodb_uri': po % d,
            'who_secret': 'secret',
            'who_cookie': 'pnutbtr',
            'var': self.var
            }
        return TestApp(make_app(settings))

    def test_visitor_homepage(self):
        app = self.make_application()
        response = app.get('/fs/login.html')
        self.assertEqual(response.status, '200 OK')
        self.failUnless("Coupon" in response.body)

