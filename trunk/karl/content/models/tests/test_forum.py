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
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp

class ForumsFolderTests(unittest.TestCase):
    def _getTargetClass(self):
        from karl.content.models.forum import ForumsFolder
        return ForumsFolder

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IForum(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IForumsFolder
        verifyClass(IForumsFolder, self._getTargetClass())

    def test_instance_conforms_to_IForum(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IForumsFolder
        verifyObject(IForumsFolder, self._makeOne())


class ForumTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.forum import Forum
        return Forum

    def _makeOne(self, title='title', description='description', creator=None):
        return self._getTargetClass()(title, description, creator)

    def test_class_conforms_to_IForum(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IForum
        verifyClass(IForum, self._getTargetClass())

    def test_instance_conforms_to_IForum(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IForum
        verifyObject(IForum, self._makeOne())

class ForumTopicTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.forum import ForumTopic
        return ForumTopic

    def _makeOne(self, title=u'title', text=u'text', creator=u'admin' ):
        return self._getTargetClass()(title, text, creator)

    def test_class_conforms_to_IForumTopic(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import IForumTopic
        verifyClass(IForumTopic, self._getTargetClass())

    def test_instance_conforms_to_IForumTopic(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import IForumTopic
        verifyObject(IForumTopic, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.text, u'text')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        self.failUnless('comments' in instance)

        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ICommentsFolder
        verifyObject(ICommentsFolder, instance['comments'])

    def test_instance_construct_with_none(self):
        instance = self._makeOne(text=None)
        self.assertEqual(instance.text, u'')

class TestForumsToolFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from karl.content.models.forum import forums_tool_factory
        return forums_tool_factory

    def test_it(self):
        from repoze.lemonade.interfaces import IContentFactory
        testing.registerAdapter(lambda *arg, **kw: DummyContent, (None,),
                                IContentFactory)
        context = testing.DummyModel()
        request = testing.DummyRequest
        factory = self._makeOne()
        factory.add(context, request)
        self.failUnless(context['forums'])
        self.failUnless(factory.is_present(context, request))
        factory.remove(context, request)
        self.failIf(factory.is_present(context, request))


class DummyContent:
    pass
