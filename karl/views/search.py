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

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IGroupSearchFactory
from karl.models.interfaces import IProfile
from karl.utils import coarse_datetime_repr
from karl.utils import get_content_type_name
from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch_grid
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from repoze.lemonade.interfaces import IContent
from repoze.lemonade.listitem import get_listitems
from repoze.lemonade.content import get_content_types
from simplejson import JSONEncoder
from webob.exc import HTTPBadRequest
from webob import Response
from zope.component import queryUtility
from zope.index.text.parsetree import ParseError
import datetime


def advancedsearch_view(context, request):

    page_title = 'Advanced Search'
    api = TemplateAPI(context, request, page_title)

    type_choices = []
    for t in get_content_types():
        if t.queryTaggedValue('search_option', False):
            # this content type should be on the list of types to search
            iid = interface_id(t)
            name = t.queryTaggedValue('name', iid)
            type_choices.append((name, iid))
    type_choices.sort()

    this_year = datetime.datetime.now().year
    year_choices = [str(i) for i in range(2007, this_year+1)]

    return render_template_to_response(
        'templates/advancedsearch.pt',
        api=api,
        post_url=model_url(context, request, "searchresults.html"),
        type_choices=type_choices,
        year_choices=year_choices,
        )


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

    tags = params.getall('tags')
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


def searchresults_view(context, request):
    # We can get here from either the LiveSearch or advanced search
    # screens

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

    try:
        batch, terms = get_batch(context, request)
    except ParseError, e:
        error = 'Error: %s' % e
    else:
        if not terms:
            error = 'No Search Parameters Supplied.'

    if batch:
        # Flatten the batch into data for use in the ZPT.
        results = []
        for result in batch['entries']:
            try:
                description = result.description[0:300]
            except AttributeError:
                description = ''
            result = {
                'title': getattr(result, 'title', '<No Title>'),
                'description': description,
                'url': model_url(result, request),
                'type': get_content_type_name(result),
                }
            results.append(result)
        total = batch['total']
    else:
        batch = {'batching_required': False}
        results = ()
        total = 0

    return render_template_to_response(
        'templates/searchresults.pt',
        api=api,
        layout=layout,
        error=error,
        terms=terms,
        community=community,
        results=results,
        total=total,
        batch_info=batch,
        )


class LivesearchResults(list):

    def __init__(self):
        list.__init__(self)
        self.set_header('')

    def set_header(self, header, pre="", post=""):
        self.header = header
        self.pre = pre
        self.post = post

    def append_to(self, title, href, rowclass):
        if self.header:
            rowclass += ' hasheader'
        self.append(dict(
                rowclass = rowclass,
                header = self.header,
                title = title,
                href = href,
                pre = self.pre,
                post = self.post,
                ))
        self.set_header('')


def jquery_livesearch_view(context, request):
    # Prefix search is with a wildcard at the end
    searchterm = request.params.get('val', None)

    if searchterm is None:
        # The request forgot to send the key we use to do a search, so
        # make a friendly error message.  Important for the unit test.
        msg = "Client failed to send a 'val' parameter as the searchterm"
        return HTTPBadRequest(msg)
    else:
        searchterm = searchterm + '*'

    records = LivesearchResults()
    principals = effective_principals(request)

    site_path = model_path(context)

    records.set_header('',
        pre = '<div class="header"></div>',
        )
    records.append_to(
        rowclass = 'showall',
        title = 'Show All',
        href = model_url(context, request, 'searchresults.html',
                    query = {'body':searchterm},
                    ),
            )

    for listitem in get_listitems(IGroupSearchFactory):
        utility = listitem['component']

        factory = utility(context, request, searchterm)

        if factory is None:
            continue

        try:
            num, docids, resolver = factory()
        except ParseError:
            continue

        groupname = listitem['title']

        records.set_header(groupname,
            pre = '<div class="header">%s</div>' % (groupname, ),
            )

        results = filter(None, map(resolver, docids))

        qs = {'body':searchterm, 'kind':groupname}
        sr_href = model_url(context, request, 'searchresults.html', query=qs)

        for result in results:
            records.append_to(
                rowclass = 'result',
                title = getattr(result, 'title', '<No Title>'),
                href = model_url(result, request),
                )

        if results:
            records.append_to(
                rowclass = 'showall',
                title = 'Show All',
                href = sr_href,
                )
        else:
            records.append_to(
                rowclass = 'noresult',
                title = 'No Result',
                href = sr_href,
                )

    result = JSONEncoder().encode(list(records))
    return Response(result, content_type="application/x-json")
