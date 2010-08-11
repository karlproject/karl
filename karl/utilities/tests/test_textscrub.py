import unittest

from zope.testing.cleanup import cleanUp

test_message = """A message for *you*.

You are nice.
--- Reply ABOVE THIS LINE to post a comment ---
A quote of some sort.
"""

test_message_gmail = """A message for *you*.

You are nice.

On Tue, Mar 24, 2009 at 5:56 PM, Chris chris@example.org wrote:

> --- Reply ABOVE THIS LINE to post a comment ---
> A quote of some sort.
"""

test_message_outlook = """A message for *you*.

You are nice.

________________________________

From: KARL [mailto:staff-8-test@carlos.agendaless.com]
Sent: Wednesday, March 25, 2009 10:12 AM
To: Test User
Subject: [Staff 8 Test] Email Alert Test

--- Reply ABOVE THIS LINE to post a comment ---

A quote of some sort.
"""

test_message_outlook_express = """A message for *you*.

You are nice.

  ----- Original Message -----
  From: KARL
  To: Test User
  Sent: Tuesday, March 24, 2009 5:00 PM
  Subject: [Staff 8 Test] Email Alert Test

  A quote of some sort.
  """

test_message_thunderbird = """A message for *you*.

You are nice.

KARL wrote:
> --- Reply ABOVE THIS LINE to post a comment ---
> A quote of some sort.
"""

test_message_w_url_w_underscores = """This message contains a url:

http://example.com/fi_fai_fo_fum.mp3

I hope it comes out ok!
"""

class TestMailinTextScrubber(unittest.TestCase):
    def test_bad_mimetype(self):
        from karl.utilities.textscrub import text_scrubber
        self.assertRaises(Exception, text_scrubber, "TEXT", "text/html")

    def test_no_mimetype(self, text=test_message, is_reply=True):
        from karl.utilities.textscrub import text_scrubber
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(text, is_reply=True))

    def test_good_mimetype_reply(self):
        from karl.utilities.textscrub import text_scrubber
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(test_message,
                                                 mimetype="text/plain",
                                                 is_reply=True))

    def test_message_w_url_w_underscores(self):
        from karl.utilities.textscrub import text_scrubber
        expected = (u'<p>This message contains a url:</p>\n\n'
                    u'<p><a href="http://example.com/fi_fai_fo_fum.mp3">'
                    u'http://example.com/fi_fai_fo_fum.mp3</a></p>\n\n'
                    u'<p>I hope it comes out ok!</p>\n')
        self.assertEqual(
            expected, text_scrubber(test_message_w_url_w_underscores)
        )

    def test_gmail_reply(self):
        self.test_no_mimetype(test_message_gmail)

    def test_outlook_reply(self):
        self.test_no_mimetype(test_message_outlook)

    def test_outlook_express_reply(self):
        self.test_no_mimetype(test_message_outlook_express)

    def test_outlook_express_not_reply(self):
        from karl.utilities.textscrub import text_scrubber
        expected = (
            u'<p>A message for <em>you</em>.</p>\n\n'
            u'<p>You are nice.</p>\n\n'
            u'<p>----- Original Message -----\n'
            u'  From: KARL\n'
            u'  To: Test User\n'
            u'  Sent: Tuesday, March 24, 2009 5:00 PM\n'
            u'  Subject: [Staff 8 Test] Email Alert Test</p>\n\n'
            u'<p>A quote of some sort.</p>\n'
        )
        self.assertEqual(
            expected, text_scrubber(test_message_outlook_express)
        )

    def test_thunderbird_reply(self):
        self.test_no_mimetype(test_message_thunderbird)

