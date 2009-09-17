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


