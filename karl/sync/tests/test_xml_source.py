import unittest

class XMLContentSourceTests(unittest.TestCase):
    def _make_one(self, test_file='test_xml_source_1.xml'):
        import pkg_resources
        stream = pkg_resources.resource_stream(__name__, test_file)
        assert stream is not None

        from karl.sync.xml_source import XMLContentSource
        return XMLContentSource(stream)

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

        #<attributes>
            #<attribute name="title" type="text"> Why Radio is Awesome </attribute>
            #<attribute name="text" type="text"> Radio is awesome because ... </attribute>
            #<attribute name="description" type="text" none="True"/>
        #</attributes>

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
