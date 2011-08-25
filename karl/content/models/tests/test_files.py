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

import unittest
from zope.testing.cleanup import cleanUp
from repoze.bfg import testing

class CommunityRootFolderTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.files import CommunityRootFolder
        return CommunityRootFolder

    def _makeOne(self, title=u''):
        return self._getTargetClass()()

    def test_class_conforms_to_ICommunityRootFolder(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import ICommunityRootFolder
        verifyClass(ICommunityRootFolder, self._getTargetClass())

    def test_instance_conforms_to_ICommunityRootFolder(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import ICommunityRootFolder
        verifyObject(ICommunityRootFolder, self._makeOne())


class CommunityFolderTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.files import CommunityFolder
        return CommunityFolder

    def _makeOne(self, title=u'', creator=u'admin'):
        return self._getTargetClass()(title, creator)

    def test_class_conforms_to_ICommunityFolder(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import ICommunityFolder
        verifyClass(ICommunityFolder, self._getTargetClass())

    def test_instance_conforms_to_ICommunityFolder(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import ICommunityFolder
        verifyObject(ICommunityFolder, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')


class CommunityFolderObjectVersionTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.files import CommunityFolderObjectVersion
        return CommunityFolderObjectVersion

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_wo_modified_by(self):
        class Dummy(testing.DummyModel):
            pass
        root = testing.DummyModel()
        context = root['folder'] = Dummy(title='Testing',
                                         docid=42,
                                         creator='unittest',
                                         modified_by=None,
                                        )
        version = self._makeOne(context)
        self.assertEqual(version.title, 'Testing')
        self.assertEqual(version.docid, 42)
        self.assertEqual(version.path, '/folder')
        self.assertEqual(version.attrs,
                        {'creator': 'unittest', 'modified_by': None})
        self.failUnless(version.klass is None)
        self.assertEqual(version.user, 'unittest')
        self.assertEqual(version.comment, None)

    def test_w_modified_by(self):
        class Dummy(testing.DummyModel):
            pass
        root = testing.DummyModel()
        context = root['folder'] = Dummy(title='Testing',
                                         docid=42,
                                         creator='unittest',
                                         modified_by='otherbloke',
                                        )
        version = self._makeOne(context)
        self.assertEqual(version.title, 'Testing')
        self.assertEqual(version.docid, 42)
        self.assertEqual(version.path, '/folder')
        self.assertEqual(version.attrs,
                        {'creator': 'unittest', 'modified_by': 'otherbloke'})
        self.failUnless(version.klass is None)
        self.assertEqual(version.user, 'otherbloke')
        self.assertEqual(version.comment, None)



class CommunityFolderContainerVersionTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.files import CommunityFolderContainerVersion
        return CommunityFolderContainerVersion

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_container_version(self):
        root = testing.DummyModel()
        folder = root['folder'] = testing.DummyModel('folder')
        folder.docid = 5
        folder['one'] = testing.DummyModel(docid=6)
        folder['two'] = testing.DummyModel(docid=7)
        folder['three'] = testing.DummyModel(docid=8)
        container = self._makeOne(folder)
        self.assertEqual(container.container_id, 5)
        self.assertEqual(container.path, '/folder')
        self.assertEqual(container.map, {
            'one': 6,
            'two': 7,
            'three': 8
        })
        self.assertEqual(container.ns_map, {})


class CommunityFileTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.files import CommunityFile
        return CommunityFile

    def _makeOne(self,
                 title=u'title',
                 stream=None,
                 mimetype='text/plain',
                 filename='afile.txt',
                 creator=u'admin',
                 ):
        if stream is None:
            stream = DummyFile()
        return self._getTargetClass()(
            title, stream, mimetype, filename, creator)

    def test_class_conforms_to_ICommunityFile(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import ICommunityFile
        verifyClass(ICommunityFile, self._getTargetClass())

    def test_instance_conforms_to_ICommunityFile(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import ICommunityFile
        verifyObject(ICommunityFile, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        self.assertEqual(instance.blobfile.open().read(), 'FAKECONTENT')
        self.assertEqual(instance.size, 11)
        self.assertEqual(instance.mimetype, 'text/plain')
        self.assertEqual(instance.filename, 'afile.txt')
        self.failIf(instance.is_image)

        from karl.content.interfaces import IImage
        self.failIf(IImage.providedBy(instance))

    def test_jpg(self):
        from karl.content.interfaces import IImage
        from pkg_resources import resource_stream
        stream = resource_stream('karl.content.models.tests', 'test.jpg')
        o = self._makeOne(stream=stream, mimetype='image/jpeg')
        self.failUnless(o.is_image)
        self.failUnless(IImage.providedBy(o))
        self.assertEqual(o.image_size, (390, 569))
        self.assertEqual(o.image().size, (390, 569))

        from zope.interface.verify import verifyObject
        verifyObject(IImage, o)
        return o

    def test_bad_image(self):
        o = self._makeOne(mimetype='image/jpeg')
        self.failIf(o.is_image)

    def test_from_image_to_nonimage(self):
        o = self.test_jpg()
        self.failUnless(o.is_image)
        o.upload(DummyFile())
        self.failIf(o.is_image)

    def test_thumbnail(self):
        from pkg_resources import resource_stream
        stream = resource_stream('karl.content.models.tests', 'test.jpg')
        o = self._makeOne(stream=stream, mimetype='image/jpeg')
        thumb = o.thumbnail((200, 200))
        self.assertEqual(thumb.image_size, (137, 200))

    def test_non_rgb_thumbnail(self):
        from cStringIO import StringIO
        from PIL import Image
        from pkg_resources import resource_stream
        stream = resource_stream('karl.content.models.tests', 'test.jpg')
        image = Image.open(stream)
        buf = StringIO()
        image.save(buf, 'GIF')
        buf.seek(0)
        o = self._makeOne(stream=buf, mimetype='image/jpeg')
        thumb = o.thumbnail((200, 200))
        self.assertEqual(thumb.image_size, (137, 200))

    def test_revert(self):
        from pkg_resources import resource_stream
        o = self._makeOne(mimetype='image/gif')
        class DummyVersion:
            docid = 5l
            created = 'created'
            title = 'title'
            modified = 'modified'
            attrs = {
                'filename': 'filename',
                'mimetype': 'image/jpg',
                'creator': 'creator'
            }
            user = 'user'
            blobs = {'blob': resource_stream(
                'karl.content.models.tests', 'test.jpg')}
        self.failIf(o.is_image)
        o.revert(DummyVersion)
        self.assertEqual(o.docid, 5)
        self.failUnless(type(o.docid) is int)
        self.assertEqual(o.created, 'created')
        self.assertEqual(o.title, 'title')
        self.assertEqual(o.modified, 'modified')
        self.assertEqual(o.filename, 'filename')
        self.assertEqual(o.mimetype, 'image/jpg')
        self.assertEqual(o.creator, 'creator')
        self.assertEqual(o.modified_by, 'user')
        self.failUnless(o.is_image)


class CommunityFileVersionTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.files import CommunityFileVersion
        return CommunityFileVersion

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_wo_modified_by(self):
        OPEN_FILE = object()
        class DummyBlobfile(object):
            def open(self):
                return OPEN_FILE
        class Dummy(testing.DummyModel):
            pass
        root = testing.DummyModel()
        folder = root['folder'] = testing.DummyModel()
        context = folder['file'] = Dummy(title='Testing',
                                         docid=42,
                                         creator='unittest',
                                         created='CREATED',
                                         modified_by=None,
                                         modified='MODIFIED',
                                         filename='FILENAME',
                                         mimetype='MIMETYPE',
                                         blobfile=DummyBlobfile(),
                                        )
        version = self._makeOne(context)
        self.assertEqual(version.title, 'Testing')
        self.assertEqual(version.description, None)
        self.assertEqual(version.created, 'CREATED')
        self.assertEqual(version.modified, 'MODIFIED')
        self.assertEqual(version.docid, 42)
        self.assertEqual(version.path, '/folder/file')
        self.assertEqual(version.attrs,
                        {'creator': 'unittest',
                         'filename': 'FILENAME',
                         'mimetype': 'MIMETYPE'})
        self.assertEqual(version.blobs, {'blob': OPEN_FILE})
        self.failUnless(version.klass is None)
        self.assertEqual(version.user, 'unittest')
        self.assertEqual(version.comment, None)

    def test_w_modified_by(self):
        OPEN_FILE = object()
        class DummyBlobfile(object):
            def open(self):
                return OPEN_FILE
        class Dummy(testing.DummyModel):
            pass
        root = testing.DummyModel()
        folder = root['folder'] = testing.DummyModel()
        context = folder['file'] = Dummy(title='Testing',
                                         docid=42,
                                         creator='unittest',
                                         created='CREATED',
                                         modified_by='otherbloke',
                                         modified='MODIFIED',
                                         filename='FILENAME',
                                         mimetype='MIMETYPE',
                                         blobfile=DummyBlobfile(),
                                        )
        version = self._makeOne(context)
        self.assertEqual(version.title, 'Testing')
        self.assertEqual(version.description, None)
        self.assertEqual(version.created, 'CREATED')
        self.assertEqual(version.modified, 'MODIFIED')
        self.assertEqual(version.docid, 42)
        self.assertEqual(version.path, '/folder/file')
        self.assertEqual(version.attrs,
                        {'creator': 'unittest',
                         'filename': 'FILENAME',
                         'mimetype': 'MIMETYPE'})
        self.assertEqual(version.blobs, {'blob': OPEN_FILE})
        self.failUnless(version.klass is None)
        self.assertEqual(version.user, 'otherbloke')
        self.assertEqual(version.comment, None)


class TestThumbnail(unittest.TestCase):
    def _getTargetClass(self):
        from karl.content.models.files import Thumbnail
        return Thumbnail

    def _makeOne(self, pil_img=None, size=(200, 200)):
        if pil_img is None:
            import pkg_resources
            img_file = pkg_resources.resource_stream(
                'karl.content.models.tests', 'test.jpg'
            )
            import PIL.Image
            pil_img = PIL.Image.open(img_file)

        return self._getTargetClass()(pil_img, size)

    def test_thumb(self):
        thumb = self._makeOne()
        self.assertEqual(thumb.image_size, (137, 200))
        self.assertEqual(thumb.image().size, (137, 200))

    def test_wide_thumb(self):
        thumb = self._makeOne(size=(200, 600))
        self.assertEqual(thumb.image_size, (200, 291))
        self.assertEqual(thumb.image().size, (200, 291))

class TestFilesToolFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from karl.content.models.files import files_tool_factory
        return files_tool_factory

    def test_factory(self):
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg, **kw: DummyContent, (None,),
                                IContentFactory)
        context = testing.DummyModel()
        request = testing.DummyRequest
        factory = self._makeOne()
        factory.add(context, request)
        self.failUnless(context['files'])
        self.failUnless(factory.is_present(context, request))
        factory.remove(context, request)
        self.failIf(factory.is_present(context, request))

class DummyContent:
    pass

class DummyFile:
    def __init__(self, content='FAKECONTENT'):
        self.content = content

    def read(self, num):
        content = self.content[:num]
        self.content = self.content[num:]
        return content

