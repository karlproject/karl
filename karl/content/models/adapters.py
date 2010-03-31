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

from zope.interface import implements
from zope.component import queryUtility

from ZODB.POSException import POSKeyError

from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_interface

from karl.models.interfaces import ITextIndexData
from karl.content.interfaces import ICalendar
from karl.utilities.converters.interfaces import IConverter
from karl.utilities.converters.entities import convert_entities
from karl.utilities.converters.stripogram import html2text


import logging
log = logging.getLogger(__name__)

class FlexibleTextIndexData(object):

    implements(ITextIndexData)

    ATTR_WEIGHT_CLEANER = [('title', 10, None),
                           ('description', 1, None),
                           ('text', 1, None),
                          ]

    def __init__(self, context):
        self.context = context

    def __call__(self):
        parts = []
        for attr, weight, cleaner in self.ATTR_WEIGHT_CLEANER:
            if callable(attr):
                value = attr(self.context)
            else:
                value = getattr(self.context, attr, None)
            if value is not None:
                if cleaner is not None:
                    value = cleaner(value)
                parts.extend([value] * weight)
        return ' '.join(filter(None, parts))

def makeFlexibleTextIndexData(attr_weights):
    if not attr_weights:
        raise ValueError('Must have at least one (attr, weight).')
    class Derived(FlexibleTextIndexData):
        ATTR_WEIGHT_CLEANER = attr_weights
    return Derived

def extract_text_from_html(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'replace')
    return html2text(convert_entities(text))

TitleAndDescriptionIndexData = makeFlexibleTextIndexData(
                                [('title', 10, None),
                                 ('description', 1, None),
                                ])

TitleAndTextIndexData = makeFlexibleTextIndexData(
                                [('title', 10, None),
                                 ('text', 1, extract_text_from_html),
                                ])

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
            assert filename, "Can't find filename for blob."
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

    datum = stream.read(1<<21) # XXX dont read too much into RAM
    if encoding is not None:
        try:
            datum = datum.decode(encoding)
        except UnicodeDecodeError:
            # XXX Temporary workaround to get import working
            # The "encoding" is a lie.  Coerce to ascii.
            log.error("Converted text is not %s: %s" %
                        (encoding, filename))
            if len(datum) > 0:
                datum = repr(datum)[2:-2]

    return datum

FileTextIndexData = makeFlexibleTextIndexData(
                                [('title', 10, None),
                                 (_extract_file_data, 1, None),
                                ])

class CalendarEventCategoryData(object):
    def __init__(self, context):
        self.context = context

    def __call__(self):
        category = getattr(self.context, 'calendar_category', None)
        if not category:
            calendar = find_interface(self.context, ICalendar)
            category = model_path(calendar)
        return category




