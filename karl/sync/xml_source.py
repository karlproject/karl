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
from karl.sync.interfaces import IContentItem
from karl.sync.interfaces import IContentSource

_marker = object()

NAMESPACE = 'http://namespaces.karlproject.org/xml-sync'
NAMESPACES = {'k': NAMESPACE}

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
    def location(self):
        return self.root.get('location')

    @property
    def items(self):
        l = []
        for element in self.root.iterchildren('{%s}item' % NAMESPACE):
            yield XMLContentItem(element)

class XMLContentItem(object):
    """
    XXX
    """
    implements(IContentItem)

    def __init__(self, element):
        self.element = element


