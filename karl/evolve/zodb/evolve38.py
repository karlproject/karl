from repoze.bfg.traversal import model_path
from repoze.folder.interfaces import IFolder
from zope.component import queryAdapter

from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IObjectVersion
from karl.scripts.init_repozitory import init_repozitory
from karl.utils import find_repo
from karl.utils import get_setting


def evolve(site):
    """
    Initialize repozitory.
    """
    repo = find_repo(site)
    if repo is not None:
        init_repozitory(repo, site)
