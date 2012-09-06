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
from cStringIO import StringIO

from BTrees.OOBTree import OOBTree

from pyramid.traversal import resource_path
import PIL.Image
from ZODB.blob import Blob
from persistent import Persistent
from repoze.folder import Folder

from repoze.lemonade.content import create_content
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides

from karl.content.interfaces import ICommunityRootFolder
from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IEventContainer
from karl.content.interfaces import IImage
from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IObjectVersion
from karl.models.interfaces import IToolFactory
from karl.models.tool import ToolFactory


class CommunityRootFolder(Folder):
    implements(ICommunityRootFolder, IEventContainer)
    title = u'Files'


class CommunityFolder(Folder):
    implements(ICommunityFolder, IEventContainer)
    modified_by = None

    def __init__(self, title='', creator=''):
        super(CommunityFolder, self).__init__()
        self.title = unicode(title)
        self.creator = unicode(creator)
        self.modified_by = self.creator

    def revert(self, version):
        # catalog document map blows up if you feed it a long int
        self.title = version.title
        self.created = version.created
        self.modified = version.modified
        self.docid = int(version.docid)
        self.creator = version.attrs['creator']
        self.modified_by = version.user


class CommunityFolderObjectVersion(object):
    implements(IObjectVersion)

    def __init__(self, folder):
        self.title = folder.title
        self.description = None
        self.created = folder.created
        self.modified = folder.modified
        self.docid = folder.docid
        self.path = resource_path(folder)
        self.attrs = dict((name, getattr(folder, name)) for name in [
            'creator',
            'modified_by',
        ])
        self.klass = folder.__class__ # repozitory can't detect we are a shim
        self.user = folder.modified_by
        if self.user is None:
            self.user = folder.creator
        self.comment = None


class CommunityFolderContainerVersion(object):
    implements(IContainerVersion)

    def __init__(self, folder):
        self.container_id = folder.docid
        self.path = resource_path(folder)
        self.map = dict((name, page.docid) for name, page in folder.items())
        self.ns_map = {}


class CommunityFile(Persistent):
    implements(ICommunityFile)
    modified_by = None  # Sorry, persistence
    is_image = False    # Sorry, persistence

    def __init__(self,
                 title=u'',
                 stream=None,
                 mimetype=u'',
                 filename=u'',
                 creator=u''):
        self.title = unicode(title)
        self.mimetype = mimetype
        self.filename = filename
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self.blobfile = Blob()
        if stream is not None:
            self.upload(stream)

    def image(self):
        assert self.is_image, "Not an image."
        return PIL.Image.open(self.blobfile.open())

    def thumbnail(self, size):
        assert self.is_image, "Not an image."
        key = '%dx%d' % size
        thumbnail = self._thumbs.get(key, None)
        if thumbnail is None:
            image = self.image()
            if image.format == 'TIFF' and 'compression' in image.info:
                if image.info['compression'] in ['group3', 'group4']:
                    image = self.get_default_tiff_thumbnail()
            self._thumbs[key] = thumbnail = Thumbnail(image, size)
        return thumbnail

    def get_default_tiff_thumbnail(self):
        here = os.path.dirname(__file__)
        path = os.path.join(here, '..', '..', 'views', 'static',
                'images', 'tiff.png')
        tiff = PIL.Image.open(path)
        return tiff

    def upload(self, stream):
        f = self.blobfile.open('w')
        size = upload_stream(stream, f)
        f.close()
        self.size = size
        self._init_image()

    def _check_image(self):
        if not self.mimetype.startswith('image'):
            return

        try:
            image = PIL.Image.open(self.blobfile.open())
        except IOError:
            return

        return image

    def _init_image(self):
        image = self._check_image()

        if image is not None:
            self._thumbs = OOBTree()
            self.image_size = image.size
            self.is_image = True
            alsoProvides(self, IImage)

        elif self.is_image:
            del self._thumbs
            del self.image_size
            self.is_image = False
            noLongerProvides(self, IImage)

    def revert(self, version):
        # catalog document map blows up if you feed it a long int
        self.docid = int(version.docid)
        self.created = version.created
        self.title = version.title
        self.modified = version.modified
        self.filename = version.attrs['filename']
        self.mimetype = version.attrs['mimetype']
        self.creator = version.attrs['creator']
        self.modified_by = version.user
        self.upload(version.blobs['blob'])
        # make sure file data is re-indexed
        self._extracted_data = None


def upload_stream(stream, file):
    size = 0
    while 1:
        data = stream.read(1<<21)
        if not data:
            break
        size += len(data)
        file.write(data)
    return size


class Thumbnail(Persistent):
    mimetype = 'image/jpeg'

    def __init__(self, image, max_size):
        thumb_size = _thumb_size(image.size, max_size)
        thumb_img = image.resize(thumb_size, PIL.Image.ANTIALIAS)
        img_buf = StringIO()
        if thumb_img.mode != 'RGB':
            thumb_img = thumb_img.convert('RGB')
        thumb_img.save(img_buf, 'JPEG', quality=90)

        data = img_buf.getvalue()
        self.size = len(data)
        self.blobfile = blob = Blob()
        blob.open('w').write(data)
        self.image_size = thumb_img.size

    def image(self):
        return PIL.Image.open(self.blobfile.open())


def _thumb_size(orig_size, max_size):
    orig_x, orig_y = orig_size
    max_x, max_y = max_size

    x = max_x
    ratio = float(max_x) / float(orig_x)
    y = int(orig_y * ratio)

    if y <= max_y:
        return x, y

    y = max_y
    ratio = float(max_y) / float(orig_y)
    x = int(orig_x * ratio)

    assert x < max_x
    return x, y


class CommunityFileVersion(object):
    implements(IObjectVersion)

    def __init__(self, file):
        self.title = file.title
        self.description = None
        self.created = file.created
        self.modified = file.modified
        self.docid = file.docid
        self.path = resource_path(file)
        self.attrs = dict((name, getattr(file, name)) for name in [
            'mimetype',
            'filename',
            'creator',
        ])
        self.blobs = {'blob': file.blobfile.open()}
        self.klass = file.__class__ # repozitory can't detect we are a shim
        self.user = file.modified_by
        if self.user is None:
            self.user = file.creator
        self.comment = None


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
