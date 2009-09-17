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

import lxml.etree
import datetime
import pytz
import time

from zope.interface import implements
from karl.sync.interfaces import IContentItem
from karl.sync.interfaces import IContentSource

_marker = object()

NAMESPACE = 'http://namespaces.karlproject.org/xml-sync'
NAMESPACES = {'k': NAMESPACE}

_marker = object()
def memoize(f):
    attr = '_memoize_' + f.__name__
    def wrapper(self):
        value = getattr(self, attr, _marker)
        if value is _marker:
            value = f(self)
            setattr(self, attr, value)
        return value
    return wrapper

def _element_value(node, name):
    return node.xpath('k:' + name, namespaces=NAMESPACES)[0].text

class XMLContentSource(object):
    """
    A content source which reads an XML stream.

    XXX Document xml format.  Currently you can look in test xml files under
        tests/
    """
    implements(IContentSource)


    def __init__(self, stream):
        self.doc = lxml.etree.parse(stream)
        self.root = self.doc.getroot()

    @property
    @memoize
    def id(self):
        return _element_value(self.root, 'id')

    @property
    @memoize
    def location(self):
        return self.root.get('location')

    @property
    @memoize
    def incremental(self):
        v = self.root.get('incremental')
        return v in ('t', 'T', 'true', 'True', '1', 'y', 'Y', 'yes', 'Yes')

    @property
    @memoize
    def modified(self):
        v = _element_value(self.root, 'modified')

        # Whoever decided to make strptime not be able to parse simple numeric
        # timezone offsets should be punched on the face.
        v, tzinfo = v[:-6], v[-6:]
        t = time.strptime(v, '%Y-%m-%dT%H:%M:%S')
        tzh, tzm = [int(x) for x in tzinfo.split(':')]
        tz = pytz.FixedOffset(tzh * 60 + tzm)
        tzinfo = dict(tzinfo=tz)
        return datetime.datetime(*t[:6], **tzinfo)

    @property
    def items(self):
        for element in self.root.iterchildren('{%s}item' % NAMESPACE):
            yield XMLContentItem(element)

    @property
    @memoize
    def deleted_items(self):
        return [element.text for element in
             self.root.iterchildren('{%s}deleted-item' % NAMESPACE)]

class XMLContentItem(object):
    """
    XXX
    """
    implements(IContentItem)

    def __init__(self, element):
        self.element = element


