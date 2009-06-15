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

import os
from subprocess import Popen
from subprocess import PIPE
import tempfile

from zope.interface import implements
from karl.utilities.converters.interfaces import IConverter

class BaseConverterError(Exception):
    pass

class BaseConverter:
    """ Base class for all converters """

    content_type = None
    content_description = None

    implements(IConverter)

    def __init__(self):
        if not self.content_type:
            raise BaseConverterError('content_type undefinied')

        if not self.content_description:
            raise BaseConverterError('content_description undefinied')

    def execute(self, com):
        out = tempfile.TemporaryFile()
        PO = Popen(com, shell=True, stdout=out, close_fds=True)
        PO.communicate()
        out.seek(0)
        return out

    def getDescription(self):   
        return self.content_description

    def getType(self):          
        return self.content_type

    def getDependency(self):    
        return getattr(self, 'depends_on', None)

    def __call__(self, s):      
        return self.convert(s)
   
    def isAvailable(self):

        depends_on = self.getDependency()
        if depends_on:
            try:
                cmd = 'which %s' % depends_on
                PO =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
            except OSError:
                return 'no'
            else:
                out = PO.stdout.read()
                PO.wait()
                del PO
            if (
                ( out.find('no %s' % depends_on) > - 1 ) or
                ( out.lower().find('not found') > -1 ) or
                ( len(out.strip()) == 0 )
                ):
                return 'no'
            return 'yes'
        else:
            return 'always'

