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
Code taken from Dieter Maurer's CatalogSupport Module
http://www.handshake.de/~dieter/pyprojects/zope
Thank you!

$Id: StripTagParser.py 1072 2005-05-01 12:05:51Z ajung $
"""

from sgmllib import SGMLParser

class StripTagParser(SGMLParser):
  '''SGML Parser removing any tags and translating HTML entities.'''

  data= None

  def handle_data(self,data):
    if self.data is None: self.data=[]
    self.data.append(data)

  def __str__(self):
    if self.data is None: return ''
    return ' '.join(self.data)

