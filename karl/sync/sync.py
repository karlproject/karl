import copy

from repoze.folder.interfaces import IFolder
from karl.sync.interfaces import IContentSource
from karl.sync.factory import create_generic_content
from karl.sync.factory import update_generic_content

WING_IDE = False

class Synchronizer(object):
    def __init__(self, source, folder):
        if WING_IDE:
            assert isinstance(source, IContentSource)
        assert IContentSource.providedBy(source)

        self.source = source
        self.folder = folder

    def __call__(self):
        self._import_items(self.folder, self.source.items)

    def _import_items(self, folder, items):
        for item in items:
            self._import_item(folder, item)

    def _import_item(self, folder, item):
        # Add required attributes to attributes dict.  This
        attrs = copy.copy(item.attributes)
        attrs.update(
            created=item.created,
            created_by=item.created_by,
            modified=item.modified,
            modified_by=item.modified_by
            )

        content = _get_prev_content(folder, item)
        if content is not None:
            # Update
            update_generic_content(content, attrs)
        else:
            content = create_generic_content(item.type, attrs)
            folder[item.name] = content

        _content_synced(folder, item, content)

def _get_prev_content(folder, item):
    """
    If content already exists from previous sync, get that content item.  If
    content of same name exists in folder but its sync id doesn't match that
    of previous item, don't return that content.  It will be overwritten rather
    than updated.
    """
    if not hasattr(folder, '_sync_content'):
        folder._sync_content = {}
        return None

    name = folder._sync_content.get(item.id, None)
    if name is None:
        return None

    content = folder.get(name, None)
    if content is None:
        return None

    content_id = getattr(content, '_sync_id', None)
    if content_id != item.id:
        return None

    return content

def _content_synced(folder, item, content):
    """
    Records some history about the sync for reference in later syncs.
    """
    sync_content = getattr(folder, '_sync_content', None)
    if sync_content is None:
        sync_content = {}
    sync_content[item.id] = content.__name__
    folder._sync_content = sync_content

    content._sync_id = item.id
    content._sync_timestamp = item.modified
