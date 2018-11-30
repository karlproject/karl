# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""Support code for KARL scripts
"""
import argparse
import atexit
import codecs
import gc
import os
import pwd
import signal
import sys
import time
import ConfigParser

from logging import getLogger
from logging.config import fileConfig

from paste.deploy import loadapp
from ZODB.POSException import ConflictError
from pyramid.scripting import get_root
from pyramid.paster import bootstrap

_debug_object_refs = hasattr(sys, 'getobjects')

LOCKDIR = '/var/run/karl/'

#
#   Replaceable shims for unit testing.
#
_TIME_TIME = None
_TIME_SLEEP = None

def _time_time():
    if _TIME_TIME is not None:
        return _TIME_TIME()
    return time.time() #pragma NO COVERAGE

def _time_sleep(interval):
    if _TIME_SLEEP is not None:
        return _TIME_SLEEP(interval)
    return time.sleep(interval) #pragma NO COVERAGE

def get_default_config():
    """Get the default configuration file name.

    This should be called by a console script. We assume that the
    console script lives in the 'bin' dir of a sandbox or buildout, and
    that the karl.ini file lives in the 'etc' directory of the sandbox
    or buildout.
    """
    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    config = os.path.join(sandbox, 'etc', 'karl.ini')
    return os.path.abspath(os.path.normpath(config))

def open_root(config, name='karl'): #pragma NO COVERAGE
    """Open the database root object, given a Paste Deploy config file name.

    Returns (root, closer).  Call the closer function to close the database
    connection.
    """
    config = os.path.abspath(os.path.normpath(config))
    app = loadapp('config:%s' % config, name=name)
    return get_root(app)

def only_one(func, registry, name):
    logger = getLogger('karl')
    var = registry.settings['var']
    locks = os.path.join(var, 'lock')
    lock = os.path.join(locks, '%s.pid' % name)
    if os.path.exists(lock):
        pid = open(lock).read().strip()
        if os.path.exists(os.path.join('/proc', pid)):
            logger.warn("%s already running with pid %s" % (name, pid))
            logger.warn("Exiting.")
            sys.exit(1)
        else:
            logger.warn("Found stale lock file for %s (pid %s)" % (name, pid))
    if not os.path.exists(locks):
        os.makedirs(locks)
    with open(lock, 'w') as f:
        print >> f, os.getpid()

    def wrapper(*arg, **kw):
        try:
            func(*arg, **kw)
        finally:
            os.remove(lock)

    return wrapper

def daemonize_function(func, interval):
    logger = getLogger('karl')
    def wrapper(*args):
        def finish(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, finish)

        try:
            def run():
                func(*args)
            run_daemon(func.__name__, run, interval)
        except KeyboardInterrupt:
            logger.info("Exiting.")
    return wrapper

def run_daemon(name, func, interval=300,
               retry_period=30*60, retry_interval=60, retryable=None,
               proceed=None):
    logger = getLogger('karl')

    if retryable is None:
        retryable = (ConflictError,)

    if proceed == None: #pragma NO COVERAGE
        def proceed():
            return True

    while proceed():
        start_trying = _time_time()
        tries = 0
        logger.debug("Running %s", name)
        while True:
            try:
                tries += 1
                func()
                logger.debug("Finished %s", name)
                break
            except retryable:
                if _time_time() - start_trying > retry_period:
                    logger.error("Retried for %d seconds, count = %d",
                                 retry_period, tries,
                                 exc_info=True)
                    break
                logger.debug("Retrying in %d seconds, count = %d",
                             retry_interval, tries,
                             exc_info=True)
                _time_sleep(retry_interval)
            except:
                logger.error("Error in daemon process", exc_info=True)
                break
        if _debug_object_refs: #pragma NO COVERAGE
            _count_object_refs()
        sys.stderr.flush()
        sys.stdout.flush()
        _time_sleep(interval)

_ref_counts = None
def _count_object_refs(): #pragma NO COVERAGE
    """
    This function is used for debugging leaking references between business
    function calls in the run_daemon function.  It relies on a cPython built
    with Py_TRACE_REFS.  In the absence of such a Python (the standard case)
    this function does not called and we don't do this expensive object
    counting.

    On Ubuntu I was able to get a debug version of python installed by doing:

        apt-get install python2.5-dbg

    Your mileage may vary on other platforms.  I had terrible problems trying
    to build Python from source with the Py_TRACE_REFS call and do not
    recommend trying that on Ubuntu.
    """
    gc.collect()
    ref_counts = {}

    # Count all of the objects
    for obj in sys.getobjects(sys.gettotalrefcount()):
        kind = type(obj)
        if kind in ref_counts:
            ref_counts[kind]['count'] += 1
        else:
            ref_counts[kind] = dict(kind=kind, count=1, delta=0)

    global _ref_counts
    if _ref_counts == None:
        # first time
        _ref_counts = ref_counts
        return

    # Calculate how many were created since last time
    for kind, record in ref_counts.items():
        if kind in _ref_counts:
            record['delta'] = record['count'] - _ref_counts[kind]['count']
        else:
            record['delta'] = record['count']
    _ref_counts = ref_counts

    # Print the top N new objects
    N = 20
    records = list(ref_counts.values())
    records.sort(key=lambda x: (x['delta'], x['count']), reverse=True)
    for record in records[:N]:
        print "DEBUG: created %d new instances of %s (Total: %d)" % (
            record['delta'], str(record['kind']), record['count'],
        )

    if gc.garbage:
        print "DEBUG: GARBAGE: %d/%d" % (
            len(gc.garbage), len(gc.get_objects()))


def only_once(progname, config=None):
    logname = os.getenv('LOGNAME', default=pwd.getpwuid(os.getuid())[0])
    job_name = '%s-%s' % (logname, progname)
    lockdir = LOCKDIR
    if config is not None:
        cp = ConfigParser.ConfigParser()
        cp.read(config)
        lockdir = cp.get('DEFAULT', 'lockdir')
    lockfile = os.path.join(lockdir, job_name)
    if os.path.exists(lockfile):
        print >>sys.stderr, '%s still running' % job_name
        sys.exit(1)
    atexit.register(os.remove, lockfile)
    open(lockfile, 'w').write('%s running, PID=%d'
                                  % (progname, os.getpid()))

def create_karl_argparser(description='', out=None):
    if out is None:
        out = codecs.getwriter('UTF-8')(sys.stdout)
    parser =  argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-C', '--config',
        metavar='FILE',
        default=get_default_config(),
        dest='config_uri',
        help='Path to configuration ini file (defaults to $CWD/etc/karl.ini).'
        )
    def _bootstrap(config_uri):
        setup_logging(config_uri)
        return bootstrap(config_uri)
    parser.set_defaults(out=out, bootstrap=_bootstrap)
    return parser

def setup_logging(config_uri, fileConfig=fileConfig,
                  configparser=ConfigParser):
    """
    Set up logging via the logging module's fileConfig function with the
    filename specified via ``config_uri`` (a string in the form
    ``filename#sectionname``).

    ConfigParser defaults are specified for the special ``__file__``
    and ``here`` variables, similar to PasteDeploy config loading.
    """
    path, _ = _getpathsec(config_uri, None)
    parser = configparser.ConfigParser()
    parser.read([path])
    if parser.has_section('loggers'):
        config_file = os.path.abspath(path)
        return fileConfig(
            config_file,
            dict(__file__=config_file, here=os.path.dirname(config_file))
            )

def _getpathsec(config_uri, name):
    if '#' in config_uri:
        path, section = config_uri.split('#', 1)
    else:
        path, section = config_uri, 'main'
    if name:
        section = name
    return path, section
