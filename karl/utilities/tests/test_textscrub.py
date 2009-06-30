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

class TestMailinTextScrubber(unittest.TestCase):
    def test_bad_mimetype(self):
        from karl.utilities.textscrub import text_scrubber
        self.assertRaises(Exception, text_scrubber, "TEXT", "text/html")

    def test_no_mimetype(self, text=test_message):
        from karl.utilities.textscrub import text_scrubber
        from karl.utilities.textscrub import REPLY_SEPARATOR
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(text))

    def test_good_mimetype(self):
        from karl.utilities.textscrub import text_scrubber
        from karl.utilities.textscrub import REPLY_SEPARATOR
        expected = u'<p>A message for <em>you</em>.</p>\n\n<p>You are nice.</p>\n'
        self.assertEqual(expected, text_scrubber(test_message,
                                                 mimetype="text/plain"))

    def test_gmail(self):
        self.test_no_mimetype(test_message_gmail)

    def test_outlook(self):
        self.test_no_mimetype(test_message_outlook)

    def test_outlook_express(self):
        self.test_no_mimetype(test_message_outlook_express)

    def test_thunderbird(self):
        self.test_no_mimetype(test_message_thunderbird)
