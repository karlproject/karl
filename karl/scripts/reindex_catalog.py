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

""" Reindex the catalog  """

from karl.scripting import get_default_config
from karl.scripting import open_root
from optparse import OptionParser
from repoze.bfg.traversal import find_model
from zope.component import getUtility
import os
import re
import sys
import transaction

def main():
    parser = OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")
    parser.add_option('-d', '--dry-run', dest='dry_run',
        action="store_true", default=False,
        help="Don't commit the transactions")
    parser.add_option('-i', '--interval', dest='commit_interval',
        action="store", default=200,
        help="Commit every N transactions")
    parser.add_option('-p', '--path', dest='path',
        action="store", default=None, metavar='EXPR',
        help="Reindex only objects whose path matches a regular expression")

    options, args = parser.parse_args()
    if args:
        parser.error("Too many parameters: %s" % repr(args))

    commit_interval = int(options.commit_interval)
    if options.path:
        path_re = re.compile(options.path)
    else:
        path_re = None

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    def commit_or_abort():
        if options.dry_run:
            print '*** aborting ***'
            transaction.abort()
        else:
            print '*** committing ***'
            transaction.commit()

    print 'updating indexes'
    root.update_indexes()
    commit_or_abort()

    catalog = root.catalog

    i = 1

    for path, docid in catalog.document_map.address_to_docid.items():
        if path_re is not None and path_re.match(path) is None:
            continue
        print 'reindexing %s' % path
        try:
            model = find_model(root, path)
        except KeyError:
            print 'error: %s not found' % path
            continue
        catalog.reindex_doc(docid, model)
        if i % commit_interval == 0:
            commit_or_abort()
        i+=1
    commit_or_abort()

if __name__ == '__main__':
    main()
