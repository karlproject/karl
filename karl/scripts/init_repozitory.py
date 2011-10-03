import transaction

from pyramid.traversal import resource_path
from repoze.folder.interfaces import IFolder
from zope.component import queryAdapter

from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IObjectVersion
from karl.utils import find_repo
from karl.utils import get_setting


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Initialize repozitory for objects not yet in repozitory.')
    parser.add_argument('inst', metavar='instance', help='Instance name.')
    parser.set_defaults(func=main, parser=parser)


def main(args):
    site, closer = args.get_root(args.inst)
    repo = find_repo(site)
    if repo is not None:
        init_repo(repo, site)
    transaction.commit()


def init_repo(repo, context):
    if context.__name__ == 'TEMP':
        return

    if IFolder.providedBy(context):
        for child in context.values():
            init_repo(repo, child)

    try:
        repo.history(context, True)
        return
    except:
        # Not in repo
        pass

    version = queryAdapter(context, IObjectVersion)
    if version is not None:
        print "Updating version for %s" % resource_path(context)
        repo.archive(version)

    container = queryAdapter(context, IContainerVersion)
    if container is not None:
        print "Updating container version for %s" % resource_path(context)
        user = getattr(context, 'creator', None)
        if user is None:
            user = get_setting(context, 'system_user', 'admin')
        repo.archive_container(container, user)

    context._p_deactivate() # try not to run out of memory
