
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.security.interfaces import ISecurityWorkflow
from optparse import OptionParser
from repoze.bfg.traversal import traverse
import os
import re
import sys
import transaction

"""
Make arbitrary content private in a Karl3 site.  Operates on a list
of paths which can either come as arguments or from stdin.  If no arguments
are present, reads list from stdin.
"""    
import logging
LOGGER = "mkprivate"
log = logging.getLogger(LOGGER)

def main():
    logging.basicConfig()
    log.setLevel(logging.INFO)
    
    parser = OptionParser(description=__doc__,)
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to etc/karl.ini")
    parser.add_option('-d', '--dry-run', dest='dry_run', 
        action="store_true", default=False,
        help="Don't commit the transaction")
    
    options, args = parser.parse_args()
    dry_run = options.dry_run

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    if args:
        paths = args
    else:
        paths = sys.stdin.xreadlines()

    for path in paths:
        _mk_private(root, path.strip())
        
    if dry_run:
        transaction.abort()
    else:
        transaction.commit()

    log.info("All done.")
    
multi_hyphens = re.compile('-+')
elide = re.compile('[^\w/\.-]')
def _mk_private(root, path):
    _path = path
    traversal = traverse(root, path)
    context = traversal['context']
    if traversal['view_name'] or not context:
        # Our paths might be coming from Karl2 which had different rules
        # for ids.  Try making the path lower case and replacing spaces
        # with hyphens.
        path = path.lower().replace(' ', '-')
        path = elide.sub('', path)
        path = multi_hyphens.sub('-', path)
        traversal = traverse(root, path)
        context = traversal['context']
        
    if traversal['view_name'] or not context:
        log.error("No object at path: %s", _path)
        return
    
    sec = ISecurityWorkflow(context)
    sec.updateState(sharing=True)
    log.info("Set to private: %s", path)