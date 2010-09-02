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
a stupid HTML to Ascii converter

$Id: html.py 1470 2006-03-04 16:12:51Z ajung $
"""

import re
import StringIO
from karl.utilities.converters.baseconverter import BaseConverter
from karl.utilities.converters.entities import convert_entities
from karl.utilities.converters.stripogram import html2text

charset_reg = re.compile('text/html.*?charset=(.*?)"', re.I|re.M)

class Converter(BaseConverter):

    content_type = ('text/html',)
    content_description = "Converter HTML to ASCII"

    def convert(self, filename, encoding=None, mimetype=None):
        # XXX: dont read entire file into memory
        doc = open(filename, 'r').read()

        # convert to unicode
        if not encoding:
            mo = charset_reg.search(doc)
            encoding = mo.group(1)
        doc = unicode(doc, encoding, 'replace')
        doc = convert_entities(doc)
        result = html2text(doc)

        # convert back to utf-8
        return StringIO.StringIO(result.encode('utf-8')), 'utf-8'

HTMLConverter = Converter()
