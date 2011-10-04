from karl.scripts.init_repozitory import init_repozitory
from karl.utils import find_repo


def evolve(site):
    """
    Initialize repozitory.
    """
    repo = find_repo(site)
    if repo is not None:
        init_repozitory(repo, site)
