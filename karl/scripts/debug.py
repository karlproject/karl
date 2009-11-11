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

""" Run an interactive debugging session  """

from code import interact
import os
import sys
from karl.scripting import get_default_config
from karl.scripting import open_root

def main(argv=sys.argv):
    config = None
    script = None
    if '-C' in argv:
        index = argv.index('-C')
        argv.pop(index)
        config = argv.pop(index)
    if len(argv) > 1:
        script = argv[1]
    if not config:
        config = get_default_config()
    root, closer = open_root(config)

    if script is None:
        cprt = ('Type "help" for more information. "root" is the karl '
                'root object.')
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        interact(banner, local={'root':root})
    else:
        code = compile(open(script).read(), script, 'exec')
        exec code in {'root': root}

if __name__ == '__main__':
    main()
