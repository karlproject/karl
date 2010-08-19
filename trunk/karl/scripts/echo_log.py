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

""" Echo a message to syslog.  Useful for testing.  """

import optparse
import os
import sys
from karl.log import get_logger
from karl.scripting import get_default_config
from karl.scripting import open_root

def main(argv=sys.argv[1:]):
    parser = optparse.OptionParser(description=__doc__,
                                   usage='%prog [options] message')
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('-L', '--level', dest='level',
                      help='Log level: debug, info, warn or error',
                      default='info')
    options, args = parser.parse_args(argv)
    if not args:
        parser.error("No message given.")

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    func = getattr(get_logger(), options.level, None)
    if func is None:
        parser.error("Bad level: %s" % options.level)

    func(' '.join(args))

if __name__ == '__main__':
    main()
