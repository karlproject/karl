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

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import IPeopleDirectory
from karl.models.interfaces import IPeopleReport
from karl.models.interfaces import IPeopleReportGroup
from karl.utils import find_profiles
from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch
from karl.views.batch import get_catalog_batch_grid
from karl.views.utils import convert_to_script
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.security import Unauthorized
from repoze.bfg.traversal import lineage
from repoze.bfg.url import model_url
from simplejson import JSONEncoder
from webob import Response
from webob.exc import HTTPFound
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr
from zope.index.text.parsetree import ParseError
import csv
import math
import StringIO


def peopledirectory_view(context, request):
    # show the first accessible tab
    for section_id in context.order:
        section = context[section_id]
        if has_permission('view', section, request):
            return section_view(section, request)
    raise Unauthorized("No accessible sections")

def find_peopledirectory(context):
    for obj in lineage(context):
        if IPeopleDirectory.providedBy(obj):
            return obj
    raise AssertionError("No IPeopleDirectory found")

def get_tabs(peopledir, request, current_sectionid):
    """Return a list of dictionaries containing tabs to display in the UI"""
    res = []
    for sectionid in peopledir.order:
        section = peopledir[sectionid]
        if not has_permission('view', section, request):
            continue
        res.append({
            'href': model_url(section, request),
            'title': section.tab_title,
            'selected': current_sectionid == section.__name__,
            })
    return res

def render_report_group(group, request, css_class=''):
    """Produce the HTML for a report group on a section index page"""
    res = []
    if group.title:
        res.append('<h3>%s</h3>' % escape(group.title))
    if css_class:
        res.append('<ul class=%s>' % quoteattr(css_class))
    else:
        res.append('<ul>')
    for obj in group.reports:
        if IPeopleReport.providedBy(obj):
            url = model_url(obj, request)
            res.append('<li><a href=%s class=%s>%s</a></li>' % (
                quoteattr(url),
                quoteattr(obj.css_class),
                escape(obj.link_title)))
        elif IPeopleReportGroup.providedBy(obj):
            html = render_report_group(obj, request)
            res.append(html)
    res.append('</ul>')
    return '\n'.join(res)

def get_actions(context, request):
    actions = []
    profiles = find_profiles(context)
    if has_permission('administer', profiles, request):
        actions.append(('Add User', 'add.html'))
    return actions

def section_view(context, request):
    if not context.columns:
        if len(context) == 1:
            # display the single report as the content of this section
            report = context.values()[0]
            if has_permission('view', report, request):
                return report_view(report, request)
            raise Unauthorized("Report is not accessible")

    api = TemplateAPI(context, request, context.title)
    peopledir = find_peopledirectory(context)
    peopledir_tabs = get_tabs(peopledir, request, context.__name__)
    column_html = [render_report_group(column, request, 'column')
        for column in context.columns]
    return render_template_to_response(
        'templates/people_section.pt',
        api=api,
        peopledir=peopledir,
        peopledir_tabs=peopledir_tabs,
        column_html=column_html,
        actions=get_actions(context, request),
        )

def report_view(context, request):
    client_json_data = {
        'grid_data': get_grid_data(context, request),
        }
    api = TemplateAPI(context, request, context.title)
    peopledir = find_peopledirectory(context)
    section = context.__parent__
    peopledir_tabs = get_tabs(peopledir, request, section.__name__)

    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)
    kw, qualifiers = get_search_qualifiers(request)

    descriptions = get_report_descriptions(context)
    print_url = model_url(context, request, 'print.html', **kw)
    csv_url = model_url(context, request, 'csv', **kw)
    pictures_url = model_url(context, request, 'picture_view.html', **kw)

    return render_template_to_response(
        'templates/people_report.pt',
        api=api,
        peopledir=peopledir,
        peopledir_tabs=peopledir_tabs,
        head_data=convert_to_script(client_json_data),
        descriptions=descriptions,
        letters=letter_info,
        print_url=print_url,
        csv_url=csv_url,
        pictures_url=pictures_url,
        qualifiers=qualifiers,
        actions=get_actions(context, request),
        )

