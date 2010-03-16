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

import gc
import os
import sys
import time
from paste.deploy import loadapp
from ZODB.POSException import ConflictError
from repoze.bfg.scripting import get_root
from karl.log import get_logger

_debug_object_refs = hasattr(sys, 'getobjects')

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

def open_root(config, name='karl'):
    """Open the database root object, given a Paste Deploy config file name.

    Returns (root, closer).  Call the closer function to close the database
    connection.
    """
    config = os.path.abspath(os.path.normpath(config))
    app = loadapp('config:%s' % config, name=name)
    return get_root(app)

def run_daemon(name, func, interval=300, tries=3, retryable=None):
    logger = get_logger()

    if retryable is None:
        retryable = (ConflictError,)

    while True:
        tried = 0
        logger.info("Running %s", name)
        while True:
            try:
                func()
                logger.info("Finished %s", name)
                break
            except retryable:
                tried += 1
                if tried == tries:
                    logger.error("Error after %s tries" % tries, exc_info=True)
                    break
                logger.info("Retrying, count = %s" % tried, exc_info=True)
            except:
                logger.error("Error in daemon process", exc_info=True)
                break
        if _debug_object_refs:
            _count_object_refs()
        sys.stderr.flush()
        sys.stdout.flush()
        time.sleep(interval)

_ref_counts = None
def _count_object_refs():
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
