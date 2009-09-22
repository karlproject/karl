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

from zope.interface import implements
from repoze.folder import Folder
from karl.models.image import extensions as image_extensions
from karl.content.interfaces import INewsItem
from karl.content.models.attachments import AttachmentsFolder

class NewsItem(Folder):
    implements(INewsItem)

    title = None
    text = None
    creator = None
    modified_by = None
    publication_date = None

    def __init__(self, title, text, creator, publication_date,
                 caption=None, data=None):
        super(NewsItem, self).__init__(data)
        self.title = title
        self.text = text
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self.publication_date = publication_date
        self.caption = caption

        self["attachments"] = AttachmentsFolder()

    def get_photo(self):
        for ext in image_extensions.values():
            name = "photo." + ext
            if name in self:
                return self[name]
        return None
