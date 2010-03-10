import unittest

class TestMessage(unittest.TestCase):
    def _target_class(self):
        from karl.mail import Message as target
        return target

    def _make_one(self):
        return self._target_class()()

    def test_unicode_headers_roundtrip(self):
        m1 = self._make_one()
        m1['To'] = u'Ren\xe8 <test@example.com>'

        from email.parser import Parser
        parse = Parser(self._target_class()).parsestr
        m2 = parse(m1.as_string())
        self.assertEqual(m1['To'], m2['To'])

    def test_dont_encode_address(self):
        m1 = self._make_one()
        m1['To'] = u'Ren\xe8 <test@example.com>'
        msg = m1.as_string()
        to_header = [l for l in msg.split('\n') if l.startswith('To:')][0]
        self.assertEqual(to_header[-18:], '<test@example.com>')

    def test_hide_encoded_headers_beneath_api(self):
        addr = u'Ren\xe8 <test@example.com>, Chr\xecs <chris@example.com>'
        m1 = self._make_one()
        m1['To'] = addr

        from email.parser import Parser
        parse = Parser(self._target_class()).parsestr
        m2 = parse(m1.as_string())
        self.assertEqual(m1['To'], m2['To'])
        self.assertEqual(m1['To'], addr)
        self.assertEqual(m2['To'], addr)

    def test_header_not_set(self):
        m1 = self._make_one()
        self.assertEqual(m1['Date'], None)

    def test_set_header_to_none(self):
        # Merely confirms that stdlib's oddball behavior of ignoring the fact
        # that you set a header to None still works.  Bizarre, useless edge
        # case.
        addr = u'Ren\xe8 <test@example.com>'
        m1 = self._make_one()
        m1['To'] = addr
        self.assertEqual(m1['To'], addr)
        m1['To'] = None
        self.assertEqual(m1['To'], addr)

    def test_non_address_header(self):
        proverb = u"Non c'\xe9 realt\xe0, c'\xe8 solo superpollo!"
        m1 = self._make_one()
        m1['Subject'] = proverb

        from email.parser import Parser
        parse = Parser(self._target_class()).parsestr
        m2 = parse(m1.as_string())
        self.assertEqual(m1['Subject'], m2['Subject'])
        self.assertEqual(m2['Subject'], proverb)

class TestMIMEMultipPart(TestMessage):
    def _target_class(self):
        from karl.mail import MIMEMultipart as target
        return target

