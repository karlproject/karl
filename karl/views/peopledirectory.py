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
import csv
import formish
import math
import schemaish
import StringIO
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr
from urllib import basejoin

from lxml import etree
from pyramid.exceptions import Forbidden
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import resource_path
from pyramid.url import resource_url
from simplejson import JSONEncoder
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from zope.interface import providedBy
from validatish import validator
from validatish import validate
from zope.index.text.parsetree import ParseError

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import IPeopleCategories
from karl.models.interfaces import IPeopleCategory
from karl.models.interfaces import IPeopleDirectory
from karl.models.interfaces import IPeopleReport
from karl.models.interfaces import IPeopleReportGroup
from karl.models.interfaces import IPeopleSection
from karl.models.interfaces import IPeopleSectionColumn
from karl.models.peopledirectory import PeopleCategory
from karl.models.peopledirectory import PeopleCategoryItem
from karl.models.peopledirectory import PeopleRedirector
from karl.models.peopledirectory import PeopleReport
from karl.models.peopledirectory import PeopleReportCategoryFilter
from karl.models.peopledirectory import PeopleReportGroup
from karl.models.peopledirectory import PeopleReportGroupFilter
from karl.models.peopledirectory import PeopleReportIsStaffFilter
from karl.models.peopledirectory import PeopleReportMailingList
from karl.models.peopledirectory import PeopleSection
from karl.models.peopledirectory import PeopleSectionColumn
from karl.utilities.image import thumb_url
from karl.utilities.peopleconf import dump_peopledir
from karl.utilities.peopleconf import peopleconf
from karl.utils import find_peopledirectory
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import get_setting
from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch_grid
from karl.views.forms.validators import UniqueShortAddress
from karl.views.people import PROFILE_THUMB_SIZE
from karl.views.utils import convert_to_script


def admin_contents(context, request):
    peopledir = find_peopledirectory(context)
    api = TemplateAPI(context, request, 'Contents')
    if 'form.delete' in request.POST:
        if 'selected' not in request.POST:
            api.status_message = 'Please select a value'
        else:
            selected = request.POST['selected']
            if isinstance(selected, basestring):
                selected = [selected]
            for name in selected:
                del context[name]
            return HTTPFound(location=resource_url(context, request,
                                                'admin.html')
                            )
    actions = get_admin_actions(context, request)
    del actions[0]  # Get rid of "Edit" action--doesn't make sense here.
    actions += get_actions(context, request)
    return dict(api=api,
                peopledir=peopledir,
                actions=actions,
                has_categories=peopledir is context,
               )


def admin_contents_moveup_view(context, request):
    api = TemplateAPI(context, request, 'Contents')
    name = request.GET['name']
    order = context.order
    n = order.index(name)
    if n == 0:
       api.status_message = 'Already at top of list'
    else:
       order[n], order[n-1] = order[n-1], order[n]
       context.order = order
    return HTTPFound(location=resource_url(context, request, 'admin.html'))


def admin_contents_movedown_view(context, request):
    api = TemplateAPI(context, request, 'Contents')
    name = request.GET['name']
    order = context.order
    n = order.index(name)
    if n+1 == len(order):
       api.status_message = 'Already at bottom of list'
    else:
       order[n], order[n+1] = order[n+1], order[n]
       context.order = order
    return HTTPFound(location=resource_url(context, request, 'admin.html'))


def peopledirectory_view(context, request):
    # show the first accessible tab
    for section_id in context.order:
        section = context[section_id]
        if has_permission('view', section, request):
            return HTTPFound(location=resource_url(section, request))
    raise Forbidden("No accessible sections")


def download_peopledirectory_xml(context, request):
    response = Response(dump_peopledir(context))
    response.content_type = 'application/xml'
    # suggest a filename based on the report name
    response.headers.add('Content-Disposition',
        'attachment;filename=%s.xml' % str(context.__name__))
    return response


def upload_peopledirectory_xml(context, request):
    peopledir = find_peopledirectory(context)

    if 'form.submit' in request.POST:
        # 'xml' should be the uploaded file.
        xml = request.POST['xml'].file
        tree = etree.parse(xml)
        peopleconf(context, tree, force_reindex=True)
        return HTTPFound(location=resource_url(context, request))

    return dict(api=TemplateAPI(context, request, 'Upload People XML'),
                peopledir=peopledir,
                #actions=get_actions(context, request),
               )


