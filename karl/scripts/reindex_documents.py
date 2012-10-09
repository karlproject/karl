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

""" Reindex file documents """
import re

from karlserve.instance import set_current_instance
from karl.models.catalog import reindex_doc_text
import transaction


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Reindex text from all site files.')
    parser.add_argument('-i', '--interval', dest='commit_interval',
        help='Commit every n transactions (default 200)')
    parser.add_argument('-p', '--path', dest='path',
        help='Reindex only objects whose path matches a regular expression')
    parser.add_argument('--dry-run', dest='dryrun',
        action='store_true',
        help="Don't actually commit the transaction")
    helpers['config_choose_instances'](parser)
    parser.set_defaults(func=main, parser=parser,
        commit_interval=200, path=None, dryrun=False)


def main(args):
    for instance in args.instances:
        reindex(args, instance)

def output(msg):
    print msg 

def reindex(args, instance):
    root, closer = args.get_root(instance)
    set_current_instance(instance)
    commit_interval = int(args.commit_interval)
    if args.path:
        path_re = re.compile(args.path)
    else:
        path_re = None
    reindex_doc_text(root, path_re=path_re, commit_interval=commit_interval,
        dry_run=args.dryrun, output=output, transaction=transaction)
