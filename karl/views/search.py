# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""Site and community search views"""

from karl.models.adapters import ZopeTextIndexContextualSummarizer
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IContextualSummarizer
from karl.models.interfaces import IGroupSearchFactory
from karl.models.interfaces import IProfile
from karl.utils import coarse_datetime_repr
from karl.utils import find_catalog
from karl.utils import get_content_type_name
from karl.utils import find_community
from karl.utils import find_profiles
from karl.utils import get_content_type_name_and_icon
from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch_grid
from karl.views.interfaces import ILiveSearchEntry
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from repoze.lemonade.interfaces import IContent
from repoze.lemonade.listitem import get_listitems
from repoze.lemonade.content import get_content_types
from simplejson import JSONEncoder
from webob.exc import HTTPBadRequest
from webob import Response
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.index.text.parsetree import ParseError
import datetime
from dateutil.relativedelta import relativedelta
import time


def interface_id(t):
    return '%s_%s' % (t.__module__.replace('.', '_'), t.__name__)


def _iter_userids(context, request, profile_text):
    """Yield userids given a profile text search string."""
    search = ICatalogSearch(context)
    num, docids, resolver = search(
        interfaces=[IProfile], texts=profile_text)
    for docid in docids:
        profile = resolver(docid)
        if profile:
            yield profile.__name__


def make_query(context, request):
    """Given a search request, return a catalog query and a list of terms.
    """
    params = request.params
    query = {}
    terms = []
    body = params.get('body')
    if body:
        query['texts'] = body
        query['sort_index'] = 'texts'
        terms.append(body)

    creator = params.get('creator')
    if creator:
        userids = list(_iter_userids(context, request, creator))
        query['creator'] = {
            'query': userids,
            'operator': 'or',
            }
        terms.append(creator)

    types = params.getall('types')
    if types:
        type_dict = {}
        for t in get_content_types():
            type_dict[interface_id(t)] = t
        ifaces = [type_dict[name] for name in types]
        query['interfaces'] = {
            'query': ifaces,
            'operator': 'or',
            }
        terms.extend(iface.getTaggedValue('name') for iface in ifaces)
    else:
        query['interfaces'] = [IContent]

    tags = filter(None, params.getall('tags'))
    if tags:
        query['tags'] = {
            'query': tags,
            'operator': 'or',
            }
        terms.extend(tags)

    year = params.get('year')
    if year:
        year = int(year)
        begin = coarse_datetime_repr(datetime.datetime(year, 1, 1))
        end = coarse_datetime_repr(datetime.datetime(year, 12, 31, 12, 59, 59))
        query['creation_date'] = (begin, end)
        terms.append(year)

    since = params.get('since')
    if since:
        option = since_options[since]
        since = datetime.datetime.now() - option['delta']
        query['creation_date'] = (coarse_datetime_repr(since), None)
        terms.append(option['name'])

    return query, terms


def get_batch(context, request):
    """Return a batch of results and term sequence for a search request.

    If the user provided no terms, the returned batch will be None and the
    term sequence will be empty.
    """
    batch = None
    terms = ()
    kind = request.params.get("kind")
    if not kind:
        # Search form
        query, terms = make_query(context, request)
        if terms:
            context_path = model_path(context)
            if context_path and context_path != '/':
                query['path'] = {'query': context_path}
            principals = effective_principals(request)
            query['allowed'] = {'query':principals, 'operator':'or'}
            batch = get_catalog_batch_grid(context, request, **query)

    else:
        # LiveSearch
        text_term = request.params.get('body')
        if text_term:
            searcher = queryUtility(IGroupSearchFactory, kind)
            if searcher is None:
                # If the 'kind' we got is not known, return an error
                fmt = "The LiveSearch group %s is not known"
                raise HTTPBadRequest(fmt % kind)

            batch = searcher(context, request, text_term).get_batch()
            terms = [text_term, kind]

    return batch, terms


def get_contextual_summarizer(context):
    catalog = find_catalog(context)
    index = catalog.get('texts')
    return queryAdapter(index, IContextualSummarizer,
                        default=ZopeTextIndexContextualSummarizer(index))


