from karl.utils import find_catalog

def evolve(site):
    """
    Upgrade pgtextindex
    """
    catalog = find_catalog(site)
    index = catalog['texts']
    index.upgrade()
