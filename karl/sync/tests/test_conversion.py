import unittest

class ConversionTests(unittest.TestCase):
    def _get_converter(self, type):
        from karl.sync.conversion import convert
        def converter(raw):
            return convert(raw, type)
        return converter

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

    def test_timestamp(self):
        import datetime
        from pytz import FixedOffset
        converter = self._get_converter('timestamp')
        self.assertEqual(converter('2009-09-09T18:28:03-05:00'),
                         datetime.datetime(2009, 9, 9, 18, 28, 03,
                                           tzinfo=FixedOffset(-300)))
        self.assertRaises(ValueError, converter, '200909091828030500')

    def test_blob(self):
        import os
        import sys
        here = os.path.dirname(sys.modules[__name__].__file__)
        here = os.path.abspath(here)
        url = 'file://%s/test_data.dat' % here
        converter = self._get_converter('blob')
        blob = converter(url)
        self.assertEqual(blob.open().read(),
            "Cos\xc3\xac fin\xc3\xac l'amuri di du' pisci sfortunati.")
        self.failUnless(isinstance(blob.open().read(), str))
        self.assertRaises(ValueError, converter('no where in particular').open )

    def test_clob(self):
        import os
        import sys
        here = os.path.dirname(sys.modules[__name__].__file__)
        here = os.path.abspath(here)
        url = 'file://%s/test_data.dat' % here
        converter = self._get_converter('clob')
        blob = converter(url)
        self.assertEqual(blob.open().read(),
            u"Cos\xec fin\xec l'amuri di du' pisci sfortunati.")
        self.failUnless(isinstance(blob.open().read(), unicode))
        self.assertRaises(ValueError, converter('no where in particular').open )