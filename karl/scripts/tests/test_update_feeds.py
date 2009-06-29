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
from zope.testing.cleanup import cleanUp

class UpdateFeedTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _config_filename(self):
        import os
        return os.path.join(
            os.path.dirname(__file__), 'feedtests', 'testfeeds.ini')

    def test_first_update(self):
        # first update will create container and get feeds
        site = {}
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IFeedsContainer
        from karl.models.interfaces import IFeed
        from repoze.bfg.testing import DummyModel
        registerContentFactory(DummyModel, IFeedsContainer)
        registerContentFactory(DummyFeed, IFeed)

        from cStringIO import StringIO
        out = StringIO()

        from karl.scripts.update_feeds import update
        update(site, self._config_filename(), out=out, parse=FakeFeedParser)

        self.assertEquals(out.getvalue(),
            "Getting feed 'example.com' from http://example.com/atom.xml... "
            "200 (ok)\n")

        self.assertTrue('feeds' in site)
        self.assertTrue('example.com' in site['feeds'])
        self.assertEquals(1, len(site['feeds']))
        feed = site['feeds']['example.com']
        self.assertEquals(3, len(feed.entries))
        self.assertEquals(['E1', 'E2', 'E3'], [e.title for e in feed.entries])
        self.assertEquals('Overridden title', feed.title)

    def test_etag_and_modified(self):
        feed = DummyFeed('Example')
        feed.etag = "tagyoureit"
        feed.feed_modified = "yesterday"
        site = {'feeds': {'example.com': feed}}

        from cStringIO import StringIO
        out = StringIO()

        parsers = []
        def parse(*args, **kw):
            res = FakeFeedParser(*args, **kw)
            parsers.append(res)
            return res

        from karl.scripts.update_feeds import update
        update(site, self._config_filename(), out=out, parse=parse)

        self.assertEquals(out.getvalue(),
            "Getting feed 'example.com' from http://example.com/atom.xml... "
            "304 (unchanged)\n")
        self.assertEquals(parsers[0].etag, 'tagyoureit')
        self.assertEquals(parsers[0].modified, 'yesterday')

    def test_force(self):
        feed = DummyFeed('Example')
        feed.etag = "tagyoureit"
        feed.feed_modified = "yesterday"
        site = {'feeds': {'example.com': feed}}

        from cStringIO import StringIO
        out = StringIO()

        parsers = []
        def parse(*args, **kw):
            res = FakeFeedParser(*args, **kw)
            parsers.append(res)
            return res

        from karl.scripts.update_feeds import update
        update(site, self._config_filename(), force=True, out=out, parse=parse)

        self.assertEquals(out.getvalue(),
            "Getting feed 'example.com' from http://example.com/atom.xml... "
            "200 (ok)\n")

    def test_feed_gone(self):
        feed = DummyFeed('Example')
        site = {'feeds': {'example.com': feed}}

        from cStringIO import StringIO
        out = StringIO()

        def parse(uri):
            p = FakeFeedParser(uri)
            p['status'] = 410
            return p

        from karl.scripts.update_feeds import update
        update(site, self._config_filename(), out=out, parse=parse)

        self.assertEquals(out.getvalue(),
            "Getting feed 'example.com' from http://example.com/atom.xml... "
            "410 (gone)\n")
        self.assertEquals(feed.old_uri, 'http://example.com/atom.xml')
        self.assertEquals(feed.new_uri, None)

        # now try to fetch again
        out = StringIO()
        update(site, self._config_filename(), out=out, parse=parse)
        self.assertEquals(out.getvalue(),
            "Warning: Feed 'example.com' is gone. Skipping.\n")

    def test_feed_moved(self):
        feed = DummyFeed('Example')
        site = {'feeds': {'example.com': feed}}

        from cStringIO import StringIO
        out = StringIO()

        def parse(uri):
            p = FakeFeedParser(uri)
            if 'atom.xml' in uri:
                p['status'] = 301
                p['href'] = "http://example.com/rss2.xml"
            return p

        from karl.scripts.update_feeds import update
        update(site, self._config_filename(), out=out, parse=parse)

        self.assertEquals(out.getvalue(),
            "Getting feed 'example.com' from http://example.com/atom.xml... "
            "301 (moved)\n")
        self.assertEquals(feed.old_uri, 'http://example.com/atom.xml')
        self.assertEquals(feed.new_uri, "http://example.com/rss2.xml")

        # now try to fetch again
        out = StringIO()
        update(site, self._config_filename(), out=out, parse=parse)
        self.assertEquals(out.getvalue(),
            "Warning: Feed 'example.com' has moved to "
            "http://example.com/rss2.xml.\n"
            "Please update the feed configuration file.\n"
            "Getting feed 'example.com' from http://example.com/rss2.xml... "
            "200 (ok)\n")

    def test_feed_exception(self):
        feed = DummyFeed('Example')
        site = {'feeds': {'example.com': feed}}

        from cStringIO import StringIO
        out = StringIO()

        # first populate the feed storage
        from karl.scripts.update_feeds import update
        update(site, self._config_filename(), out=out, parse=FakeFeedParser)

        feed = site['feeds']['example.com']
        self.assertEquals(3, len(feed.entries))

        # simulate an exception
        def parse(uri):
            p = FakeFeedParser(uri)
            p['feed'].clear()
            del p['entries'][:]
            p.bozo = 1
            p.bozo_exception = IOError('publisher failed Turing test')
            return p

        out = StringIO()
        update(site, self._config_filename(), out=out, parse=parse)

        self.assertEquals(out.getvalue(),
            "Getting feed 'example.com' from http://example.com/atom.xml... "
            "200 (ok)\n"
            "Warning for feed 'example.com': publisher failed Turing test\n"
            "No data for feed 'example.com'. Skipping.\n"
            )

        # ensure the old entries were not removed
        feed = site['feeds']['example.com']
        self.assertEquals(3, len(feed.entries))


class FakeFeedParser(dict):
    # mock of FeedParser
    def __init__(self, uri, etag=None, modified=None):
        self.update(dict(
            uri=uri,
            bozo=0,
            feed=FakeParsedFeed('Example'),
            entries=[
                FakeParsedEntry(name) for name in 'E1', 'E2', 'E3', 'E4'],
            status=304 if etag else 200,
            etag=etag,
            modified=modified,
            ))
    def __getattr__(self, name):
        # act like FeedParser result objects
        return self[name]

class FakeParsedFeed(dict):
    def __init__(self, title):
        self['title'] = title
    def __getattr__(self, name):
        return self[name]

class FakeParsedEntry(dict):
    def __init__(self, title):
        self['title'] = title
    def __getattr__(self, name):
        return self[name]

class DummyFeed:

    subtitle = None
    link = None
    etag = None
    feed_modified = None
    old_uri = None
    new_uri = None

    def __init__(self, title):
        self.title = title

    def update(self, parser):
        self.parser = parser
        self.entries = parser.entries