def jquery_grid_view(context, request):
    sort_on = request.params.get('sortColumn', None)
    reverse = request.params.get('sortDirection') == 'desc'
    payload = get_grid_data(context, request,
        start=int(request.params['start']),
        limit=int(request.params['limit']),
        sort_on=sort_on,
        reverse=reverse,
        )
    result = JSONEncoder().encode(payload)
    return Response(result, content_type="application/x-json")

def get_column_jsdata(columns, max_width):
    """Produce a list of dictionaries about report columns for jquery"""
    total_weight = sum(c.weight for c in columns)
    res = []
    for c in columns:
        width = int(math.floor(c.weight * max_width / total_weight))
        res.append({
            'id': c.id,
            'label': c.title,
            'width': width,
            })
    return res

def profile_photo_rows(entries, request, api, columns=3):
    """Arrange profiles in a series of rows.

    Produces {'profile', 'photo_url', 'url'} for each profile.
    """
    row = []
    for profile in entries:
        photo = profile.get_photo()
        if photo is not None:
            photo_url = model_url(photo, request)
        else:
            photo_url = api.static_url + "/images/defaultUser.gif"
        url = model_url(profile, request)
        row.append({'profile': profile, 'photo_url': photo_url, 'url': url})

        if len(row) >= columns:
            yield row
            row = []
    if row:
        yield row

def picture_view(context, request):
    sort_index = COLUMNS[context.columns[0]].sort_index

    kw = get_report_query(context, request)
    try:
        batch_info = get_catalog_batch_grid(
            context, request, batch_size=12, sort_index=sort_index, **kw)
    except ParseError, e:
        # user entered something weird in the text search box.
        # show no results.
        batch_info = {'entries': [], 'total': 0, 'batching_required': False}

    api = TemplateAPI(context, request, context.title)
    rows = profile_photo_rows(batch_info['entries'], request, api)

    peopledir = find_peopledirectory(context)
    section = context.__parent__
    peopledir_tabs = get_tabs(peopledir, request, section.__name__)

    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)
    kw, qualifiers = get_search_qualifiers(request)

    descriptions = get_report_descriptions(context)
    print_url = model_url(context, request, 'print.html', **kw)
    csv_url = model_url(context, request, 'csv', **kw)
    tabular_url = model_url(context, request, **kw)

    return render_template_to_response(
        'templates/people_pictures.pt',
        api=api,
        peopledir=peopledir,
        peopledir_tabs=peopledir_tabs,
        letters=letter_info,
        descriptions=descriptions,
        print_url=print_url,
        csv_url=csv_url,
        tabular_url=tabular_url,
        qualifiers=qualifiers,
        batch_info=batch_info,
        rows=rows,
        )

def get_search_qualifiers(request):
    """Gets search qualifiers from the request.

    Returns ({'query' or empty}, [qualifier description text]).
    """
    query = {}
    qualifiers = []

    key = 'lastnamestartswith'
    if key in request.params:
        query[key] = request.params[key]
        qualifiers.append("Last names that begin with '%s'" % query[key])

    key = 'body'
    if key in request.params:
        query[key] = request.params[key]
        qualifiers.append('Search for "%s"' % query[key])

    if query:
        kw = {'query': query}
    else:
        kw = {}

    return kw, qualifiers

def get_report_query(report, request):
    """Produce query parameters for a catalog search"""
    kw = {}
    if report.query:
        kw.update(report.query)
    for catid, values in report.filters.items():
        kw['category_%s' % catid] = {'query': values, 'operator': 'or'}
    principals = effective_principals(request)
    kw['allowed'] = {'query': principals, 'operator': 'or'}
    letter = request.params.get('lastnamestartswith')
    if letter:
        kw['lastnamestartswith'] = letter.upper()
    body = request.params.get('body')
    if body:
        kw['texts'] = body.strip() + '*'
    return kw

