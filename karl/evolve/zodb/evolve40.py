from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IFolder
from zope.component import queryAdapter

from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IObjectVersion
from karl.utils import find_repo
from karl.utils import get_setting


def evolve(site):
    """
    Initialize repozitory.
    """
    repo = find_repo(site)
    if repo is not None:
        init_repo(repo, site)


def init_repo(repo, context):
    if context.__name__ == 'TEMP':
        return

    if IFolder.providedBy(context):
        for child in context.values():
            init_repo(repo, child)

    from repozitory.archive import Archive
    assert isinstance(repo, Archive)
    version = queryAdapter(context, IObjectVersion)
    if version is not None:
        try:
            repo.history(context.docid, True)
            # Already in repo
        except:
            # Not already in repo
            print "Updating version for %s" % model_path(context)
            repo.archive(version)

    container = queryAdapter(context, IContainerVersion)
    if container is not None:
        try:
            repo.container_contents(context.docid)
            # Already in repo
        except:
            # Not already in repo
            print "Updating container version for %s" % model_path(context)
            user = getattr(context, 'creator', None)
            if user is None:
                user = get_setting(context, 'system_user', 'admin')
            repo.archive_container(container, user)

    context._p_deactivate() # try not to run out of memory
