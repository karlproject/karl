from pyramid.traversal import resource_path
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog
from karl.utils import find_profiles

def evolve(root):
    former_id = 'formeruser'

    profiles = find_profiles(root)
    search = ICatalogSearch(root)
    catalog = find_catalog(root)
    creators = catalog['creator']._fwd_index.keys()
    modifiers = catalog['modified_by']._fwd_index.keys()
    userids = set(creators) | set(modifiers)
    for userid in userids:
        if userid not in profiles:
            if former_id not in profiles:
                workflow = get_workflow(IProfile, 'security')
                former_id = make_unique_name(profiles, 'formeruser')

                print "Creating profile for former user content:", former_id
                former_profile = create_content(
                    IProfile, firstname='Former', lastname='User'
                )
                profiles[former_id] = former_profile
                workflow.initialize(former_profile)
                workflow.transition_to_state(former_profile, None, 'inactive')

            count, docids, resolver = search(creator=userid)
            for docid in docids:
                doc = resolver(docid)
                print "Updating 'creator' for", resource_path(doc)
                doc.creator = former_id


            count, docids, resolver = search(modified_by=userid)
            for docid in docids:
                doc = resolver(docid)
                print "Updating 'modified_by' for", resource_path(doc)
                doc.modified_by = former_id
