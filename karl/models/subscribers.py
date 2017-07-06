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
from datetime import timedelta
import logging
import math
import os
from pprint import pformat

from zope.component import queryAdapter
from zope.component import queryUtility

from pyramid.interfaces import ISettings
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request
from pyramid.traversal import resource_path
from pyramid.traversal import find_interface
from repoze.folder.interfaces import IFolder
from repoze.lemonade.content import is_content

from karl.models.interfaces import ICommunity
from karl.models.interfaces import IContainerVersion
from karl.models.interfaces import IIntranets
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import IObjectVersion
from karl.models.interfaces import IProfile
from karl.models.peopledirectory import reindex_peopledirectory
from karl.utils import find_catalog
from karl.utils import find_peopledirectory_catalog
from karl.utils import find_profiles
from karl.utils import find_repo
from karl.utils import find_site
from karl.utils import find_tags
from karl.utils import find_users

log = logging.getLogger(__name__)

_NOW = None
def _now():     # unittests can replace this to get known results
    return _NOW or datetime.now()

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
                path = resource_path(node)
                docid = getattr(node, 'docid', None)
                if docid is None:
                    docid = node.docid = catalog.document_map.add(path)
                else:
                    catalog.document_map.add(path, docid)
                catalog.index_doc(docid, node)

def set_is_created_by_staff(obj, event):
    """ set is_created_by_staff (an IObjectAddedEvent subscriber) """
    creator = getattr(obj, 'creator', None)
    if creator:
        users = find_users(obj)
        obj.is_created_by_staff = users.member_of_group(creator,
                                                        'group.KarlStaff')

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
        path = resource_path(obj)
        num, docids = catalog.search(path={'query': path,
                                           'include_path': True})
        unindex_content(obj, docids)
        cleanup_content_tags(obj, docids)

def reindex_content(obj, event):
    """ Reindex a single piece of content (non-recursive); an
    IObjectModifed event subscriber """
    catalog = find_catalog(obj)
    if catalog is not None:
        path = resource_path(obj)
        docid = catalog.document_map.docid_for_address(path)
        catalog.reindex_doc(docid, obj)

def set_modified(obj, event):
    """ Set the modified date on a single piece of content.

    This subscriber is non-recursive.

    Intended use is as an IObjectModified event subscriber.
    """
    if is_content(obj):
        now = _now()
        obj.modified = now
        _modify_community(obj, now)
        repo = find_repo(obj)
        if repo is not None:
            adapter = queryAdapter(obj, IObjectVersion)
            if adapter is not None:
                repo.archive(adapter)
                blobs = getattr(adapter, 'blobs', None)
                if blobs:
                    for blob in adapter.blobs.values():
                        blob.close()
                if adapter.comment is None:
                    adapter.comment = 'Content modified.'

def set_created(obj, event):
    """ Add modified and created attributes to obj and children.

    Only add to content objects which do not yet have them (recursively)

    Intended use is as an IObjectWillBeAddedEvent subscriber.
    """
    now = _now()
    for node in postorder(obj):
        if is_content(obj):
            if not getattr(node, 'modified', None):
                node.modified = now
            if not getattr(node, 'created', None):
                node.created = now
    parent = getattr(event, 'parent', None)
    if parent is not None:
        _modify_community(parent, now)

def add_to_repo(obj, event, update_container=True):
    """
    Add a newly created object to the version repository.

    Intended use is as an IObjectAddedEvent subscriber.
    """
    if find_interface(obj, IIntranets):
        # Exclude /offices from repo
        return

    repo = find_repo(obj)
    if repo is None:
        return

    if not repo.history(obj.docid, True):
        # It is not in the repo, so add it
        adapter = queryAdapter(obj, IObjectVersion)
        if adapter is not None:
            if adapter.comment is None:
                adapter.comment = 'Content created.'
            repo.archive(adapter)
            blobs = getattr(adapter, 'blobs', None)
            if blobs:
                for blob in adapter.blobs.values():
                    blob.close()

    if update_container:
        container = event.parent
        adapter = queryAdapter(container, IContainerVersion)
        if adapter is not None:
            # In some cases, a sibling might not have been added to the archive
            # yet.  Archiving the container before all of its children are
            # archived can result in an integrity constraint violation, so we
            # should check for this case and handle it.
            for name, docid in adapter.map.items():
                if docid == obj.docid:
                    continue
                if not repo.history(docid, True):
                    orphan = container[name]
                    log.warn("Adding object to archive: %s" %
                             resource_path(orphan))
                    add_to_repo(orphan, event, update_container=False)

            request = get_current_request()
            user = authenticated_userid(request)
            repo.archive_container(adapter, user)

    # Recurse into children if adding a subtree
    if IFolder.providedBy(obj):
        for name, child in obj.items():
            fake_event = FakeEvent()
            fake_event.parent = obj
            add_to_repo(child, fake_event)

