from persistent import Persistent

class ImageFile(Persistent): #pragma NO COVERAGE
    """ Deprecated.  Placeholder for migration.  Can be removed once all
        Karl instances have evolved to rev 10.
    """
    def __init__(self, stream, mimetype,):
        raise NotImplementedError()