def get_tabs(peopledir, request, current_sectionid):
    """Return a list of dictionaries containing tabs to display in the UI"""
    result = []
    for sectionid in peopledir.order:
        section = peopledir[sectionid]
        if not has_permission('view', section, request):
            continue
        result.append({
            'href': resource_url(section, request), # deprecated in ux2
            'url': resource_url(section, request), # ux2
            'title': section.tab_title,
            'selected': current_sectionid == section.__name__ and 'selected',
            })
    return result


def render_report_group(group, request, css_class=''):
    """Produce the HTML for a report group on a section index page"""
    if not (IPeopleSectionColumn.providedBy(group) or
            IPeopleReportGroup.providedBy(group)):
        return ''
    result = []
    title = getattr(group, 'title', '')
    if title:
        result.append('<h3>%s</h3>' % escape(group.title))
    if css_class:
        result.append('<ul class=%s>' % quoteattr(css_class))
    else:
        result.append('<ul>')
    for obj in group.values():
        if IPeopleReport.providedBy(obj):
            url = resource_url(obj, request)
            result.append('<li><a href=%s class=%s>%s</a></li>' % (
                quoteattr(url),
                quoteattr(obj.css_class),
                escape(obj.link_title)))
        elif IPeopleReportGroup.providedBy(obj):
            html = render_report_group(obj, request)
            result.append('<li>')
            result.append(html)
            result.append('</li>')
    result.append('</ul>')
    return '\n'.join(result)


_ADDABLES = {
    IPeopleDirectory: [('Section', 'add_section.html'),
                      ],
    IPeopleCategories: [('Category', 'add_category.html'),
                       ],
    IPeopleCategory: [('CategoryItem', 'add_category_item.html'),
                     ],
    IPeopleSection: [('Column', 'add_section_column.html'),
                     ('ReportGroup', 'add_report_group.html'),
                     ('Report', 'add_report.html'),
                     ('Redirector', 'add_redirector.html'),
                    ],
    IPeopleSectionColumn: [('ReportGroup', 'add_report_group.html'),
                           ('Report', 'add_report.html'),
                          ],
    IPeopleReportGroup: [('Report', 'add_report.html'),
                        ],
    IPeopleReport: [('CategoryFilter', 'add_category_report_filter.html'),
                    ('GroupFilter', 'add_group_report_filter.html'),
                    ('IsStaffFilter', 'add_is_staff_report_filter.html'),
                    ('MailingList', 'add_mailing_list.html'),
                   ],
}


def get_admin_actions(context, request):
    actions = []
    if has_permission('administer', context, request):
        actions.append(('Edit', 'edit.html'))
        ifaces = list(providedBy(context))
        if ifaces:
            for name, path_elem in _ADDABLES.get(ifaces[0], ()):
                if name == 'MailingList' and 'mailinglist' in context:
                    continue
                actions.append(('Add %s' % name, path_elem))
    return actions


def get_actions(context, request):
    actions = []
    profiles = find_profiles(context)
    if has_permission('administer', profiles, request):
        if request.view_name != 'admin.html':
            #actions.append(('Admin', 'admin.html'))
            pass # see LP #668489
        actions.append(('Add User', resource_url(profiles, request, 'add.html')))
    return actions


def section_view(context, request):

    subs = [sub for sub in context.values()
              if has_permission('view', sub, request) and
                 IPeopleReport.providedBy(sub)]

    if len(subs) == 1:
        return HTTPFound(location=resource_url(subs[0], request))

    api = TemplateAPI(context, request, context.title)
    peopledir = find_peopledirectory(context)
    peopledir_tabs = get_tabs(peopledir, request, context.__name__)
    columns = [{'html': render_report_group(x, request, 'column'),
                'width': getattr(x, 'width', 50)}
                        for x in context.values()]
    columns = [x for x in columns if x['html']]
    return dict(api=api,
                peopledir=peopledir,
                peopledir_tabs=peopledir_tabs, # deprecated in ux2
                context_tools=peopledir_tabs,
                columns=columns,
                actions=get_actions(context, request),
               )


def section_column_view(context, request):
    return HTTPFound(location=context.__parent__)


