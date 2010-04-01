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

    def test_bad_image(self):
        o = self._makeOne(mimetype='image/jpeg')
        self.failIf(o.is_image)

    def test_thumbnail(self):
        from pkg_resources import resource_stream
        stream = resource_stream('karl.content.models.tests', 'test.jpg')
        o = self._makeOne(stream=stream, mimetype='image/jpeg')
        thumb = o.thumbnail((200, 200))
        self.assertEqual(thumb.image_size, (137, 200))

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

