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

"""Set or clear the KARL site announcement:

  site_announce             (show the current announcement text).

  site_announce --clear     (clear any existing announcement text).

  site_announce <text>      (update the announcment text).
"""

from karl.scripting import get_default_config
from karl.scripting import open_root
from optparse import OptionParser

import transaction

import logging
logging.basicConfig()

def clear_site_announce(root, *args):
    previous, root.site_announcement = getattr(root, 'site_announcement',
                                               ''), ''
    return previous, ''

def set_site_announce(root, *args):
    previous = getattr(root, 'site_announcement', '')

    if not args:
        return previous, previous

    now = root.site_announcement = ' '.join(args)
    return previous, now

def main():
    parser = OptionParser(description=__doc__,
                          usage='usage: %prog [options] username password')
    parser.add_option('-C', '--config', dest='config', default=None,
                      help="Specify a paster config file. "
                           "Defaults to$CWD/etc/karl.ini")
    parser.add_option('--clear', dest='clear', default=False,
                      action='store_true',
                      help="Clear any existing announcement. Default false.")
    parser.add_option('-n', '--dry-run', dest='dry_run', default=False,
                      action='store_true',
                      help="Don't actually commit any change.")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      default='1', help="Show more information.")
    parser.add_option('-q', '--quiet', dest='verbose', action='store_const',
                      const=0, help="Show no extra information.")

    options, args = parser.parse_args()
    if options.clear:
        if args:
            parser.error("No arguments allowed with '--clear'")
        func = clear_site_announce
    else:
        func = set_site_announce

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    try:
        previous, now = func(root, *args)
    except:
        transaction.abort()
        raise
    if options.verbose:
        print 'Before:', previous
        print 'After:', now
    if options.dry_run:
        transaction.abort()
    else:
        transaction.commit()

if __name__ == '__main__':
    main()
