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

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.sax.handler import ErrorHandler

from zope.interface import implements
from karl.sync.interfaces import IContentSource

_marker = object()

NAMESPACE = 'http://namespaces.karlproject.org/xml-sync'

class XMLContentSource(object):
    """
    A content source which reads an XML stream.  The format of the XML stream
    is as follows:

    <?xml version="1.0" ?>

    <source xmlns="http://namespaces.karlproject.org/xml-sync"
            path="foo/bar">
        <item>
            <id>765b078b-ccd7-4bb0-a197-ec23d03be430</id>
            <path>wxdu/blog</path>
            <name>why-radio-is-awesome</name>
            <type>IBlogEntry</type>
            <factory-signature>
              title, text, description, creator,
              reference=reference
            </factory-signature>
            <workflow-state>inherit</workflow-state>
            <created>2009-09-09T18:28:03-05:00</created>
            <created-by>crossi</created-by>
            <modified>2009-09-09T18:28:03-05:00</modified>
            <modified-by>crossi</modified-by>
            <attribute name="title" type="text">
                Why Radio is Awesome
            </attribute>
            <attribute name="text" type="text">
                Radio is awesome because ...
            </attribute>
            <attribute name="description" type="text"
                       none="True"/>
            <attribute name="creator" type="string">
                crossi
            </attribute>
        </item>
        <container path="abc/xyz">
            <item>
                ...
            </item>
            ...
        </container>
        ...
    </source>

    Attributes are converted from strings to Python objects according to their
    type.  Possible types are:

      - int
      - bool
      - float
      - timestamp
      - text
      - string

    """
    implements(IContentSource)


    def __init__(self, stream):
        self.stream = stream
        self.handler = _SAXHandler(self)
        parser = make_parser()
        parser.setFeature('http://xml.org/sax/features/namespaces', True)
        parser.setContentHandler(self.handler)
        parser.setErrorHandler(self.handler)
        self.parser = parser

        parser.parse(stream)

    _name = _marker

    @property
    def name(self):
        return self._name

class _SAXHandler(ContentHandler, ErrorHandler):
    def __init__(self, source):
        self.source = source
        self.state = _InSourceState(self, self.source)

    def startElementNS(self, name, qname, attrs):
        namespace, name = name
        if namespace == NAMESPACE:
            self.state.startElement(name, attrs)

    def endElementNS(self, name, qname):
        namespace, name = name
        if namespace == NAMESPACE:
            self.state.endElement(name)

    def characters(self, content):
        self.state.characters(content)

    def error(self, e):
        raise e

    def warning(self, e):
        raise e

    def fatalError(self, e):
        raise e

class _InSourceState(ContentHandler):
    def __init__(self, handler, source):
        self.handler = handler
        self.source = source

    def startElement(self, name, attrs):
        if name == 'name':
            self.handler.state = _SetAttributeFromElementValueState(
                self.handler, self, self.source, '_name'
            )

class _SetAttributeFromElementValueState(ContentHandler):
    def __init__(self, handler, parent, source, name):
        self.handler = handler
        self.parent = parent
        self.source = source
        self.name = name
        self.value = ''

    def startElement(self, name, attrs):
        raise Exception("%s element not allowed here" % name)

    def characters(self, content):
        self.value += content

    def endElement(self, name):
        setattr(self.source, self.name, self.value)
        self.handler.state = self.parent
