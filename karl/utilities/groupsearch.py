from zope.interface import directlyProvides
from zope.interface import implements

from repoze.bfg.security import effective_principals

from karl.content.interfaces import ICalendarEvent
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IGroupSearchFactory
from karl.models.interfaces import IGroupSearch
from karl.models.interfaces import IPeople
from karl.models.interfaces import IPosts
from karl.models.interfaces import IFiles
from karl.models.interfaces import IPages

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
def events_group_search(context, request, term):
    search = GroupSearch(context, request, [ICalendarEvent], term)
    return search

@groupsearchfactory
def communities_group_search(context, request, term):
    search = GroupSearch(context, request, [ICommunity], term)
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
        q = WeightedQuery(self.term)
        if len(self.interfaces) == 1:
            q.marker = self.interfaces[0].queryTaggedValue('marker')
        criteria['interfaces'] = {'query':self.interfaces, 'operator':'or'}
        criteria['texts'] = q
        criteria['allowed'] = {'query':principals, 'operator':'or'}
        return criteria


try:
    from repoze.pgtextindex.interfaces import IWeightedQuery
except ImportError: # pragma NO COVERAGE
    IWeightedQuery = None


class WeightedQuery(unicode):
    if IWeightedQuery is not None:
        implements(IWeightedQuery)

    weight_factor = 32.0

    A = 1.0
    B = A / weight_factor
    C = B / weight_factor
    D = C / weight_factor

    marker = None

    @property
    def text(self):
        return self
