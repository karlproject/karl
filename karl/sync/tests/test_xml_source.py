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

    def test_path(self):
        o = self._make_one()
        self.assertEqual(o.path, 'foo/bar')
