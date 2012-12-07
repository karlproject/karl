import unittest

class LogParserTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.scripts.analyze_queries import LogParser
        return LogParser

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        parser = self._makeOne()
        self.assertEqual(len(parser), 0)

    def test_empty_stream(self):
        from StringIO import StringIO
        input = StringIO()
        parser = self._makeOne()
        count, errors = parser.parse(input)
        self.assertEqual(count, 0)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(parser), 0)

    def test_invalid_summary_line(self):
        from StringIO import StringIO
        input = StringIO('XXXX')
        parser = self._makeOne()
        count, errors = parser.parse(input)
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.failUnless(errors[0].startswith('Invalid summary line:'))
        self.assertEqual(len(parser), 0)

    def test_valid_summary_line_empty_query_dict(self):
        from StringIO import StringIO
        input = StringIO('2010-09-13T16:54:43.811343    0.001      1\n')
        parser = self._makeOne()
        count, errors = parser.parse(input)
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.failUnless(errors[0].startswith('Empty query params dict'))
        self.assertEqual(len(parser), 0)

    def test_valid_summary_line_bogus_query_dict(self):
        from StringIO import StringIO
        input = StringIO('2010-09-13T16:54:43.811343    0.001      1\n XXX')
        parser = self._makeOne()
        count, errors = parser.parse(input)
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 1)
        self.failUnless(errors[0].startswith('Invalid query params dict:'))
        self.assertEqual(len(parser), 0)

    def test_valid_summary_line_non_empty_query_dict(self):
        from datetime import datetime
        from pprint import pformat
        QUERY = {'foo': 'bar'}
        QTEXT = pformat(QUERY, indent=1)
        from StringIO import StringIO
        input = StringIO('2010-09-13T16:54:43.811343    0.001      1\n %s'
                            % QTEXT)
        parser = self._makeOne()
        count, errors = parser.parse(input)
        self.assertEqual(count, 1)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(parser), 1)
        query = parser[0]
        self.assertEqual(query.timestamp,
                         datetime(2010, 9, 13, 16, 54, 43, 811343))
        self.assertEqual(query.duration_ms, 1)
        self.assertEqual(query.params, QUERY)
