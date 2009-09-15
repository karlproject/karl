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

from zope.interface import implements
from karl.sync.interfaces import IContentSource

_marker = object()

NAMESPACE = 'http://namespaces.karlproject.org/xml-sync'
NAMESPACES = {'k': NAMESPACE}

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
        self.doc = lxml.etree.parse(stream)
        self.element = self.doc.getroot()

    @property
    def path(self):
        return self.element.get('path')

