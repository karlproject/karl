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

""" Run the KARL server directly.
"""
import os
import sys
from paste.script.serve import ServeCommand
from karl.scripting import get_default_config

def main():
    os.environ['PASTE_CONFIG_FILE'] = get_default_config()

    cmd = ServeCommand('karlctl')
    cmd.description = """\
    Run the KARL application.

    If start/stop/restart is given, then --daemon is implied, and it will
    start (normal operation), stop (--stop-daemon), or do both.

    You can also include variable assignments like 'http_port=8080'
    and then use %(http_port)s in your config files.
    """
    exit_code = cmd.run(sys.argv[1:])
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
