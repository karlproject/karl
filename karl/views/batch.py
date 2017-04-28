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

"""Catalog results batching functions"""

import datetime

from itertools import islice

from pyramid.security import has_permission
from pyramid.url import resource_url
from pyramid.url import urlencode
from karl.models.interfaces import ICatalogSearch
from karl.utils import find_catalog

def get_catalog_batch(context, request, catalog_iface=ICatalogSearch, **kw):
    batch_start = kw.pop('batch_start', 0)
    batch_start = int(request.params.get("batch_start", batch_start))
    batch_size = kw.pop('batch_size', 20)
    batch_size = int(request.params.get("batch_size", batch_size))
    sort_index = kw.pop('sort_index', None)
    sort_index = request.params.get('sort_index', sort_index)
    reverse = kw.pop('reverse', False)
    reverse = bool(int(request.params.get('reverse', reverse)))

    # XXX Asserting a default 'modified' sort order here is
    # fragrant.  It's unclear which callers depend on the behavior
    # and which don't.  Most callers probably don't even know we
    # do this.  We should make this each caller's responsibility
    # instead of embedding this policy here.
    if sort_index is None:
        sort_index = 'modified_date'
    kw['sort_index'] = sort_index
    # the reverse parameter is only useful when there's a sort index
    kw['reverse'] = reverse

    # Adding a limit will cause some indexes to use an NBEST sort
    # which is dramatically faster than sorting an entire large result set.
    kw['limit'] = batch_start + batch_size

    searcher = catalog_iface(context)
    numdocs, docids, resolver = searcher(**kw)

    # Use of indirection here is to avoid having to rewrite 70 tests to
    # use repoze.catalog.catalog.ResultSetSize instead of int
    total = getattr(numdocs, 'total', numdocs)
    if total < batch_start:
        batch_start = total

    # Lazily slice a lazy generator for getting models from result set
    docs = (model for model in
            (resolver(docid) for docid in docids)
            if model is not None)
    batch = list(islice(docs, batch_start, batch_start + batch_size))
    batch_end = batch_start + len(batch)

    info = {
        'entries': batch,
        'batch_start': batch_start,
        'batch_size': batch_size,
        'batch_end': batch_end,
        'total': getattr(numdocs, 'total', numdocs),
        'sort_index': sort_index,
        'reverse': reverse,
        }

    _add_link_data(info, context, request)
    return info

def _add_link_data(batch_info, context, request):
    """
    Add previous_batch, next_batch, and batching_required to batch info.
    """
    batch_start = batch_info['batch_start']
    batch_size = batch_info['batch_size']
    total = batch_info['total']

    def batchURL(newquery, batch_start=0):
        newquery['batch_start'] = batch_start
        newquery['batch_size'] = batch_size
        if batch_info.get('sort_index'):
            newquery['sort_index'] = batch_info['sort_index']
        if 'reverse' in batch_info:
            newquery['reverse'] = str(int(batch_info['reverse']))
        return resource_url(context, request, request.view_name, query=newquery)

    previous_start = batch_start - batch_size
    if previous_start < 0:
        previous_batch_info = None
    else:
        previous_end = min(previous_start + batch_size, total)
        size = previous_end - previous_start
        previous_batch_info = {}
        query = dict(request.GET)
        previous_batch_info['url'] = batchURL(query, previous_start)
        previous_batch_info['name'] = (
            'Previous %s entries (%s - %s)' % (size, previous_start+1,
                                               previous_end))
    batch_info['previous_batch'] = previous_batch_info

    next_start = batch_start + batch_size
    if next_start >= total:
        next_batch_info = None
    else:
        next_end = min(next_start + batch_size, total)
        size = next_end - next_start
        next_batch_info = {}
        query = dict(request.GET)
        next_batch_info['url'] = batchURL(query, next_start)
        next_batch_info['name'] = (
            'Next %s entries (%s - %s of about %s)' % (size,
                                                       next_start+1,
                                                       next_end,
                                                       total))
    batch_info['next_batch'] = next_batch_info
    batch_info['batching_required'] = bool(
        next_batch_info or previous_batch_info)


