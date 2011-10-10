from pyramid.traversal import resource_path
from repoze.workflow import get_workflow
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog

def evolve(root):
    search = ICatalogSearch(root)
    num, docids, resolver = search(interfaces=[IProfile])
    allowed_index = find_catalog(root)['allowed']
    for docid in docids:
        profile = resolver(docid)
        if profile.security_state != 'inactive':
            continue

        print "Updating acl for %s" % resource_path(profile)
        workflow = get_workflow(IProfile, 'security', profile)
        workflow.reset(profile)
        allowed_index.reindex_doc(docid, profile)

