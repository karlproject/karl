# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import unittest

class ExtractDescriptionTests(unittest.TestCase):

    def _callFUT(self, htmlstring):
        from karl.content.views.utils import extract_description
        return extract_description(htmlstring)

    def test_plain_bytes(self):
        summary = self._callFUT("I am text")
        self.assertEqual(summary, "I am text")

    def test_plain_unicode(self):
        summary = self._callFUT(u"I am text")
        self.assertEqual(summary, u"I am text")

    def test_html_body(self):
        summary = self._callFUT("<html><body>I am text</body></html>")
        self.assertEqual(summary, "I am text")

    def test_html_elements(self):
        summary = self._callFUT("<div>I</div> <span>am</span> <b>text</b>")
        self.assertEqual(summary, "I am text")

    def test_bad_html(self):
        summary = self._callFUT("<b>I <i>am</i> <u>broken text")
        self.assertEqual(summary, "I am broken text")

    def test_newline(self):
        summary = self._callFUT("I am \r\n divided text")
        self.assertEqual(summary, "I am divided text")

    def test_wiki_markup(self):
        summary = self._callFUT("I am ((wiki linked)) text")
        self.assertEqual(summary, "I am wiki linked text")

    def test_limit(self):
        summary = self._callFUT("I am quite long text. " * 50)
        self.assertEqual(len(summary), 222)
        self.assertTrue(summary.endswith('...'))