def get_catalog_batch_grid(context, request, **kw):
    batch = get_catalog_batch(context, request, **kw)

    query_terms = [('batch_size', str(batch['batch_size']))]
    for k, v in request.params.items():
        if k not in ('batch_start', 'batch_size'):
            query_terms.append((k, v))

    # Add information for the gridstyle_batching macro
    def pagemaker(page):
        batch_start = str((page - 1) * batch['batch_size'])
        url = '?%s' % urlencode([('batch_start', batch_start)] + query_terms)
        return dict(page=page, url=url)
    def empty(page):
        return dict(page=page, url=None)

    # The HTML produces a UI widget that looks something like this:
    # [<] [1] ... [12] [13] [14] (15) [16] [17] [18] ... [30] [>]

    current = batch['batch_start'] / batch['batch_size'] + 1
    last = (batch['total'] - 1) / batch['batch_size'] + 1
    batch['current_page'] = current
    batch['last_page'] = last
    # before contains page numbers shortly before the current page
    before = range(max(current - 3, 1), current)
    # after contains page numbers shortly after the current page
    after = range(current + 1, min(current + 4, last))
    if current > 1:
        prev = pagemaker(current - 1)
    else:
        prev = empty(None)
    if current > 2 and not 2 in before:
        ellipsis_begin = pagemaker(page=1)
    else:
        ellipsis_begin = empty(None)
        if current > 1 and not 1 in before:
            before.insert(0, 1)
    if current < last - 1 and not last - 1 in after:
        ellipsis_end = pagemaker(page=last)
    else:
        ellipsis_end = empty(None)
        if current < last and not last in after:
            after.append(last)
    if current < last:
        next = pagemaker(current + 1)
    else:
        next = empty(None)

    # make a paging status, identical to how js does it
    if batch['batch_end'] == batch['batch_start'] + 1:
        # single item only. start from 1
        fromto = "%i" % (batch['batch_start'] + 1, )
    else:
        # start from 1, finish at last item
        fromto = "%i-%i" % (batch['batch_start'] + 1, batch['batch_end'])
    batch['status'] = "Result %s of %i" % (fromto, batch['total'])

    #
    # Construct html
    # We do it this way and not with a template, because the current
    # markup is inline, and with TAL we can't seem to avoid whitespaces
    # inserted between the <a> and <span> tags. These whitespaces then
    # would destroy the layout.
    html = []
    if prev['url']:
        html.append(
            '<a class="ui-state-default ui-grid-pagination-icon" '
            'href="%(url)s">'
            '<div class="ui-icon ui-icon-circle-arrow-w">Prev</div>'
            '</a>' % prev)
    else:
        html.append(
            '<span class="ui-state-default ui-state-disabled '
            'ui-grid-pagination-icon">'
            '<div class="ui-icon ui-icon-circle-arrow-w">Prev</div>'
            '</span>')

    if ellipsis_begin['url']:
        html.append(
            '<a class="ui-state-default" href="%(url)s">%(page)s</a>'
            '<span class="ui-grid-pagination-dots">...</span>'
            % ellipsis_begin)

    for item in before:
        html.append('<a class="ui-state-default" href="%(url)s">%(page)s</a>'
            % pagemaker(item))

    html.append(
        '<span class="ui-state-active">%(page)s</span>' % empty(current))

    for item in after:
        html.append('<a class="ui-state-default" href="%(url)s">%(page)s</a>'
            % pagemaker(item))

    if ellipsis_end['url']:
        html.append(
            '<span class="ui-grid-pagination-dots">...</span>'
            '<a class="ui-state-default" href="%(url)s">%(page)s</a>'
            % ellipsis_end)

    if next['url']:
        html.append(
            '<a class="ui-state-default ui-grid-pagination-icon" '
            'href="%(url)s">'
            '<div class="ui-icon ui-icon-circle-arrow-e">Next</div>'
            '</a>' % next)
    else:
        html.append(
            '<span class="ui-state-default ui-state-disabled '
            'ui-grid-pagination-icon">'
            '<div class="ui-icon ui-icon-circle-arrow-e">Next</div>'
            '</span>')

    batch['gridbatch_snippet'] = ''.join(html)

    return batch


