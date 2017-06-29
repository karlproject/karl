import csv
from StringIO import StringIO
from datetime import datetime
from osi.interfaces import IMetricsMonthFolder
from osi.utilities.metrics import month_string
from karl.utils import get_layout_provider
from karl.views.api import TemplateAPI
from karl.views.api import xhtml
from pyramid.renderers import get_renderer
from pyramid.url import model_url
from webob.exc import HTTPFound
from webob.exc import Response

def _metrics_macros():
    macros = get_renderer('templates/metrics/macros.pt').implementation()
    macros.doctype = xhtml
    return macros.macros

def csv_response(request, filename, header, data, generate_row_fn):
    request.response_content_type = 'text/plain'
    download_header = 'attachment; filename="%s"' % filename
    header_list = [('Content-Disposition', download_header)]

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow(header)

    for elt in data:
        row = generate_row_fn(elt)
        encoded_row = []
        for cell in row:
            if isinstance(cell, unicode):
                encoded_row.append(cell.encode('utf-8'))
            else:
                encoded_row.append(cell)
        writer.writerow(encoded_row)

    response = Response(
        status = 200,
        headerlist = header_list,
        content_type = 'text/csv',
        body = buffer.getvalue(),
        )

    buffer.close()

    return response

def container_view(context, request):
    api = TemplateAPI(context, request, 'Metrics')
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()
    years = context.keys()

    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        years = years,
        )

def month_name(year, month):
    return datetime(int(year), int(month), 1).strftime('%b')

def format_date(datetime_object):
    return datetime_object.strftime('%Y/%m/%d')

def year_view(context, request):
    year = context.__name__
    api = TemplateAPI(context, request, 'Metrics for %s' % year)
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    months_data = []
    for month in sorted(context.keys()):
        months_data.append(dict(num=month,
                                name=month_name(year, month)))

    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        months_data = months_data,
        backto = backto_metrics(context, request),
        )

def year_contenttype_view(context, request):
    year = context.__name__
    api = TemplateAPI(context, request, '%s content type metrics' % year)
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    months = []
    contenttypes = {}

    # pull the data into a dict structure
    for month_num, month in sorted(context.items()):
        if IMetricsMonthFolder.providedBy(month):
            months.append(month_name(year, month_num))
            for typename, typedata in month.contenttypes.items():
                contenttypes.setdefault(typename, {})[month_num] = typedata

    # assemble the data to make it easy for the template to consume it
    contenttypes_result = []
    contenttypes_list = sorted(contenttypes.items(), key=lambda x:x[0])
    for contenttype_name, contenttype_data in contenttypes_list:
        months_result = []
        months_list = sorted(contenttype_data.items(), key=lambda x:int(x[0]))
        for month_num, month_data in months_list:
            months_result.append(month_data)
        contenttypes_result.append(dict(name=contenttype_name,
                                        months=months_result))

    if 'csv' in request.GET:

        def generate_csv_row(contenttype):
            return ([contenttype['name'].title()] +
                    [x['created'] for x in contenttype['months']])

        header_row = ['Content Type'] + [month.title() for month in months]
        return csv_response(
            request,
            '%s-contenttype.csv' % year,
            header_row,
            contenttypes_result,
            generate_csv_row)


    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        backto = backto_metrics(context, request),
        months = months,
        year = year,
        contenttypes = contenttypes_result,
        )

