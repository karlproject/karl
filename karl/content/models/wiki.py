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
import re
import htmlentitydefs
import urllib

from repoze.bfg.security import authenticated_userid
from repoze.bfg.traversal import model_path
from repoze.lemonade.content import create_content
from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IObjectVersion

from repoze.folder import Folder
from zope.interface import implements

from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url

from karl.models.tool import ToolFactory
from karl.models.interfaces import IToolFactory

from karl.content.models.adapters import extract_text_from_html
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
        self.creator = creator
        self._create_front_page()

    def _create_front_page(self):
        self['front_page'] = create_content(
            IWikiPage,
            u'Front Page',
            FRONT_PAGE_CONTENT,
            FRONT_PAGE_DESCRIPTION,
            self.creator,
            )

    def __delitem__(self, name):
        super(Wiki, self).__delitem__(name)
        if name == 'front_page':
            self._create_front_page()


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

class WikiPage(Folder):
    implements(IWikiPage)
    modified_by = None

    def __init__(self, title=u'', text=u'', description=u'', creator=u''):
        super(WikiPage, self).__init__()
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
            cleaned = extract_text_from_html(wikilink)
            for page in self.__parent__.values():
                if _eq_loose(page.title, cleaned):
                    url = model_url(page, request)
                    subs.append(WIKI_LINK % (url, wikilink))
                    break
            else:
                quoted = urllib.quote(cleaned.encode('UTF-8'))
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

    def get_attachments(self):
        return self

    def revert(self, version):
        # catalog document map blows up if you feed it a long int
        self.docid = int(version.docid)
        self.created = version.created
        self.title = version.title
        self.description = version.description
        self.modified = version.modified
        self.text = version.attrs['text']
        self.creator = version.attrs['creator']
        self.modified_by = version.user


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


class WikiPageVersion(object):
    implements(IObjectVersion)

    def __init__(self, page):
        self.title = page.title
        self.description = page.description
        self.created = page.created
        self.modified = page.modified
        self.docid = page.docid
        self.path = model_path(page)
        self.attrs = dict((name, getattr(page, name)) for name in [
            'text',
            'creator',
        ])
        self.attachments = None
        self.klass = page.__class__ # repozitory can't detect we are a shim
        self.user = page.modified_by
        if self.user is None:
            self.user = page.creator
        self.comment = None


class WikiContainerVersion(object):
    implements(IContainerVersion)

    def __init__(self, wiki):
        self.container_id = wiki.docid
        self.path = model_path(wiki)
        self.map = dict((name, page.docid) for name, page in wiki.items())
        self.ns_map = {}


class WikiPageContainerVersion(object):
    implements(IContainerVersion)

    def __init__(self, page):
        self.container_id = page.docid
        self.path = model_path(page)
        self.map = dict((name, attachment.docid)
                        for name, attachment in page.items())
        self.ns_map = {}
