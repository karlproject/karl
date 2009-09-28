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

class KARLUsersTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.models.site import KARLUsers
        return KARLUsers

    def _makeOne(self, site):
        return self._getTargetClass()(site)

    def test_add_fires_IUserAdded(self):
        from karl.models.interfaces import IUserAdded
        events = testing.registerEventListener(IUserAdded)
        ku = self._makeOne(self)
        ku.add('userid', 'login_name', 'password', ('group_1',))
        self.assertEqual(len(events), 1)
        self.failUnless(events[0].site is self)
        self.assertEqual(events[0].id, 'userid')
        self.assertEqual(events[0].login, 'login_name')
        self.assertEqual(len(events[0].groups), 1)
        self.failUnless('group_1' in events[0].groups)

    def test_remove_fires_IUserRemoved(self):
        from karl.models.interfaces import IUserRemoved
        events = testing.registerEventListener(IUserRemoved)
        ku = self._makeOne(self)
        ku.add('userid', 'login_name', 'password', ('group_1',))
        ku.remove('userid')
        self.assertEqual(len(events), 1)
        self.failUnless(events[0].site is self)
        self.assertEqual(events[0].id, 'userid')
        self.assertEqual(events[0].login, 'login_name')
        groups = list(events[0].groups)
        self.assertEqual(len(groups), 1)
        self.failUnless('group_1' in events[0].groups)

    def test_add_group_fires_IUserAddedGroup(self):
        from karl.models.interfaces import IUserAddedGroup
        events = testing.registerEventListener(IUserAddedGroup)
        ku = self._makeOne(self)
        ku.add('userid', 'login_name', 'password', ('group_1',))
        ku.add_group('userid', 'group_2')
        self.assertEqual(len(events), 1)
        self.failUnless(events[0].site is self)
        self.assertEqual(events[0].id, 'userid')
        self.assertEqual(events[0].login, 'login_name')
        groups = events[0].groups
        self.assertEqual(len(groups), 2)
        self.failUnless('group_1' in groups)
        self.failUnless('group_2' in groups)
        old_groups = list(events[0].old_groups)
        self.assertEqual(len(old_groups), 1)
        self.assertEqual(old_groups[0], 'group_1')

    def test_add_group_unchanged_does_not_fire_IUserAddedGroup(self):
        from karl.models.interfaces import IUserAddedGroup
        events = testing.registerEventListener(IUserAddedGroup)
        ku = self._makeOne(self)
        ku.add('userid', 'login_name', 'password', ('group_1',))
        ku.add_group('userid', 'group_1')
        self.assertEqual(len(events), 0)

    def test_remove_group_fires_IUserRemovedGroup(self):
        from karl.models.interfaces import IUserRemovedGroup
        events = testing.registerEventListener(IUserRemovedGroup)
        ku = self._makeOne(self)
        ku.add('userid', 'login_name', 'password', ('group_1', 'group_2'))
        ku.remove_group('userid', 'group_2')
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, 'userid')
        self.assertEqual(events[0].login, 'login_name')
        groups = events[0].groups
        self.assertEqual(len(groups), 1)
        self.failUnless(events[0].site is self)
        self.failUnless('group_1' in groups)
        old_groups = events[0].old_groups
        self.assertEqual(len(old_groups), 2)
        self.failUnless('group_1' in old_groups)
        self.failUnless('group_2' in old_groups)

    def test_remove_group_unchanged_does_not_fire_IUserRemovedGroup(self):
        from karl.models.interfaces import IUserRemovedGroup
        events = testing.registerEventListener(IUserRemovedGroup)
        ku = self._makeOne(self)
        ku.add('userid', 'login_name', 'password', ('group_1', 'group_2'))
        ku.remove_group('userid', 'nonesuch')
        self.assertEqual(len(events), 0)

class SiteTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.models.site import Site
        return Site

    def _registerUtilities(self):
        from karl.models.interfaces import ICatalogSearchCache
        cache = DummyCache()
        testing.registerUtility(cache, ICatalogSearchCache)
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import ICommunities
        from karl.models.interfaces import IProfiles
        from karl.models.interfaces import IPeopleDirectory
        registerContentFactory(lambda *x: testing.DummyModel(), ICommunities)
        registerContentFactory(lambda *x: testing.DummyModel(), IProfiles)
        registerContentFactory(lambda *x: testing.DummyModel(),
            IPeopleDirectory)

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_ISite(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ISite
        verifyClass(ISite, self._getTargetClass())

    def test_instance_conforms_to_ISite(self):
        self._registerUtilities()
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ISite
        verifyObject(ISite, self._makeOne())

    def test_catalog_indexes(self):
        self._registerUtilities()
        site = self._makeOne()
        for index_name, type_name in (('name', 'CatalogFieldIndex'),
                                      ('title', 'CatalogFieldIndex'),
                                      ('titlestartswith', 'CatalogFieldIndex'),
                                      ('interfaces', 'CatalogKeywordIndex'),
                                      ('texts', 'CatalogTextIndex'),
                                      ('path', 'CatalogPathIndex2'),
                                      ('creation_date', 'CatalogFieldIndex'),
                                      ('modified_date', 'CatalogFieldIndex'),
                                      ('publication_date', 'CatalogFieldIndex'),
                                      ('start_date', 'CatalogFieldIndex'),
                                      ('end_date', 'CatalogFieldIndex'),
                                      ('mimetype', 'CatalogFieldIndex'),
                                      ('email', 'CatalogFieldIndex'),
                                     ):
            index = site.catalog[index_name]
            self.assertEqual(index.__class__.__name__, type_name)

    def test_verify_constructor(self):
        self._registerUtilities()
        site = self._makeOne()
        self.failUnless('communities' in site)
        self.failUnless('profiles' in site)
        self.failUnless(hasattr(site, 'catalog'))
        self.failUnless('people' in site)

class TestGetTextRepr(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, object, default):
        from karl.models.site import get_textrepr
        return get_textrepr(object, default)

    def test_no_adapter(self):
        context = testing.DummyModel()
        context.title = 'title'
        context.description = 'description'
        textrepr = self._callFUT(context, None)
        self.assertEqual(textrepr, 'title description')
    
    def test_with_adapter(self):
        context = testing.DummyModel()
        from karl.models.interfaces import ITextIndexData
        class DummyAdapter:
            def __init__(self, context):
                self.context = context
            def __call__(self):
                return 'stuff'
        testing.registerAdapter(DummyAdapter, (None,), ITextIndexData)
        textrepr = self._callFUT(context, None)
        self.assertEqual(textrepr, 'stuff')

class _TestGetDate(object):

    def test_not_set(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, None)

    def test_w_datetime(self):
        import datetime
        from karl.utils import coarse_datetime_repr
        context = testing.DummyModel()
        now = datetime.datetime.now()
        self._decorate(context, now)
        result = self._callFUT(context, None)
        self.assertEqual(result, coarse_datetime_repr(now))

    def test_w_date(self):
        import datetime
        from karl.utils import coarse_datetime_repr
        context = testing.DummyModel()
        today = datetime.date.today()
        self._decorate(context, today)
        result = self._callFUT(context, None)
        self.assertEqual(result, coarse_datetime_repr(today))

    def test_w_invalid_value(self):
        context = testing.DummyModel()
        self._decorate(context, 'notadatetime')
        result = self._callFUT(context, None)
        self.assertEqual(result, None)

class TestGetCreationDate(unittest.TestCase, _TestGetDate):
    def _callFUT(self, object, default):
        from karl.models.site import get_creation_date
        return get_creation_date(object, default)

    def _decorate(self, context, val):
        context.created = val
        
class TestGetModifiedDate(unittest.TestCase, _TestGetDate):
    def _callFUT(self, object, default):
        from karl.models.site import get_modified_date
        return get_modified_date(object, default)

    def _decorate(self, context, val):
        context.modified = val
        
class TestGetStartDate(unittest.TestCase, _TestGetDate):
    def _callFUT(self, object, default):
        from karl.models.site import get_start_date
        return get_start_date(object, default)

    def _decorate(self, context, val):
        context.startDate = val

class TestGetEndDate(unittest.TestCase, _TestGetDate):
    def _callFUT(self, object, default):
        from karl.models.site import get_end_date
        return get_end_date(object, default)

    def _decorate(self, context, val):
        context.endDate = val

class TestGetPublicationDate(unittest.TestCase, _TestGetDate):
    def _callFUT(self, object, default):
        from karl.models.site import get_publication_date
        return get_publication_date(object, default)

    def _decorate(self, context, val):
        context.publication_date = val

class TestGetPath(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_path
        return get_path(object, default)

    def test_it(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, '/')
    
class TestGetInterfaces(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_interfaces
        return get_interfaces(object, default)

    def test_it(self):
        from zope.interface import Interface
        from zope.interface import alsoProvides
        context = testing.DummyModel()
        class Dummy1(Interface):
            pass
        class Dummy2(Interface):
            pass
        alsoProvides(context, Dummy1)
        alsoProvides(context, Dummy2)
        result = self._callFUT(context, None)
        self.assertEqual(sorted(result), [Dummy1, Dummy2, Interface])
    
class TestGetTitleFirstletter(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_title_firstletter
        return get_title_firstletter(object, default)

    def test_withtitle(self):
        context = testing.DummyModel()
        context.title = 'AB'
        result = self._callFUT(context, None)
        self.assertEqual(result, 'A')
    
    def test_notitle(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, None)

    def test_list_title(self):
        context = testing.DummyModel()
        context.title = [None]
        result = self._callFUT(context, None)
        self.assertEqual(result, None)

    def test_int_title(self):
        context = testing.DummyModel()
        context.title = 1
        result = self._callFUT(context, None)
        self.assertEqual(result, None)

class TestGetName(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_name
        return get_name(object, default)

    def test_it(self):
        class Dummy:
            pass
        context = Dummy()
        result = self._callFUT(context, None)
        self.assertEqual(result, None)
        context.__name__= 'bar'
        result = self._callFUT(context, None)
        self.assertEqual(result, 'bar')
        

class TestGetTitle(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_title
        return get_title(object, default)

    def test_it(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, '')
        context.title = 'foo'
        result = self._callFUT(context, None)
        self.assertEqual(result, 'foo')

    def test_lowercase(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, '')
        context.title = 'FoobaR'
        result = self._callFUT(context, None)
        self.assertEqual(result, 'foobar')

class TestGetACL(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_acl
        return get_acl(object, default)

    def test_it(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, None)
        context.__acl__ = 'foo'
        result = self._callFUT(context, None)
        self.assertEqual(result, 'foo')

class TestGetAllowedToView(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_allowed_to_view
        return get_allowed_to_view(object, default)

    def test_it(self):
        context = testing.DummyModel()
        result = self._callFUT(context, None)
        self.assertEqual(result, ['system.Everyone'])

class TestGetVirtual(unittest.TestCase):
    def _callFUT(self, object, default):
        from karl.models.site import get_virtual
        return get_virtual(object, default)

    def test_no_adapter(self):
        context = testing.DummyModel()
        data = self._callFUT(context, None)
        self.assertEqual(data, None)
    
    def test_with_adapter(self):
        context = testing.DummyModel()
        from karl.models.interfaces import IVirtualData
        class DummyAdapter:
            def __init__(self, context):
                self.context = context
            def __call__(self):
                return 'stuff'
        testing.registerAdapter(DummyAdapter, (None,), IVirtualData)
        data = self._callFUT(context, None)
        self.assertEqual(data, 'stuff')

class DummyCache(dict):
    generation = None
    
