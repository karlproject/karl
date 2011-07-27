from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IFolder
from repozitory.interfaces import IContainerVersion
from repozitory.interfaces import IObjectVersion
from zope.component import queryAdapter

from karl.utils import find_repo
from karl.utils import get_setting


def evolve(site):
    """
    Initialize repozitory.
    """
    has_repo = get_setting(site, 'repozitory_db_string') is not None
    if has_repo:
        repo = find_repo(site)
        init_repo(repo, site)


def init_repo(repo, context):
    if IFolder.providedBy(context):
        for child in context.values():
            init_repo(repo, child)

    version = queryAdapter(context, IObjectVersion)
    if version is not None:
        print "Updating version for %s" % model_path(context)
        repo.archive(version)

    container = queryAdapter(context, IContainerVersion)
    if container is not None:
        print "Updating container version for %s" % model_path(context)
        repo.archive_container(container, context.creator)

    context._p_deactivate() # try not to run out of memory
