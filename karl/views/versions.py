
import datetime
import logging
import re
import time

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.url import resource_url
from sqlalchemy.orm.exc import NoResultFound

from karl.models.interfaces import IContainerVersion
from karl.content.interfaces import ICommunityFile

from karl.models.subscribers import index_content
from karl.utilities.lock import lock_info_for_view
from karl.utils import find_catalog
from karl.utils import find_repo
from karl.utils import find_profiles
from karl.views.api import TemplateAPI
from karl.views.utils import make_unique_name

log = logging.getLogger(__name__)


def show_history(context, request, tz=None):
    repo = find_repo(context)
    profiles = find_profiles(context)

    # downloading files using ajax shows information bar in IE
    # We need to disable that if context is a file
    use_ajax = True
    preview_view = 'preview.html'
    if ICommunityFile.providedBy(context):
        use_ajax = False
        preview_view = 'download_preview'

    def display_record(record):
        editor = profiles[record.user]
        return {
            'date': format_local_date(record.archive_time, tz),
            'editor': {
                'name': editor.title,
                'url': resource_url(editor, request),
                },
            'preview_url': resource_url(
                context, request, preview_view,
                query={'version_num': str(record.version_num)}),
            'restore_url': resource_url(
                context, request, 'revert',
                query={'version_num': str(record.version_num)}),
            'is_current': record.current_version == record.version_num,
        }

    # newest to oldest
    history = map(display_record, repo.history(context.docid))

    page_title = 'History for %s' % context.title

    backto = {
        'href': resource_url(context, request),
        'title': context.title
    }

    return {
        'api': TemplateAPI(context, request, page_title),
        'history': history,
        'use_ajax': use_ajax,
        'backto': backto,
        'lock_info': lock_info_for_view(context, request),
    }


def revert(context, request):
    repo = find_repo(context)
    version_num = int(request.params['version_num'])
    for version in repo.history(context.docid):
        if version.version_num == version_num:
            break
    else:
        raise ValueError('No such version: %d' % version_num)
    context.revert(version)
    repo.reverted(context.docid, version_num)
    catalog = find_catalog(context)
    catalog.reindex_doc(context.docid, context)
    return HTTPFound(location=resource_url(context, request))


def decode_trash_path(s):
    """Decode a string into a trash path (a list of (name, docid) pairs).

    Unlike normal paths, a trash path can descend into deleted containers
    and deleted items. The docid of each path segment can be None, causing
    the path to be ambiguous but still useful.
    """
    res = []
    for part in s.split('/'):
        mo = re.match(r'{([0-9\-]+)}(.+)', part)
        if mo is not None:
            # docid specified.
            res.append((mo.group(2), int(mo.group(1))))
        else:
            # No docid specified.
            res.append((part, None))
    return res


def encode_trash_path(path):
    """Encode a trash path as a string."""
    parts = []
    for name, docid in path:
        if docid is not None:
            parts.append('{%d}%s' % (docid, name))
        else:
            parts.append(name)
    return '/'.join(parts)


def traverse_trash(context, path):
    """Yield (name, docid, deleted_item or None) for elements in a trash path.

    A trash path is a list of (name, docid) pairs. The docid of each path
    segment can be None, causing the path to be ambiguous; this function
    will react by choosing the first match it finds.

    Raises ValueError if an element of the path is not found or is not
    valid. The ValueError may indicate a security violation attempt,
    since invalid trash paths could be a way to expose sensitive info.
    """
    repo = find_repo(context)
    container_id = context.docid
    for name, docid in path:
        try:
            contents = repo.container_contents(container_id)
        except NoResultFound:
            raise ValueError("Document %d is not a container." % container_id)

        if docid is not None:
            docid = int(docid)
        else:
            docid = contents.map.get(name)

        if contents.map.get(name) == docid:
            yield name, docid, None
            container_id = docid
            continue

        for item in contents.deleted:
            if (item.name == name
                    and (docid is None or item.docid == docid)
                    and not item.new_container_ids):
                yield name, item.docid, item
                container_id = item.docid
                break
        else:
            raise ValueError("Subfolder not found in trash: %s (docid %s)"
                % (name, docid))


