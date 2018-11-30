import unittest


class Test_get_default_config(unittest.TestCase):

    def _callFUT(self):
        from karl.scripting import get_default_config
        return get_default_config()

    def test_it(self):
        import os.path
        path = self._callFUT()
        self.assertTrue(path.endswith('/etc/karl.ini'))
        # Expect to find a bin dir next to etc/karl.ini.
        sandbox = os.path.dirname(os.path.dirname(path))
        bindir = os.path.join(sandbox, 'bin')
        self.assertTrue(os.path.exists(bindir), 'Expected to find %s' % bindir)


class Test_run_daemon(unittest.TestCase):

    def setUp(self):
        from karl import scripting
        self.time = DummyTimeModule()
        scripting._TIME_TIME = self.time.time
        scripting._TIME_SLEEP = self.time.sleep

        self._saved_get_logger = scripting.getLogger
        self.log = DummyLogger()
        scripting.getLogger = lambda x: self.log

    def tearDown(self):
        from karl import scripting
        scripting._TIME_TIME = scripting._TIME_SLEEP = None
        scripting.getLogger = self._saved_get_logger

    def _callFUT(self, *args, **kw):
        from karl.scripting import run_daemon
        return run_daemon(*args, **kw)

    def test_run_once(self):
        class Script(DummyCallable):
            def f1(self):
                self.f1_called = True
            steps = (f1,)
        f = Script()
        def proceed():
            return not not f.iterations
        self._callFUT('foo', f, proceed=proceed)
        self.failUnless(f.f1_called)
        self.assertEqual(self.time.sleeps, [300,])
        self.assertEqual(len(self.log.errors), 0, self.log.errors)
        self.assertEqual(len(self.log.debugs), 2, self.log.infos)

    def test_run_twice(self):
        class Script(DummyCallable):
            def f1(self):
                self.f1_called = True
            steps = (f1, f1)
        f = Script()
        def proceed():
            return not not f.iterations
        self._callFUT('foo', f, proceed=proceed)
        self.failUnless(f.f1_called)
        self.assertEqual(self.time.sleeps, [300, 300,])
        self.assertEqual(len(self.log.errors), 0, self.log.errors)
        self.assertEqual(len(self.log.debugs), 4, self.log.infos)

    def test_exception(self):
        class Script(DummyCallable):
            def f1(myself):
                self.time._time += 10
                raise Exception("I threw up.")
            def f2(myself):
                self.time._time += 10
                myself.ok = True
            steps = (f1, f2)
        f = Script()
        def proceed():
            return not not f.iterations
        self._callFUT('foo', f, proceed=proceed)
        self.failUnless(f.ok)
        self.assertEqual(self.time.sleeps, [300, 300])
        self.assertEqual(len(self.log.errors), 1, self.log.errors)
        self.assertEqual(len(self.log.debugs), 3, self.log.infos)

    def test_retry_once(self):
        from ZODB.POSException import ConflictError

        class Script(DummyCallable):
            def f1(myself):
                self.time._time += 10
                raise ConflictError
            def f2(myself):
                self.time._time += 10
                myself.ok = True
            steps = (f1, f2)
        f = Script()
        def proceed():
            return not not f.iterations
        self._callFUT('foo', f, proceed=proceed)
        self.failUnless(f.ok)
        self.assertEqual(self.time.sleeps, [60, 300])
        self.assertEqual(len(self.log.errors), 0, self.log.errors)
        self.assertEqual(len(self.log.debugs), 3, self.log.infos)

    def test_retry_twice(self):
        from ZODB.POSException import ConflictError

        class Script(DummyCallable):
            def f1(myself):
                self.time._time += 10
                raise ConflictError
            def f2(myself):
                self.time._time += 10
                myself.ok = True
            steps = (f1, f1, f2)
        f = Script()
        def proceed():
            return not not f.iterations
        self._callFUT('foo', f, proceed=proceed)
        self.failUnless(f.ok)
        self.assertEqual(self.time.sleeps, [60, 60, 300])
        self.assertEqual(len(self.log.errors), 0, self.log.errors)
        self.assertEqual(len(self.log.debugs), 4, self.log.infos)

    def test_retry_fail(self):
        from ZODB.POSException import ConflictError

        class Script(DummyCallable):
            def f1(myself):
                self.time._time += 370
                raise ConflictError
            def f2(myself):
                self.time._time += 10
                myself.ok = True
            steps = (f1, f1, f1, f1, f1, f2)
        f = Script()
        def proceed():
            return not not f.iterations
        self._callFUT('foo', f, proceed=proceed)
        self.failUnless(f.ok)
        self.assertEqual(len(self.log.errors), 1, self.log.errors)
        self.assertEqual(len(self.log.debugs), 7, self.log.infos)


