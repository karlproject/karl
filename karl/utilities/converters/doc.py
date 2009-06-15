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
WinWord converter

$Id: doc.py 1171 2005-05-23 14:31:41Z ajung $
"""

import os
import sys

from karl.utilities.converters.baseconverter import BaseConverter
here = os.path.dirname(__file__)
wvConf_file = os.path.join(here, 'wvText.xml')

class Converter(BaseConverter):

    content_type = ('application/msword',
                    'application/ms-word','application/vnd.ms-word')
    content_description = "Microsoft Word"
    depends_on = 'wvWare'

    def convert(self, filename, encoding, mimetype):
        """Convert WinWord document to raw text"""
        
        if sys.platform == 'win32':
            return self.execute(
                'wvWare -c utf-8 --nographics -x "%s" "%s" 2> nul:' % (
                wvConf_file, filename)), 'utf-8'
        else:
            return self.execute(
                'wvWare -c utf-8 --nographics -x "%s" "%s" 2> /dev/null' % (
                wvConf_file, filename)), 'utf-8'

DocConverter = Converter()
