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

""" 
a simple OpenOffice converter 

$Id: ooffice.py 1331 2005-09-23 07:21:47Z ajung $
"""

import xml.sax
import zipfile
import tempfile
from xml.sax.handler import ContentHandler

from karl.utilities.converters.baseconverter import BaseConverter

class ootextHandler(ContentHandler):

    def characters(self, ch):
        self._data.write(ch.encode("utf-8") + ' ')

    def startDocument(self):
        self._data = tempfile.NamedTemporaryFile()

    def getxmlcontent(self, file):
        doctype = """<!DOCTYPE office:document-content PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">"""
        xmlstr = zipfile.ZipFile(file).read('content.xml')
        xmlstr = xmlstr.replace(doctype,'')       
        return xmlstr

    def getStream(self):
        self._data.seek(0)
        return self._data

class Converter(BaseConverter):

    content_type = ('application/vnd.sun.xml.calc',
          'application/vnd.sun.xml.calc.template',
          'application/vnd.sun.xml.draw',
          'application/vnd.sun.xml.draw.template',
          'application/vnd.sun.xml.impress',
          'application/vnd.sun.xml.impress.template',
          'application/vnd.sun.xml.math',
          'application/vnd.sun.xml.writer',
          'application/vnd.sun.xml.writer.global',
          'application/vnd.sun.xml.writer.template',
          'application/vnd.oasis.opendocument.chart',
          'application/vnd.oasis.opendocument.database',
          'application/vnd.oasis.opendocument.formula',
          'application/vnd.oasis.opendocument.graphics',
          'application/vnd.oasis.opendocument.graphics-template otg',
          'application/vnd.oasis.opendocument.image',
          'application/vnd.oasis.opendocument.presentation',
          'application/vnd.oasis.opendocument.presentation-template otp',
          'application/vnd.oasis.opendocument.spreadsheet',
          'application/vnd.oasis.opendocument.spreadsheet-template ots',
          'application/vnd.oasis.opendocument.text',
          'application/vnd.oasis.opendocument.text-master',
          'application/vnd.oasis.opendocument.text-template ott',
          'application/vnd.oasis.opendocument.text-web')
    content_description = "OpenOffice"

    def convert(self, filename, encoding, mimetype):
        handler = ootextHandler()
        xmlstr = handler.getxmlcontent(open(filename, 'r'))
        xml.sax.parseString(xmlstr, handler)
        return handler.getStream(), 'utf-8'

OOfficeConverter = Converter()
