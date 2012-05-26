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

from datetime import datetime
import hashlib
import re
import shlex

from appendonly import AppendStack
from appendonly import Archive
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.interface import implements

from karl.models.interfaces import IChatterbox
from karl.models.interfaces import IQuip
from karl.models.subscribers import set_created


_NOW = None
def _now():
    if _NOW is None:
        return datetime.utcnow()
    return _NOW

_NAME = re.compile(r'@\w+')
_TAG = re.compile(r'#\w+')
_COMMUNITY = re.compile(r'&\w+')
_ANY = re.compile(r'(?P<marker>[@#&])(?P<name>\w+)')


class Chatterbox(Persistent):
    implements(IChatterbox)

    def __init__(self):
        self._quips = OOBTree()
        self._followed = OOBTree()
        # AppendStack defaults seem too low for search to make sense
        self._recent = AppendStack(max_layers=20, max_length=500)
        self._archive = Archive()

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

    def addQuip(self, text, creator, repost=None, reply=None):
        """ See IChatterbox.
        """
        quip = Quip(text, creator, repost, reply)
        sha = hashlib.sha512(text)
        sha.update(creator)
        sha.update(quip.created.isoformat())
        key = sha.hexdigest()
        self._quips[key] = quip
        quip.__name__ = key
        quip.__parent__ = self
        self._recent.push(quip, self._archive.addLayer)
        return key

    def listFollowed(self, userid):
        """ See IChatterbox.
        """
        return self._followed.get(userid, ())

    def setFollowed(self, userid, followed):
        """ See IChatterbox.
        """
        self._followed[userid] = tuple(followed)

    def listFollowing(self, userid):
        """ See IChatterbox.
        """
        for name, following in self._followed.items():
            if userid in following:
                yield name

    def recent(self):
        """ See IChatterbox.
        """
        for gen, index, quip in self._recent:
            yield quip

    def recentFollowed(self, userid):
        """ See IChatterbox.
        """
        creators = (userid,) + self.listFollowed(userid)
        return self.recentWithCreators(*creators)

    def recentWithTag(self, tag):
        """ See IChatterbox.
        """
        for quip in self.recent():
            if tag in quip.tags:
                yield quip

    def recentWithCommunities(self, *communities):
        """ See IChatterbox.
        """
        communities = set(communities)
        for quip in self.recent():
            if communities & quip.communities:
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

    def recentTags(self):
        """ See IChatterbox.
        """
        tags = set()
        for quip in self.recent():
            for tag in quip.tags:
                tags.add(tag)
        return list(tags)

    def recentPrivate(self, user):
        """ See IChatterbox.
        """
        for quip in self.recent():
            if not bool(getattr(quip, '__acl__', ())):
                continue
            allowed = [e[2] for e in quip.__acl__]
            if user in allowed:
                yield quip

    def recentCorrespondents(self, user):
        """ See IChatterbox.
        """
        correspondents = {}
        for quip in self.recent():
            if not bool(getattr(quip, '__acl__', ())):
                continue
            allowed = []
            conversed = False
            for acl in quip.__acl__:
                if acl[2] == user:
                    conversed = True
                    continue
                if acl[0] != 'Deny':
                    allowed.append(acl[2])
            if not allowed or not conversed:
                continue
            if allowed[0] not in correspondents:
                correspondents[allowed[0]] = {'timeago': quip.created,
                                           'summary': quip.text[:40]}
        return correspondents

    def recentConversations(self, user, correspondent):
        """ See IChatterbox.
        """
        for quip in self.recent():
            if not bool(getattr(quip, '__acl__', ())):
                continue
            allowed = [e[2] for e in quip.__acl__]
            if user in allowed and correspondent in allowed:
                yield quip

    def recentInReplyTo(self, quipid):
        """ See IChatterbox.
        """
        for quip in self.recent():
            if quip.reply == quipid:
                yield quip

    def recentWithMatch(self, query):
        """ See IChatterbox.
        """
        query = query.replace('*', '.*')
        patterns = [(word, re.compile("\\b%s\\b" % word, re.IGNORECASE))
                       for word in shlex.split(query.encode('utf-8'))]
        for quip in self.recent():
            match_expr = query.replace('"', '')
            fallback_and = True
            for word, pattern in patterns:
                if word in ['and', 'or', 'not']:
                    continue
                if pattern.search(quip.text):
                    match_expr = match_expr.replace(word, 'True')
                else:
                    match_expr = match_expr.replace(word, 'False')
                    fallback_and = False
            try:
                match = eval(match_expr,
                    {'__builtins__': {'True': True, 'False': False}})
            except SyntaxError:
                match = fallback_and
            if match:
                yield quip


def _renderHTML(text):
    chunks = []
    last = 0
    for match in _ANY.finditer(text):
        chunks.append(text[last:match.start()])
        if match.group('marker') == '@':
            exp = match.expand('<a class="quip-name" ref="\g<name>" '
                                  'href="#">@\g<name></a>')
        elif match.group('marker') == '#':
            exp = match.expand('<a class="quip-tag" ref="\g<name>" '
                                  'href="#">#\g<name></a>')
        elif match.group('marker') == '&':
            exp = match.expand('<a class="quip-community" ref="\g<name>" '
                                  'href="#">&\g<name></a>')
        else:
            raise ValueError("Unknown quip syntax: %s" % text)
        chunks.append(exp)
        last = match.end()
    chunks.append(text[last:])
    return '<div class="quip">\n%s\n</div>' % ''.join(chunks)


class Quip(Persistent):
    implements(IQuip)
    # add a few class attributes for backwards compatibility
    _html = None
    repost = None
    reply = None

    def __init__(self, text, creator, repost=None, reply=None):
        self._text = text
        self._html = _renderHTML(text)
        self._names = frozenset([x[1:] for x in _NAME.findall(self._text)])
        self._tags = frozenset([x[1:] for x in _TAG.findall(self._text)])
        self._communities = frozenset(
            [x[1:] for x in _COMMUNITY.findall(self._text)])
        self.creator = self.modified_by = creator
        set_created(self, None)
        self.modified = self.created = _now()
        self.repost = repost
        self.reply = reply

    def __repr__(self):
        return 'Quip: %s [%s]' % (self._text, self.creator)

    text = property(lambda self: self._text,)

    html = property(lambda self: self._html,)

    names = property(lambda self: self._names,)

    tags = property(lambda self: self._tags,)

    communities = property(lambda self: self._communities,)
