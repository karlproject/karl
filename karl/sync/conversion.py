import base64
import datetime
import pytz
import time
import urllib2

from zope.component import queryAdapter
from karl.sync.interfaces import IDataConverter

def convert(raw, type):
    converter = queryAdapter(raw, IDataConverter, type)
    if converter is None:
        converter = _builtin_converters.get(type, None)
        if converter is None:
            raise TypeError("Unable to convert type: %s" % type)
        return converter(raw)
    return converter()

def _parse_date(s):
    # Whoever decided to make strptime not be able to parse simple numeric
    # timezone offsets should be punched in the face.
    s, tzinfo = s[:-6], s[-6:]
    t = time.strptime(s, '%Y-%m-%dT%H:%M:%S')
    tzh, tzm = [int(x) for x in tzinfo.split(':')]
    tz = pytz.FixedOffset(tzh * 60 + tzm)
    tzinfo = dict(tzinfo=tz)
    return datetime.datetime(*t[:6], **tzinfo)

def _boolean(value):
    if value is None:
        return False

    value = value.lower()
    if value in ('t', 'true', 'y', 'yes'):
        return True
    if value in ('f', 'false', 'n', 'no'):
        return False
    try:
        return not not int(value)
    except ValueError:
        raise ValueError("Can't convert to boolean: %s" % value)

class _Blob(object):
    def __init__(self, url):
        self.url = url

    def open(self):
        return urllib2.urlopen(self.url)

class _Clob(object):
    def __init__(self, url):
        self.url = url

    def open(self, encoding='utf-8'):
        # Supposedly codecs.EncodedFile is supposed to be able to wrap a stream
        # and read unicode, but I couldn't get it to work--always returns raw
        # string.
        # This monkey patch is being peformed to replace just the read method
        # with a version that decodes the stream and returns unicode, still
        # allowing access to url.info, in case calling code wants to see http
        # headers or status code.
        def decode_read(read_raw):
            def read(size=-1):
                data = read_raw(size)
                if data:
                    data = unicode(data, encoding)
                return data
            return read

        url = urllib2.urlopen(self.url)
        url.read = decode_read(url.read)
        return url

_builtin_converters = {
    'int': int,
    'float': float,
    'bool': _boolean,
    'bytes': base64.b64decode,
    'text': unicode,
    'timestamp': _parse_date,
    'blob': _Blob,
    'clob': _Clob,
    }
