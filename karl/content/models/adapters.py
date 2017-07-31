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

import re
import zlib

from persistent import Persistent
from zope.interface import implements
from zope.component import queryUtility

from ZODB.POSException import POSKeyError

from pyramid.traversal import resource_path
from pyramid.traversal import find_interface

from karl.models.interfaces import ITextIndexData
from karl.content.interfaces import ICalendar
from karl.utilities.converters.interfaces import IConverter
from karl.utilities.converters.entities import convert_entities
from karl.utilities.converters.stripogram import html2text
from karl.utils import get_setting

import logging
log = logging.getLogger(__name__)

class FlexibleTextIndexData(object):

    implements(ITextIndexData)

    weighted_attrs_cleaners = (('title', None),
                               ('description', None),
                               ('text', None),)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        parts = []
        for attr, cleaner in self.weighted_attrs_cleaners:
            if callable(attr):
                value = attr(self.context)
            else:
                value = getattr(self.context, attr, None)
            if value is not None:
                if cleaner is not None:
                    value = cleaner(value)
                parts.append(value)
        # Want to remove empty attributes from the front of the list, but
        # leave empty attributes at the tail in order to preserve weight.
        while parts and not parts[0]:
            del parts[0]
        return tuple(parts)

def makeFlexibleTextIndexData(attr_weights):
    class Derived(FlexibleTextIndexData):
        weighted_attrs_cleaners = attr_weights
    return Derived

def extract_text_from_html(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'replace')
    return convert_entities(html2text(convert_entities(text))).strip()

TitleAndDescriptionIndexData = makeFlexibleTextIndexData(
                                [('title', None),
                                 ('description', None),
                                ])

TitleAndTextIndexData = makeFlexibleTextIndexData(
                                [('title', None),
                                 ('text', extract_text_from_html),
                                ])

class _CachedData(Persistent):
    encoding = None

    def __init__(self, data):
        if isinstance(data, unicode):
            self.encoding = 'utf8'
            data = data.encode('utf8')
        self.data = zlib.compress(data, 1)

    def get(self):
        data = zlib.decompress(self.data)
        if self.encoding:
            data = data.decode('utf8')
        return data

_MAX_CACHE_SIZE = 1<<18 # 256kb

def _extract_and_cache_file_data(context):
    cached_data = getattr(context, '_extracted_data', None)
    if isinstance(cached_data, _CachedData):
        return cached_data.get()

    if not cached_data:
        data = _extract_file_data(context)
    else:
        # Sorry, persistence.  We were storing this as directly as a string
        # attribute, but we'd prefer not to load it into memory if we don't
        # have to, so we're changing these to Persistent objects.
        data = cached_data
        del context._extracted_data

    if data and len(data) <= _MAX_CACHE_SIZE:
        context._extracted_data = cached_data = _CachedData(data)
    return data

def TO_READ():
    v = int(get_setting(None, 'pgtextindex.maxlen', 1<<21)) + 1
    global TO_READ
    TO_READ = lambda : v
    return v

def _extract_file_data(context):
    converter = queryUtility(IConverter, context.mimetype)
    if converter is None:
        return ''
    try:
        blobfile = context.blobfile
        if hasattr(blobfile, '_current_filename'):
            # ZODB < 3.9
            filename = context.blobfile._current_filename()
        else:
            # ZODB >= 3.9
            filename = blobfile._p_blob_uncommitted
            if not filename:
                filename = blobfile._p_blob_committed
            if not filename:
                # Blob file does not exist on filesystem
                return ''
    except POSKeyError, why:
        if why[0] != 'No blob file':
            raise
        return ''

    try:
        stream, encoding = converter.convert(filename, encoding=None,
                                             mimetype=context.mimetype)
    except Exception, e:
        # Just won't get indexed
        log.exception("Error converting file %s" % filename)
        return ''

    datum = stream.read(TO_READ()) # XXX dont read too much into RAM
    if encoding is not None:
        try:
            datum = datum.decode(encoding)
        except UnicodeDecodeError:
            # XXX Temporary workaround to get import working
            # The "encoding" is a lie.  Coerce to ascii.
            log.warning("Converted text is not %s: %s" %
                        (encoding, filename))
            if len(datum) > 0:
                datum = repr(datum)[2:-2]

    return datum

FileTextIndexData = makeFlexibleTextIndexData(
                                [('title', None),
                                 (_extract_and_cache_file_data, None),
                                ])

WIKILINK_RE = re.compile('\(\((.+)\)\)')

class WikiTextIndexData(TitleAndTextIndexData):

    def __call__(self):
        parts = super(WikiTextIndexData, self).__call__()
        def repl(match):
            return match.groups()[0]
        return tuple(WIKILINK_RE.sub(repl, part) for part in parts)


class CalendarEventCategoryData(object):
    def __init__(self, context):
        self.context = context

    def __call__(self):
        category = getattr(self.context, 'calendar_category', None)
        if not category:
            calendar = find_interface(self.context, ICalendar)
            category = resource_path(calendar)
        return category

