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

""" A commenting facility that can be hung off resources"""

from zope.interface import implements
from repoze.folder import Folder

from karl.models.interfaces import ICommentsFolder
from karl.models.interfaces import IComment

class CommentsFolder(Folder):
    implements(ICommentsFolder)
    title = u'Comments Folder'

    @property
    def next_id(self):
        """Return a string with the next highest number key"""
        try:
            maxkey = self.data.maxKey()
        except ValueError:
            # no members
            return u'001'
        return u"%03d" % (int(maxkey) + 1)

class Comment(Folder):
    """ A comment can contain attachments """

    implements(IComment)
    attachments = None
    modified_by = None

    # XXX: description is probalby not needed--not sure when that would show
    #      up in UI.
    def __init__(self, title, text, description, creator):
        super(Comment, self).__init__()
        self.title = unicode(title)
        if text is None:
            self.text = u''
        else:
            self.text = unicode(text)
        if description is None:
            self.description = u''
        else:
            self.description = unicode(description)
        self.creator = unicode(creator)
        self.modified_by = self.creator