class ShowTrash(object):
    """View that shows one folder of trash."""

    def __init__(self, context, request, tz=None):
        self.context = context
        self.request = request
        self.tz = tz
        self.repo = find_repo(context)
        self.profiles = find_profiles(context)
        self.deleted_branch = None
        self.container_id = context.docid
        self.error = None
        self.deleted = []
        self.subfolder_path = []

        subfolder = self.request.params.get('subfolder')
        if subfolder:
            try:
                path = decode_trash_path(subfolder)
                for name, container_id, deleted_item in traverse_trash(
                        self.context, path):
                    if deleted_item is not None:
                        self.deleted_branch = deleted_item
                    self.container_id = container_id
                    self.subfolder_path.append((name, container_id))
            except (ValueError, TypeError), e:
                log.exception("Invalid trash subfolder: %s", subfolder)
                self.error = e

    def __call__(self):
        tapi = TemplateAPI(self.context, self.request, 'Trash')
        if self.error is None:
            self.fill_deleted()
        else:
            tapi.set_status_message(unicode(self.error))
        return {'api': tapi, 'deleted': self.deleted}

    def fill_deleted(self):
        """Fill self.deleted."""
        try:
            contents = self.repo.container_contents(self.container_id)
        except NoResultFound:
            # Not a container.
            return

        # Show items deleted (but not moved) from this container.
        contents_deleted = contents.deleted
        container_ids = set(self.repo.filter_container_ids(
            item.docid for item in contents_deleted))
        for item in contents_deleted:
            if item.new_container_ids:
                continue
            is_container = item.docid in container_ids
            self.add(item.name, item.docid, item, is_container)

        if self.deleted_branch is not None:
            # This container has been deleted, so show
            # all items in this container as deleted items.
            container_ids = set(self.repo.filter_container_ids(
                contents.map.values()))
            for name, docid in contents.map.items():
                is_container = docid in container_ids
                self.add(name, docid, self.deleted_branch, is_container)

        else:
            # Show child containers that contain something deleted.
            which_contain_deleted = set(
                self.repo.which_contain_deleted(contents.map.values()))
            for name, docid in contents.map.items():
                if docid in which_contain_deleted:
                    self.add(name, docid, None, True)

        self.deleted.sort(key=lambda x: x['title'])

    def add(self, name, docid, deleted_item, is_container):
        """Add an item to self.deleted."""
        version = self.repo.history(docid, only_current=True)[0]
        item_path = encode_trash_path(self.subfolder_path + [(name, docid)])

        if is_container:
            url = resource_url(self.context, self.request, 'trash', query={
                'subfolder': item_path})
        else:
            url = None

        if deleted_item is not None:
            deleted_by = self.profiles[deleted_item.deleted_by]
            self.deleted.append({
                'date': format_local_date(deleted_item.deleted_time, self.tz),
                'deleted_by': {
                    'name': deleted_by.title,
                    'url': resource_url(deleted_by, self.request),
                },
                'restore_url': resource_url(
                    self.context, self.request, 'restore',
                    query={'path': item_path}),
                'title': version.title,
                'url': url,
            })
        else:
            self.deleted.append({
                'date': None,
                'deleted_by': None,
                'restore_url': None,
                'title': version.title,
                'url': url,
            })


def _restore(repo, parent, docid, name):
    version = repo.history(docid, only_current=True)[0]
    doc = version.klass()
    doc.revert(version)

    if name in parent:
        # Choose a non-conflicting name to restore to. (LP #821206)
        name = make_unique_name(parent, name)

    parent.add(name, doc, send_events=False)
    return doc


def _restore_subtree(repo, parent, request):
    try:
        contents = repo.container_contents(parent.docid)
    except NoResultFound:
        pass
    else:
        for child_name, child_docid in contents.map.items():
            doc = _restore(repo, parent, child_docid, child_name)
            _restore_subtree(repo, doc, request)
        repo.archive_container(IContainerVersion(parent),
                               authenticated_userid(request))
    index_content(parent, None)


def undelete(context, request):
    repo = find_repo(context)
    path = decode_trash_path(request.params['path'])
    parent = context
    for name, docid, _ in traverse_trash(context, path):
        try:
            doc = parent[name]
        except KeyError:
            doc = None
        if doc is None or doc.docid != docid:
            # Restore this item.
            doc = _restore(repo, parent, docid, name)
            repo.archive_container(IContainerVersion(parent),
                                   authenticated_userid(request))
            index_content(parent, None)
        parent = doc

    # If the user undeleted a container, restore everything it contained.
    _restore_subtree(repo, parent, request)

    return HTTPFound(location=resource_url(parent, request))

epoch = datetime.datetime.utcfromtimestamp(0)

def format_local_date(date, tz=None, time_module=time):
    """Format a UTC datetime for the local time zone."""
    # time_module is a testing hook.
    if tz is None:
        if not time_module.daylight:
            # DST does not apply to the local time zone.
            tz = time_module.timezone
        else:
            # Figure out whether DST applied on the given date in the
            # local time zone.
            delta = date - epoch
            seconds = delta.days * 86400 + delta.seconds
            struct_time = time_module.localtime(seconds)
            if struct_time.tm_isdst:
                tz = time_module.altzone
            else:
                tz = time_module.timezone

    local = date - datetime.timedelta(seconds=tz)
    return local.strftime('%Y-%m-%d %H:%M')
