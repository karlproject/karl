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
class NewsItemTests(unittest.TestCase):
    def _getTargetClass(self):
        from karl.content.models.news import NewsItem
        return NewsItem

    def _makeOne(self, title=u'title', text=u'text', creator=u'admin',
                 publication_date=None, caption=u"caption"):
        if publication_date is None:
            import datetime
            publication_date = datetime.datetime.now()
        return self._getTargetClass()(title, text, creator, publication_date,
                                      caption)

    def test_class_conforms_to_IBlogEntry(self):
        from zope.interface.verify import verifyClass
        from karl.content.interfaces import INewsItem
        verifyClass(INewsItem, self._getTargetClass())

    def test_instance_conforms_to_IBlogEntry(self):
        from zope.interface.verify import verifyObject
        from karl.content.interfaces import INewsItem
        verifyObject(INewsItem, self._makeOne())

    def test_instance_has_valid_construction(self):
        instance = self._makeOne()
        self.assertEqual(instance.title, u'title')
        self.assertEqual(instance.text, u'text')
        self.assertEqual(instance.creator, u'admin')
        self.assertEqual(instance.modified_by, u'admin')
        self.assertEqual(instance.caption, u'caption')
        self.failUnless('attachments' in instance)
        
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IAttachmentsFolder
        verifyObject(IAttachmentsFolder, instance['attachments'])
        