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

from datetime import datetime
import math
import os
from pprint import pformat

from zope.component import queryUtility

from repoze.bfg.interfaces import ISettings
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_interface
from repoze.folder.interfaces import IFolder
from repoze.lemonade.content import is_content

from karl.models.interfaces import ILetterManager
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IProfile
from karl.utils import find_catalog
from karl.utils import find_peopledirectory_catalog
from karl.utils import find_tags

from karl.utils import find_users

def postorder(startnode):
    def visit(node):
        if IFolder.providedBy(node):
            for child in node.values():
                for result in visit(child):
                    yield result
        yield node
    return visit(startnode)

def index_content(obj, event):
    """ Index content (an IObjectAddedEvent subscriber) """
    catalog = find_catalog(obj)
    if catalog is not None:
        for node in postorder(obj):
            if is_content(obj):
                path = model_path(node)
                docid = getattr(node, 'docid', None)
                if docid is None:
                    docid = node.docid = catalog.document_map.add(path)
                else:
                    catalog.document_map.add(path, docid)
                catalog.index_doc(docid, node)

def unindex_content(obj, docids):
    """ Unindex given 'docids'.
    """
    catalog = find_catalog(obj)
    if catalog is not None:
        for docid in docids:
            catalog.unindex_doc(docid)
            catalog.document_map.remove_docid(docid)

def cleanup_content_tags(obj, docids):
    """ Remove any tags associated with 'docids'.
    """
    tags = find_tags(obj)
    if tags is not None:
        for docid in docids:
            tags.delete(item=docid)

def handle_content_removed(obj, event):
    """ IObjectWillBeRemovedEvent subscriber.
    """
    catalog = find_catalog(obj)
    if catalog is not None:
        path = model_path(obj)
        num, docids = catalog.search(path={'query': path,
                                           'include_path': True})
        unindex_content(obj, docids)
        cleanup_content_tags(obj, docids)

def reindex_content(obj, event):
    """ Reindex a single piece of content (non-recursive); an
    IObjectModifed event subscriber """
    catalog = find_catalog(obj)
    if catalog is not None:
        path = model_path(obj)
        docid = catalog.document_map.docid_for_address(path)
        catalog.reindex_doc(docid, obj)

def set_modified(obj, event):
    """ Set the modified date on a single piece of content
    unconditionally (non-recursive); an IObjectModified event
    subscriber"""
    now = datetime.now()
    obj.modified = now
    _modify_community(obj, now)

def set_created(obj, event):
    """ Add modified and created attributes to nodes which do not yet
    have them (recursively); an IObjectWillBeAddedEvent subscriber"""
    now = datetime.now()
    for node in postorder(obj):
        if is_content(obj):
            if not getattr(node, 'modified', None):
                node.modified = now
            if not getattr(node, 'created', None):
                node.created = now
    _modify_community(obj, now)

def _modify_community(obj, when):
    # manage content_modified on community whenever a piece of content
    # in a community is changed
    community = find_interface(obj, ICommunity)
    if community is not None and community is not obj:
         community.content_modified = when

def delete_community(obj, event):
    # delete the groups related to the community when a community is
    # deleted
    context = obj
    users = find_users(context)
    users.delete_group(context.members_group_name)
    users.delete_group(context.moderators_group_name)

# manage alphabet ('title startswith') listing: optimization for letter links

def alpha_added(obj, event):
    adapter = ILetterManager(obj)
    adapter.delta(1)

def alpha_removed(obj, event):
    adapter = ILetterManager(obj)
    adapter.delta(-1)

# "Index" profile e-mails into the profiles folder.

def _remove_email(parent, name):
    mapping = getattr(parent, 'email_to_name')
    filtered = [x for x in mapping.items() if x[1] != name]
    mapping.clear()
    mapping.update(filtered)

def profile_added(obj, event):
    parent = obj.__parent__
    name = obj.__name__
    _remove_email(parent, name)
    parent.email_to_name[obj.email] = name

def profile_removed(obj, event):
    parent = obj.__parent__
    name = obj.__name__
    _remove_email(parent, name)

def index_profile(obj, event):
    """ Index profile (an IObjectAddedEvent subscriber) """
    catalog = find_peopledirectory_catalog(obj)
    if catalog is not None:
        for node in postorder(obj):
            if IProfile.providedBy(node):
                path = model_path(node)
                docid = getattr(node, 'docid', None)
                if docid is None:
                    docid = node.docid = catalog.document_map.add(path)
                else:
                    catalog.document_map.add(path, docid)
                catalog.index_doc(docid, node)

def unindex_profile(obj, event):
    """ Unindex profile (an IObjectWillBeRemovedEvent subscriber) """
    catalog = find_peopledirectory_catalog(obj)
    if catalog is not None:
        path = model_path(obj)
        path_docid = catalog.document_map.docid_for_address(path)
        num, docids = catalog.search(path=path)
        for docid in docids:
            # unindex any children of the path first
            catalog.unindex_doc(docid)
            catalog.document_map.remove_docid(docid)
        if path_docid is not None:
            # and then finally the parent
            catalog.unindex_doc(path_docid)
            catalog.document_map.remove_docid(path_docid)

def reindex_profile(obj, event):
    """ Reindex a single piece of profile (non-recursive); an
    IObjectModifed event subscriber """
    catalog = find_peopledirectory_catalog(obj)
    if catalog is not None:
        path = model_path(obj)
        docid = catalog.document_map.docid_for_address(path)
        catalog.unindex_doc(docid)
        catalog.index_doc(docid, obj)


class QueryLogger(object):
    """Event listener that logs ICatalogQueryEvents to a directory.

    Divides the log files by the magnitude of the query duration,
    making it easy to find expensive queries.
    """

    def __init__(self):
        self._configured = False
        self.log_dir = None
        self.min_duration = None

    def configure(self, settings):
        self.log_dir = getattr(settings, 'query_log_dir', None)
        if self.log_dir:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        self.min_duration = float(
            getattr(settings, 'query_log_min_duration', 0.0))
        self._configured = True

    def __call__(self, event):
        if not self._configured:
            settings = queryUtility(ISettings)
            if settings is not None:
                self.configure(settings)
        if not self.log_dir:
            return
        duration = event.duration
        if duration < self.min_duration:
            return
        t = datetime.now().isoformat()
        query = '  ' + pformat(event.query).replace('\n', '\n  ')
        msg = '%s %8.3f %6d\n%s\n' % (
            t, duration, event.result[0], query)
        magnitude = math.ceil(math.log(duration, 2))
        fn = '%07d.log' % int(1000 * 2**magnitude)
        path = os.path.join(self.log_dir, fn)
        f = open(path, 'a')
        try:
            f.write(msg)
        finally:
            f.close()

log_query = QueryLogger()
