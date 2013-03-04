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
"""Content feeds views
"""
from csv import DictWriter
from itertools import islice
from StringIO import StringIO
from urlparse import urljoin

from pyramid.response import Response
from pyramid.security import effective_principals
from pyramid.security import authenticated_userid

from karl.utils import find_events
from karl.views.api import TemplateAPI


_FILTER_COOKIE = 'karl.feed_filter'


def _get_criteria(request):
    principals = effective_principals(request)
    principals = [x for x in principals if not x.startswith('system.')]

    # Check to see if we're asking for only "my" communities.
    filterby = request.params.get('filter', '')
    # cookie must be set even if param is empty or non-existent, to make
    # the no-filter button sticky.
    #header = ('Set-Cookie', '%s=%s; Path=/' % (_FILTER_COOKIE, str(filterby)))
    request.cookies[_FILTER_COOKIE] = filterby
    request.response.set_cookie(_FILTER_COOKIE, str(filterby), path='/')

    if filterby == 'mycommunities':
        principals = [x for x in principals if not x.startswith('group.Karl')]

    if filterby == 'mycontent':
        created_by = authenticated_userid(request)
    elif filterby.startswith('profile:'):
        created_by = filterby[len('profile:'):]
    elif filterby.startswith('community:'):
        created_by = None
        community = filterby[len('community:'):]
        prefix = 'group.community:%s' % community
        principals = [x for x in principals if x.startswith(prefix)]
    else:
        created_by = None

    return principals, created_by

def _update_feed_items(entries, app_url):
    if not app_url.endswith('/'):
        app_url += '/'

    def reroot(fi, name):
        if name not in fi:
            return
        url = fi[name]
        if url is None:
            return
        if url.startswith('/'):
            url = url[1:]
        fi[name] = urljoin(app_url, url)

    feed_items = [dict(x[2]) for x in entries]

    for fi in feed_items:
        fi['timeago'] = str(fi.pop('timestamp').strftime('%Y-%m-%dT%H:%M:%SZ'))
        reroot(fi, 'url')
        reroot(fi, 'context_url')
        reroot(fi, 'profile_url')
        reroot(fi, 'thumbnail')
        del fi['allowed']

    return feed_items

def newest_feed_items(context, request):

    principals, created_by = _get_criteria(request)
    events = find_events(context)

    # Check to see if we're asking for most recent
    newer_than = request.params.get('newer_than')

    if newer_than:
        last_gen, last_index = newer_than.split(':')
        last_gen = long(last_gen)
        last_index = int(last_index)
        latest = list(events.newer(last_gen, last_index,
                                   principals, created_by))
    else:
        last_gen = -1L
        last_index = -1
        latest = list(islice(events.checked(principals, created_by), 20))

    if not latest:
        return (last_gen, last_index, last_gen, last_index, ())

    last_gen, last_index, ignored = latest[0]
    earliest_gen, earliest_index, ignored = latest[-1]

    feed_items = _update_feed_items(latest, request.application_url)

    return last_gen, last_index, earliest_gen, earliest_index, feed_items


def older_feed_items(context, request):
    older_than = request.params.get('older_than')

    # If we don't have params, bail out.
    if older_than is None:
        return -1, -1, ()

    principals, created_by = _get_criteria(request)
    events = find_events(context)

    earliest_gen, earliest_index = older_than.split(':')
    earliest_gen = long(earliest_gen)
    earliest_index = int(earliest_index)
    older = list(islice(events.older(earliest_gen, earliest_index,
                                principals, created_by), 20))

    if not older:
        return (earliest_gen, earliest_index, ())

    earliest_gen, earliest_index, ignored = older[-1]

    feed_items = _update_feed_items(older, request.application_url)

    return earliest_gen, earliest_index, feed_items


def show_feeds_view(context, request):
    api = TemplateAPI(context, request, 'Latest Activity')
    filter_cookie = request.cookies.get(_FILTER_COOKIE) or ''
    layout = request.layout_manager.layout
    layout.section_style = "none"
    return {'api': api,
            'page_title': 'Latest Activity',
            'show_filter': True,
            'sticky_filter': filter_cookie,
           }


def profile_feed_view(context, request):
    api = TemplateAPI(context, request, 'Latest Activity')
    layout = request.layout_manager.layout
    layout.section_style = "none"
    return {'api': api,
            'show_filter': False,
            'page_title': 'Latest Activity',
            'sticky_filter': 'profile:%s' % context.__name__,
           }


def community_feed_view(context, request):
    api = TemplateAPI(context, request, 'Latest Activity')
    layout = request.layout_manager.layout
    layout.section_style = "none"
    return {'api': api,
            'show_filter': False,
            'page_title': 'Latest Activity',
            'sticky_filter': 'community:%s' % context.__name__,
           }


def _CSV_JOIN_ITEMS(x):
    if x is None:
        return ''
    if isinstance(x, basestring):
        return x
    return ':'.join(x)

_CSV_KEYS = (('content_type', None),
        ('userid', None),
        ('flavor', None),
        ('operation', None),
        ('context_name', None),
        ('context_url', None),
        ('content_creator', None),
        ('url', None),
        ('title', None),
        ('description', None),
        ('short_description', None),
        ('allowed', _CSV_JOIN_ITEMS),
        ('comment_count', None),
        ('tags', _CSV_JOIN_ITEMS),
        ('author', None),
        ('profile_url', None),
        ('thumbnail', None),
        ('timestamp', None),
        ('tagname', None),
        )
_CSV_MAP = dict([x for x in _CSV_KEYS if x[1] is not None])
_CSV_FIELD_NAMES = [x[0] for x in _CSV_KEYS]
def feed_dump_csv(context, request):
    buf = StringIO()
    buf.write(','.join(_CSV_FIELD_NAMES) + '\n')
    writer = DictWriter(buf, _CSV_FIELD_NAMES)
    for gen, index, event_info in find_events(context):
        for key in list(event_info):
            if key not in _CSV_FIELD_NAMES:
                del event_info[key]
        for key, xform in _CSV_MAP.items():
            event_info[key] = xform(event_info.get(key))
        writer.writerow(event_info)
    response = Response(buf.getvalue())
    response.content_type = 'application/x-csv'
    response.headers.add('Content-Disposition',
                         'attachment;filename=feed_dump.csv')
    return response
