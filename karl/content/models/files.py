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

from persistent import Persistent

from repoze.lemonade.content import create_content

from zope.interface import implements

from karl.models.tool import ToolFactory
from karl.models.interfaces import IToolFactory

from karl.content.interfaces import ICommunityRootFolder
from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import ICommunityFile

from repoze.folder import Folder
from ZODB.blob import Blob

class CommunityRootFolder(Folder):
    implements(ICommunityRootFolder)
    title = u'Files'

class CommunityFolder(Folder):
    implements(ICommunityFolder)
    modified_by = None

    def __init__(self, title, creator):
        super(CommunityFolder, self).__init__()
        self.title = unicode(title)
        self.creator = unicode(creator)
        self.modified_by = self.creator

class CommunityFile(Persistent):
    implements(ICommunityFile)
    modified_by = None

    def __init__(self, title, stream, mimetype, filename, creator=u''):
        self.title = unicode(title)
        self.mimetype = mimetype
        self.filename = filename
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self.blobfile = Blob()
        self.upload(stream)

    def upload(self, stream):
        f = self.blobfile.open('w')
        size = upload_stream(stream, f)
        f.close()
        self.size = size

def upload_stream(stream, file):
    size = 0
    while 1:
        data = stream.read(1<<21)
        if not data:
            break
        size += len(data)
        file.write(data)
    return size

class FilesToolFactory(ToolFactory):
    implements(IToolFactory)
    name = 'files'
    interfaces = (ICommunityRootFolder, ICommunityFolder, ICommunityFile)
    def add(self, context, request):
        files = create_content(ICommunityRootFolder)
        context['files'] = files

    def remove(self, context, request):
        del context['files']

files_tool_factory = FilesToolFactory()