def _get_mailto(context, peopledir):
    mailinglist = context.get('mailinglist')
    if mailinglist is not None:
        system_email_domain = get_setting(context, "system_email_domain")
        system_list_subdomain = get_setting(context, "system_list_subdomain",
                                            system_email_domain)
        return 'mailto:%s@%s' % (mailinglist.short_address,
                                 system_list_subdomain)

def report_view(context, request, pictures=False):
    api = TemplateAPI(context, request, context.title)
    peopledir = find_peopledirectory(context)
    section = context.__parent__
    section_name = section.__name__
    while section and not IPeopleSection.providedBy(section):
        section = section.__parent__
    if section:
        section_name = section.__name__
    peopledir_tabs = get_tabs(peopledir, request, section_name)
    report_data = get_grid_data(context, request)
    batch = report_data['batch']
    if pictures:
        rows = profile_photo_rows(batch['entries'], request, api)
    else:
        rows = None
    del(report_data['batch']) # non-json serializable
    client_json_data = {'grid_data': report_data}

    descriptions = get_report_descriptions(context)
    mgr = ILetterManager(context)
    letter_info = mgr.get_info(request)

    kw, qualifiers = get_search_qualifiers(request)
    print_url = resource_url(context, request, 'print.html', **kw)
    csv_url = resource_url(context, request, 'csv', **kw)
    pictures_url = resource_url(context, request, 'picture_view.html', **kw)
    tabular_url = resource_url(context, request, **kw)
    opensearch_url = resource_url(context, request, 'opensearch.xml')
    mailto=_get_mailto(context, peopledir)

    formats = [   # ux2
        {'name': 'tabular',
         'selected': not pictures,
         'bs-icon': 'icon-th-list',
         'url': tabular_url,
         'title': 'Tabular View',
         'description': 'Show table'},
        {'name': 'picture',
         'selected': pictures,
         'bs-icon': 'icon-th',
         'url': pictures_url,
         'title': 'Picture View',
         'description': 'Show pictures'}
    ]

    actions = [
        {'name': 'print', 'title': 'Print',
         'description': 'Print this report', 'bs-icon': 'icon-print',
         'url': request.resource_url(context, 'print.html')},
        {'name': 'csv', 'title': 'Export as CSV',
         'description': 'Export this report as CSV', 'bs-icon': 'icon-download',
         'url': request.resource_url(context, 'csv')}]

    if mailto:
        actions.insert(0, {
            'name': 'email', 'title': 'Email', 'bs-icon': 'icon-envelope',
            'description': 'Email', 'url': mailto})

    if opensearch_url:
        actions.insert(0, {
            'name': 'opensearch', 'title': 'Opensearch',
            'bs-icon': 'icon-search',
            'description': 'Add KARL People Search to your browser toolbar',
            'url': "javascript:window.external.AddSearchProvider('%s');" %
                   opensearch_url})

    return dict(
        api=api,   # deprecated in ux2
        peopledir=peopledir,   # deprecated in ux2
        peopledir_tabs=peopledir_tabs, # deprecated in ux2
        context_tools=peopledir_tabs,
        head_data=convert_to_script(client_json_data), # deprecated in ux2
        report_data=report_data, # ux2
        batch_info=batch, # deprecated in ux2
        batch=batch, # ux2
        rows=rows,
        descriptions=descriptions,
        letters=letter_info,
        formats=formats, # ux2
        report_actions=actions, # ux2
        print_url=print_url,        # deprecated in ux2
        csv_url=csv_url,            # deprecated in ux2
        pictures_url=pictures_url,  # deprecated in ux2
        tabular_url=tabular_url,    # deprecated in ux2
        qualifiers=qualifiers,      # deprecated in ux2
        opensearch_url=opensearch_url, # deprecated in ux2
        actions=get_actions(context, request),
        mailto=mailto,              # deprecated in ux2
    )


def jquery_grid_view(context, request):
    sort_on = request.params.get('sortColumn', None)
    reverse = request.params.get('sortDirection') == 'desc'
    payload = get_grid_data(context, request,
        start=int(request.params.get('start', '0')),
        limit=int(request.params.get('limit', '12')),
        sort_on=sort_on,
        reverse=reverse,
    )
    del payload['batch']
    result = JSONEncoder().encode(payload)
    return Response(result, content_type="application/x-json")


def get_column_jsdata(columns, max_width):
    """Produce a list of dictionaries about report columns for jquery
    """
    total_weight = sum(c.weight for c in columns)
    result = []
    for c in columns:
        width = int(math.floor(c.weight * max_width / total_weight))
        result.append({'id': c.id,
                       'label': c.title,
                       'width': width,
                      })
    return result