def year_profiles_view(context, request):
    year = context.__name__
    api = TemplateAPI(context, request, '%s profile metrics' % year)
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    months = []
    profiles = {}

    default_values = dict(
        created='',
        is_staff=False,
        )

    # not all users necessarily contain values for each month
    # for example, those that were created in the middle of the year
    # we stub those values out here
    year_defaults = {}
    for month_num_string in context.keys():
        year_defaults[month_num_string] = default_values.copy()

    # pull the data into a dict structure
    for month_num, month in sorted(context.items()):
        if IMetricsMonthFolder.providedBy(month):
            months.append(month_name(year, month_num))
            for userid, profiledata in month.profiles.items():
                userdata = profiles.get(userid, None)
                if userdata is None:
                    userdata = year_defaults.copy()
                    profiles[userid] = userdata
                userdata[month_num] = profiledata

    # assemble the data to make it easy for the template to consume it
    profiles_result = []
    profiles_list = sorted(profiles.items(), key=lambda x:x[0])
    for userid, profiledata in profiles_list:
        months_result = []
        months_list = sorted(profiledata.items(), key=lambda x:int(x[0]))
        for month_num, month_data in months_list:
            months_result.append(month_data)
        # take the last month's staff result as the value for the row
        is_staff = months_result[-1]['is_staff']
        profiles_result.append(dict(name=userid,
                                    is_staff=is_staff,
                                    months=months_result))

    if 'csv' in request.GET:

        def generate_csv_row(profile):
            return ([profile['name'].title(), profile['is_staff']] +
                    [x['created'] for x in profile['months']])

        header_row = ['Profile', 'Staff'] + [month.title() for month in months]
        return csv_response(
            request,
            '%s-profile.csv' % year,
            header_row,
            profiles_result,
            generate_csv_row)


    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        backto = backto_metrics(context, request),
        months = months,
        year = year,
        profiles = profiles_result,
        )

def year_communities_view(context, request):
    year = context.__name__
    api = TemplateAPI(context, request, '%s communities metrics' % year)
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    months = []
    communities = {}
    communityid_to_title = {}

    # not all communities necessarily contain values for each month
    # for example, those that were created in the middle of the year
    # we stub those values out here
    year_defaults = {}
    for month_num_string in context.keys():
        year_defaults[month_num_string] = 0

    # pull the data into a dict structure
    for month_num, month in sorted(context.items()):
        if IMetricsMonthFolder.providedBy(month):
            months.append(month_name(year, month_num))
            # XXX total/created structures?
            for communityid, data in month.communities['created'].items():
                communityid_to_title[communityid] = data['title']
                # this total is the total of all the created objects
                created = data['total']
                communitydata = communities.get(communityid, None)
                if communitydata is None:
                    communitydata = year_defaults.copy()
                    communities[communityid] = communitydata
                communitydata[month_num] = created

    # assemble the data to make it easy for the template to consume it
    communities_result = []
    communities_list = sorted(communities.items(), key=lambda x:x[0])
    for communityid, data in communities_list:
        months_result = []
        months_list = sorted(data.items(), key=lambda x:int(x[0]))
        for month_num, month_data in months_list:
            # only need created objects for the columns
            months_result.append(month_data)
        title = communityid_to_title[communityid]
        communities_result.append(dict(name=title, months=months_result))

    if 'csv' in request.GET:

        def generate_csv_row(community):
            return [community['name'].title()] + community['months']

        header_row = ['Community'] + [month.title() for month in months]
        return csv_response(
            request,
            '%s-communities.csv' % year,
            header_row,
            communities_result,
            generate_csv_row)


    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        backto = backto_metrics(context, request),
        months = months,
        year = year,
        communities = communities_result,
        )

def year_users_view(context, request):
    year = context.__name__
    api = TemplateAPI(context, request, '%s user metrics' % year)
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    months_data = []
    for month_num, month in sorted(context.items()):
        if IMetricsMonthFolder.providedBy(month):
            month_data = dict(
                month = month_name(year, month_num),
                total = month.users['total'],
                )
            months_data.append(month_data)

    if 'csv' in request.GET:

        def generate_csv_row(row):
            data = row['total']
            return [
                row['month'],
                data['staff'],
                data['core_office'],
                data['national_foundation'],
                data['former'],
                data['affiliate'],
                data['active'],
                data['total'],
                ]

        header_row = [
            'Month',
            'Staff',
            'Core Offices',
            'National Foundations',
            'Former Staff',
            'Affiliates',
            'Active',
            'Total',
            ]
        return csv_response(
            request,
            '%s-users.csv' % year,
            header_row,
            months_data,
            generate_csv_row)


    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        backto = backto_metrics(context, request),
        months_data = months_data,
        year = year,
        )


