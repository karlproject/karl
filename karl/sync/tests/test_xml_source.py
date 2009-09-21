import unittest

class XMLContentSourceTests(unittest.TestCase):
    def _target_class(self):
        from karl.sync.xml_source import XMLContentSource
        return XMLContentSource

    def _make_one(self, test_file='test_xml_source_1.xml'):
        import pkg_resources
        stream = pkg_resources.resource_stream(__name__, test_file)
        assert stream is not None
        return self._target_class()(stream)

    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.sync.interfaces import IContentSource
        verifyClass(IContentSource, self._target_class())

    def test_instance_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.sync.interfaces import IContentSource
        verifyObject(IContentSource, self._make_one())

    def test_import(self):
        from karl.sync.xml_source import XMLContentSource

    def test_location(self):
        o = self._make_one()
        self.assertEqual(o.location, 'http://foo.com/bar')

    def test_incremental(self):
        o = self._make_one()
        self.assertTrue(o.incremental)

    def test_id(self):
        o = self._make_one()
        self.assertEqual(o.id, 'abcdef')

    def test_modified(self):
        import datetime
        import pytz
        o = self._make_one()
        expected = datetime.datetime(
            2009, 9, 10, 18, 28, 3, tzinfo=pytz.FixedOffset(-300)
        )
        self.assertEqual(o.modified, expected)

    def test_items(self):
        o = self._make_one()
        self.assertEqual(2, len(list(o.items)))

    def test_deleted_items(self):
        o = self._make_one()
        self.assertEqual(o.deleted_items,
                         ['64071160-f25e-4221-a2d7-cd85b76395fb',
                          'a66af600-718c-4f60-ad78-63dc7018de78'])

    def test_relaxng_validates(self):
        import lxml.etree
        import pkg_resources

        schema = lxml.etree.RelaxNG(lxml.etree.parse(
            pkg_resources.resource_stream(__name__, 'karl_export.rng')
            ))

        doc = lxml.etree.parse(
            pkg_resources.resource_stream(__name__, 'test_xml_source_1.xml')
            )

        self.failUnless(schema.validate(doc))

class XMLContentItemTests(unittest.TestCase):
    def _make_some(self, test_file='test_xml_source_1.xml'):
        import pkg_resources
        stream = pkg_resources.resource_stream(__name__, test_file)
        assert stream is not None

        from karl.sync.xml_source import XMLContentSource
        return XMLContentSource(stream).items


    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.sync.interfaces import IContentItem
        from karl.sync.xml_source import XMLContentItem
        verifyClass(IContentItem, XMLContentItem)

    def test_instance_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.sync.interfaces import IContentItem
        verifyObject(IContentItem, self._make_some().next())

    def test_id(self):
        o = self._make_some().next()
        self.assertEqual(o.id, '765b078b-ccd7-4bb0-a197-ec23d03be430')

    def test_name(self):
        o = self._make_some().next()
        self.assertEqual(o.name, 'why-radio-is-awesome')

    def test_type(self):
        o = self._make_some().next()
        from karl.models.interfaces import IProfile
        self.assertEqual(o.type, IProfile)

    def test_type_no_sys_modules(self):
        from karl.models.interfaces import IProfile
        o = self._make_some().next()

        import sys
        save_modules = sys.modules
        sys.modules = {}
        try:
            self.assertEqual(o.type, IProfile)
        finally:
            sys.modules = save_modules

    def test_workflow_state(self):
        o = self._make_some().next()
        self.assertEqual(o.workflow_state, 'inherit')

    def test_created(self):
        import datetime
        import pytz
        o = self._make_some().next()
        expected = datetime.datetime(2009, 9, 9, 18, 28, 3,
                                     tzinfo=pytz.FixedOffset(-300))
        self.assertEqual(o.created, expected)

    def test_created_by(self):
        o = self._make_some().next()
        self.assertEqual(o.created_by, 'crossi')

    def test_modified(self):
        import datetime
        import pytz
        o = self._make_some().next()
        expected = datetime.datetime(2009, 9, 9, 18, 28, 3,
                                     tzinfo=pytz.FixedOffset(-300))
        self.assertEqual(o.modified, expected)

    def test_modified_by(self):
        o = self._make_some().next()
        self.assertEqual(o.modified_by, 'crossi')

    def test_attributes(self):
        o = self._make_some().next()
        attrs = o.attributes
        for v in attrs.values():
            self.failUnless(isinstance(v, unicode) or v is None)
        self.assertEqual(attrs['title'], u'Why Radio is Awesome')
        self.assertEqual(attrs['text'],
                         u'La radio \xe8 straordinaria perch\xe9 ...')
        self.assertEqual(attrs['description'], None)

    def test_children(self):
        o = list(self._make_some())[1]
        children = list(o.children)
        self.assertEqual(len(children), 1)
        child = children[0]
        self.assertEqual(child.id, '234jjlkj3423')
        self.assertEqual(child.name, 'some-doc-in-folder')

    def test_deleted_children(self):
        o = list(self._make_some())[1]
        self.assertEqual(o.deleted_children, ['abc123'])

