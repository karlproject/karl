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

import datetime

import feedparser
from karl.models.interfaces import IFeed
from karl.models.interfaces import IFeedEntry
from karl.models.interfaces import IFeedsContainer
from persistent import Persistent
from persistent.list import PersistentList
from repoze.folder import Folder
from repoze.lemonade.content import create_content
from zope.interface import implements


_marker = object()

class FeedsContainer(Folder):
    implements(IFeedsContainer)


class Feed(Persistent):
    implements(IFeed)

    _feed_fields = ('title', 'subtitle', 'link')

    subtitle = None
    link = None
    etag = None
    feed_modified = None
    old_uri = None
    new_uri = None

    def __init__(self, title):
        self.title = title
        self.entries = PersistentList()

    def update(self, parser):
        for field in self._feed_fields:
            value = parser.feed.get(field)
            if getattr(self, field, _marker) != value:
                setattr(self, field, value)

        etag = parser.get('etag')
        if self.etag != etag:
            self.etag = etag

        modified = parser.get('modified')
        if self.feed_modified != modified:
            self.feed_modified = modified

        new_entries = [FeedEntry(e) for e in parser.entries]
        if new_entries != list(self.entries):
            self.entries[:] = new_entries


class FeedEntry(Persistent):
    implements(IFeedEntry)

    _entry_fields = ('title', 'summary', 'link', 'id')
    _date_fields = ('published', 'updated')

    def __init__(self, parser_entry):
        self.update(parser_entry)

    def update(self, parser_entry):
        for field in self._entry_fields:
            value = parser_entry.get(field)
            if getattr(self, field, _marker) != value:
                setattr(self, field, value)

        for field in self._date_fields:
            value = parser_entry.get(field + '_parsed')
            if value is not None:
                value = datetime.datetime(*value[:6])
            if getattr(self, field, _marker) != value:
                setattr(self, field, value)

        entry_content = parser_entry.get('content')
        if entry_content:
            content_list = []
            for content in entry_content:
                # *Always* sanitize the content HTML.
                # FeedParser sometimes doesn't sanitize, such as when
                # the input is base64 encoded.
                value = feedparser._sanitizeHTML(content.value, 'utf-8')
                content_list.append(value)
            content_html = '\n'.join(content_list)
        else:
            content_html = None
        if getattr(self, 'content_html', _marker) != content_html:
            self.content_html = content_html

    def __eq__(self, other):
        if not isinstance(other, FeedEntry):
            return False
        for field in self._entry_fields + self._date_fields:
            if getattr(self, field, _marker) != getattr(other, field, _marker):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)
