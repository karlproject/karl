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
    def _make_one(self, test_file='test_xml_source_1.xml'):
        import pkg_resources
        stream = pkg_resources.resource_stream(__name__, test_file)
        assert stream is not None

        from karl.sync.xml_source import XMLContentSource
        return XMLContentSource(stream).items[0]

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
