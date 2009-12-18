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

import calendar
import datetime

from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.index.text.parsetree import ParseError

from repoze.bfg.url import model_url
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path

from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch_grid
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import get_user_home

from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import INewsItem
from karl.views.interfaces import ILayoutProvider

from karl.utils import coarse_datetime_repr
from karl.utils import get_folder_addables
from karl.utils import get_layout_provider

def get_catalog_events(context, request,
                       searchterm=None, year=None, month=None,
                       past_events=None):

    # Build up a query
    query = dict(
        path={'query': model_path(context)},
        allowed={'query': effective_principals(request), 'operator': 'or'},
        interfaces=[ICalendarEvent],
        sort_index="start_date",
        reverse=True,
        use_cache=False,
        )

    if searchterm is not None:
        query['texts'] = searchterm

    if year is not None or month is not None:
        if year is not None:
            year = int(year)
        else:
            # No year given, assume this year
            year = datetime.datetime.now().year

        if month is not None:
            month = int(month)
            last_day = calendar.monthrange(year, month)[1]
            first_moment = coarse_datetime_repr(
                datetime.datetime(year, month, 1))
            last_moment = coarse_datetime_repr(
                datetime.datetime(year, month, last_day, 23, 59, 59))

        else:
            # No month given, search entire year
            first_moment = coarse_datetime_repr(datetime.datetime(year, 1, 1))
            last_moment = coarse_datetime_repr(datetime.datetime(year+1, 1, 1))

        query['start_date'] = (None, last_moment)
        query['end_date'] = (first_moment, None)

    else:
        # Show either all future or all past events
        now = coarse_datetime_repr(datetime.datetime.now())
        if past_events:
            # Past; show the most recent first
            query['end_date'] = (None, now)
            query['reverse'] = True
        else:
            # Future; show the soonest first
            query['end_date'] = (now, None)
            query['reverse'] = False

    batch = get_catalog_batch_grid(context, request, **query)

    return batch

def get_catalog_news(context, request,
                     searchterm=None, year=None, month=None):

    # Build up a query
    query = dict(
        path={'query': model_path(context)},
        allowed={'query': effective_principals(request), 'operator': 'or'},
        interfaces=[INewsItem],
        sort_index="publication_date",
        reverse=True,
        )

    if searchterm is not None:
        query['texts'] = searchterm

    now = coarse_datetime_repr(datetime.datetime.now())
    if year is not None or month is not None:
        if year is not None:
            year = int(year)
        else:
            # No year given, assume this year
            year = datetime.datetime.now().year

        if month is not None:
            month = int(month)
            last_day = calendar.monthrange(year, month)[1]
            first_moment = coarse_datetime_repr(
                datetime.datetime(year, month, 1))
            last_moment = coarse_datetime_repr(
                datetime.datetime(year, month, last_day, 23, 59, 59))

        else:
            # No month given, search entire year
            first_moment = coarse_datetime_repr(datetime.datetime(year, 1, 1))
            last_moment = coarse_datetime_repr(datetime.datetime(year+1, 1, 1))

        # Never show news items that aren't published yet
        last_moment = min(last_moment, now)

        query['publication_date'] = (first_moment, last_moment)

    else:
        # Don't show news from future
        query['publication_date'] = (None, now)

    batch = get_catalog_batch_grid(context, request, **query)

    return batch

def _get_short_date(start_date, end_date):
    """For network events listing, return 'April 4-5, 2009'"""

    # Per KARL2, make an attempt to collapse the day display
    start_day = start_date.day
    end_day = end_date.day
    start_month = start_date.strftime('%B')
    end_month = end_date.strftime('%B')
    start_year = start_date.strftime('%Y')
    end_year = end_date.strftime('%Y')

    if start_month == end_month and start_year==end_year:
        if start_day == end_day:
            fmt = '%s %s, %s'
            short_date = fmt % (start_month, start_day, start_year)
        else:
            fmt = '%s %s-%s, %s'
            short_date = fmt % (start_month, start_day, end_day, start_year)
    else:
        # Go for the completely long form, like 'April 2, 2009 -
        # February 1, 20010'
        fmt = '%s %s, %s - %s %s, %s'
        short_date = fmt % (start_month, start_day, start_year,
                            end_month, end_day, end_year)

    return short_date


