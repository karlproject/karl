from pyramid.traversal import model_path
from repoze.lemonade.content import get_content_type
from repoze.workflow import get_workflow

from karl.security.workflow import postorder
from karl.workflow import _reindex


def evolve(site):
    offices = site.get('offices')
    if offices is None:
        return

    for doc in postorder(offices):
        if hasattr(doc, '__custom_acl__'):
            continue

        try:
            ct = get_content_type(doc)
        except:
            continue

        if ct is None:
            continue

        wf = get_workflow(ct, 'security', doc)
        if wf is None:
            continue

        if wf.name != 'intranet-content':
            continue

        print 'Resetting workflow for', model_path(doc)
        wf.reset(doc)

    _reindex(offices)
