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
from pyramid import testing

import karl.testing

class BlogTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.blog import Blog
        return Blog

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IBlog(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IBlog
        verifyClass(IBlog, self._getTargetClass())

    def test_instance_conforms_to_IBlog(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IBlog
        verifyObject(IBlog, self._makeOne())

class BlogEntryTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from karl.content.models.blog import BlogEntry
        return BlogEntry

    def _makeOne(self, title=u'title', text=u'text', description=u'text',
                 creator=u'admin',
                 ):
        return self._getTargetClass()(
            title, text, description, creator)

    def test_class_conforms_to_IBlogEntry(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IBlogEntry
        verifyClass(IBlogEntry, self._getTargetClass())

    def test_instance_conforms_to_IBlogEntry(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IBlogEntry
        verifyObject(IBlogEntry, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.text, u'text')
        self.assertEqual(instance.description, u'text')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        self.failUnless('comments' in instance)

        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ICommentsFolder
        verifyObject(ICommentsFolder, instance['comments'])

    def test_get_attachments(self):
        instance = self._makeOne()
        self.assertEqual(instance.get_attachments(), instance['attachments'])

class TestBlogToolFactory(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _makeOne(self):
        from karl.content.models.blog import blog_tool_factory
        return blog_tool_factory

    def test_it(self):
        from repoze.lemonade.interfaces import IContentFactory
        karl.testing.registerAdapter(lambda *arg, **kw: DummyContent, (None,),
                                     IContentFactory)
        context = testing.DummyModel()
        request = testing.DummyRequest
        factory = self._makeOne()
        factory.add(context, request)
        self.failUnless(context['blog'])
        self.failUnless(factory.is_present(context, request))
        factory.remove(context, request)
        self.failIf(factory.is_present(context, request))

class TestMailinTracerBlog(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        from karl.content.models import blog
        self._save_os = blog.os
        blog.os = self
        self._utime_called = None
        self._exists = set()

        karl.testing.registerSettings(mailin_trace_file='trace_file')

    def tearDown(self):
        testing.cleanUp()

        from karl.content.models import blog
        blog.os = self._save_os

    @property
    def path(self):
        return self

    def exists(self, path):
        return path in self._exists

    def split(self, path):
        return self._save_os.path.split(path)

    def makedirs(self, path):
        pass

    def utime(self, path, time):
        self.assertEqual(self._utime_called, None)
        self._utime_called = (path, time)

    def _getTargetClass(self):
        from karl.content.models.blog import MailinTraceBlog as cut
        return cut

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IBlog(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IBlog
        verifyClass(IBlog, self._getTargetClass())

    def test_instance_conforms_to_IBlog(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IBlog
        verifyObject(IBlog, self._makeOne())

    def test_it_file_exists(self):
        self._exists.add('trace_file')
        tool = self._makeOne()
        tool['foo'] = 'bar'
        self.assertEqual(self._utime_called, ('trace_file', None))

    def test_it_file_does_not_exist(self):
        tool = self._makeOne()
        tool['foo'] = 'bar'
        self.assertEqual(self._utime_called, ('trace_file', None))

class DummyContent:
    pass
