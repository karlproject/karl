# -*- coding: utf-8 -*-

# Adapted from:
# https://github.com/zacharyvoase/slugify/blob/master/src/slugify.py
# to leave dots alone and not lower case.

"""A generic slugifier utility (currently only for Latin-based scripts)."""

import re
import unicodedata

__version__ = '0.0.1'


def slugify(string):
    if isinstance(string, str):
        string = string.decode('latin-1')

    return re.sub(r'[-\s]+', '-',
            unicode(
                re.sub(r'[^.\w\s-]', '',
                    unicodedata.normalize('NFKD', string)
                    .encode('ascii', 'ignore'))
                .strip()))
