from zope.interface import directlyProvides
from zope.interface import implements

from pyramid.security import effective_principals
from pyramid.traversal import resource_path
from repoze.lemonade.interfaces import IContent

from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import IForumTopic
from karl.content.interfaces import INewsItem
from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IWikiPage
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IComment
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IGroupSearchFactory
from karl.models.interfaces import IGroupSearch
from karl.models.interfaces import IPeople
from karl.models.interfaces import IPosts
from karl.models.interfaces import IFiles
from karl.models.interfaces import IPages

import logging
logger = logging.getLogger(__name__)

def groupsearchfactory(advanced_search=True, livesearch=True,
                       live_to_advanced=None, icon='blue-document.png'):
    def wrapper(unwrapped):
        directlyProvides(unwrapped, IGroupSearchFactory)
        unwrapped.advanced_search = advanced_search
        unwrapped.livesearch = livesearch
        unwrapped.livesearch_all = True
        unwrapped.live_to_advanced = live_to_advanced
        unwrapped.icon = icon
        return unwrapped
    return wrapper

@groupsearchfactory(icon='user.png')
def people_group_search(context, request, term):
    search = GroupSearch(context, request, [IPeople], term)
    return search

@groupsearchfactory(advanced_search=False, live_to_advanced='wiki',
                    icon='wiki.png')
def pages_group_search(context, request, term):
    search = GroupSearch(context, request, [IPages], term)
    return search

@groupsearchfactory(livesearch=False, icon='wiki.png')
def wiki_group_search(context, request, term):
    search = GroupSearch(context, request, [IWikiPage], term)
    return search

@groupsearchfactory(advanced_search=False, live_to_advanced='blog',
                    icon='blog.png')
def posts_group_search(context, request, term):
    search = GroupSearch(context, request, [IPosts], term)
    return search

@groupsearchfactory(livesearch=False, icon='blog.png')
def blog_group_search(context, request, term):
    search = GroupSearch(context, request, [IBlogEntry], term)
    return search

@groupsearchfactory(livesearch=False, icon='quill.png')
def comments_group_search(context, request, term):
    search = GroupSearch(context, request, [IComment], term)
    return search

@groupsearchfactory(livesearch=False, icon='blue-document.png')
def forums_group_search(context, request, term):
    search = GroupSearch(context, request, [IForumTopic], term)
    return search

@groupsearchfactory(livesearch=False, icon='newspaper.png')
def news_group_search(context, request, term):
    search = GroupSearch(context, request, [INewsItem], term)
    return search

@groupsearchfactory(icon='blue-document-text.png')
def files_group_search(context, request, term):
    search = GroupSearch(context, request, [IFiles], term)
    return search

@groupsearchfactory(icon='calendar-select.png')
def events_group_search(context, request, term):
    search = GroupSearch(context, request, [ICalendarEvent], term)
    return search

@groupsearchfactory(icon='building.png')
def communities_group_search(context, request, term):
    search = GroupSearch(context, request, [ICommunity], term)
    return search

@groupsearchfactory(livesearch=False, icon='referencemanual_icon.gif')
def manuals_group_search(context, request, term):
    search = GroupSearch(context, request, [], term, [IReferenceManual])
    return search

@groupsearchfactory()
def default_group_search(context, request, term):
    search = GroupSearch(context, request, [], term)
    return search

class GroupSearch:
    implements(IGroupSearch)
    def __init__(self, context, request, interfaces, term,
                 containment=None, limit=5):
        self.context = context
        self.request = request
        self.interfaces = interfaces
        self.term = term
        self.containment = containment
        if containment is not None:
            logger.info('GroupSearch containment %r', containment)
        self.limit = limit
        self.criteria = self._makeCriteria()

    def __call__(self):
        criteria = self.criteria.copy()
        criteria['limit'] = self.limit
        searcher = ICatalogSearch(self.context)
        num, docids, resolver = searcher(**criteria)
        return num, docids, resolver

    def _makeCriteria(self):
        principals = effective_principals(self.request)
        # this is always assumed to be a global search; it does no
        # path filtering
        criteria = {}
        if self.term:
            criteria['sort_index'] = 'texts'
            criteria['texts'] = self.term
        interfaces = self.interfaces
        if not interfaces:
            interfaces = [IContent]
        criteria['interfaces'] = {'query':interfaces, 'operator':'or'}
        criteria['allowed'] = {'query':principals, 'operator':'or'}
        containment = self.containment
        if containment:
            criteria['containment'] = {'query': containment, 'operator': 'or'}
        if self.context.__parent__: # if context is not site root
            criteria['path'] = resource_path(self.context)
        return criteria


class IntranetGroupSearch(GroupSearch):
    implements(IGroupSearch, IGroupSearchFactory)

    advanced_search = False
    livesearch = True
    livesearch_all = False
    live_to_advanced = ''
    icon = 'blue-document.png'
    interfaces = ()
    containment = None

    def __init__(self, context, request, term):
        self.context = context
        self.request = request
        self.term = term
        self.criteria = self._makeCriteria()
        if term:
            self.criteria['texts'].marker = 'Intranet'


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
    cache_enabled = True
    cache = None

    @property
    def text(self):
        return self

    def __getstate__(self):
        """Don't include the cache in the pickled state."""
        return None

    def __setstate__(self, state):
        pass
