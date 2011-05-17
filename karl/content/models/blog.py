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
import transaction

from zope.interface import implements

from repoze.bfg.settings import get_settings
from repoze.lemonade.content import create_content
from repoze.folder import Folder

from karl.models.interfaces import IToolFactory
from karl.models.tool import ToolFactory

from karl.content.interfaces import IBlog
from karl.content.interfaces import IBlogEntry

from karl.content.models.commenting import CommentsFolder
from karl.content.models.attachments import AttachmentsFolder

class Blog(Folder):
    implements(IBlog)
    title = u'Blog'

class BlogEntry(Folder):
    implements(IBlogEntry)
    modified_by = None

    def __init__(self, title, text, description, creator):
        super(BlogEntry, self).__init__()
        assert title is not None
        assert text is not None
        assert description is not None
        assert creator is not None
        self.title = unicode(title)
        self.text = unicode(text)
        self.description = unicode(description)
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self['comments'] = CommentsFolder()
        self['attachments'] = AttachmentsFolder()

    def get_attachments(self):
        return self['attachments']

class BlogToolFactory(ToolFactory):
    implements(IToolFactory)
    name = 'blog'
    interfaces = (IBlog, IBlogEntry)
    def add(self, context, request):
        blog = create_content(IBlog)
        context['blog'] = blog

    def remove(self, context, request):
        del context['blog']

blog_tool_factory = BlogToolFactory()


class MailinTraceBlog(Folder):
    """
    This tool can be used in place of a Blog in a specially set up test
    community for testing mailin. When a message is picked up by mailin that
    is destined for this tool, mailin will then try to add a BlogEntry to this
    tool as though it were a regular blog. Rather than storing the passed in
    blog entry the way that a regular blog would, this tool updates the
    timestamp on a file in the filesystem.  The timestamp on that file can then
    be monitored externally.  Assuming an external process which is sending
    email messages to this tool at regular intervals, if the timestamp fails
    to update for a period of time one can presume that something is broken
    in mailin and a developer can be alerted to investigate.
    """
    implements(IBlog)
    title = u'Mailin Trace Blog'

    def __setitem__(self, name, value):
        path = get_settings()['mailin_trace_file']
        if not os.path.exists(path):
            folder, fname = os.path.split(path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            open(path, 'w').close()
        os.utime(path, None)


