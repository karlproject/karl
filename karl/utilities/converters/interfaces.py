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

from zope.interface import Interface

class IConverter(Interface):
    """ interface for converters """

    def getDescription():   
        """ return a string describing what the converter is for """

    def getType():          
        """ returns a list of supported mime-types """

    def getDependency():   
        """ return a string or a sequence of strings with external
            dependencies (external programs) for the converter
        """

    def isAvailable():
        """ Check the converter fulfills the dependency on some 
            external converter tools. Return 'yes', 'no' or 'unknown'.
        """

    def convert(doc, encoding, mimetype):
        """ Perform a transformation of 'doc' to (converted_text,
            new_encoding). 'encoding' and 'mimetype' can be used by
            the converter to adjust the conversion process.
            'converted_text' is either a Python string or a Python
            unicode string. 'new_encoding' is the encoding of
            'converted_text'. It must be set to 'unicode' if the 
            converted_text is a Python unicode string.
        """
