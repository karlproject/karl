import BTrees
import sys
import transaction

from sqlalchemy.orm.exc import NoResultFound

from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from zope.component import queryAdapter

from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IIntranets
from karl.models.interfaces import IObjectVersion
from karl.scripting import create_karl_argparser
from karl.utils import find_catalog
from karl.utils import find_interface
from karl.utils import find_repo
from karl.utils import get_setting

Set = BTrees.family32.OI.Set

def main(argv=sys.argv):
    parser =  create_karl_argparser(description="Change creator of content.")
    parser.add_argument('--batch-size', type=int, default=500,
                        help='Number of objects to initialize per transaction.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    repo = find_repo(root)
    if repo is None:
        args.parser.error("No repository is configured.")
    init_repozitory(repo, root, args.batch_size)
    closer()


def init_repozitory(repo, site, batch_size=500):
    docids = getattr(site, '_init_repozitory_docids', None)
    if docids is None:
        # Store tuple of (path, docid) in order to guarantee sort order by
        # path, which means children will be after their parents in the set
        # ordering.
        catalog = find_catalog(site)
        docids = Set(catalog.document_map.address_to_docid.items())
        site._init_repozitory_docids = docids

    while docids:
        for i in xrange(min(batch_size, len(docids))):
            # Iterate backwards over documents so that children are processed
            # before their parents, since adding a container requires that its
            # children already be added.
            path, docid = docids[-1]
            init_history(docid, path, repo, site)
            init_container(docid, path, repo, site)
            docids.remove((path, docid))
        transaction.commit()

    del site._init_repozitory_docids
    transaction.commit()


def init_history(docid, path, repo, site):
    if repo.history(docid, True):
        # Already in repo
        return

    context = find_resource(site, path)
    if context.__name__ == 'TEMP':
        return
    if find_interface(context, IIntranets):
        return

    version = queryAdapter(context, IObjectVersion)
    if version is not None:
        print "Updating version for %s" % resource_path(context)
        repo.archive(version)

    context._p_deactivate()


def init_container(docid, path, repo, site):
    try:
        repo.container_contents(docid)
        # Already in repo
        return
    except NoResultFound:
        # Not in repo
        pass

    context = find_resource(site, path)
    if context.__name__ == 'TEMP':
        return
    if find_interface(context, IIntranets):
        return

    container = queryAdapter(context, IContainerVersion)
    if container is not None:
        print "Updating container version for %s" % resource_path(context)
        user = getattr(context, 'creator', None)
        if user is None:
            user = get_setting(context, 'system_user', 'admin')
        repo.archive_container(container, user)

    context._p_deactivate()
