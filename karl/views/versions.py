from collections import deque
import datetime
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
import json


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


def traverse_subfolders(context, subfolder_path):
    """Yield (docid, exists) for each element in a JSON subfolder path.

    Raises ValueError if the path is not valid.
    """
    if not subfolder_path:
        return

    repo = find_repo(context)
    parts = json.loads(subfolder_path)  # May raise ValueError
    container_id = context.docid

    for name, docid in parts:
        docid = int(docid)
        try:
            contents = repo.container_contents(container_id)
        except NoResultFound:
            raise ValueError("Document %d is not a container." % container_id)
        if contents.map.get(name) == docid:
            yield docid, True
            container_id = docid
            continue

        for item in contents.deleted:
            if item.name == name and item.docid == docid:
                yield docid, False
                break
        else:
            raise ValueError("Subfolder %s (docid %d) not found in trash."
                % (repr(name), docid))


def get_subfolder_id(context, subfolder_path):
    docid = context.docid
    for docid, _exists in traverse_subfolders(context, subfolder_path):
        pass
    return docid


def show_trash(context, request, tz=None):
    repo = find_repo(context)
    profiles = find_profiles(context)

    def display_deleted_item(docid, deleted_item, is_container):
        version = repo.history(docid, only_current=True)[0]
        if is_container:
            url = resource_url(context, request, 'trash', query={
                'subfolder': str(docid)})
        else:
            url = None
        if deleted_item:
            deleted_by = profiles[deleted_item.deleted_by]
            return {
                'date': format_local_date(deleted_item.deleted_time, tz),
                'deleted_by': {
                    'name': deleted_by.title,
                    'url': resource_url(deleted_by, request),
                    },
                'restore_url': resource_url(
                    context, request, 'restore',
                    query={'docid': str(deleted_item.docid),
                           'name': deleted_item.name}),
                'title': version.title,
                'url': url}
        else:
            return {
                'date': None,
                'deleted_by': None,
                'restore_url': None,
                'title': version.title,
                'url': url}

    subfolder = request.params.get('subfolder')
    if not subfolder:
        subfolder = context.docid

    contents = repo.container_contents(subfolder)
    deleted = []

    contents_deleted = contents.deleted
    deleted_container_children = set(repo.filter_container_ids(
        item.docid for item in contents_deleted))
    for item in contents_deleted:
        is_container = item.docid in deleted_container_children
        deleted.append(display_deleted_item(item.docid, item, is_container))

    for docid in repo.which_contain_deleted(contents.map.values()):
        deleted.append(display_deleted_item(docid, None, True))

    deleted.sort(key=lambda x: x['title'])

    return {
        'api': TemplateAPI(context, request, 'Trash'),
        'deleted': deleted,
    }


def generate_trash_tree(repo, docid):

    # Download the container hierarchy all at once.
    hierarchy = dict((contents.container_id, contents) for contents in
        repo.iter_hierarchy(docid, follow_deleted=True))

    class FakeDeletedItem(object):
        """
        Show descendents of deleted folders as having been deleted themselves
        in trash UI.
        """
        def __init__(self, docid, deleted_branch):
            self.docid = docid
            self.name = deleted_branch.name
            self.deleted_by = deleted_branch.deleted_by
            self.deleted_time = deleted_branch.deleted_time

    class TreeNode(dict):
        deleted_item = None
        paths = None

        def find(self, docid):
            node = self
            for child_docid in self.paths[docid]:
                node = node[child_docid]
            return node

    paths = {}

    def add_item_to_tree(deleted_item, path, tree):
        node = tree
        for node_docid in path:
            next_node = node.get(node_docid)
            if next_node is None:
                node[node_docid] = next_node = TreeNode()
            node = next_node
        node.deleted_item = deleted_item

    def visit(docid, path, tree, deleted_branch=None):
        paths[docid] = tuple(path)
        contents = hierarchy.get(docid)
        if contents is None:
            return

        for deleted_item in contents.deleted:
            if deleted_item.new_container_ids:
                continue

            path.append(deleted_item.docid)
            add_item_to_tree(deleted_item, path, tree)
            visit(deleted_item.docid, path, tree, deleted_item)
            path.pop()

        for child_docid in contents.map.values():
            path.append(child_docid)
            if deleted_branch:
                add_item_to_tree(FakeDeletedItem(child_docid, deleted_branch),
                                 path, tree)
            visit(child_docid, path, tree, deleted_branch)
            path.pop()

    trash = TreeNode()
    visit(docid, deque(), trash)
    trash.paths = paths
    return trash


def _undelete(repo, parent, docid, name, restore_children):
    version = repo.history(docid, only_current=True)[0]
    doc = version.klass()
    doc.revert(version)

    if restore_children:
        try:
            container = repo.container_contents(docid)
        except NoResultFound:
            container = None

        if container is not None:
            for child_name, child_docid in container.map.items():
                _undelete(repo, doc, child_docid, child_name, True)

    if name in parent:
        # Choose a non-conflicting name to restore to. (LP #821206)
        name = make_unique_name(parent, name)

    parent.add(name, doc, send_events=False)
    return doc


def undelete(context, request):
    repo = find_repo(context)
    docid = int(request.params['docid'])
    name = request.params['name']

    # Find parent folder to restore file into
    trash = generate_trash_tree(repo, context.docid)
    parent = context
    for child_docid in trash.paths[docid][:-1]:
        for child in parent.values():
            if child.docid == child_docid:
                next_parent = child
                break
        else:
            # Need to restore a folder in order to place file in proper place
            # in tree.
            container = repo.container_contents(parent.docid)
            for deleted_item in container.deleted:
                if deleted_item.docid == child_docid:
                    next_parent = _undelete(repo, parent, child_docid,
                                            deleted_item.name, False)
                    repo.archive_container(IContainerVersion(parent),
                                           authenticated_userid(request))
                    break
            else: #pragma NO COVERAGE
                # Will only get here in case of programmer error or db
                # corruption (due to programmer error)
                raise RuntimeError("Cannot find container to restore: %d" %
                                   child_docid)
        parent = next_parent

    doc = _undelete(repo, parent, docid, name, True)
    repo.archive_container(IContainerVersion(parent),
                           authenticated_userid(request))
    index_content(parent, None)
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
