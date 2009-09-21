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

import base64
import lxml.etree
import datetime
import pytz
import sys
import time
import types

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

def _module(name):
    module = sys.modules.get(name, None)
    if module is None:
        try:
            module = __import__(name, globals(), locals(),
                                name.split('.')[:-1])
        except ImportError:
            return None
    return module

def _resolve_type(name):
    def _error():
        raise ValueError("Cannot resolve type: %s" % name)

    parts = name.split('.')
    cur = _module(parts.pop(0))
    if cur is None:
        _error()

    for part in parts:
        next = None
        if type(cur) == types.ModuleType:
            next = _module('.'.join((cur.__name__,part)))
        if next is None:
            next = getattr(cur, part, None)
        if next is None:
            _error()
        cur = next

    return cur

def _parse_date(s):
    # Whoever decided to make strptime not be able to parse simple numeric
    # timezone offsets should be punched in the face.
    s, tzinfo = s[:-6], s[-6:]
    t = time.strptime(s, '%Y-%m-%dT%H:%M:%S')
    tzh, tzm = [int(x) for x in tzinfo.split(':')]
    tz = pytz.FixedOffset(tzh * 60 + tzm)
    tzinfo = dict(tzinfo=tz)
    return datetime.datetime(*t[:6], **tzinfo)

def _boolean(value):
    if value is None:
        return False

    value = value.lower()
    if value in ('t', 'true', 'y', 'yes'):
        return True
    if value in ('f', 'false', 'n', 'no'):
        return False
    try:
        return not not int(value)
    except ValueError:
        raise ValueError("Can't convert to boolean: %s" % value)

# XXX Might need to make these pluggable at some point.
#     Can make these adapters and register with ZCA if need be.
_attr_converters = {
    'int': int,
    'float': float,
    'bool': _boolean,
    'bytes': base64.b64decode,
    'text': unicode,
    'timestamp': _parse_date,
    # XXX blob/clob external
    }

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
        return _boolean(self.root.get('incremental'))

    @property
    @memoize
    def modified(self):
        return _parse_date(_element_value(self.root, 'modified'))

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

    @property
    @memoize
    def id(self):
        return _element_value(self.element, 'id')


    @property
    @memoize
    def name(self):
        return _element_value(self.element, 'name')

    @property
    @memoize
    def type(self):
        return _resolve_type(_element_value(self.element, 'type'))

    @property
    @memoize
    def workflow_state(self):
        return _element_value(self.element, 'workflow-state')

    @property
    @memoize
    def created(self):
        return _parse_date(_element_value(self.element, 'created'))

    @property
    @memoize
    def created_by(self):
        return _element_value(self.element, 'created-by')

    @property
    @memoize
    def modified(self):
        return _parse_date(_element_value(self.element, 'modified'))

    @property
    @memoize
    def modified_by(self):
        return _element_value(self.element, 'modified-by')

    @property
    @memoize
    def attributes(self):
        attrs = {}
        for element in self.element.xpath('k:attributes/k:attribute',
                                          namespaces=NAMESPACES):
            name = element.get('name')
            if _boolean(element.get('none')):
                attrs[name] = None
            else:
                type = element.get('type')
                converter = _attr_converters[type]
                value = converter(element.text)
                attrs[name] = value

        return attrs

    @property
    def children(self):
        for element in self.element.xpath('k:item', namespaces=NAMESPACES):
            yield XMLContentItem(element)

    @property
    @memoize
    def deleted_children(self):
        return [element.text for element in
             self.element.iterchildren('{%s}deleted-item' % NAMESPACE)]
