from schemaish.attr import DateTime

class KarlDateTime(DateTime):
    """
    Empty subclass.  Exists only so we can register our own converter
    that uses a different string format.
    """
    type = 'KarlDateTime'
