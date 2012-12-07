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

import StringIO
from karl.utilities.converters.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('text/plain',)
    content_description = "Convert plaintext to UTF-8 encoded ASCII"

    def convert(self, filename, encoding=None, mimetype=None):
        # XXX: dont read entire file into memory
        doc = open(filename, 'r').read()

        # convert to unicode
        if encoding:
            result = unicode(doc, encoding)
        else:
            try:
                # try utf-8 encoding first
                result = unicode(doc, 'utf-8')
            except UnicodeDecodeError:
                # try latin-1 if we can't decode using utf-8, punt if
                # we can't decode and replace unknowable characters
                result = unicode(doc, 'latin-1', 'replace')

        # convert back to utf-8
        return StringIO.StringIO(result.encode('utf-8')), 'utf-8'

PlainTextConverter = Converter()
