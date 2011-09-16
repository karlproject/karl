import BTrees
import transaction

from repoze.bfg.traversal import find_model
from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IFolder
from zope.component import queryAdapter

from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IIntranets
from karl.models.interfaces import IObjectVersion
from karl.utils import find_catalog
from karl.utils import find_interface
from karl.utils import find_repo
from karl.utils import get_setting

Set = BTrees.family32.OI.Set


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Initialize repozitory for objects not yet in repozitory.')
    parser.add_argument('--batch-size', type=int, default=500,
                        help='Number of objects to initialize per transaction.')
    parser.add_argument('inst', metavar='instance', help='Instance name.')
    parser.set_defaults(func=main, parser=parser)


def main(args):
    site, closer = args.get_root(args.inst)
    repo = find_repo(site)
    if repo is None:
        args.parser.error("No repository is configured.")

    docids = getattr(site, '_init_repozitory_docids', None)
    if docids is None:
        # Store tuple of (path, docid) in order to guarantee sort order by
        # path, which means children will be after their parents in the set
        # ordering.
        catalog = find_catalog(site)
        docids = Set(catalog.document_map.address_to_docid.items())
        site._init_repozitory_docids = docids

    while docids:
        for i in xrange(min(args.batch_size, len(docids))):
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

    context = find_model(site, path)
    if context.__name__ == 'TEMP':
        return
    if find_interface(context, IIntranets):
        return

    version = queryAdapter(context, IObjectVersion)
    if version is not None:
        print "Updating version for %s" % model_path(context)
        repo.archive(version)

    context._p_deactivate()


def init_container(docid, path, repo, site):
    try:
        repo.container_contents(docid)
        # Already in repo
        return
    except:
        # Not in repo
        pass

    context = find_model(site, path)
    if context.__name__ == 'TEMP':
        return
    if find_interface(context, IIntranets):
        return

    container = queryAdapter(context, IContainerVersion)
    if container is not None:
        print "Updating container version for %s" % model_path(context)
        user = getattr(context, 'creator', None)
        if user is None:
            user = get_setting(context, 'system_user', 'admin')
        repo.archive_container(container, user)

    context._p_deactivate()
