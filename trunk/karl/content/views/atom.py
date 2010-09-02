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

from zope.component import getAdapter
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from karl.models.interfaces import ICatalogSearch
from karl.views.atom import format_datetime
from karl.views.atom import AtomFeed
from karl.views.atom import AtomEntry
from karl.views.utils import convert_entities
from karl.utils import find_profiles
from karl.utils import find_community
from karl.content.interfaces import IBlog
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IWikiPage

N_ENTRIES = 20

def xml_content(f):
    """
    A decorator for xml content which performs entity conversions from HTML
    to numeric XML-friendly entities.
    """
    def wrapper(*args, **kw):
        return convert_entities(f(*args, **kw))
    return wrapper

class BlogAtomFeed(AtomFeed):
    @property
    def _entry_models(self):
        search = getAdapter(self.context, ICatalogSearch)
        count, docids, resolver = search(
            limit=N_ENTRIES,
            path=model_path(self.context),
            sort_index="modified_date",
            reverse=True,
            interfaces=[IBlogEntry,]
        )

        return [resolver(docid) for docid in docids]

def blog_atom_view(context, request):
    return BlogAtomFeed(context, request)()

class CalendarAtomFeed(AtomFeed):
    @property
    def _entry_models(self):
        search = getAdapter(self.context, ICatalogSearch)
        count, docids, resolver = search(
            limit=N_ENTRIES,
            path=model_path(self.context),
            sort_index="modified_date",
            reverse=True,
            interfaces=[ICalendarEvent,]
        )

        return [resolver(docid) for docid in docids]

DATETIME_DISPLAY_FORMAT = "%A %B %d, %Y %I:%M %p"
class CalendarEventAtomEntry(AtomEntry):
    @property
    @xml_content
    def content(self):
        c = self.context
        return _calendar_event_content % {
            'start_date': c.startDate.strftime(DATETIME_DISPLAY_FORMAT),
            'end_date': c.endDate.strftime(DATETIME_DISPLAY_FORMAT),
            'location': c.location,
            'text': c.text,
        }

def calendar_atom_view(context, request):
    return CalendarAtomFeed(context, request)()

_calendar_event_content = """
<div><b>Start date:</b> %(start_date)s</div>
<div><b>End date:</b> %(end_date)s</div>
<div><b>Location:</b> %(location)s</div>
<br/>
%(text)s
"""

class WikiAtomFeed(AtomFeed):
    @property
    def _entry_models(self):
        search = getAdapter(self.context, ICatalogSearch)
        count, docids, resolver = search(
            limit=N_ENTRIES,
            path=model_path(self.context),
            sort_index="modified_date",
            reverse=True,
            interfaces=[IWikiPage,]
        )

        return [resolver(docid) for docid in docids]

def wiki_atom_view(context, request):
    return WikiAtomFeed(context, request)()

class CommunityFilesAtomFeed(AtomFeed):
    @property
    def title(self):
        c = find_community(self.context)
        return "%s Files" % c.title

    @property
    def _entry_models(self):
        search = getAdapter(self.context, ICatalogSearch)
        count, docids, resolver = search(
            limit=N_ENTRIES,
            path=model_path(self.context),
            sort_index="modified_date",
            reverse=True,
            interfaces={ "operator": "or",
                         "query": [ICommunityFolder, ICommunityFile,]}
        )

        return [resolver(docid) for docid in docids]

class CommunityFileAtomEntry(AtomEntry):
    """ Adapts a community file to an atom entry--content is a link
    to the file.
    """
    @property
    @xml_content
    def content(self):
        return '<a href="%s">%s</a>' % (
            model_url(self.context, self.request),
            self.context.filename
        )

def community_files_atom_view(context, request):
    return CommunityFilesAtomFeed(context, request)()