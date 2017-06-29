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

import os
import re
import sys
import urllib
import urlparse
import transaction

from optparse import OptionParser

import lxml.html
from lxml.html import fragment_fromstring
from lxml.etree import ParserError
from lxml.etree import XMLSyntaxError
from zope.component import getMultiAdapter

from pyramid.interfaces import IRequest
from pyramid.interfaces import IView
from pyramid.registry import registry_manager
from pyramid.traversal import model_path
from pyramid.traversal import traverse

from repoze.lemonade.interfaces import IContent

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ICommunity
from karl.views.utils import make_name
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import IWikiPage

from karl.scripting import get_default_config
from karl.scripting import open_root

import logging
log = logging.getLogger(__name__)
logging.basicConfig()

dry_run = False
config = None
unknown_schemes = set()
check_link = None

wiki_link_re = re.compile("\(\(([^(]+)\)\)")

def _strip(s):
    """
    For passing to sub method of re pattern.
    """
    return s.strip()

def fix_wiki_links(site):
    """
    Check wiki pages for malformed links.

    """
    searcher = ICatalogSearch(site)
    total, docids,resolver = searcher(
        interfaces=[IWikiPage,],
        )

    for docid in docids:
        doc = resolver(docid)
        changes = doc.fix_links()
        if changes:
            # log the changes
            path = model_path(doc)
            for old_link, new_link in changes:
                log.info("Replaced wiki link at %s: ((%s)) -> ((%s))",
                         path, old_link, new_link)

def scrub(site):
    """
    Given root, find content with HTML body, look for bad links or other
    errors.

    """

    searcher = ICatalogSearch(site)
    total, docids, resolver = searcher(
        interfaces=[IContent],
        )

    log.info("Found a total of %d documents", total)
    for docid in docids:
        doc = resolver(docid)

        if not hasattr(doc, 'text'):
            continue

        path = model_path(doc)
        log.debug("Checking %s", path)

        text = doc.text

        if not text:
            # Some types we're expecting not to have text, so don't warn
            # about those
            if not(ICommunity.providedBy(doc) or
                   ICalendarEvent.providedBy(doc)):
                log.warn("No text: %s %s", type(doc), path)
            continue

        try:
            try:
                # Will throw ParserError if fragment doesn't have a single
                # root element.
                html = fragment_fromstring(doc.text)
            except ParserError:
                # Wrap in a single div to make the parser happy
                html = fragment_fromstring('<div>%s</div>' % doc.text)

        except XMLSyntaxError:
            log.error("Unparseable: %s", path, exc_info=True)

        # Check and fix links
        def callback(link):
            fixed = _rewrite_link(site, path, link)
            if fixed != link:
                log.info("Link rewritten at %s", path)
                log.info("Old link: %s", link)
                log.info("New link: %s", fixed)

            if not isinstance(fixed, unicode):
                fixed = unicode(fixed, 'utf-8')

            return fixed

        html.rewrite_links(callback)

        # Need to also change any instances of the 'mce_href' attribute to
        # match newly rewritten 'href' attribute.
        for element in html.getiterator():
            if 'mce_href' in element.keys():
                element.set('mce_href', element.get('href'))

        doc.text = unicode(lxml.html.tostring(html, 'utf-8'), 'utf-8')

    log.info("Done.")
    log.info("Unknown schemes: %s", ', '.join(unknown_schemes))

def _rewrite_link(site, path, link):
    url = urlparse.urlparse(link)

    scheme = url.scheme
    if scheme == 'mailto':
        # We can ignore mailto links
        return link

    if scheme == 'file':
        log.error("User linked to local filesystem at %s: %s",
                  path, link)
        return link

    if scheme and scheme not in ('http', 'https'):
        unknown_schemes.add(scheme)
        log.warn("Unknown scheme in link at %s: %s", path, link)
        return link

    if url.hostname and url.hostname != 'karl.soros.org':
        # Skip external links
        return link

    link = url.path

    if link.startswith("#"):
        # Skip anchors
        return link

    log.debug("Check link: %s", link)

    if not link.startswith('/'):
        # Try to resolve relative url
        link = urlparse.urljoin(path, link)

    # Some links still have '..' even after rewriting
    # These kill traverse
    link = link.replace("../", "")

    if isinstance(link, unicode):
        link = link.encode('utf-8')

    # Attempt BFG traversal and see what that gets us
    traversal = traverse(site, link)
    context = traversal["context"]
    view_name = traversal["view_name"]

    if view_name is None:
        # Path led right up to an existing object.
        # Awesome.  Next.
        return link

    if not _check_view(context, view_name):
        # We didn't end up at a leaf node with a view
        # Need to see if we can fix this broken link.
        return _broken_link(site, path, link)

    return link

def _check_view(context, view_name):
    adapters = registry_manager.get().adapters

    for iface in context.__provides__.__iro__:
        if adapters.lookup((iface, IRequest), IView, view_name) is not None:
            return True

    return False

