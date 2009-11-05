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

"""
Move a piece of content to another folder.  Constraints:

- ** DO NOT SEND ALERT EMAILS DURING THIS PROCESS !! **

- All blog entries/comments, not a subset

- Retain the docid, owner, and create/modified dates

- If the owner can't be found, assign to the System User

- Put a <p><em>This ${content type} was originally authored in the
"Information Program Staff Community" community.</em></p> in the top
of the body text.
"""

from karl.security.interfaces import ISecurityWorkflow
from karl.utils import find_catalog
from karl.utils import find_community
from karl.utils import find_users
from karl.views.utils import make_unique_name
from optparse import OptionParser
from osi.scripting import get_default_config
from osi.scripting import open_root
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_model
from repoze.folder.interfaces import IFolder

import logging
import sys
import transaction

log = logging.getLogger(__name__)


def postorder(startnode):

    def visit(node):
        if IFolder.providedBy(node):
            for child in node.values():
                for result in visit(child):
                    yield result
        yield node
        if hasattr(node, '_p_deactivate'):
            # attempt to not run out of memory
            node._p_deactivate()
    return visit(startnode)


def main(argv=sys.argv):
    logging.basicConfig()
    log.setLevel(logging.INFO)

    parser = OptionParser(
        description="Move content to another folder",
        usage="%prog [options] content_path dest_folder",
        )
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")
    parser.add_option('-d', '--dry-run', dest='dry_run',
        action="store_true", default=False,
        help="Don't commit the transaction")
    parser.add_option('-S', '--security-state', dest='security_state',
                      default=None,
                      help="Force workflow transition to given state.  By "
                      "default no transition is performed.")
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error("Source content and destination folder are required")

    config = options.config
    if not config:
        config = get_default_config()
    root, closer = open_root(config)

    try:
        try:
            context = find_model(root, args[0])
        except KeyError:
            parser.error("Source content not found: %s" % args[0])

        try:
            dest = find_model(root, args[1])
        except KeyError:
            parser.error("Destination folder not found: %s" % args[1])

        src_community = find_community(context)

        catalog = find_catalog(root)
        assert catalog is not None
        users = find_users(root)
        assert users is not None

        if src_community is not None:
            move_header = ('<p><em>This was originally authored '
                           'in the "%s" community.</em></p>' %
                           src_community.title)
        else:
            move_header = ''

        src_folder = context.__parent__
        name = context.__name__

        log.info("Moving %s", model_path(context))
        for obj in postorder(context):
            if hasattr(obj, 'docid'):
                docid = obj.docid
                catalog.document_map.remove_docid(docid)
                catalog.unindex_doc(docid)
        del src_folder[name]

        if (context.creator != 'admin'
                and users.get_by_id(context.creator) is None):
            # give the entry to the system admin
            log.warning(
                "User %s not found; reassigning to admin", context.creator)
            context.creator = 'admin'

        if name in dest:
            name = make_unique_name(dest, dest.title)

        dest[name] = context
        for obj in postorder(context):
            if hasattr(obj, 'docid'):
                docid = obj.docid
                catalog.document_map.add(model_path(obj), docid)
                catalog.index_doc(docid, obj)

        if options.security_state is not None:
            wf = ISecurityWorkflow(context)
            if getattr(context, 'security_state',
                       None) != options.security_state:
                wf.execute(None, options.security_state)

        if hasattr(context, 'text'):
            context.text = "%s\n%s" % (move_header, context.text)

    except:
        transaction.abort()
        raise

    else:
        if options.dry_run:
            log.info("Aborting transaction.")
            transaction.abort()
        else:
            log.info("Committing transaction.")
            transaction.commit()


if __name__ == '__main__':
    main()
