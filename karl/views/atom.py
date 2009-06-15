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

import time

from zope.component import getMultiAdapter
from repoze.bfg.interfaces import IView

from webob import Response
from zope.interface import implements
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.url import model_url

from karl.utils import find_profiles
from karl.views.community import get_recent_items_batch
from karl.views.interfaces import IAtomFeed
from karl.views.interfaces import IAtomEntry
from karl.models.interfaces import ICommunity

def format_datetime(d):
    formatted = d.strftime("%Y-%m-%dT%H:%M:%S")
    if d.tzinfo:
        tz = d.strftime("%z")
        assert len(tz) == 5
        formatted = "%s%s:%s" % (formatted, tz[:3], tz[3:])
    else:
        offset = -time.timezone
        sign = "-" if offset < 0 else "+"
        h, m = abs(offset / 3600), abs((offset % 3600) / 60)
        tz = "%s%02d:%02d" % (sign, h, m)
        formatted += tz

    return formatted

class AtomFeed(object):
    """ Atom/xml view.
    """
    implements(IView, IAtomFeed)
    _entries = None
    _template = "templates/atomfeed.pt"
    _subtitle = u"Recent Items"
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self._url = model_url(context, request)
        
    def __call__(self):
        xml = render_template(self._template, view=self)
        response = Response(xml, content_type="application/atom+xml")
        return response
            
    @property
    def title(self):
        return self.context.title
        
    @property
    def subtitle(self):
        return self._subtitle
        
    @property
    def link(self):
        return self._url
    
    id = link
    
    @property
    def entries(self):
        if self._entries is None:
            request = self.request
            def adapt(context):
                return getMultiAdapter((context, request), IAtomEntry)
            self._entries = map(adapt, self._entry_models)

        return self._entries
    
    @property
    def _entry_models(self):
        """Provides actual content objects that need to be adapted to atom feed
        entries.
        """
        raise NotImplementedError(
            "Method must be overridden by concrete subclass.")

class AtomEntry(object):
    """ Abstract atom entry class that can adapt most model objects to an
    atom entry, except for the entry content.
    """
    implements(IAtomEntry)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def title(self):
        return self.context.title
    
    @property
    def uri(self):
        return model_url(self.context, self.request)

    @property
    def published(self):
        return format_datetime(self.context.created)
    
    @property
    def updated(self):
        return format_datetime(self.context.modified)
    
    @property
    def author(self):
        profiles = find_profiles(self.context)
        profile = profiles[self.context.creator]
        return {
            "name": profile.title,
            "uri": model_url(profile, self.request)
        }
    
    @property
    def content(self):
        raise NotImplementedError(
            "Method must be overridden by concrete subclass.")

class NullContentAtomEntry(AtomEntry):
    """ An adapter for objects that don't really have textual content 
    appropriate for including in a feed.
    """
    @property
    def content(self):
        return None
    
class GenericAtomEntry(AtomEntry):
    """ Can adapt any model object with a "text" or "description" attribute,
    favoring "text" if it is available.
    """
    @property
    def content(self):
        if hasattr(self.context, "text"):
            return self.context.text
        if hasattr(self.context, "description"):
            return self.context.description
        raise ValueError("Cannot adapt %s" % self.context)
    
class CommunityAtomFeed(AtomFeed):
    """ Presents "Recent Activity" for community as an atom feed.
    """
    _subtitle = u"Recent Activity"
    
    def __init__(self, context, request):
        assert ICommunity.providedBy(context)
        super(CommunityAtomFeed, self).__init__(context, request)
        
    @property
    def _entry_models(self):
        batch = get_recent_items_batch(self.context, self.request, size=20)
        return batch["entries"]

def community_atom_view(context, request):
    return CommunityAtomFeed(context, request)()