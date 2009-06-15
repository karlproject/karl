from webob import Response
from karl.models.interfaces import IFile

# XXX Todo: implement If-modified-since headers and 304 responses.

def serve_file_view(context, request):
    assert IFile.providedBy(context)
    
    headers = [
        ("Content-Type", context.mimetype),
        ("Content-Length", str(context.size)),
    ]
    
    return Response(
        headerlist=headers,
        app_iter=StreamIterator(context.stream)
    )

CHUNK_SIZE = 1<<16
class StreamIterator(object):
    def __init__(self, stream):
        self.stream = stream
        
    def __iter__(self):
        return self
    
    def next(self):
        chunk = self.stream.read(CHUNK_SIZE)
        if len(chunk) == 0:
            raise StopIteration
        return chunk
    