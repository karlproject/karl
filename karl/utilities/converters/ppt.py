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
PowerPoint converter

$Id: ppt.py 1331 2005-09-23 07:21:47Z ajung $
"""

import sys
from karl.utilities.converters.baseconverter import BaseConverter
from karl.utilities.converters.stripogram import html2text


class Converter(BaseConverter):

    content_type = ('application/mspowerpoint', 'application/ms-powerpoint', 
                'application/vnd.ms-powerpoint')
    content_description = "Microsoft PowerPoint"
    depends_on = 'ppthtml'

    def convert(self, filename, encoding, mimetype):
        """Convert PowerPoint document to raw text"""
        # XXX don't read entire file into RAM
        
        if sys.platform == 'win32':
            return self.execute('ppthtml "%s" 2> nul:' % filename), 'utf-8'
        else:
            return self.execute('ppthtml "%s" 2> /dev/null' % filename), 'utf-8'

PPTConverter = Converter()
