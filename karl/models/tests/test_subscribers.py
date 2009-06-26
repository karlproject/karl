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

class TestPostorder(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, node):
        from karl.models.subscribers import postorder
        return postorder(node)

    def test_None_node(self):
        result = list(self._callFUT(None))
        self.assertEqual(result, [None])
        
    def test_IFolder_node_no_children(self):
        from repoze.folder.interfaces import IFolder
        from zope.interface import directlyProvides
        model = testing.DummyModel()
        directlyProvides(model, IFolder)
        result = list(self._callFUT(model))
        self.assertEqual(result, [model])

    def test_IFolder_node_nonfolder_children(self):
        from repoze.folder.interfaces import IFolder
        from zope.interface import directlyProvides
        model = testing.DummyModel()
        one = testing.DummyModel()
        two = testing.DummyModel()
        model['one'] = one
        model['two'] = two
        directlyProvides(model, IFolder)
        result = list(self._callFUT(model))
        self.assertEqual(result, [two, one, model])

    def test_IFolder_node_folder_children(self):
        from repoze.folder.interfaces import IFolder
        from zope.interface import directlyProvides
        model = testing.DummyModel()
        one = testing.DummyModel()
        two = testing.DummyModel()
        directlyProvides(two, IFolder)
        model['one'] = one
        model['two'] = two
        three = testing.DummyModel()
        four = testing.DummyModel()
        two['three'] = three
        two['four'] = four
        directlyProvides(model, IFolder)
        result = list(self._callFUT(model))
        self.assertEqual(result, [four, three, two, one, model])

