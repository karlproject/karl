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
import sys
import types

from zope.interface import implements
from karl.sync.conversion import convert
from karl.sync.interfaces import IContentItem
from karl.sync.interfaces import IContentNode
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

def _element_value(node, name, default=_marker):
    nodes = node.xpath('k:' + name, namespaces=NAMESPACES)
    if not nodes:
        if default is not _marker:
            return default
        raise LookupError('No such element: %s' % name)

    if len(nodes) > 1:
        raise LookupError('Too many elements: %s' % name)

    return nodes[0].text.strip()

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

def _simple_attr_value(element):
    type = element.get('type')
    if type is None:
        type = 'text'
    return convert(element.text.strip(), type)

def _list_attr_value(element):
    return [_simple_attr_value(item) for item in
            element.xpath('k:item', namespaces=NAMESPACES)]

def _dict_attr_value(element):
    return dict([(item.get('name'), _simple_attr_value(item)) for item in
            element.xpath('k:item', namespaces=NAMESPACES)])

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
    def location(self):
        return self.root.get('location')

    @property
    @memoize
    def incremental(self):
        return convert(self.root.get('incremental'), 'bool')

    @property
    def content(self):
        for element in self.root.iterchildren('{%s}content' % NAMESPACE):
            yield XMLContentItem(element)

    @property
    def nodes(self):
        for element in self.root.iterchildren('{%s}node' % NAMESPACE):
            yield XMLContentNode(element)

    @property
    @memoize
    def deleted_content(self):
        return [element.text.strip() for element in
             self.root.iterchildren('{%s}deleted-content' % NAMESPACE)]


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
        timestamp = _element_value(self.element, 'created', None)
        if timestamp is not None:
            return convert(timestamp, 'timestamp')
        return datetime.datetime.now()

    @property
    @memoize
    def created_by(self):
        return _element_value(self.element, 'created-by')

    @property
    @memoize
    def modified(self):
        timestamp = _element_value(self.element, 'modified', None)
        if timestamp is not None:
            return convert(timestamp, 'timestamp')
        return datetime.datetime.now()

    @property
    @memoize
    def modified_by(self):
        return _element_value(self.element, 'modified-by')

    @property
    @memoize
    def attributes(self):
        attrs = {}
        for element in self.element.xpath('k:attributes/k:*',
                                          namespaces=NAMESPACES):
            name = element.get('name')
            if convert(element.get('none'), 'bool'):
                attrs[name] = None
            else:
                if element.tag == '{%s}simple' % NAMESPACE:
                    attrs[name] = _simple_attr_value(element)
                elif element.tag == '{%s}list' % NAMESPACE:
                    attrs[name] = _list_attr_value(element)
                elif element.tag == '{%s}dict' % NAMESPACE:
                    attrs[name] = _dict_attr_value(element)

        return attrs

    @property
    def children(self):
        for element in self.element.xpath('k:content', namespaces=NAMESPACES):
            yield XMLContentItem(element)

    @property
    @memoize
    def deleted_children(self):
        return [element.text.strip() for element in
             self.element.iterchildren('{%s}deleted-content' % NAMESPACE)]

class XMLContentNode(object):
    """
    XXX
    """
    implements(IContentNode)

    def __init__(self, element):
        self.element = element

    @property
    @memoize
    def name(self):
        return self.element.get('name')

    @property
    def nodes(self):
        for element in self.element.iterchildren('{%s}node' % NAMESPACE):
            yield XMLContentNode(element)

    @property
    def content(self):
        for element in self.element.xpath('k:content', namespaces=NAMESPACES):
            yield XMLContentItem(element)

    @property
    @memoize
    def deleted_content(self):
        return [element.text.strip() for element in
             self.element.iterchildren('{%s}deleted-content' % NAMESPACE)]
