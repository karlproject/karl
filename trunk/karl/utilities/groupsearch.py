from zope.interface import directlyProvides
from zope.interface import implements

from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IGroupSearchFactory
from karl.models.interfaces import IGroupSearch
from karl.models.interfaces import IPeople
from karl.models.interfaces import IPosts
from karl.models.interfaces import IFiles
from karl.models.interfaces import IPages
from karl.models.interfaces import IOthers

from karl.views.batch import get_catalog_batch_grid

def groupsearchfactory(unwrapped):
    directlyProvides(unwrapped, IGroupSearchFactory)
    return unwrapped

@groupsearchfactory
def people_group_search(context, request, term):
    search = GroupSearch(context, request, [IPeople], term)
    return search

@groupsearchfactory
def pages_group_search(context, request, term):
    search = GroupSearch(context, request, [IPages], term)
    return search

@groupsearchfactory
def posts_group_search(context, request, term):
    search = GroupSearch(context, request, [IPosts], term)
    return search

@groupsearchfactory
def files_group_search(context, request, term):
    search = GroupSearch(context, request, [IFiles], term)
    return search

@groupsearchfactory
def others_group_search(context, request, term):
    search = GroupSearch(context, request, [IOthers], term)
    return search

class GroupSearch:
    implements(IGroupSearch)
    def __init__(self, context, request, interfaces, term, limit=5):
        self.context = context
        self.request = request
        self.interfaces = interfaces
        self.term = term
        self.limit = limit

    def __call__(self):
        criteria = self._makeCriteria()
        criteria['limit'] = self.limit
        searcher = ICatalogSearch(self.context)
        num, docids, resolver = searcher(**criteria)
        return num, docids, resolver

    def get_batch(self):
        return get_catalog_batch_grid(
            self.context, self.request, **self._makeCriteria())

    def _makeCriteria(self):
        principals = effective_principals(self.request)
        # this is always assumed to be a global search; it does no
        # path filtering
        criteria = {}
        criteria['sort_index'] = 'texts'
        criteria['texts'] = self.term
        criteria['interfaces'] = {'query':self.interfaces, 'operator':'or'}
        criteria['allowed'] = {'query':principals, 'operator':'or'}
        return criteria
    

