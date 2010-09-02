from karl.content.interfaces import IForumTopic
from karl.models.interfaces import ICatalogSearch
from karl.security.workflow import has_custom_acl
from repoze.bfg.traversal import find_root
from repoze.bfg.traversal import model_path
from repoze.workflow import get_workflow

def evolve(context):
    root = find_root(context)
    searcher = ICatalogSearch(root)
    total, docids, resolver = searcher(interfaces=[IForumTopic])
    count = 0
    workflow = get_workflow(IForumTopic, 'security')
    for docid in docids:
        topic = resolver(docid)
        if has_custom_acl(topic):
            continue # don't mess with objects customized via edit_acl
        try:
            state, msg = workflow.reset(topic)
        except:
            print "ERROR while resetting topic workflow: %s" % model_path(topic)
        else:
            print "Reset topic workflow: %s" % model_path(topic)
            count += 1
    print "Updated %d forum topic workflows" % count
