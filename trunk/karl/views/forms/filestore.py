from ZODB.blob import Blob
from persistent.mapping import PersistentMapping
from karl.utils import get_session

class ZODBFileStore(object):
    """ Tempfile store for formish upload widgets """
    def __init__(self, persistent_map):
        self.persistent_map = persistent_map

    def get(self, key):
        headers = []
        cache_tag = None
        blobfile = None
        result = self.persistent_map.get(key)
        if result is not None:
            headers, cache_tag, blobfile = result
            blobfile = blobfile.open('r')
        return (cache_tag, headers, blobfile)

    def put(self, key, src, cache_tag, headers=()):
        blobfile = Blob()
        self.persistent_map[key] = (headers, cache_tag, blobfile)
        f = blobfile.open('w')
        size = 0
        while 1:
            data = src.read(1<<21)
            if not data:
                break
            size += len(data)
            f.write(data)
        f.close()

    def delete(self, key, glob=False):
        del self.persistent_map[key]

    def clear(self):
        self.persistent_map.clear()

def get_filestore(context, request, form_id):
    session = get_session(context, request)
    mapping = session.get(form_id)
    if mapping is None:
        session[form_id] = PersistentMapping()
        mapping = session[form_id]
    filestore = ZODBFileStore(mapping)
    return filestore

