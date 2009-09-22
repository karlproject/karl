import copy

from repoze.folder.interfaces import IFolder
from karl.sync.interfaces import IContentSource
from karl.sync.factory import create_generic_content

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
        attrs = copy.copy(item.attributes)
        attrs.update(
            created=item.created,
            created_by=item.created_by,
            modified=item.modified,
            modified_by=item.modified_by
            )

        content = create_generic_content(item.type, attrs)
        folder[item.name] = content
