# Copyright (C) 2010 Open Society Institute
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

"""Reset all content security workflows.

  reset_security_workflow [/path/to/object]
"""

import sys
from repoze.bfg.traversal import find_model

from karl.scripting import get_default_config
from karl.scripting import open_root
from optparse import OptionParser
from karl.security.workflow import reset_security_workflow
import transaction

def main():
    parser = OptionParser(description=__doc__,
                          usage='usage: %prog [options] username password')
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")
    parser.add_option('--dry-run', '-n', dest='dry_run',
        action='store_true', default=False,
        help="Don't actually commit any transaction")

    path = '/'
    options, args = parser.parse_args()
    if args:
        path = args[0]

    config = options.config
    if config is None:
        config = get_default_config()

    root, closer = open_root(config)
    model = find_model(root, path)

    def out(msg):
        sys.stderr.write(msg)
        sys.stderr.write('\n')
        sys.stderr.flush()

    try:
        reset_security_workflow(model, output=out)
    except:
        transaction.abort()
        raise
    else:
        if options.dry_run:
            print 'no transaction committed due to --dry-run'
        else:
            transaction.commit()

if __name__ == '__main__':
    main()