def profile_photo_rows(entries, request, api, columns=3):
    """Arrange profiles in a series of rows.

    Produces {'profile', 'photo_url', 'url'} for each profile.
    """
    row = []
    for profile in entries:
        photo = profile.get('photo')
        if photo is not None:
            photo_url = thumb_url(photo, request, PROFILE_THUMB_SIZE)
        else:
            photo_url = api.static_url + "/images/defaultUser.gif"
        url = resource_url(profile, request)
        row.append({'profile': profile, 'photo_url': photo_url, 'url': url})

        if len(row) >= columns:
            yield row
            row = []
    if row:
        yield row


def picture_view(context, request):
    return report_view(context, request, pictures=True)


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
    """Produce query parameters for a catalog search
    """
    kw = report.getQuery()
    principals = effective_principals(request)
    kw['allowed'] = {'query': principals, 'operator': 'or'}
    letter = request.params.get('lastnamestartswith')
    if letter:
        kw['lastnamestartswith'] = letter.upper()
    body = request.params.get('body')
    if body:
        kw['texts'] = body.strip() + '*'
    return kw


GRID_WIDTH = 880
SCROLLBAR_WIDTH = 15 # need to get a 15px space for a potentially appearing scrollbar
def get_grid_data(context, request, start=0, limit=12,
        sort_on=None, reverse=False, width=GRID_WIDTH):
    """Gets the data for the jquery report grid.
    """
    columns = [COLUMNS[colid] for colid in context.columns]
    columns_jsdata = get_column_jsdata(columns, width - SCROLLBAR_WIDTH)
    if sort_on is None:
        sort_on = columns[0].id
    sort_index = COLUMNS[sort_on].sort_index

    kw = get_report_query(context, request)
    try:
        batch = get_catalog_batch_grid(context, request,
            batch_start=start,
            batch_size=limit,
            sort_index=sort_index,
            reverse=reverse,
            **kw
            )
    except ParseError:
        # user entered something weird in the text search box.
        # show no results.
        batch = {'entries': [], 'total': 0}

    records = []
    for profile in batch['entries']:
        record = [col.render_html(profile, request) for col in columns]
        records.append(record)

    kw, _ = get_search_qualifiers(request)
    fetch_url = resource_url(context, request, 'jquery_grid', **kw)

    payload = dict(
        fetch_url=fetch_url,
        columns=columns_jsdata,
        records=records,
        totalRecords=batch['total'],
        batchSize=limit,
        width=width,
        sortColumn=sort_on,
        sortDirection=(reverse and 'desc' or 'asc'),
        allocateWidthForScrollbar=True,
        scrollbarWidth=SCROLLBAR_WIDTH,
        batch=batch, # ux2
        )
    return payload


def get_report_descriptions(report):
    descriptions = []  # [(value title, description)]
    categories = find_peopledirectory(report)['categories']
    for catid, filter in report.items():
        cat = categories.get(catid)
        if cat:
            for value in filter.values:
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
            continue    #pragma NO COVERAGE
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

    return dict(api=api,
                header=header,
                rows=dumper,
               )


def opensearch_view(context, request):
    api = TemplateAPI(context, request, 'KARL People OpenSearch')
    return dict(api=api,
                report=context,
                url=resource_url(context, request),
               )


def redirector_view(context, request):
    where = context.target_url
    if not where.startswith('http'):
        if where.startswith('/'):
            where = basejoin(resource_url(context, request), where)
        else:
            elements = where.split('/')
            where = resource_url(context.__parent__, request, *elements)
    return HTTPFound(location=where)


def redirector_admin_view(context, request):
    where = resource_url(context, request, 'edit.html')
    return HTTPFound(location=where)


class ReportColumn(object):

    def __init__(self, id, title, sort_index=None, weight=1.0):
        self.id = id
        self.title = title
        if sort_index is None:
            sort_index = id
        self.sort_index = sort_index
        self.weight = weight

    def render_text(self, profile):
        value = getattr(profile, self.id, '')
        if value is None:
            value = ''
        return unicode(value).strip()

    def render_html(self, profile, request):
        value = self.render_text(profile).strip()
        if not value:
            return '&nbsp;'
        else:
            return escape(value)