class TestIndexContent(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import index_content
        return index_content(object, event)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()
        self._callFUT(model, None) # doesnt blow up

    def test_content_object(self):
        from karl.testing import DummyCatalog
        from zope.interface import directlyProvides
        from repoze.lemonade.interfaces import IContent
        from repoze.bfg.traversal import model_path
        model = testing.DummyModel()
        path = model_path(model)
        directlyProvides(model, IContent)
        catalog = DummyCatalog()
        model.catalog = catalog
        self._callFUT(model, None)
        self.assertEqual(catalog.document_map.added, [(None, path)])
        self.assertEqual(catalog.indexed, [model])
        self.assertEqual(model.docid, 1)

    def test_content_object_w_existing_docid(self):
        from karl.testing import DummyCatalog
        from zope.interface import directlyProvides
        from repoze.lemonade.interfaces import IContent
        from repoze.bfg.traversal import model_path
        model = testing.DummyModel()
        path = model_path(model)
        directlyProvides(model, IContent)
        catalog = DummyCatalog()
        model.catalog = catalog
        model.docid = 123
        self._callFUT(model, None)
        self.assertEqual(catalog.document_map.added, [(123, path)])
        self.assertEqual(catalog.indexed, [model])

    def test_noncontent_object(self):
        from karl.testing import DummyCatalog
        model = testing.DummyModel()
        catalog = DummyCatalog()
        model.catalog = catalog
        self._callFUT(model, None)
        self.assertEqual(catalog.document_map.added, [])
        self.assertEqual(catalog.indexed, [])

class TestUnindexContent(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, docids):
        from karl.models.subscribers import unindex_content
        return unindex_content(object, docids)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()
        self._callFUT(model, None) # doesnt blow up

    def test_content_object(self):
        from karl.testing import DummyCatalog
        model = testing.DummyModel()
        catalog = model.catalog = DummyCatalog()

        self._callFUT(model, [2, 4, 6])

        self.assertEqual(catalog.unindexed, [2, 4, 6])
        self.assertEqual(catalog.document_map.removed, [2, 4, 6])

class TestCleanupContentTags(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, docids):
        from karl.models.subscribers import cleanup_content_tags
        return cleanup_content_tags(object, docids)

    def test_no_tags(self):
        model = testing.DummyModel()

        self._callFUT(model, [1, 3, 5]) # doesnt blow up

    def test_w_tags(self):
        model = testing.DummyModel()
        model.docid = 123
        tags = model.tags = DummyTags()

        self._callFUT(model, [1, 3, 5])

        self.assertEqual(len(tags._delete_called_with), 3)
        self.assertEqual(tags._delete_called_with[0], (1, None, None))
        self.assertEqual(tags._delete_called_with[1], (3, None, None))
        self.assertEqual(tags._delete_called_with[2], (5, None, None))

class TestHandleContentRemoved(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import handle_content_removed
        return handle_content_removed(object, event)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()

        self._callFUT(model, None) # doesnt blow up

    def test_content_object_w_catalog_no_tags(self):
        from repoze.bfg.traversal import model_path
        from karl.testing import DummyCatalog
        model = testing.DummyModel()
        path = model_path(model)
        catalog = model.catalog = DummyCatalog({1: path,
                                                2: '%s/foo' % path,
                                                3: '%s/bar' % path,
                                               })
        self._callFUT(model, None)
        self.assertEqual(catalog.unindexed, [1, 2, 3])
        self.assertEqual(catalog.document_map.removed, [1, 2, 3])

    def test_content_object_w_catalog_w_tags(self):
        from repoze.bfg.traversal import model_path
        from karl.testing import DummyCatalog
        model = testing.DummyModel()
        path = model_path(model)
        tags = model.tags = DummyTags()
        catalog = model.catalog = DummyCatalog({1: path,
                                                2: '%s/foo' % path,
                                                3: '%s/bar' % path,
                                               })
        self._callFUT(model, None)

        self.assertEqual(catalog.unindexed, [1, 2, 3])
        self.assertEqual(catalog.document_map.removed, [1, 2, 3])
        self.assertEqual(len(tags._delete_called_with), 3)
        self.assertEqual(tags._delete_called_with[0], (1, None, None))
        self.assertEqual(tags._delete_called_with[1], (2, None, None))
        self.assertEqual(tags._delete_called_with[2], (3, None, None))

class TestReindexContent(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import reindex_content
        return reindex_content(object, event)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()
        self._callFUT(model, None) # doesnt blow up

    def test_content_object(self):
        from repoze.bfg.traversal import model_path
        from karl.testing import DummyCatalog
        model = testing.DummyModel()
        path = model_path(model)
        catalog = DummyCatalog({1:path})
        model.catalog = catalog
        self._callFUT(model, None)
        self.assertEqual(catalog.reindexed, [model])

class TestSetModified(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import set_modified
        return set_modified(object, event)

    def test_content_object(self):
        model = testing.DummyModel()
        model.modified = 'abc'
        self._callFUT(model, None)
        self.assertNotEqual(model.modified, 'abc')

    def test_with_icommunity(self):
        root = testing.DummyModel()
        root.content_modified = None
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        directlyProvides(root, ICommunity)
        model = testing.DummyModel(__parent__=root)
        self._callFUT(model, None)
        self.assertNotEqual(root.content_modified, None)

class TestSetCreated(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import set_created
        return set_created(object, event)

    def test_noncontent_object(self):
        model = testing.DummyModel()
        self._callFUT(model, None)
        self.failIf(hasattr(model, 'created'))
        self.failIf(hasattr(model, 'modified'))

    def test_content_object_no_attrs(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.interfaces import IContent
        model = testing.DummyModel()
        directlyProvides(model, IContent)
        self._callFUT(model, None)
        self.failUnless(model.created)
        self.failUnless(model.modified)

    def test_content_object_already_attrs(self):
        from zope.interface import directlyProvides
        from repoze.lemonade.interfaces import IContent
        model = testing.DummyModel()
        directlyProvides(model, IContent)
        model.created = 'abc'
        model.modified = 'def'
        self._callFUT(model, None)
        self.assertEqual(model.created, 'abc')
        self.assertEqual(model.modified, 'def')

    def test_ignores_non_community_content_modified(self):
        root = testing.DummyModel()
        model = testing.DummyModel()
        event = testing.DummyModel(name='phred', parent=root, object=model)
        self._callFUT(model, event)
        self.failIf('content_modified' in root.__dict__)

    def test_updates_community_content_modified(self):
        root = testing.DummyModel()
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        directlyProvides(root, ICommunity)
        # bogus:  __parent__ is not yet set on obj in IObjectWillBeAddedEvent
        #model = testing.DummyModel(__parent__=root)
        model = testing.DummyModel()
        event = testing.DummyModel(name='phred', parent=root, object=model)
        self._callFUT(model, event)
        self.failUnless('content_modified' in root.__dict__)

class TestDeleteCommunity(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import delete_community
        return delete_community(object, event)

    def test_it(self):
        community = testing.DummyModel()
        community.members_group_name = '1'
        community.moderators_group_name = '2'
        users = DummyUsers()
        community.users = users
        self._callFUT(community, None)
        self.assertEqual(users.groups_deleted, ['1', '2'])

class DummyUsers:
    def __init__(self):
        self.groups_deleted = []

    def delete_group(self, group_name):
        self.groups_deleted.append(group_name)

class AlphaBase(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _registerAdapter(self):
        from zope.interface import implements
        from karl.models.interfaces import ILetterManager
        class DummyLetterManager:
            implements(ILetterManager)
            delta_called = []
            def __init__(self, context):
                self.context = context
            def delta(self, how_many):
                self.delta_called.append((self.context, how_many))
        testing.registerAdapter(DummyLetterManager, provides=ILetterManager)
        return DummyLetterManager

class AlphaAddedTests(AlphaBase):
    def _callFUT(self, object, event):
        from karl.models.subscribers import alpha_added
        return alpha_added(object, event)

    def test_event(self):
        model = testing.DummyModel()
        lm_klass = self._registerAdapter()
        self._callFUT(model, None)
        self.assertEqual(lm_klass.delta_called, [(model, 1)])

class AlphaRemovedTests(AlphaBase):
    def _callFUT(self, object, event):
        from karl.models.subscribers import alpha_removed
        return alpha_removed(object, event)

    def test_event(self):
        model = testing.DummyModel()
        lm_klass = self._registerAdapter()
        self._callFUT(model, None)
        self.assertEqual(lm_klass.delta_called, [(model, -1)])


class ProfileAddedTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import profile_added
        return profile_added(object, event)

    def test_event_new(self):
        from karl.models.profile import CaseInsensitiveOOBTree
        parent = testing.DummyModel()
        parent.email_to_name = CaseInsensitiveOOBTree()
        model = testing.DummyModel()
        model.__name__ = 'phreddy'
        model.__parent__ = parent
        model.email = 'phreddy@example.com'
        self._callFUT(model, None)
        self.assertEqual(parent.email_to_name['phreddy@example.com'],
                         'phreddy')
        self.assertEqual(parent.email_to_name['Phreddy@Example.com'],
                         'phreddy')

    def test_event_updated(self):
        from karl.models.profile import CaseInsensitiveOOBTree
        parent = testing.DummyModel()
        parent.email_to_name = CaseInsensitiveOOBTree()
        model = testing.DummyModel()
        model.__name__ = 'phreddy'
        model.__parent__ = parent
        model.email = 'phreddy2@example.com'
        parent.email_to_name['phreddy@example.com'] = 'phreddy'
        self._callFUT(model, None)
        self.assertEqual(parent.email_to_name.get('phreddy@example.com'),
                         None)
        self.assertEqual(parent.email_to_name['phreddy2@example.com'],
                         'phreddy')
        self.assertEqual(parent.email_to_name['Phreddy2@Example.com'],
                         'phreddy')
        
class ProfileRemovedTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import profile_removed
        return profile_removed(object, event)

    def test_event(self):
        parent = testing.DummyModel()
        model = testing.DummyModel()
        model.__name__ = 'phreddy'
        model.__parent__ = parent
        model.email = 'phreddy@example.com'
        parent.email_to_name = {'phreddy@example.com': 'phreddy'}
        self._callFUT(model, None)
        self.assertEqual(parent.email_to_name.get('phreddy@example.com'),
                         None)

class TestIndexProfile(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import index_profile
        return index_profile(object, event)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()
        self._callFUT(model, None) # doesnt blow up

    def test_content_object(self):
        from karl.testing import DummyCatalog
        from zope.interface import directlyProvides
        from karl.models.interfaces import IProfile
        from repoze.bfg.traversal import model_path
        model = testing.DummyModel()
        model['people'] = testing.DummyModel()
        path = model_path(model)
        directlyProvides(model, IProfile)
        catalog = DummyCatalog()
        model['people'].catalog = catalog
        self._callFUT(model, None)
        self.assertEqual(catalog.document_map.added, [(None, path)])
        self.assertEqual(catalog.indexed, [model])
        self.assertEqual(model.docid, 1)

    def test_content_object_w_existing_docid(self):
        from karl.testing import DummyCatalog
        from zope.interface import directlyProvides
        from karl.models.interfaces import IProfile
        from repoze.bfg.traversal import model_path
        model = testing.DummyModel()
        model['people'] = testing.DummyModel()
        path = model_path(model)
        directlyProvides(model, IProfile)
        catalog = DummyCatalog()
        model['people'].catalog = catalog
        model.docid = 123
        self._callFUT(model, None)
        self.assertEqual(catalog.document_map.added, [(123, path)])
        self.assertEqual(catalog.indexed, [model])

    def test_noncontent_object(self):
        from karl.testing import DummyCatalog
        model = testing.DummyModel()
        model['people'] = testing.DummyModel()
        catalog = DummyCatalog()
        model['people'].catalog = catalog
        self._callFUT(model, None)
        self.assertEqual(catalog.document_map.added, [])
        self.assertEqual(catalog.indexed, [])

class TestUnindexProfile(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import unindex_profile
        return unindex_profile(object, event)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()
        self._callFUT(model, None) # doesnt blow up

    def test_content_object(self):
        model = testing.DummyModel()
        model['people'] = testing.DummyModel()
        from repoze.bfg.traversal import model_path
        path = model_path(model)
        from karl.testing import DummyCatalog
        catalog = DummyCatalog({1:path})
        model['people'].catalog = catalog
        self._callFUT(model, None)
        # 1 is repeated here because the DummyCatalog returns the map
        # above as the query result and we unindex the results but we
        # also unindex '1' as a result of it being the object passed
        # in to unindex_profile
        self.assertEqual(catalog.unindexed, [1, 1])
        self.assertEqual(catalog.document_map.removed, [1, 1])

class TestReindexProfile(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, object, event):
        from karl.models.subscribers import reindex_profile
        return reindex_profile(object, event)

    def test_content_object_no_catalog(self):
        model = testing.DummyModel()
        self._callFUT(model, None) # doesnt blow up

    def test_content_object(self):
        model = testing.DummyModel()
        model['people'] = testing.DummyModel()
        from repoze.bfg.traversal import model_path
        path = model_path(model)
        from karl.testing import DummyCatalog
        catalog = DummyCatalog({1:path})
        model['people'].catalog = catalog
        self._callFUT(model, None)
        self.assertEqual(catalog.unindexed, [1])
        self.assertEqual(catalog.indexed, [model])


class QueryLoggerTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self):
        from karl.models.subscribers import QueryLogger
        return QueryLogger()

    def test_no_log_dir(self):
        logger = self._makeOne()
        logger.configure(DummySettings(None))
        self.assertEquals(logger._configured, True)
        self.assertEquals(logger.log_dir, None)

    def test_configure_by_utility(self):
        from repoze.bfg.interfaces import ISettings
        testing.registerUtility(DummySettings(None), ISettings)
        logger = self._makeOne()
        self.assertEquals(logger._configured, False)
        logger(DummyQueryEvent())
        self.assertEquals(logger._configured, True)
        self.assertEquals(logger.log_dir, None)

    def test_log_without_settings(self):
        logger = self._makeOne()
        logger(DummyQueryEvent())
        self.assertEquals(logger._configured, False)
        self.assertEquals(logger.log_dir, None)

    def test_log(self):
        import os
        import shutil
        import tempfile
        d = tempfile.mkdtemp()
        try:
            logger = self._makeOne()
            logger.configure(DummySettings(d))
            self.assertEquals(logger._configured, True)
            self.assertEquals(logger.log_dir, d)
            logger(DummyQueryEvent())
            names = os.listdir(d)
            self.assertEquals(names, ['0000500.log'])
            path = os.path.join(d, names[0])
            self.assert_(os.path.getsize(path) > 0)
        finally:
            shutil.rmtree(d)

    def test_log_shorter_than_minimum(self):
        import os
        import shutil
        import tempfile
        d = tempfile.mkdtemp()
        try:
            logger = self._makeOne()
            # don't log queries that take less than 1 sec
            logger.configure(DummySettings(d, '1'))
            self.assertEquals(logger._configured, True)
            self.assertEquals(logger.log_dir, d)
            logger(DummyQueryEvent())
            names = os.listdir(d)
            self.assertEquals(names, [])
        finally:
            shutil.rmtree(d)

class DummyTags:
    _delete_called_with = None

    def delete(self, item=None, user=None, tag=None):
        if self._delete_called_with is None:
            self._delete_called_with = []
        self._delete_called_with.append((item, user, tag))

class DummyQueryEvent:
    catalog = None
    query = {'creator': 'me'}
    duration = 0.4
    result = (1, [99])

class DummySettings:
    def __init__(self, log_dir, min_duration=0):
        self.query_log_dir = log_dir
        self.query_log_min_duration = min_duration