def searchresults_view(context, request):
    request.unicode_errors = 'ignore'
    page_title = 'Search Results'
    api = TemplateAPI(context, request, page_title)
    if ICommunity.providedBy(context):
        layout = api.community_layout
        community = context.title
    else:
        layout = api.generic_layout
        community = None

    batch = None
    terms = ()
    error = None
    params = request.params.copy()
    if 'batch_start' in params:
        del params['batch_start']
    if 'batch_size' in params:
        del params['batch_size']

    type_knob = []
    selected_type = params.get('types')
    for t in get_content_types():
        if t.queryTaggedValue('search_option', False):
            id = interface_id(t)
            query = params.copy()
            query['types'] = id
            type_name = t.getTaggedValue('name')
            type_knob.append({
                'name': type_name,
                'display_text': facet_display_text.get(type_name, type_name),
                'icon': t.queryTaggedValue('icon', 'blue-document.png'),
                'url': model_url(context, request, request.view_name,
                                 query=query),
                'selected': id == selected_type,
            })
    def key_func(option):
        """
        OSF has a particular order they want the type facets to appear in.
        Which is sort of odd, since we use tagged values to decide which facets
        to show.  This func will cause the facets we're expecting to see to
        sort in the order specified by OSF.  Any unexpected facets will sort
        at the end.
        """
        facet_order = {
            'Person': 0,
            'Wiki Page': 1,
            'Blog Entry': 2,
            'Comment': 3,
            'Forum Topic': 4,
            'News Item': 5,
            'File': 6,
            'Event': 7,
            'Community': 8,
        }
        return facet_order.get(option['name'], 100)

    type_knob.sort(key=key_func)
    query = params.copy()
    if 'types' in query:
        del query['types']
    type_knob.insert(0, {
        'name': 'All Content',
        'display_text': 'All Content',
        'icon': None,
        'url': model_url(context, request, request.view_name, query=query),
        'selected': not selected_type,
    })

    since_knob = []
    selected_since = params.get('since')
    for id in since_order:
        option = since_options[id].copy()
        query = params.copy()
        if id is not None:
            query['since'] = id
        elif 'since' in query:
            del query['since']
        option['url'] = model_url(context, request, request.view_name,
                                  query=query)
        option['selected'] = id == selected_since
        since_knob.append(option)

    start_time = time.time()
    try:
        batch, terms = get_batch(context, request)
    except ParseError, e:
        error = 'Error: %s' % e
    else:
        if not terms:
            error = 'No Search Parameters Supplied.'
    finally:
        elapsed = time.time() - start_time

    profiles = find_profiles(context)
    if batch:
        # Flatten the batch into data for use in the ZPT.
        summarizer = get_contextual_summarizer(context)
        text_term = params.get('body')
        results = []
        for doc in batch['entries']:
            description = summarizer(doc, text_term)
            type_name, icon = get_content_type_name_and_icon(doc)
            result = {
                'title': getattr(doc, 'title', '<No Title>'),
                'description': description,
                'url': model_url(doc, request),
                'type': type_name,
                'icon': icon,
                'timeago': doc.modified.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'author': None,
            }

            result_community = find_community(doc)
            if result_community is not None:
                result['community'] = {
                    'title': result_community.title,
                    'url': model_url(result_community, request),
                }
            else:
                result['community'] = None

            if hasattr(doc, 'creator'):
                author = profiles.get(doc.creator)
                if author is not None:
                    result['author'] = {
                        'name': author.title,
                        'url': model_url(author, request),
                    }

            results.append(result)

        total = batch['total']

    else:
        batch = {'batching_required': False}
        results = ()
        total = 0

    return dict(
        api=api,
        layout=layout,
        error=error,
        terms=terms,
        community=community,
        results=results,
        total=total,
        batch_info=batch,
        type_knob=type_knob,
        since_knob=since_knob,
        params=params,
        elapsed='%0.2f' % elapsed
        )

def jquery_livesearch_view(context, request):
    request.unicode_errors = 'ignore'
    try:
        searchterm = request.params.get('val', None)
    except UnicodeDecodeError:
        # Probably windows client didn't set request encoding. Try again.
        request.charset = 'ISO-8859-1'
        searchterm = request.params.get('val', None)

    if searchterm is None:
        # The request forgot to send the key we use to do a search, so
        # make a friendly error message.  Important for the unit test.
        msg = "Client failed to send a 'val' parameter as the searchterm"
        return HTTPBadRequest(msg)

    # maybe do some * checking to verify that we don't have a
    # prefix search < 3 chars

    records = []

    # we return back 5 results for each type of search
    results_per_type = 5

    kind = request.params.get('kind', None)
    if kind is None:
        listitems = get_listitems(IGroupSearchFactory)
    else:
        search_utility = queryUtility(IGroupSearchFactory, kind)
        if search_utility is None:
            msg = "The LiveSearch kind %s is not known" % kind
            return HTTPBadRequest(msg)
        else:
            # simulate a list item for the loop below
            listitems = (dict(component=search_utility),)
            # we'll just have on type of results, so we return back 20 results
            results_per_type = 20
    for listitem in listitems:
        utility = listitem['component']
        factory = utility(context, request, searchterm)
        if factory is None:
            continue
        factory.limit = results_per_type

        try:
            num, docids, resolver = factory()
        except ParseError:
            continue

        for result in (resolver(x) for x in docids):
            if result is None:
                continue
            record = queryMultiAdapter((result, request), ILiveSearchEntry)
            assert record is not None, (
                "Unexpected livesearch result: " + result.__class__.__name__)
            records.append(record)

    result = JSONEncoder().encode(records)
    return Response(result, content_type="application/json")


since_options = {
    None: {
        'name': 'Any time',
        'delta': None,
    },
    'hour': {
        'name': 'Past hour',
        'delta': relativedelta(hours=1),
    },
    'day': {
        'name': 'Past day',
        'delta': relativedelta(days=1),
    },
    'week': {
        'name': 'Past week',
        'delta': relativedelta(weeks=1),
    },
    'month': {
        'name': 'Past month',
        'delta': relativedelta(months=1),
    },
    'year': {
        'name': 'Past year',
        'delta': relativedelta(years=1),
    },
}

since_order = (
    None, 'hour', 'day', 'week', 'month', 'year',
)

facet_display_text = {
    'Person': u'People',
    'Wiki Page': u'Wikis',
    'Blog Entry': u'Blogs',
    'Comment': u'Comments',
    'Forum Topic': u'Forums',
    'News Item': u'News Items',
    'File': u'Files',
    'Event': u'Events',
    'Community': u'Communities',
}
