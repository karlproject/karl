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
import re

from persistent import Persistent
from zope.interface import implements

from karl.models.interfaces import IChatterbox
from karl.models.interfaces import IQuip
from karl.models.subscribers import set_created


_NAME = re.compile(r'@\w+')
_TAG = re.compile(r'#\w+')
_COMMUNITY = re.compile(r'&\w+')


class Chatterbox(Persistent):
    implements(IChatterbox)


class Quip(Persistent):
    implements(IQuip)

    def __init__(self, text):
        self._text = text
        set_created(self, None)

    def _getText(self):
        return self._text
    text = property(_getText,)

    def _getNames(self):
        return [x[1:] for x in _NAME.findall(self._text)]
    names = property(_getNames,)

    def _getTags(self):
        return [x[1:] for x in _TAG.findall(self._text)]
    tags = property(_getTags,)

    def _getCommunities(self):
        return [x[1:] for x in _COMMUNITY.findall(self._text)]
    communities = property(_getCommunities,)