class Test_only_once(unittest.TestCase):

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmpdir)

    def _callFUT(self, progname, config=None, tempdir=None):
        import os.path
        import subprocess
        import sys
        if tempdir is None:
            tempdir = self._tmpdir
        python_cmds = ('from karl import scripting as s; '
                       's.LOCKDIR = "%s"; '
                       's.only_once("%s", %r); '
                       'print "OK"' % (tempdir, progname, config))
        bindir = os.path.dirname(sys.argv[0])
        py = os.path.join(bindir, 'py')
        if not os.path.exists(py):
            self.fail("Expected to find python interpreter at %s" % py)
        child = subprocess.Popen([py, '-c', python_cmds],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                )
        stdout, stderr = child.communicate()
        return child, stdout, stderr

    def _makeConfig(self):
        import os
        config = os.path.join(self._tmpdir, 'testing.ini')
        f = open(config, 'w')
        f.write('[DEFAULT]\nlockdir = %s\n' % self._tmpdir)
        f.flush()
        f.close()
        return config

    def test_lockfile_present_wo_config(self):
        import os
        import pwd
        logname = os.getenv('LOGNAME', default=pwd.getpwuid(os.getuid())[0])
        job_name = '%s-testing' % logname
        filename = os.path.join(self._tmpdir, job_name)
        open(filename, 'w').write('testing')
        child, stdout, stderr = self._callFUT('testing')
        self.assertEqual(child.returncode, 1)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '%s still running\n' % job_name)

    def test_lockfile_present_w_config(self):
        import os
        import pwd
        logname = os.getenv('LOGNAME', default=pwd.getpwuid(os.getuid())[0])
        job_name = '%s-testing' % logname
        filename = os.path.join(self._tmpdir, job_name)
        open(filename, 'w').write('testing')
        config = self._makeConfig()
        child, stdout, stderr = self._callFUT('testing', config, '/tmp')
        self.assertEqual(child.returncode, 1)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '%s still running\n' % job_name)

    def test_lockfile_not_present_wo_config(self):
        import os
        import pwd
        logname = os.getenv('LOGNAME', default=pwd.getpwuid(os.getuid())[0])
        job_name = '%s-testing' % logname
        filename = os.path.join(self._tmpdir, job_name)
        child, stdout, stderr = self._callFUT('testing')
        self.assertEqual(child.returncode, 0)
        self.assertEqual(stdout, 'OK\n')
        self.assertEqual(stderr, '')
        self.failIf(os.path.exists(filename))

    def test_lockfile_not_present_w_config(self):
        import os
        import pwd
        logname = os.getenv('LOGNAME', default=pwd.getpwuid(os.getuid())[0])
        job_name = '%s-testing' % logname
        filename = os.path.join(self._tmpdir, job_name)
        config = self._makeConfig()
        child, stdout, stderr = self._callFUT('testing', config, '/tmp')
        self.assertEqual(child.returncode, 0)
        self.assertEqual(stdout, 'OK\n')
        self.assertEqual(stderr, '')
        self.failIf(os.path.exists(filename))


class DummyTimeModule(object):
    def __init__(self):
        self.sleeps = []
        self._time = 0

    def time(self):
        return self._time

    def sleep(self, t):
        self.sleeps.append(t)


class DummyCallable(object):
    def __init__(self):
        self.iterations = list(self.steps)

    def __call__(self):
        if self.iterations:
            return self.iterations.pop(0)(self)


class DummyLogger(object):
    def __init__(self):
        self.errors = []
        self.infos = []
        self.debugs = []

    def error(self, *args, **kw):
        self.errors.append(args[0] % args[1:])

    def info(self, *args, **kw):
        self.infos.append(args[0] % args[1:])

    def debug(self, *args, **kw):
        self.debugs.append(args[0] % args[1:])
