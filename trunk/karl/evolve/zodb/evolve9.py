from repoze.bfg.authorization import Allow
from repoze.bfg.traversal import model_path

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.security.policy import DELETE_COMMUNITY
from karl.utils import find_catalog

def update_acl(context):
    acl = context.__acl__
    new_acl = []
    for ace in acl:
        allow, who, what = ace
        if allow == Allow and who == 'group.KarlAdmin':
            what = what + (DELETE_COMMUNITY,)
            ace = (allow, who, what)
        new_acl.append(ace)
    context.__acl__ = new_acl

def evolve(site):
    print "Updating acl for /"
    update_acl(site)

    catalog = find_catalog(site)
    search = ICatalogSearch(site)
    cnt, docids, resolver = search(interfaces=[ICommunity])
    for docid in docids:
        obj = resolver(docid)
        if obj is None:
            continue # Work around catalog bug
        print "Updating acl for %s" % model_path(obj)
        update_acl(obj)
