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

import datetime
import unittest

from zope.testing.cleanup import cleanUp
from repoze.bfg import testing

class EasternTimeZone(datetime.tzinfo):
    """'The datetime module does not supply any concrete subclasses of tzinfo.'
    """
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5)

    def __repr__(self):
        return "est"

    def dst(self, dt):
        return datetime.timedelta(0)

timezone = EasternTimeZone()

class BlogAtomFeedTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Set up a dummy blog
        from karl.content.interfaces import IBlog
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        from zope.interface import directlyProvides

        community = DummyCommunity()
        blog = community["blog"] = testing.DummyModel()
        directlyProvides(blog, IBlog)
        blog.title = "Blog Title"

        site = community.__parent__.__parent__
        profiles = site["profiles"] = testing.DummyModel()
        chris = profiles["chris"] = DummyProfile()
        chris.title = "Chris Rossi"

        self.context = blog

        # Register dummy catalog
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(dummy_catalog_search, Interface,
                                ICatalogSearch)

        # Register blog entry adapter
        from karl.views.interfaces import IAtomEntry
        from karl.content.interfaces import IBlogEntry
        from karl.views.atom import GenericAtomEntry
        testing.registerAdapter(GenericAtomEntry, (IBlogEntry, Interface),
                                IAtomEntry)

    def _create_dummy_blog_entries(self, count=1,
                                   creator="chris",
                                   title_fmt="Blog Entry %02d",
                                   created=datetime.datetime
                                     (2009, 03, 17, 12, 03, tzinfo=timezone),
                                   modified=datetime.datetime
                                     (2009, 03, 17, 12, 05, tzinfo=timezone),
                                   text=u"Some&nbsp;Text"):
        from zope.interface import directlyProvides
        from karl.content.interfaces import IBlogEntry

        id_base = 1
        for i in xrange(count):
            id = "entry%02d" % id_base
            while id in self.context:
                id_base += 1
                id = "entry%02d" % id_base
            tdelta = datetime.timedelta(id_base-1)
            entry = self.context[id] = testing.DummyModel()
            entry.creator = creator
            entry.title = title_fmt % id_base
            entry.created = created + tdelta
            entry.modified = modified + tdelta
            entry.text = text
            directlyProvides(entry, IBlogEntry)


    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.atom import BlogAtomFeed
        return BlogAtomFeed(context, request)

    def _callFUT(self, context, request):
        from karl.content.views.atom import blog_atom_view
        return blog_atom_view(context, request)

    def test_title(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(self.context.title, view.title)

    def test_subtitle(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(u"Recent Items", view.subtitle)

    def test_link(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual("http://example.com/communities/community/blog/",
                         view.link)

    def test_entries(self):
        self._create_dummy_blog_entries(5)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        entries = view.entries

        self.assertEqual(5, len(entries))
        entry = entries[-1]
        self.assertEquals("Blog Entry 01", entry.title)
        self.assertEquals(
            "http://example.com/communities/community/blog/entry01/",
            entry.uri)
        self.assertEquals("2009-03-17T12:03:00-05:00", entry.published)
        self.assertEquals("2009-03-17T12:05:00-05:00", entry.updated)
        self.assertEquals("Chris Rossi", entry.author["name"])
        self.assertEquals("http://example.com/profiles/chris/",
                          entry.author["uri"])
        self.assertEquals(u"Some&#160;Text", entry.content)

    def test_lots_of_entries(self):
        self._create_dummy_blog_entries(30)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)

        self.assertEquals(20, len(view.entries))

    def test_view(self):
        self._create_dummy_blog_entries(5)
        request = testing.DummyRequest()
        response = self._callFUT(self.context, request)

        self.assertEquals("application/atom+xml", response.content_type)

class CalendarAtomFeedTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Set up a dummy calendar
        from karl.content.interfaces import ICalendar
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        from zope.interface import directlyProvides

        community = DummyCommunity()
        cal = community["calendar"] = testing.DummyModel()
        directlyProvides(cal, ICalendar)
        cal.title = "Calendar"

        site = community.__parent__.__parent__
        profiles = site["profiles"] = testing.DummyModel()
        chris = profiles["chris"] = DummyProfile()
        chris.title = "Chris Rossi"

        self.context = cal

        # Register dummy catalog
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(dummy_catalog_search, Interface,
                                ICatalogSearch)

        # Register atom entry adapter
        from karl.views.interfaces import IAtomEntry
        from karl.content.views.atom import CalendarEventAtomEntry
        testing.registerAdapter(CalendarEventAtomEntry, (Interface, Interface),
                                IAtomEntry)

    def _create_dummy_calendar_events(self, count=1,
                                      creator="chris",
                                      title_fmt="Calendar Event %02d",
                                      created=datetime.datetime
                                      (2009, 03, 17, 12, 03, tzinfo=timezone),
                                      modified=datetime.datetime
                                      (2009, 03, 17, 12, 05, tzinfo=timezone),
                                      text=u"Some&nbsp;Text",
                                      startDate=datetime.datetime
                                      (2009, 4, 16, 11, 06, tzinfo=timezone),
                                      endDate=datetime.datetime
                                      (2009, 4, 16, 12, 06, tzinfo=timezone),
                                      location='The Big House'):
        from zope.interface import directlyProvides
        from karl.content.interfaces import ICalendarEvent

        id_base = 1
        for i in xrange(count):
            id = "entry%02d" % id_base
            while id in self.context:
                id_base += 1
                id = "entry%02d" % id_base
            tdelta = datetime.timedelta(id_base-1)
            entry = self.context[id] = testing.DummyModel()
            entry.creator = creator
            entry.title = title_fmt % id_base
            entry.created = created + tdelta
            entry.modified = modified + tdelta
            entry.text = text
            entry.startDate = startDate + datetime.timedelta(hours=count)
            entry.endDate = endDate + datetime.timedelta(hours=count)
            entry.location = location
            directlyProvides(entry, ICalendarEvent)


    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.atom import CalendarAtomFeed
        return CalendarAtomFeed(context, request)

    def _callFUT(self, context, request):
        from karl.content.views.atom import calendar_atom_view
        return calendar_atom_view(context, request)

    def test_title(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(self.context.title, view.title)

    def test_subtitle(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(u"Recent Items", view.subtitle)

    def test_link(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual("http://example.com/communities/community/calendar/",
                         view.link)

    def test_entries(self):
        self._create_dummy_calendar_events(5)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        entries = view.entries

        self.assertEqual(5, len(entries))
        entry = entries[-1]
        self.assertEquals("Calendar Event 01", entry.title)
        self.assertEquals(
            "http://example.com/communities/community/calendar/entry01/",
            entry.uri)
        self.assertEquals("2009-03-17T12:03:00-05:00", entry.published)
        self.assertEquals("2009-03-17T12:05:00-05:00", entry.updated)
        self.assertEquals("Chris Rossi", entry.author["name"])
        self.assertEquals("http://example.com/profiles/chris/",
                          entry.author["uri"])
        self.assertTrue("Some&#160;Text" in entry.content)

    def test_lots_of_entries(self):
        self._create_dummy_calendar_events(30)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)

        self.assertEquals(20, len(view.entries))

    def test_view(self):
        self._create_dummy_calendar_events(5)
        request = testing.DummyRequest()
        response = self._callFUT(self.context, request)

        self.assertEquals("application/atom+xml", response.content_type)

class WikiAtomFeedTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Set up a dummy wiki
        from karl.content.interfaces import IWiki
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        from zope.interface import directlyProvides

        community = DummyCommunity()
        wiki = community["wiki"] = testing.DummyModel()
        directlyProvides(wiki, IWiki)
        wiki.title = "Wiki Title"

        site = community.__parent__.__parent__
        profiles = site["profiles"] = testing.DummyModel()
        chris = profiles["chris"] = DummyProfile()
        chris.title = "Chris Rossi"

        self.context = wiki

        # Register dummy catalog
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(dummy_catalog_search, Interface,
                                ICatalogSearch)

        # Register atom entry adapter
        from karl.views.interfaces import IAtomEntry
        from karl.views.atom import GenericAtomEntry
        testing.registerAdapter(GenericAtomEntry, (Interface, Interface),
                                IAtomEntry)

    def _create_dummy_wiki_pages(self, count=1,
                                   creator="chris",
                                   title_fmt="Wiki Page %02d",
                                   created=datetime.datetime
                                     (2009, 03, 17, 12, 03, tzinfo=timezone),
                                   modified=datetime.datetime
                                     (2009, 03, 17, 12, 05, tzinfo=timezone),
                                   text=u"Some&nbsp;Text"):
        from zope.interface import directlyProvides
        from karl.content.interfaces import IWikiPage

        id_base = 1
        for i in xrange(count):
            id = "entry%02d" % id_base
            while id in self.context:
                id_base += 1
                id = "entry%02d" % id_base
            tdelta = datetime.timedelta(id_base-1)
            entry = self.context[id] = testing.DummyModel()
            entry.creator = creator
            entry.title = title_fmt % id_base
            entry.created = created + tdelta
            entry.modified = modified + tdelta
            entry.text = text
            directlyProvides(entry, IWikiPage)


    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.atom import WikiAtomFeed
        return WikiAtomFeed(context, request)

    def _callFUT(self, context, request):
        from karl.content.views.atom import wiki_atom_view
        return wiki_atom_view(context, request)

    def test_title(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(self.context.title, view.title)

    def test_subtitle(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(u"Recent Items", view.subtitle)

    def test_link(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual("http://example.com/communities/community/wiki/",
                         view.link)

    def test_entries(self):
        self._create_dummy_wiki_pages(5)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        entries = view.entries

        self.assertEqual(5, len(entries))
        entry = entries[-1]
        self.assertEquals("Wiki Page 01", entry.title)
        self.assertEquals(
            "http://example.com/communities/community/wiki/entry01/",
            entry.uri)
        self.assertEquals("2009-03-17T12:03:00-05:00", entry.published)
        self.assertEquals("2009-03-17T12:05:00-05:00", entry.updated)
        self.assertEquals("Chris Rossi", entry.author["name"])
        self.assertEquals("http://example.com/profiles/chris/",
                          entry.author["uri"])
        self.assertEquals(u"Some&#160;Text", entry.content)

    def test_lots_of_entries(self):
        self._create_dummy_wiki_pages(30)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)

        self.assertEquals(20, len(view.entries))

    def test_view(self):
        self._create_dummy_wiki_pages(5)
        request = testing.DummyRequest()
        response = self._callFUT(self.context, request)

        self.assertEquals("application/atom+xml", response.content_type)

class CommunityFilesAtomFeedTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        # Set up a dummy community files folder
        from karl.content.interfaces import ICommunityRootFolder
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        from zope.interface import directlyProvides

        community = DummyCommunity()
        files = community["files"] = testing.DummyModel()
        directlyProvides(files, ICommunityRootFolder)

        site = community.__parent__.__parent__
        profiles = site["profiles"] = testing.DummyModel()
        chris = profiles["chris"] = DummyProfile()
        chris.title = "Chris Rossi"

        self.context = files

        # Register dummy catalog
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        testing.registerAdapter(dummy_catalog_search, Interface,
                                ICatalogSearch)

        # Register atom entry adapter
        from karl.views.interfaces import IAtomEntry
        from karl.content.views.atom import CommunityFileAtomEntry
        testing.registerAdapter(CommunityFileAtomEntry, (Interface, Interface),
                                IAtomEntry)

    def _create_dummy_files(self, count=1,
                            creator="chris",
                            title_fmt="File %02d",
                            created=datetime.datetime
                              (2009, 03, 17, 12, 03, tzinfo=timezone),
                            modified=datetime.datetime
                              (2009, 03, 17, 12, 05, tzinfo=timezone)):
        from zope.interface import directlyProvides
        from karl.content.interfaces import ICommunityFile

        id_base = 1
        for i in xrange(count):
            id = "file%02d" % id_base
            while id in self.context:
                id_base += 1
                id = "file%02d" % id_base
            tdelta = datetime.timedelta(id_base-1)
            entry = self.context[id] = testing.DummyModel()
            entry.creator = creator
            entry.title = title_fmt % id_base
            entry.created = created + tdelta
            entry.modified = modified + tdelta
            entry.filename = id + ".txt"
            directlyProvides(entry, ICommunityFile)


    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.atom import CommunityFilesAtomFeed
        return CommunityFilesAtomFeed(context, request)

    def _callFUT(self, context, request):
        from karl.content.views.atom import community_files_atom_view
        return community_files_atom_view(context, request)

    def test_title(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(u"Dummy Communit\xe0 Files", view.title)

    def test_subtitle(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual(u"Recent Items", view.subtitle)

    def test_link(self):
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        self.assertEqual("http://example.com/communities/community/files/",
                         view.link)

    def test_entries(self):
        self._create_dummy_files(5)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)
        entries = view.entries

        self.assertEqual(5, len(entries))
        entry = entries[-1]
        self.assertEquals("File 01", entry.title)
        self.assertEquals(
            "http://example.com/communities/community/files/file01/",
            entry.uri)
        self.assertEquals("2009-03-17T12:03:00-05:00", entry.published)
        self.assertEquals("2009-03-17T12:05:00-05:00", entry.updated)
        self.assertEquals("Chris Rossi", entry.author["name"])
        self.assertEquals("http://example.com/profiles/chris/",
                          entry.author["uri"])
        self.assertEquals(
            u'<a href="http://example.com/communities/community/files/file01/">file01.txt</a>',
            entry.content)

    def test_lots_of_entries(self):
        self._create_dummy_files(30)
        request = testing.DummyRequest()
        view = self._makeOne(self.context, request)

        self.assertEquals(20, len(view.entries))

    def test_view(self):
        self._create_dummy_files(5)
        request = testing.DummyRequest()
        response = self._callFUT(self.context, request)

        self.assertEquals("application/atom+xml", response.content_type)

def dummy_catalog_search(context):
    def resolver(id):
        return context[id]

    def search(limit=None, sort_index=None, reverse=False, **kw):
        if sort_index == "modified_date":
            sort_index = "modified"

        batch = [entry for entry in context.values()]
        if sort_index:
            batch.sort(key=lambda x: getattr(x, sort_index),
                       reverse=reverse)
        if limit:
            batch = batch[:limit]

        ids = [entry.__name__ for entry in batch]
        return len(batch), ids, resolver

    return search