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
from itertools import islice
import mimetypes

from repoze.bfg.interfaces import IView
from repoze.bfg.security import has_permission
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content
from zope.interface import providedBy
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter

from karl.content.interfaces import ICommunityFile
from karl.content.views.interfaces import IFileInfo
from karl.content.views.interfaces import IShowSendalert
from karl.content.views.adapters import DefaultShowSendalert
from karl.utilities.converters.html import html2text
from karl.utils import get_setting
from karl.views.utils import basename_of_filepath
from karl.views.utils import make_unique_name


def fetch_attachments(attachments_folder, request):
    return [getMultiAdapter((attachment, request), IFileInfo)
                   for attachment in attachments_folder.values()]

def upload_attachments(attachments, folder, creator, request):
    """ This creates *and removes* attachments based on information
    retrieved from a form"""
    for attachment in attachments:
        if attachment.filename:
            mimetype = get_upload_mimetype(attachment)
            filename = make_unique_name(
                folder,
                basename_of_filepath(attachment.filename)
                )
            folder[filename] = obj = create_content(
                ICommunityFile,
                title = filename,
                stream = attachment.file,
                mimetype = mimetype,
                filename = filename,
                creator = creator,
                )
            max_size = int(get_setting(folder, 'upload_limit', 0))
            if max_size and obj.size > max_size:
                msg = 'File size exceeds upload limit of %d.' % max_size
                raise ValueError(msg)
        else:
            meta = attachment.metadata
            if meta.get('remove') and meta.get('default'):
                name = meta['default']
                if name in folder:
                    ob = folder[name]
                    if has_permission('delete', ob, request):
                        del folder[name]


def _find_view(context, request, name):
    # Cribbed from repoze.bfg.view.render_view_to_response
    provides = map(providedBy, (request, context))
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry()
    return reg.adapters.lookup(provides, IView, name=name)

def get_previous_next(context, request, viewname=''):

    # Reference Manual sections have inter-item navigation, which
    # means (sigh) that files and pages do as well.

    # Only works on resources whose parents are orderable
    parent = context.__parent__
    ordering = getattr(parent, 'ordering', None)
    if ordering is None:
        return None, None

    # Be a chicken and sync
    ordering.sync(parent.keys())

    # Find the prev/next names, then flatten some info about them for
    # the ZPT
    current_name = context.__name__
    previous = parent.get(ordering.previous_name(current_name))
    next = parent.get(ordering.next_name(current_name))

    if previous:
        if _find_view(previous, request, viewname) is not None:
            href = model_url(previous, request, viewname)
        else:
            href = model_url(previous, request)
        previous = {'title': previous.title, 'href': href}

    if next:
        if _find_view(next, request, viewname) is not None:
            href = model_url(next, request, viewname)
        else:
            href = model_url(next, request)
        next = {'title': next.title, 'href': href}

    return previous, next

_WIKI_WORDS = re.compile(r'[(][(]([^)]+)[)][)]')

def _crack_words(text):
    text = text.strip()
    text = _WIKI_WORDS.sub(r'\1', text)
    for word in text.split():
        yield word.strip()

def _crack_html_words(htmlstring):
    # Yield words from markup.
    for word in _crack_words(html2text(htmlstring)):
        yield word

def extract_description(htmlstring):
    """ Get a summary-style description from the HTML in text field """
    # Lots of resources don't have a user-visible description field,
    # which is good, as it is one less field for authors to be
    # confronted with.  We still need a description to show in blog
    # listing and search results, for example.  So extract a
    # description from the HTML text.

    summary_limit = 50 # number of "words"

    words = list(islice(_crack_html_words(htmlstring), summary_limit + 1))
    summary_list = words[0:summary_limit]
    summary = " ".join(summary_list)
    if len(words) > summary_limit:
        summary = summary + "..."

    return summary

def get_show_sendalert(context, request):
    show_sendalert = queryMultiAdapter((context, request), IShowSendalert)
    if show_sendalert is None:
        show_sendalert = DefaultShowSendalert(context, request)
    return show_sendalert.show_sendalert

def split_lines(lines):
    """
    Splits the provided text value by line breaks, strips each result,
    and returns a list of the non-empty results.
    """
    result = []
    for line in lines.split('\n'):
        stripped = line.strip()
        if stripped:
            result.append(stripped)
    return result

# Table mapping mime types sent by IE to standard types
ie_types = {
    "image/x-png": "image/png",
    "image/pjpeg": "image/jpeg",
}


def get_upload_mimetype(upload):
    mimetype = getattr(upload, 'mimetype', None)
    if mimetype is None:
        mimetype = getattr(upload, 'type', None)
    mimetype = ie_types.get(mimetype, mimetype)
    if mimetype in (
            'application/x-download',
            'application/x-application',
            'application/binary',
            'application/octet-stream',
            ):
        # The browser sent a meaningless file type.  Firefox on Ubuntu
        # does this to some people:
        #  https://bugs.launchpad.net/ubuntu/+source/firefox-3.0/+bug/84880
        # Try to guess a more sensible mime type from the filename.
        guessed_type, _ = mimetypes.guess_type(upload.filename)
        if guessed_type:
            mimetype = guessed_type
    return mimetype