def get_container_batch(container, request, batch_start=0, batch_size=20,
        sort_index=None, reverse=False, permission='view',
        filter_func=None, interfaces=None):

    if 'batch_start' in request.params:
        batch_start = int(request.params['batch_start'])
    if 'batch_size' in request.params:
        batch_size = int(request.params['batch_size'])

    if sort_index == 'modified_date':
        now = datetime.datetime.now()

        # Use fine-grained sort keys for the modified_date.
        def sort_func(item, default):
            try:
                return item.modified
            except AttributeError:
                return now

    elif sort_index:
        catalog = find_catalog(container)
        index = catalog[sort_index]
        # XXX this is not part of ICatalogIndex, but it happens to work
        # for most indexes. It might be useful to expand ICatalogIndex.
        sort_func = index.discriminator

    else:
        sort_func = None

    entries = []  # [(sort key, name, item)]
    for name, item in container.items():
        if interfaces:
            # item must provide at least one of the given interfaces
            for iface in interfaces:
                if iface.providedBy(item):
                    break
            else:
                continue
        if permission:
            if not has_permission(permission, item, request):
                continue
        if filter_func:
            if not filter_func(name, item):
                continue
        if sort_func is not None:
            sort_key = sort_func(item, None)
        else:
            sort_key = None
        entries.append((sort_key, name, item))
    entries.sort()
    if reverse:
        entries.reverse()
    page_entries = entries[batch_start : batch_start + batch_size]

    info = {
        'entries': [item for _, _, item in page_entries],
        'batch_start': batch_start,
        'batch_size': batch_size,
        'batch_end': batch_start + len(page_entries),
        'total': len(entries),
        }
    _add_link_data(info, container, request)
    return info

def get_fileline_batch(fp, context, request, batch_start=0, batch_size=20,
                       backwards=False, line_filter=None):
    if 'batch_start' in request.params:
        batch_start = int(request.params['batch_start'])
    if 'batch_size' in request.params:
        batch_size = int(request.params['batch_size'])

    entries = []
    last = batch_start + batch_size

    i = 0
    j = 0

    if backwards:
        fp = backwards_reader(fp)

    for line in fp:
        i = i + 1
        if line_filter:
            line = line_filter(line)
            if line is None:
                continue
        if j <= last:
            entries.append(line)
        # we have to continue counting in order to show total
        # line count
        j = j + 1

    page_entries = entries[batch_start : last]

    info = {
        'entries': page_entries,
        'batch_start': batch_start,
        'batch_size': batch_size,
        'batch_end': batch_start + len(page_entries),
        'total': j,
        }
    _add_link_data(info, context, request)
    return info

def get_simple_batch(results, context, request, batch_start=0, batch_size=20):
    if 'batch_start' in request.params:
        batch_start = int(request.params['batch_start'])
    if 'batch_size' in request.params:
        batch_size = int(request.params['batch_size'])

    entries = []
    last = batch_start + batch_size

    i = 0
    j = 0

    for result in results:
        i = i + 1
        if j <= last:
            entries.append(result)
        # we have to continue counting in order to show total
        # line count
        j = j + 1

    page_entries = entries[batch_start : last]

    info = {
        'entries': page_entries,
        'batch_start': batch_start,
        'batch_size': batch_size,
        'batch_end': batch_start + len(page_entries),
        'total': j,
        }
    _add_link_data(info, context, request)
    return info

def backwards_reader(file, BLKSIZE=4096):
    buf = ""
    file.seek(-1, 2)
    lastchar = file.read(1)
    trailing_newline = (lastchar == "\n")

    while 1:
        newline_pos = buf.rfind("\n")
        pos = file.tell()
        if newline_pos != -1:
            # Found a newline
            line = buf[newline_pos+1:]
            buf = buf[:newline_pos]
            if pos or newline_pos or trailing_newline:
                line += "\n"
            yield line
        elif pos:
            # Need to fill buffer
            toread = min(BLKSIZE, pos)
            file.seek(-toread, 1)
            buf = file.read(toread) + buf
            file.seek(-toread, 1)
            if pos == toread:
                buf = "\n" + buf
        else:
            # Start-of-file
            return
