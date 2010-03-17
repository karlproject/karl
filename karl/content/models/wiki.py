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

import re
import htmlentitydefs
import urllib

from persistent import Persistent

from repoze.bfg.security import authenticated_userid
from repoze.lemonade.content import create_content

from repoze.folder import Folder
from zope.interface import implements

from repoze.bfg.url import model_url

from karl.models.tool import ToolFactory
from karl.models.interfaces import IToolFactory

from karl.content.interfaces import IWiki
from karl.content.interfaces import IWikiPage

pattern = re.compile(r'\(\(([\w\W]+?)\)\)') # wicked-style
WICKED = '((%s))'

def _ijoin(a,b):
    """yield a0,b0,a1,b1.. if len(a) = len(b)+1"""
    yield(a[0])
    for i in range(1,len(a)):
        yield(b[i-1])
        yield(a[i])

class Wiki(Folder):
    implements(IWiki)
    title = u'Wiki'
    def __init__(self, creator):
        super(Wiki, self).__init__()
        self['front_page'] = create_content(
            IWikiPage,
            u'Front Page',
            FRONT_PAGE_CONTENT,
            FRONT_PAGE_DESCRIPTION,
            creator,
            )

_rm_chars = re.compile('[\W]', re.U)
def _eq_loose(s1, s2):
    """
    Performs a 'loose' string comparison--case insenstitive, ignoring
    non-alphanumeric characters and unescaping any html entities.
    """
    s1 = _unescape(s1)
    s2 = _unescape(s2)
    s1 = _rm_chars.sub('', s1.lower())
    s2 = _rm_chars.sub('', s2.lower())
    return s1 == s2

def _unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class WikiPage(Persistent):
    implements(IWikiPage)
    modified_by = None

    def __init__(self, title, text, description, creator):
        self.title = unicode(title)
        if text is None:
            self.text = u''
        else:
            self.text = unicode(text)
        if description is None:
            self.description = u''
        else:
            self.description = unicode(description)
        self.creator = unicode(creator)
        self.modified_by = self.creator

    def change_title(self, title):
        title = unicode(title)
        if not pattern.match(WICKED % title):
            raise ValueError(title)
        pages = self.__parent__.values()

        for page in pages:
            if page is not self and page.title == title:
                raise ValueError('Duplicate page title "%s"' % title)

        for page in pages:
            subs = []
            chunks = pattern.split(page.text)
            for linked_name in chunks[1::2]:
                if _eq_loose(self.title, linked_name):
                    subs.append(WICKED % title)
                else:
                    subs.append(WICKED % linked_name)
            page.text = u''.join(_ijoin(chunks[::2], subs))
        self.title = title

    def cook(self, request):

        chunks = pattern.split(self.text)
        if len(chunks) == 1: # fastpath
            return self.text

        subs = []

        # Every other chunk is a wiki link
        for wikilink in chunks[1::2]:
            for page in self.__parent__.values():
                if _eq_loose(page.title, wikilink):
                    url = model_url(page, request)
                    subs.append(WIKI_LINK % (url, wikilink))
                    break
            else:
                quoted = urllib.quote(wikilink)
                subs.append(ADD_WIKIPAGE_LINK % (
                        wikilink, quoted))

        # Now join the two lists (knowing that len(text) == subs+1)
        return u''.join(_ijoin(chunks[::2], subs))

    def fix_links(self):
        """Change all loose wiki links to exact links.

        Returns a list of changes: [(old link, new link)]
        """
        changes = []  # [(old link, new link)]

        def replace(match):
            old_link = match.group(1)
            link = old_link.strip()
            page = self.__parent__.get(link)
            if page is None:
                for page in self.__parent__.values():
                    if _eq_loose(page.title, link):
                        link = page.title
                        break
            if link != old_link:
                changes.append((old_link, link))
            return "((%s))" % link

        new_text = pattern.sub(replace, self.text)
        if changes:
            self.text = new_text
        return changes

FRONT_PAGE_CONTENT = u"""\
This is the front page of your wiki.
"""

FRONT_PAGE_DESCRIPTION = u"""\
This is the front page of your wiki.
"""

ADD_WIKIPAGE_LINK = (
u'<span class="wicked_unresolved">%s</span> '
 '<a href="../add_wikipage.html?title=%s">+</a>'
)

WIKI_LINK = (
u'<a href="%s"><span class="wicked_resolved">%s</span></a>'
)

class WikiToolFactory(ToolFactory):
    implements(IToolFactory)
    name = 'wiki'
    interfaces = (IWiki, IWikiPage)
    def add(self, context, request):
        creator = authenticated_userid(request)
        wiki = create_content(IWiki, creator)
        context['wiki'] = wiki

    def remove(self, context, request):
        del context['wiki']

wiki_tool_factory = WikiToolFactory()
