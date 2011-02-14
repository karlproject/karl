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

class FlexibleTextIndexDataTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.content.models.adapters import FlexibleTextIndexData
        return FlexibleTextIndexData

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_class_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ITextIndexData
        verifyClass(ITextIndexData, self._getTargetClass())

    def test_instance_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ITextIndexData
        context = testing.DummyModel()
        verifyObject(ITextIndexData, self._makeOne(context))

    def test___call___defaults_no_matching_attrs(self):
        context = testing.DummyModel()
        adapter = self._makeOne(context)
        self.assertEqual(adapter(), ())

    def test___call___defaults_skips_empty_attrs(self):
        context = testing.DummyModel(title = '',
                                     text = 'b',
                                    )
        adapter = self._makeOne(context)
        self.assertEqual(adapter(), ('b',))

    def test___call___defaults_some_matching_attrs(self):
        context = testing.DummyModel(title = 'a',
                                     text = 'b',
                                    )
        adapter = self._makeOne(context)
        self.assertEqual(adapter(), ('a','b'))

    def test___call___defaults_all_matching_attrs(self):
        context = testing.DummyModel(title = 'a',
                                     description = 'b',
                                     text = 'c',
                                    )
        adapter = self._makeOne(context)
        self.assertEqual(adapter(), ('a', 'b',  'c'))

    def test___call___derived(self):
        context = testing.DummyModel(title = 'a',
                                     description = 'b',
                                     text = 'c',
                                    )
        class Derived(self._getTargetClass()):
            weighted_attrs_cleaners = [('description', None)]
        context = testing.DummyModel(description='b')
        adapter = Derived(context)
        self.assertEqual(adapter(), ('b',))

    def test___call___derived_w_extractor(self):
        context = testing.DummyModel(title = 'a',
                                     description = 'b',
                                     text = 'c',
                                    )
        class Derived(self._getTargetClass()):
            weighted_attrs_cleaners = [(lambda x: 'z', None),
                                       ('description', None),
                                       ]
        context = testing.DummyModel(description='b')
        adapter = Derived(context)
        self.assertEqual(adapter(), ('z', 'b'))

    def test___call___derived_w_cleaner(self):
        context = testing.DummyModel(title = 'a',
                                     description = 'b',
                                     text = 'c',
                                    )
        class Derived(self._getTargetClass()):
            weighted_attrs_cleaners = [('title', lambda x: 'y'),]
        context = testing.DummyModel(title='a')
        adapter = Derived(context)
        self.assertEqual(adapter(), ('y',))

class Test_makeFlexibleTextIndexData(unittest.TestCase):

    def _callFUT(self, attr_weights):
        from karl.content.models.adapters import makeFlexibleTextIndexData
        return makeFlexibleTextIndexData(attr_weights)

    def test_w_attr_weights(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ITextIndexData
        def cleaner(s):
            return s.replace('x', 'y')
        factory = self._callFUT([('title', None),
                                 ('description', cleaner),
                                ])
        context = testing.DummyModel()
        adapter = factory(context)
        verifyObject(ITextIndexData, adapter)
        self.assertEqual(adapter(), ())
        context.title = 'a'
        self.assertEqual(adapter(), ('a',))
        context.description = 'x y z'
        self.assertEqual(adapter(), ('a', 'y y z'))

class TestTitleAndDescriptionIndexData(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.content.models.adapters import TitleAndDescriptionIndexData
        return TitleAndDescriptionIndexData

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_class_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ITextIndexData
        verifyClass(ITextIndexData, self._getTargetClass())

    def test_instance_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ITextIndexData
        context = testing.DummyModel()
        verifyObject(ITextIndexData, self._makeOne(context))

    def test_no_description(self):
        context = testing.DummyModel()
        context.title = 'thetitle'
        context.description = ''
        adapter = self._makeOne(context)
        data = adapter()
        self.assertEqual(data, ('thetitle', ''))

    def test_w_description(self):
        context = testing.DummyModel()
        context.title = 'thetitle'
        context.description = 'Hi!'
        adapter = self._makeOne(context)
        data = adapter()
        self.assertEqual(data, ('thetitle', 'Hi!'))

class TestTitleAndTextIndexData(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.content.models.adapters import TitleAndTextIndexData
        return TitleAndTextIndexData

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_class_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ITextIndexData
        verifyClass(ITextIndexData, self._getTargetClass())

    def test_instance_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ITextIndexData
        context = testing.DummyModel()
        verifyObject(ITextIndexData, self._makeOne(context))

    def test_no_text(self):
        context = testing.DummyModel(title = 'thetitle',
                                     text = '',
                                    )
        adapter = self._makeOne(context)
        data = adapter()
        self.assertEqual(data, ('thetitle', ''))

    def test_w_text(self):
        context = testing.DummyModel(title = 'thetitle',
                                     text = '<html><body>Hi!</body></html>',
                                    )
        adapter = self._makeOne(context)
        data = adapter()
        self.assertEqual(data, ('thetitle', '\n\nHi!\n\n'))

class TestFileTextIndexData(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.content.models.adapters import FileTextIndexData
        return FileTextIndexData

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_class_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ITextIndexData
        verifyClass(ITextIndexData, self._getTargetClass())

    def test_instance_conforms_to_ITextIndexData(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ITextIndexData
        context = testing.DummyModel()
        verifyObject(ITextIndexData, self._makeOne(context))

    def test_no_converter(self):
        context = testing.DummyModel()
        context.title = 'Some Title'
        context.mimetype = 'nonexistent'
        adapter = self._makeOne(context)
        self.assertEqual(adapter(), ('Some Title', ''))

    def test_with_converter(self):
        from karl.utilities.converters.interfaces import IConverter
        converter = DummyConverter('stuff')
        testing.registerUtility(converter, IConverter, 'mimetype')
        context = testing.DummyModel()
        context.title = 'Some Title'
        context.mimetype = 'mimetype'
        context.blobfile = DummyBlobFile()
        adapter = self._makeOne(context)
        self.assertEqual(adapter(), ('Some Title', 'stuff'))

    def test_cache_with_converter(self):
        from karl.utilities.converters.interfaces import IConverter
        converter = DummyConverter('stuff')
        testing.registerUtility(converter, IConverter, 'mimetype')
        context = testing.DummyModel()
        context.title = 'Some Title'
        context.mimetype = 'mimetype'
        context.blobfile = DummyBlobFile()
        adapter = self._makeOne(context)
        self.assertEqual(converter.called, 0)
        self.assertEqual(adapter(), ('Some Title', 'stuff'))
        self.assertEqual(converter.called, 1)
        self.assertEqual(adapter(), ('Some Title', 'stuff'))
        self.assertEqual(converter.called, 1) # Didn't call converter again

class TestCalendarEventCategoryData(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.content.models.adapters import CalendarEventCategoryData
        return CalendarEventCategoryData

    def _makeOne(self, context):
        return self._getTargetClass()(context)

    def test_it(self):
        from zope.interface import directlyProvides
        from karl.content.interfaces import ICalendar
        community = testing.DummyModel()
        directlyProvides(community, ICalendar)
        context = testing.DummyModel()
        context.calendar_category = 'virt'
        community['context'] = context
        adapter = self._makeOne(context)
        result = adapter()
        self.assertEqual(result, 'virt')


class DummyConverter:
    def __init__(self, data):
        self.data = data
        self.called = 0

    def convert(self, filename, encoding=None, mimetype=None):
        self.called += 1
        import StringIO
        return StringIO.StringIO(self.data), 'ascii'

class DummyBlobFile:
    def _current_filename(self):
        return None


