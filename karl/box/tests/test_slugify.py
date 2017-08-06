# -*- coding: utf-8 -*-

import unittest

class SlugifyTests(unittest.TestCase):

    def test_slugify(self):
        from ..slugify import slugify
        self.assertEqual(slugify(u" Héllo\tWörld.\n"), 'Hello-World.')
