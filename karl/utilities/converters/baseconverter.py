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

import os
from subprocess import Popen
from subprocess import PIPE
import threading
import tempfile
import time

from zope.interface import implements
from karl.utilities.converters.interfaces import IConverter

class BaseConverterError(Exception):
    pass

class BaseConverter:
    """ Base class for all converters """

    content_type = None
    content_description = None
    timeout = 5

    implements(IConverter)

    def __init__(self):
        if not self.content_type:
            raise BaseConverterError('content_type undefinied')

        if not self.content_description:
            raise BaseConverterError('content_description undefinied')

    def execute(self, com):
        out = tempfile.TemporaryFile()
        PO = Popen(com, shell=True, stdout=out, close_fds=True)
        timeout = _ProcTimeout(PO, timeout=self.timeout)
        timeout.start()
        PO.communicate()
        timeout.stop()
        timeout.join()
        out.seek(0)
        return out

    def getDescription(self):
        return self.content_description

    def getType(self):
        return self.content_type

    def getDependency(self):
        return getattr(self, 'depends_on', None)

    def __call__(self, s):
        return self.convert(s)

    def isAvailable(self):

        depends_on = self.getDependency()
        if depends_on:
            try:
                cmd = 'which %s' % depends_on
                PO =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
            except OSError:
                return 'no'
            else:
                out = PO.stdout.read()
                PO.wait()
                del PO
            if (
                ( out.find('no %s' % depends_on) > - 1 ) or
                ( out.lower().find('not found') > -1 ) or
                ( len(out.strip()) == 0 )
                ):
                return 'no'
            return 'yes'
        else:
            return 'always'


class _ProcTimeout(threading.Thread):
    """
    Implements a timeout on a running subprocess.  Polls subprocess on a
    separate thread to see if it has finished running.  If process has not
    finished by the time the timeout has expired, it then attempts to terminate
    the process.

    Some external converter programs (wvConvert) have been known to hang
    indefinitely with certain inputs.
    """
    def __init__(self, process, poll_interval=.01, timeout=5):
        super(_ProcTimeout, self).__init__()
        self.process = process
        self.poll_interval = poll_interval
        self.timeout = timeout
        self._run = True

    def run(self):
        start_time = time.time()
        process = self.process
        poll_interval = self.poll_interval
        timeout = self.timeout
        time.sleep(poll_interval)
        while self._run and not process.poll():
            elapsed = time.time() - start_time
            if hasattr(process, "terminate"): # >=2.6
                if elapsed > timeout * 2:
                    process.kill()
                elif elapsed > timeout:
                    process.terminate()
            else: # < 2.6
                # Will (hopefully) fail quietly on Windows
                # Occasionally it seems that process.poll() tells us we are
                # still running even when we're not, so we check the error
                # status code from os.system() and break out if there is an
                # error, usually because there is no such process.
                if elapsed > timeout * 2:
                    if os.system("kill -KILL %d > /dev/null 2>&1" % process.pid) != 0:
                        break
                elif elapsed > timeout:
                    if os.system("kill %d > /dev/null 2>&1" % process.pid) != 0:
                        break
            time.sleep(poll_interval)

    def stop(self):
        self._run = False