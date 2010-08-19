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

from repoze.lemonade.content import create_content
from repoze.folder import Folder

from karl.models.interfaces import IToolFactory
from karl.models.tool import ToolFactory

from karl.content.interfaces import IForum
from karl.content.interfaces import IForumTopic
from karl.content.interfaces import IForumsFolder

from karl.content.models.commenting import CommentsFolder
from karl.content.models.attachments import AttachmentsFolder

class ForumsFolder(Folder):
    implements(IForumsFolder)
    title = u'Forums'

class Forum(Folder):
    implements(IForum)
    modified_by = None

    def __init__(self, title, description='', creator=None):
        super(Forum, self).__init__()
        self.title = unicode(title)
        self.description = unicode(description)
        self.creator = unicode(creator)
        self.modified_by = self.creator

class ForumTopic(Folder):
    implements(IForumTopic)
    modified_by = None

    def __init__(self, title='', text='', creator=None):
        super(ForumTopic, self).__init__()
        self.title = unicode(title)
        if text is None:
            self.text = u''
        else:
            self.text = unicode(text)
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self['comments'] = CommentsFolder()
        self['attachments'] = AttachmentsFolder()

class ForumsToolFactory(ToolFactory):
    implements(IToolFactory)
    name = 'forums'
    interfaces = (IForumsFolder, IForum, IForumTopic)
    def add(self, context, request):
        forums = create_content(IForumsFolder)
        context['forums'] = forums

    def remove(self, context, request):
        del context['forums']

forums_tool_factory = ForumsToolFactory()