class FakeEvent(object):
    pass

def delete_in_repo(obj, event):
    """
    Add object to deleted items in repozitory.

    Intended use is as an IObjectRemovedEvent subscriber.
    """
    container = event.parent
    if find_interface(container, IIntranets):
        # Exclude /offices from repo
        return

    repo = find_repo(container)
    if repo is not None:
        adapter = queryAdapter(container, IContainerVersion)
        if adapter is not None:
            request = get_current_request()
            user = authenticated_userid(request)
            repo.archive_container(adapter, user)

def _modify_community(obj, when):
    # manage content_modified on community whenever a piece of content
    # in a community is changed
    community = find_interface(obj, ICommunity)
    if community is not None:
        community.content_modified = when
        catalog = find_catalog(community)
        if catalog is not None:  # may not be wired into the site yet
            index = catalog.get('content_modified')
            if index is not None:
                index.index_doc(community.docid, community)

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

# Add / remove list aliases from the root 'list_aliases' index.

def add_mailinglist(obj, event):
    # When this handler is called while loading a peopleconf configuration,
    # this will get called before the maillist has been added to the site,
    # so we won't actually have a path to the site.  In this case we'll get
    # back a report object that doesn't have a 'list_aliases' attribute.  We
    # safely do nothing here, since the peopleconf loader will go back and
    # add the aliases when it has finished loading.
    site = find_site(obj)
    aliases = getattr(site, 'list_aliases', None)
    if aliases is not None:
        aliases[obj.short_address] = resource_path(obj.__parent__)

def remove_mailinglist(obj, event):
    aliases = find_site(obj).list_aliases
    try:
        del aliases[obj.short_address]
    except KeyError:
        pass

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
                path = resource_path(node)
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
        path = resource_path(obj)
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
        path = resource_path(obj)
        docid = catalog.document_map.docid_for_address(path)
        catalog.unindex_doc(docid)
        catalog.index_doc(docid, obj)

def reindex_profile_after_group_change(event):
    """ Subscriber for group change events to reindex the profile
    in peopledir catalog """
    profiles = find_profiles(event.site)
    profile = profiles.get(event.id)
    if profile is not None:
        catalog = find_peopledirectory_catalog(profile)
        if catalog is not None:
            path = resource_path(profile)
            docid = catalog.document_map.docid_for_address(path)
            catalog.unindex_doc(docid)
            catalog.index_doc(docid, profile)

def set_new_profile_password_expiration_date(obj, event):
    obj.password_expiration_date = (datetime.utcnow() + timedelta(days=180))

def update_peopledirectory_indexes(event):
    """Updates the peopledir catalog schema.

    This is an IPeopleDirectorySchemaChanged subscriber.
    """
    peopledir = event.peopledir
    if peopledir.update_indexes():
        reindex_peopledirectory(peopledir)


class QueryLogger(object):
    """Event listener that logs ICatalogQueryEvents to a directory.

    Performs 2 tasks:
    1. Divides the log files by the magnitude of the query duration,
       making it easy to find expensive queries.
    2. Log all queries to a single file for comparison across systems
    """

    def __init__(self):
        self._configured = False
        self.log_dir = None
        self.min_duration = None
        self.log_all = None

    def configure(self, settings):
        self.log_dir = getattr(settings, 'query_log_dir', None)
        if self.log_dir:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        self.min_duration = float(
            getattr(settings, 'query_log_min_duration', 0.0))
        self.log_all = bool(
            getattr(settings, 'query_log_all', False))
        self._configured = True

    def __call__(self, event):
        if not self._configured:
            settings = queryUtility(ISettings)
            if settings is not None:
                self.configure(settings)
        if not self.log_dir:
            return
        t = datetime.now().isoformat()
        duration = event.duration
        query = '  ' + pformat(event.query).replace('\n', '\n  ')
        if self.log_all:
            self._log(t, duration, event.result[0], query)
        if duration >= self.min_duration:
            self._log_by_magnitude(t, duration, event.result[0], query)

    def _log(self, ts, duration, num_results, query, fname='everything.log'):
        msg = '%s %8.3f %6d\n%s\n' % (
            ts, duration, num_results, query)
        path = os.path.join(self.log_dir, fname)
        f = open(path, 'a')
        try:
            f.write(msg)
        finally:
            f.close()

    def _log_by_magnitude(self, ts, duration, num_results, query):
        magnitude = math.ceil(math.log(duration, 2))
        fn = '%07d.log' % int(1000 * 2**magnitude)
        self._log(ts, duration, num_results, query, fname=fn)

log_query = QueryLogger()
