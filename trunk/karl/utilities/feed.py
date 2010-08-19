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
"""Download each feed defined in a config file and put it into ZODB.
"""

from ConfigParser import ConfigParser
from karl.models.interfaces import IFeed
from karl.models.interfaces import IFeedsContainer
from repoze.lemonade.content import create_content
import feedparser
import sys


def update_feeds(site, config_filename, force=False,
        out=sys.stdout, parse=feedparser.parse):
    """Get feeds and store their content."""
    container = site.get('feeds')
    if container is None:
        container = create_content(IFeedsContainer)
        site['feeds'] = container

    config = ConfigParser()
    config.read(config_filename)

    for section_name in config.sections():
        if ':' not in section_name:
            continue
        t, feed_name = section_name.split(':', 1)
        if t != 'feed':
            continue

        configured_uri = config.get(section_name, 'uri')
        uri = configured_uri
        if config.has_option(section_name, 'max'):
            max_entries = config.getint(section_name, 'max')
        else:
            max_entries = 0

        if config.has_option(section_name, 'title'):
            override_title = config.get(section_name, 'title')
        else:
            override_title = None

        kw = {}
        feed = container.get(feed_name)
        if feed is not None:
            if not force:
                # Use information from an earlier parsed feed to
                # fetch the feed with bandwidth savings.
                if feed.etag:
                    kw['etag'] = feed.etag
                if feed.feed_modified:
                    kw['modified'] = feed.feed_modified
            if feed.old_uri == uri:
                uri = feed.new_uri
                if not uri:
                    out.write(
                        "Warning: Feed '%s' is gone. Skipping.\n" % feed_name)
                    continue
                else:
                    out.write(
                        "Warning: Feed '%s' has moved to %s.\n"
                        "Please update the feed configuration file.\n"
                        % (feed_name, uri))

        out.write("Getting feed '%s' from %s... " % (feed_name, uri))
        out.flush()
        parser = parse(uri, **kw)
        status = parser.get('status', '(failed)')

        if status == 200:
            out.write('%s (ok)\n' % parser.status)
        elif status == 301:
            out.write('%s (moved)\n' % parser.status)
            if feed is not None:
                feed.old_uri = configured_uri
                feed.new_uri = parser.href
        elif status == 304:
            out.write('%s (unchanged)\n' % parser.status)
            continue
        elif status == 410:
            out.write('%s (gone)\n' % parser.status)
            if feed is not None:
                feed.old_uri = configured_uri
                feed.new_uri = None
        else:
            out.write('%s\n' % status)

        if parser.bozo:
            exc = parser.bozo_exception
            out.write("Warning for feed '%s': %s\n" % (feed_name, exc))

        if parser.feed:
            if feed is None:
                feed = create_content(IFeed, parser.feed.title)
                container[feed_name] = feed
            feed.update(parser)
            if max_entries and len(feed.entries) > max_entries:
                del feed.entries[max_entries:]
            if override_title and feed.title != override_title:
                feed.title = override_title
        else:
            out.write("No data for feed '%s'. Skipping.\n" % feed_name)

