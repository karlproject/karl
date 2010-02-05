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
"""Download each feed defined in a config file and put it into ZODB.
"""

from karl.log import set_subsystem
from karl.scripting import get_default_config
from karl.scripting import run_daemon
from karl.utilities.feed import update_feeds
import optparse
from paste.deploy import loadapp
from repoze.bfg.scripting import get_root
import sys
import transaction

def main(argv=sys.argv, root=None, update_func=update_feeds, tx=transaction):
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/karl.ini)',
        metavar='FILE')
    parser.add_option('-f', '--force', dest='force',
        action='store_true', default=False,
        help='Update all feeds, even if unchanged')
    parser.add_option('--dry-run', dest='dryrun',
        action='store_true', default=False,
        help="Don't actually commit the transaction")
    parser.add_option('--daemon', '-D', dest='daemon',
                      action='store_true', default=False,
                      help='Run in daemon mode.')
    parser.add_option('--interval', '-i', dest='interval', type='int',
                      default=300,
                      help='Interval, in seconds, between executions when in '
                           'daemon mode.')
    options, args = parser.parse_args(argv[1:])

    if args:
        parser.error("Too many parameters: %s" % repr(args))

    config = options.config
    if config is None:
        config = get_default_config()
    if root is None:
        app = loadapp('config:%s' % config, name='karl')
    #else: unit test

    def run(root=root):
        closer = lambda: None  # unit test
        try:
            if root is None:
                root, closer = get_root(app)
            #else: unit test
            set_subsystem('update_feeds')
            update_func(root, config, force=options.force)
        except:
            tx.abort()
            closer()
            raise
        else:
            if options.dryrun:
                tx.abort()
            else:
                tx.commit()
            closer()

    if options.daemon:
        run_daemon('update_feeds', run, options.interval)
    else:
        run()

if __name__ == '__main__':
    main()