class AttributeConversionTests(unittest.TestCase):
    def _get_converter(self, name):
        from karl.sync.xml_source import _attr_converters
        return _attr_converters[name]

    def test_int(self):
        converter = self._get_converter('int')
        self.assertEqual(converter('1'), 1)
        self.assertEqual(converter('-5'), -5)
        self.assertEqual(converter('00'), 0)
        self.assertRaises(ValueError, converter, '')
        self.assertRaises(ValueError, converter, '1.1')
        self.assertRaises(ValueError, converter, 'foo')

    def test_float(self):
        converter = self._get_converter('float')
        self.assertEqual(converter('1'), 1.0)
        self.assertEqual(converter('1.1'), 1.1)
        self.assertEqual(converter('-106.66'), -106.66)
        self.assertEqual(converter('0'), 0.0)
        self.assertRaises(ValueError, converter, '')
        self.assertRaises(ValueError, converter, '1 / 2')
        self.assertRaises(ValueError, converter, 'foo')

    def test_bool(self):
        converter = self._get_converter('bool')
        self.assertEqual(converter('True'), True)
        self.assertEqual(converter('true'), True)
        self.assertEqual(converter('t'), True)
        self.assertEqual(converter('T'), True)
        self.assertEqual(converter('Yes'), True)
        self.assertEqual(converter('yes'), True)
        self.assertEqual(converter('YES'), True)
        self.assertEqual(converter('y'), True)
        self.assertEqual(converter('1'), True)

        self.assertEqual(converter('False'), False)
        self.assertEqual(converter('false'), False)
        self.assertEqual(converter('f'), False)
        self.assertEqual(converter('F'), False)
        self.assertEqual(converter('No'), False)
        self.assertEqual(converter('NO'), False)
        self.assertEqual(converter('no'), False)
        self.assertEqual(converter('n'), False)
        self.assertEqual(converter('0'), False)

        self.assertRaises(ValueError, converter, 'Hell yeah')
        self.assertRaises(ValueError, converter, 'No way, man')

    def test_bytes(self):
        from base64 import b64encode as encode
        converter = self._get_converter('bytes')
        s = 'My name is Chris'
        self.assertEqual(converter(encode(s)), s)
        self.failUnless(isinstance(converter(encode(s)), str))
        s = '\0\x02\x03\x45'
        self.assertEqual(converter(encode(s)), s)

        self.assertRaises(TypeError, converter, s)

    def test_text(self):
        converter = self._get_converter('text')
        self.failUnless(isinstance(converter('Chris'), unicode))
        self.assertEqual(converter('Chris'), u'Chris')
        self.assertEqual(converter(u'Dub revolution'), u'Dub revolution')

class MemoizeTests(unittest.TestCase):
    def test_it(self):
        from karl.sync.xml_source import memoize

        class Foo(object):
            count = 0

            @property
            @memoize
            def f(self):
                self.count += 1
                return self.count

        foo = Foo()
        self.failIf(hasattr(foo, '_memoize_f'))
        self.assertEqual(foo.f, 1)
        self.assertEqual(foo.f, 1) # doesn't increment
        self.assertEqual(foo._memoize_f, 1)