def _broken_link(root, path, link):
    fixed = _fix_link_traverser(root, [], link[1:].split('/'))
    if fixed is not None:
        log.debug("Link fixer fixed link at %s", path)
        return fixed
    else:
        log.error("Broken link in %s: %s", path, link)
        return link

def _fix_link_traverser(context, traversed, subpath):
    if not subpath:
        # We're done, return traversed path
        return '/' + '/'.join(traversed)

    next = subpath.pop(0)

    # Easy case, normal traversal
    if hasattr(context, '__getitem__') and next in context:
        traversed.append(next)
        return _fix_link_traverser(context[next], traversed, subpath)

    # Karl2 site was actually rooted at /Plone/public
    # Although you wouldn't normally include that in a link url,
    # because of acquisition you could!
    # If we find this or some variation at the beginning of a link
    # just try to skip it.
    skippable = ('Plone', 'public',)
    if not traversed and next in skippable:
        return _fix_link_traverser(context, traversed, subpath)

    # An 'index_html' at the end is not necessary and skippable.
    # Some links inexplicably end with a '/&', which is also
    # skippable.
    skippable2 = ('index_html', '&',)
    if next in skippable2:
        return _fix_link_traverser(context, traversed, subpath)

    # Can't find next element.  Maybe it is a view
    if _check_view(context, next):
        # We can stop here, traversed path with view
        traversed.append(next)
        return '/' + '/'.join(traversed + subpath)

    # In Karl2 there was a content type for images that used a view
    # In Karl3, these are just files, so where we might have had a
    # view named 'image' in Karl2, we just have the 'dl' view in Karl3
    if next == 'image' and _check_view(context, 'dl'):
        # Got the view, we can stop here
        traversed.append('dl')
        return '/' + '/'.join(traversed + subpath)

    # Maybe next was resolved via acquisition in Karl2
    aq_context = _acquire(context, next)
    if aq_context:
        # Rewrite the leading part of this path as the model_path of the
        # acquired context.
        aq_path = model_path(aq_context)
        log.debug("Acquisition: rewrote path: %s -> %s",
                  traversed, aq_path)
        traversed = aq_path[1:].split('/')
        return _fix_link_traverser(aq_context, traversed, subpath)

    # Next may have been processed through make_name in Karl3.  Try
    # processing the name and see if that finds the next element.
    if hasattr(context, '__getitem__'):
        # This fix only makes sense if current node is traversable
        try:
            name = make_name({}, urllib.unquote(next))
            if name in context:
                traversed.append(name)
                return _fix_link_traverser(context[name], traversed, subpath)
        except ValueError:
            # make_name will throw ValueError if there are no alphanumerics
            # in next
            pass

    # Some links in Karl2 are to /profile/<user> rather than
    # /profiles/<user>.  Try changing profile to profiles and
    # see if that fixes the problem.
    if next == 'profile':
        subpath.insert(0, 'profiles')
        return _fix_link_traverser(context, traversed, subpath)

    # Links to /osipeople_*.html can be rewritten as just /people
    if next.startswith('osipeople_') and next.endswith('.html'):
        subpath.insert(0, 'people')
        return _fix_link_traverser(context, traversed, subpath)

    # There are some links to just /network-news and /network-events.
    # These are located in /offices/files
    if next in ('network-news', 'network-events'):
        subpath.insert(0, next)
        subpath.insert(0, 'files')
        subpath.insert(0, 'offices')
        return _fix_link_traverser(context, traversed, subpath)

    # Out of tricks, give up
    log.debug("Couldn't fix")
    log.debug("Traversed: %s", traversed)
    log.debug("Not found: %s", next)

    return None

def _acquire(context, name):
    while not(hasattr(context, '__getitem__') and name in context):
        context = context.__parent__
        if context is None:
            return None

    return context[name]

def _parse_options(argv):
    parser = OptionParser(
        description="Import a Karl2 GenericSetup dump into Karl3. The "
            "import_source is the path to a Karl 2 dump",)

    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    parser.add_option('-d', '--dry-run', dest='dry_run',
        action="store_true", default=False,
        help="Don't commit the transaction")

    parser.add_option('-L', '--link', dest='link', default=None,
        help="Check a single link")

    options, args = parser.parse_args()

    if args:
        parser.error()

    global config
    config = options.config
    if config is None:
        config = get_default_config()

    global dry_run
    dry_run = options.dry_run

    global check_link
    check_link = options.link
    print "check link:", check_link

def main(argv=sys.argv[1:]):
    _parse_options(argv)

    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    root, closer = open_root(config)

    try:
        if check_link is not None:
            print _rewrite_link(root, '', check_link)

        else:
            scrub(root)
            fix_wiki_links(root)
    except:
        transaction.abort()
        raise
    else:
        if dry_run:
            transaction.abort()
        else:
            transaction.commit()

if __name__ == '__main__':
    main()
