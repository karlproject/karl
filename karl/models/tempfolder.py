import datetime
import uuid

from zope.interface import implements

from repoze.folder import Folder

from repoze.bfg.authorization import Allow
from repoze.bfg.authorization import Everyone

from karl.models.interfaces import ITempFolder

class TempFolder(Folder):
    """
    Container for temporarily storing content.

    Might eventually have other uses, but this was created to support the
    Image Drawer case where a user is uploading an image that is to be attached
    to a piece of content that hasn't been created yet, such as when filling
    out a create form.
    """
    implements(ITempFolder)

    __acl__ = [(Allow, Everyone, ('view',)),]
    LIFESPAN = datetime.timedelta(hours=24)
    title = 'Temporary Folder'

    def add_document(self, doc):
        name = str(uuid.uuid4())  # Random uuid.
        self[name] = doc

    def cleanup(self):
        now = datetime.datetime.now()
        for name, doc in self.items():
            if now - doc.modified > self.LIFESPAN:
                del self[name]

