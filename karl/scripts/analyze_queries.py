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

"""Analyze the catalog query log.
"""
from datetime import datetime
from optparse import OptionParser
import os
import sys

from karl.scripting import get_default_config


def _parseISOTimestamp(stamp):
    if sys.version_info[:2] >= (2, 6):
        # '%f' is not supported in Python 2.5
        return datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%S.%f')
    stamp, micros = stamp.rsplit('.', 1)
    when = datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%S')
    return when.replace(microsecond=int(micros))


class _LogRecord(object):
    def __init__(self, stamp, duration, count, params):
        self.timestamp = _parseISOTimestamp(stamp)
        self.duration_ms = float(duration) * 1000
        self.count = int(count)
        self.params = params


class _Stream(object):
    def __init__(self, stream):
        self._stream = stream
        self._pushback = []

    def pushBack(self, line):
        self._pushback.append(line)

    def readline(self):
        try:
            return self._pushback.pop()
        except IndexError:
            return self._stream.readline()

class LogParser(object):

    def __init__(self):
        self.records = []

    def _parseDict(self, stream):
        lines = []
        line = stream.readline()
        while line and line.startswith(' '):
            lines.append(line.lstrip())
            line = stream.readline()
        if line:
            stream.pushBack(line)
        if lines:
            return eval(' '.join(lines), {}, {})
        return {}

    def parse(self, stream_or_filename):
        record_count = 0
        errors = []
        if isinstance(stream_or_filename, str):
            if os.path.exists(os.path.abspath(stream_or_filename)):
                stream_or_filename = open(stream_or_filename)
        stream = _Stream(stream_or_filename)
        header = stream.readline()
        while header:
            record_count += 1
            try:
                stamp, duration, count = header.strip().split()
            except Exception, e:
                errors.append('Invalid summary line: %s' % str(e))
            else:
                try:
                    params = self._parseDict(stream)
                except Exception, e:
                    errors.append('Invalid query params dict: %s' % str(e))
                else:
                    if params:
                        record = _LogRecord(stamp, duration, count, params)
                        self.records.append(record)
                    else:
                        errors.append('Empty query params dict')
            header = stream.readline()
        return record_count, errors

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        return self.records[index]


def main():
    parser = OptionParser(description=__doc__,
                          usage='usage: %prog [options]')
    parser.add_option('-C', '--config', dest='config', default=None,
                      help="Specify a paster config file. "
                           "Defaults to$CWD/etc/karl.ini")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      default='1', help="Show more information.")
    parser.add_option('-q', '--quiet', dest='verbose', action='store_const',
                      const=0, help="Show no extra information.")

    options, args = parser.parse_args()

    config = options.config
    if config is None:
        config = get_default_config()


if __name__ == '__main__':
    main()
