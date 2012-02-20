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
import hashlib
import re

from appendonly import AppendStack
from BTrees.OOBTree import OOBTree
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

    def __init__(self):
        self._quips = OOBTree()
        self._recent = AppendStack() #XXX parms?  10 layers x 100 items default

    def __iter__(self):
        return iter(self._quips)

    def __len__(self):
        """ See IChatterbox.
        """
        return len(self._quips)

    def __getitem__(self, key):
        """ See IChatterbox.
        """
        return self._quips[key]

    def addQuip(self, text, creator):
        """ See IChatterbox.
        """
        quip = Quip(text, creator)
        sha = hashlib.sha512(text)
        sha.update(creator)
        sha.update(quip.created.isoformat())
        key = sha.hexdigest()
        self._quips[key] = quip
        quip.__name__ = key
        quip.__parent__ = self
        self._recent.push(quip
                         # TODO:  pruner=???
                         )
        return key

    def recent(self):
        """ See IChatterbox.
        """
        for gen, index, quip in self._recent:
            yield quip

    def recentWithTag(self, tag):
        """ See IChatterbox.
        """
        for quip in self.recent():
            if tag in quip.tags:
                yield quip

    def recentWithCommunity(self, community):
        """ See IChatterbox.
        """
        for quip in self.recent():
            if community in quip.communities:
                yield quip

    def recentWithCreators(self, *creators):
        """ See IChatterbox.
        """
        names = set(creators)
        for quip in self.recent():
            if quip.creator in creators:
                yield quip

    def recentWithNames(self, *names):
        """ See IChatterbox.
        """
        names = set(names)
        for quip in self.recent():
            if names & quip.names:
                yield quip


class Quip(Persistent):
    implements(IQuip)

    def __init__(self, text, creator):
        self._text = text
        self._names = frozenset([x[1:] for x in _NAME.findall(self._text)])
        self._tags = frozenset([x[1:] for x in _TAG.findall(self._text)])
        self._communities = frozenset(
            [x[1:] for x in _COMMUNITY.findall(self._text)])
        self.creator = self.modified_by = creator
        set_created(self, None)

    text = property(lambda self: self._text,)

    names = property(lambda self: self._names,)

    tags = property(lambda self: self._tags,)

    communities = property(lambda self: self._communities,)