class NameColumn(ReportColumn):

    def render_text(self, profile):
        return unicode(profile.title).strip()

    def render_html(self, profile, request):
        value = unicode(profile.title)
        url = resource_url(profile, request)
        return '%s<a href=%s style="display: none;"/>' % (
            escape(value), quoteattr(url))


class PhoneColumn(ReportColumn):

    def render_text(self, profile):
        value = super(PhoneColumn, self).render_text(profile)
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


class EditBase(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_defaults(self):
        context = self.context
        defaults = {}
        for field_name, field in self.schema:
            defaults[field_name] = getattr(context, field_name)
        return defaults

    def form_fields(self):
        return self.schema

    def __call__(self):
        context = self.context
        request = self.request
        api = TemplateAPI(context, request)
        actions = (get_admin_actions(context, request) +
                   get_actions(context, request))
        return {'api':api,
                'actions':actions,
                'page_title': self.page_title,
                }

    def handle_cancel(self):
        location = resource_url(self.context, self.request, 'admin.html')
        return HTTPFound(location=location)

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        self.before_edit()
        for name, field in self.schema:
            setattr(context, name, converted[name])
        self.after_edit()
        location = resource_url(context, request, 'admin.html')
        return HTTPFound(location=location)

    def before_edit(self):
        pass

    def after_edit(self):
        pass

name_schema = [
    ('name', schemaish.String(validator=validator.Required())),
]


class AddBase(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_fields(self):
        return name_schema + self.schema

    def __call__(self):
        context = self.context
        request = self.request
        layout = request.layout_manager.layout
        layout.page_title = self.page_title
        api = TemplateAPI(context, request)
        return {'api':api,   # deprecated in ux2
                'actions': [],   # deprecated in ux2
                'page_title': self.page_title,   # deprecated in ux2
                }

    def handle_cancel(self):
        location = resource_url(self.context, self.request, 'admin.html')
        return HTTPFound(location=location)

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        name = converted['name']
        to_add = context[name] = self.factory()
        self.before_edit()
        for field_name, field in self.schema:
            setattr(to_add, field_name, converted[field_name])
        self.after_edit()
        location = resource_url(to_add, request, 'admin.html')
        return HTTPFound(location=location)

    def before_edit(self):
        pass

    def after_edit(self):
        pass


category_schema = [
    ('title', schemaish.String(
                    validator=validator.All(
                        validator.Length(max=100),
                        validator.Required(),
                     ))),
]


def edit_categories_view(context, request):
    # There is nothing useful to be done here.
    return HTTPFound(location=resource_url(context, request, 'admin.html'))


class EditCategoryFormController(EditBase):
    page_title = 'Edit Category'
    schema = category_schema


class AddCategoryFormController(AddBase):
    page_title = 'Add Category'
    schema = category_schema
    factory = PeopleCategory


category_item_schema = [
    ('title', schemaish.String(
                    validator=validator.All(
                        validator.Length(max=100),
                        validator.Required(),
                     ))),
    ('description', schemaish.String()),
]


class EditCategoryItemFormController(EditBase):
    page_title = 'Edit Category Item'
    schema = category_item_schema


class AddCategoryItemFormController(AddBase):
    page_title = 'Add Category Item'
    schema = category_item_schema
    factory = PeopleCategoryItem


section_schema = [
    ('title', schemaish.String(
                    validator=validator.All(
                        validator.Length(max=100),
                        validator.Required(),
                     ))),
    ('tab_title', schemaish.String(
                    validator=validator.All(
                        validator.Length(max=20),
                        validator.Required(),
                     ))),
]


class EditSectionFormController(EditBase):
    page_title = 'Edit Section'
    schema = section_schema


class AddSectionFormController(AddBase):
    page_title = 'Add Section'
    schema = section_schema
    factory = PeopleSection


report_group_schema = [
    ('title', schemaish.String(
                    validator=validator.All(
                        validator.Length(max=100),
                        validator.Required(),
                     ))),
]


class EditReportGroupFormController(EditBase):
    page_title = 'Edit Report Group'
    schema = report_group_schema


class AddReportGroupFormController(AddBase):
    page_title = 'Add Report Group'
    schema = report_group_schema
    factory = PeopleReportGroup


section_column_schema = [
   ('width', schemaish.Integer()),
]


class EditSectionColumnFormController(EditBase):
    page_title = 'Edit Section Column'
    schema = section_column_schema


class AddSectionColumnFormController(AddBase):
    page_title = 'Add Section Column'
    schema = section_column_schema
    factory = PeopleSectionColumn


report_filter_schema = [
    ('values', schemaish.Sequence(
                  schemaish.String())),
]


class AddCategoryReportFilterFormController(AddBase):
    page_title = 'Add Category Report Filter'
    schema = report_filter_schema
    factory = PeopleReportCategoryFilter

    def form_widgets(self, schema):
        widgets = {
            'values':formish.TextArea(rows=5,
                           converter_options={'delimiter':'\n'}),
                  }
        return widgets


class AddGroupReportFilterFormController(AddBase):
    page_title = 'Add Group Report Filter'
    schema = report_filter_schema
    factory = PeopleReportGroupFilter

    def form_widgets(self, schema):
        widgets = {
            'values':formish.TextArea(rows=5,
                           converter_options={'delimiter':'\n'}),
                  }
        return widgets


class EditReportFilterFormController(EditBase):
    page_title = 'Edit Report Filter'
    schema = report_filter_schema

    def form_widgets(self, schema):
        widgets = {'values':formish.TextArea(rows=5,
                                             converter_options={
                                                    'delimiter':'\n'}),
                  }
        return widgets


is_staff_schema = [('include_staff', schemaish.Boolean())]


class AddIsStaffReportFilterFormController(AddBase):
    page_title = 'Add IsStaff Report Filter'
    schema = is_staff_schema
    factory = PeopleReportIsStaffFilter

    def form_widgets(self, schema):
        widgets = {'include_staff':formish.Checkbox()}
        return widgets


class EditIsStaffReportFilterFormController(EditBase):
    page_title = 'Edit Report Filter'
    schema = is_staff_schema

    def form_widgets(self, schema):
        widgets = {'include_staff':formish.Checkbox(),
                  }
        return widgets


mailing_list_schema = [
    ('short_address', schemaish.String(),),
]


class AddReportMailingListFormController(AddBase):
    page_title = 'Add Report Mailing List'
    schema = [] # don't expose 'short_address' on add.
    factory = PeopleReportMailingList

    def form_widgets(self, schema):
        widgets = {
            'name':formish.Hidden(),
                  }
        return widgets

    def form_defaults(self):
        return {'name': 'mailinglist'}


class EditReportMailingListFormController(EditBase):
    page_title = 'Edit Mailing List'
    schema = mailing_list_schema

    def form_defaults(self):
        return {'short_address': self.context.short_address}

    def form_fields(self):
        return [('short_address',
                 schemaish.String(validator=UniqueShortAddress(self.context)),
                ),
               ]

    def before_edit(self):
        context = self.context
        aliases = find_site(context).list_aliases
        try:
            del aliases[context.short_address]
        except KeyError:
            pass

    def after_edit(self):
        context = self.context
        aliases = find_site(context).list_aliases
        aliases[context.short_address] = resource_path(context.__parent__)


report_schema = [
    ('title', schemaish.String(
                    validator=validator.All(
                        validator.Length(max=100),
                        validator.Required(),
                     ))),
    ('link_title', schemaish.String()),
    ('css_class', schemaish.String()),
    ('columns', schemaish.Sequence(
                    schemaish.String(
                       validator = lambda v:
                           validate.is_one_of(v, COLUMNS.keys())))),
]


class AddReportFormController(AddBase):
    page_title = 'Add Report'
    schema = report_schema
    factory = PeopleReport

    def form_widgets(self, schema):
        widgets = {
            'columns':formish.TextArea(rows=5,
                            converter_options={'delimiter':'\n'}),
                  }
        return widgets


class EditReportFormController(EditBase):
    page_title = 'Edit Report'
    schema = report_schema

    def form_widgets(self, schema):
        widgets = {
            'columns':formish.TextArea(rows=5,
                            converter_options={'delimiter':'\n'}),
        }
        return widgets


redirector_schema = [
    ('target_url', schemaish.String(validator=validator.Required())),
]


class AddRedirectorFormController(AddBase):
    page_title = 'Edit Redirector'
    schema = redirector_schema
    factory = PeopleRedirector

    def form_defaults(self):
        return {'target_url': self.request.params.get('target_url', '')}


class EditRedirectorFormController(EditBase):
    page_title = 'Edit Redirector'
    schema = redirector_schema