def get_grid_data(context, request, start=0, limit=12,
        sort_on=None, reverse=False, width=880):
    """Gets the data for the jquery report grid.
    """
    columns = [COLUMNS[colid] for colid in context.columns]
    columns_jsdata = get_column_jsdata(columns, width)
    if sort_on is None:
        sort_on = columns[0].id
    sort_index = COLUMNS[sort_on].sort_index

    kw = get_report_query(context, request)
    try:
        batch = get_catalog_batch(context, request,
            batch_start=start,
            batch_size=limit,
            sort_index=sort_index,
            reverse=reverse,
            **kw
            )
    except ParseError, e:
        # user entered something weird in the text search box.
        # show no results.
        batch = {'entries': [], 'total': 0}

    records = []
    for profile in batch['entries']:
        record = [col.render_html(profile, request) for col in columns]
        records.append(record)

    kw, _ = get_search_qualifiers(request)
    fetch_url = model_url(context, request, 'jquery_grid', **kw)

    payload = dict(
        fetch_url=fetch_url,
        columns=columns_jsdata,
        records=records,
        totalRecords=batch['total'],
        batchSize=limit,
        width=width,
        sortColumn=sort_on,
        sortDirection=(reverse and 'desc' or 'asc'),
        )
    return payload

def get_report_descriptions(report):
    descriptions = []  # [(value title, description)]
    categories = find_peopledirectory(report).categories
    for catid, values in report.filters.items():
        cat = categories.get(catid)
        if cat:
            for value in values:
                catitem = cat.get(value)
                if catitem:
                    descriptions.append((catitem.title, catitem.description))
    descriptions.sort()
    return [d for (t, d) in descriptions]

def text_dump(report, request):
    """Generates a table of text for a report.

    Yields a header row, followed by data rows.
    """
    columns = [COLUMNS[colid] for colid in report.columns]
    sort_on = columns[0].id
    sort_index = COLUMNS[sort_on].sort_index
    header = [column.title for column in columns]
    yield header

    kw = get_report_query(report, request)
    searcher = ICatalogSearch(report)
    total, docids, resolver = searcher(sort_index=sort_index, **kw)

    for docid in docids:
        profile = resolver(docid)
        if profile is None:
            continue
        record = [column.render_text(profile) for column in columns]
        yield record

def csv_view(context, request):
    dumper = text_dump(context, request)
    csv_file = StringIO.StringIO()
    writer = csv.writer(csv_file)
    for record in dumper:
        writer.writerow([s.encode("utf-8") for s in record])

    response = Response(csv_file.getvalue())
    response.content_type = 'application/x-csv'
    # suggest a filename based on the report name
    response.headers.add('Content-Disposition',
        'attachment;filename=%s.csv' % str(context.__name__))
    return response

def print_view(context, request):
    dumper = text_dump(context, request)
    header = dumper.next()
    api = TemplateAPI(context, request, context.title)

    return render_template_to_response(
        'templates/people_print.pt',
        api=api,
        header=header,
        rows=dumper,
    )

def add_user_view(context, request):
    profiles = find_profiles(context)
    return HTTPFound(location=model_url(profiles, request, 'add.html'))


class ReportColumn(object):

    def __init__(self, id, title, sort_index=None, weight=1.0):
        self.id = id
        self.title = title
        if sort_index is None:
            sort_index = id
        self.sort_index = sort_index
        self.weight = weight

    def render_text(self, profile):
        return unicode(getattr(profile, self.id, ''))

    def render_html(self, profile, request):
        value = self.render_text(profile)
        if not value:
            return '&nbsp;'
        else:
            return escape(value)

class NameColumn(ReportColumn):

    def render_text(self, profile):
        return unicode(profile.title)

    def render_html(self, profile, request):
        value = unicode(profile.title)
        url = model_url(profile, request)
        return '%s<a href=%s style="display: none;"/>' % (
            escape(value), quoteattr(url))

class PhoneColumn(ReportColumn):

    def render_text(self, profile):
        value = unicode(getattr(profile, self.id, ''))
        ext = getattr(profile, 'extension', None)
        if ext and ext.strip():
            value += ' x %s' % ext
        return value

COLUMNS = {
    'name': NameColumn('name', 'Name', sort_index='lastfirst'),
    'department': ReportColumn('department', 'Department'),
    'email': ReportColumn('email', 'Email'),
    'location': ReportColumn('location', 'Location'),
    'organization': ReportColumn('organization', 'Organization'),
    'phone': PhoneColumn('phone', 'Phone'),
    'position': ReportColumn('position', 'Position'),
    }