class CustomFolderView(object):
    _past_events = None
    past_events_url = None
    future_events_url = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

        searchterm = request.params.get('searchterm', None)
        if searchterm == '':
            searchterm = None
        self.searchterm = searchterm

        year = request.params.get('year', None)
        if year == 'all':
            year = None
        self.year = year

        month = request.params.get('month', None)
        if month == 'all':
            month = None
        self.month = month

    def __call__(self):
        """ Folder contents for the INetworkEvents marker"""
        context = self.context
        request = self.request

        page_title = context.title
        api = TemplateAPI(context, request, page_title)

        # Data for the filter bar, get the list of possible years and months
        this_year = datetime.datetime.now().year
        fb_years = [str(i) for i in range(2007, this_year+1)]
        fb_months = [('1', 'January'), ('2', 'February'), ('3', 'March'),
                     ('4', 'April'), ('5', 'May'), ('6', 'June'),
                     ('7', 'July'), ('8', 'August'), ('9', 'September'),
                     ('10', 'October'), ('11', 'November'), ('12', 'December')]

        # Flatten the search results into ZPT data
        try:
            batch = self._get_batch()
        except ParseError, e:
            api.set_error_message('Error: %s' % e)
            batch = {'entries': (), 'batching_required': False}

        entries = []
        for entry in batch["entries"]:
            info = {}
            info['url'] = model_url(entry, request)
            info['title'] = entry.title
            info['date'] = self._get_date(entry)
            entries.append(info)

        # Actions and backlink
        actions = []
        if has_permission('create', context, request):
            addables = get_folder_addables(context, request)
            if addables is not None:
                actions.extend(addables())
            actions.append(('Edit', 'edit.html'))
            actions.append(('Delete', 'delete.html'))
            # admins see an Advanced action that puts markers on a folder.
            actions.append(('Advanced', 'advanced.html'))

        back_target, extra_path = get_user_home(context, request)
        backto = {
            'href': model_url(back_target, request, *extra_path),
            'title': getattr(back_target, "title", "Home")
            }

        client_json_data = dict(
            tagbox = get_tags_client_data(context, request),
            )

        # Get a layout
        layout_provider = get_layout_provider(context, request)
        layout = layout_provider('community')

        return render_template_to_response(
            'templates/custom_folder.pt',
            api=api,
            actions=actions,
            head_data=convert_to_script(client_json_data),
            backto=backto,
            layout=layout,
            entries=entries,
            fb_years=fb_years,
            fb_months=fb_months,
            searchterm=self.searchterm,
            selected_year=self.year,
            selected_month=self.month,
            batch_info=batch,
            past_events_url=self.past_events_url,
            future_events_url=self.future_events_url,
            )


class NetworkEventsView(CustomFolderView):
    itype = ICalendarEvent
    sort_index = "start_date"

    def __init__(self, context, request):
        super(NetworkEventsView, self).__init__(context, request)

        past_events = request.params.get('past_events', None)
        if past_events is not None:
            past_events = (past_events == 'True')

        self._past_events = past_events

    @property
    def past_events_url(self):
        if not self._past_events:
            return model_url(self.context, self.request,
                             query={"past_events":"True"})
        return None

    @property
    def future_events_url(self):
        if self._past_events:
            return model_url(self.context, self.request,
                             query={"past_events":"False"})
        return None

    def _get_date(self, entry):
        return _get_short_date(entry.startDate, entry.endDate)

    def _get_batch(self):
        batch = get_catalog_events(self.context, self.request, self.searchterm,
                                   self.year, self.month, self._past_events)
        return batch

def network_events_view(context, request):
    return NetworkEventsView(context, request)()

class NetworkNewsView(CustomFolderView):
    itype = INewsItem
    sort_index = "publication_date"

    def _get_date(self, entry):
        return _get_short_date(entry.publication_date, entry.publication_date)

    def _get_batch(self):
        batch = get_catalog_news(self.context, self.request, self.searchterm,
                                 self.year, self.month)
        return batch

def network_news_view(context, request):
    return NetworkNewsView(context, request)()