def month_view(context, request):
    url = model_url(context, request, 'contenttype.html')
    return HTTPFound(location=url)

def month_contenttype_view(context, request):
    year = context.__parent__.__name__
    month = context.__name__
    api = TemplateAPI(context, request,
                      '%s - %s contenttype metrics' % (year, month))
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    contenttypes = [dict(name=k, total=v['total'], created=v['created'])
                    for k, v in context.contenttypes.items()]
    contenttypes.sort(key=lambda x:x['name'])

    if 'csv' in request.GET:

        def generate_csv_row(contenttype):
            return [
                contenttype['name'].title(),
                contenttype['created'],
                contenttype['total'],
                ]

        return csv_response(
            request,
            '%s-%s-contenttype.csv' % (year, month),
            ['Content Type', 'Created', 'Total'],
            contenttypes,
            generate_csv_row)

    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        contenttypes = contenttypes,
        backto = backto_year(context, request)
        )

def month_profiles_view(context, request):
    year = context.__parent__.__name__
    month = context.__name__
    api = TemplateAPI(context, request,
                      '%s - %s profile metrics' % (year, month))
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    profiles = [dict(name=k, created=v['created'], is_staff=v['is_staff'])
                for k, v in context.profiles.items()]
    profiles.sort(key=lambda x:x['name'])

    if 'csv' in request.GET:

        def generate_csv_row(profile):
            return [
                profile['name'].title(),
                profile['is_staff'],
                profile['created'],
                ]

        return csv_response(
            request,
            '%s-%s-profiles.csv' % (year, month),
            ['User', 'Staff', 'Created'],
            profiles,
            generate_csv_row)

    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        profiles = profiles,
        backto = backto_year(context, request)
        )

def month_users_view(context, request):
    year = context.__parent__.__name__
    month = context.__name__
    api = TemplateAPI(context, request,
                      '%s - %s user metrics' % (year, month))
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    if 'csv' in request.GET:

        def generate_csv_row(row):
            return [
                row['total'],
                row['staff'],
                row['core_office'],
                row['national_foundation'],
                row['former'],
                row['affiliate'],
                row['active'],
                ]

        return csv_response(
            request,
            '%s-%s-users.csv' % (year, month),
            ['Total', 'Staff', 'Core Office', 'National Foundation',
             'Former Staff', 'Affiliate', 'Active'],
            [context.users['total']],
            generate_csv_row)

    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        userdata = context.users['total'],
        backto = backto_year(context, request)
        )

def month_communities_view(context, request):
    year = context.__parent__.__name__
    month = context.__name__
    api = TemplateAPI(context, request,
                      '%s - %s community metrics' % (year, month))
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider()

    communities = context.communities['created'].values()
    communities.sort(key=lambda x:x['title'])
    
    def update_date_values(community_data):
        result = community_data.copy()
        result['created'] = format_date(result['created'])
        result['last_activity'] = format_date(result['last_activity'])
        return result

    communities = [update_date_values(c) for c in communities]

    if 'csv' in request.GET:

        def generate_csv_row(community):
            return [
                community['title'],
                community['security_state'],
                community['created'],
                community['last_activity'],
                community['blogs'],
                community['comments'],
                community['wikis'],
                community['files'],
                community['events'],
                community['members'],
                community['moderators'],
                community['total'],
                ]

        return csv_response(
            request,
            '%s-%s-communities.csv' % (year, month),
            ['Community', 'Security', 'Created', 'Last Activity',
             'Blog posts', 'Comments', 'Wiki pages', 'Files', 'Events',
             'Members', 'Moderators', 'Total'],
            communities,
            generate_csv_row)

    return dict(
        api = api,
        layout = layout,
        metricsmacros = _metrics_macros(),
        communities = communities,
        backto = backto_year(context, request)
        )

def backto_year(month, request):
    return dict(
        title = str(month.__parent__.__name__),
        href = model_url(month.__parent__, request),
        )

def backto_metrics(year, request):
    return dict(
        title = u'Metrics',
        href = model_url(year.__parent__, request),
        )
