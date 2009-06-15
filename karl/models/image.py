from persistent import Persistent
from ZODB.blob import Blob

from zope.interface import implements

from karl.models.interfaces import IImageFile

extensions = {
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/png": "png",
}

# Convert types sent by IE to standard types
ie_types = {
    "image/x-png": "image/png",
    "image/pjpeg": "image/jpeg",
}

mimetypes = extensions.keys() + ie_types.keys()

class ImageFile(Persistent):
    implements(IImageFile)

    def __init__(self, stream, mimetype,):
        self._set_mimetype(mimetype)
        self.blobfile = Blob()
        self.upload(stream)
        
    def upload(self, stream):
        f = self.blobfile.open('w')
        size = upload_stream(stream, f)
        f.close()
        self.size = size
        
    @property
    def extension(self):
        return extensions.get(self.mimetype)
    
    @property
    def stream(self):
        return self.blobfile.open("r")

    def _set_mimetype(self, mimetype):
        if mimetype in ie_types:
            mimetype = ie_types[mimetype]

        if mimetype not in extensions:
            raise ValueError("Unsupported mime type: %s" % mimetype)
        
        self._mimetype = mimetype
        
    def _get_mimetype(self):
        # Upgrade old versions in zodb that used plain mimetype attribute
        if self.__dict__.has_key("mimetype"):
            self._mimetype = self.__dict__.pop("mimetype")
        return self._mimetype
    
    mimetype = property(_get_mimetype, _set_mimetype)
    
def upload_stream(stream, file):
    size = 0
    while 1:
        data = stream.read(1<<21)
        if not data:
            break
        size += len(data)
        file.write(data)
    return size