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
pdf converter

$Id: pdf.py 1456 2006-02-08 14:10:27Z ajung $
"""

from karl.utilities.converters.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/pdf',)
    content_description = "Adobe Acrobat PDF"
    depends_on = 'pdftotext'

    def convert(self, filename, encoding, mimetype):
        """Convert pdf data to raw text"""
        return self.execute('pdftotext -enc UTF-8 "%s" -' % filename), 'utf-8'

PDFConverter = Converter()
