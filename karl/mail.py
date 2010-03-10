"""
The primary reason to for this module is to extend the functionality of
email.message.Message in order to work around a disagreement with Postfix
about how RFC 2047 compliant headers should be encoded when email addresses
are involved.  I don't have enough information to know who is right, but this
encodes headers in a way that is compatible with Postfix, at least, and should
be understood by any MTU.

The other purpose of this module is to fix a usability issue when using
email.message.Message with RFC 2047.  In the standard library module headers
are not automatically decoded, forcing the calling code to manually call
email.header.decode_header and then manually piece together header values.  In
this author's opinion, this is a silly way to do things.  Users of the Message
class should be able to simply assign and get back unicode values for headers
without having to know about the underlying transfer encoding.  This version
of Message makes unicode headers transparent, simplifying the calling code.
"""
from email.header import decode_header as stdlib_decode_header
from email.header import Header
from email.message import Message as StdlibMessage
from email.mime.multipart import MIMEMultipart as StdlibMIMEMultipart

class Message(StdlibMessage):
    def __setitem__(self, name, value):
        StdlibMessage.__setitem__(self, name, encode_header(name, value))

    def __getitem__(self, name):
        value = StdlibMessage.__getitem__(self, name)
        return decode_header(value)

class MIMEMultipart(StdlibMIMEMultipart):
    def __setitem__(self, name, value):
        StdlibMIMEMultipart.__setitem__(self, name, encode_header(name, value))

    def __getitem__(self, name):
        value = StdlibMIMEMultipart.__getitem__(self, name)
        return decode_header(value)

def encode_header(name, value):
    if value is None:
        return None

    if not isinstance(value, unicode):
        return value

    # If can be encoded as ascii, nothing needs to be done
    try:
        return value.encode('ascii')
    except UnicodeEncodeError:
        pass

    # Needs to be RFC 2047 encoded.  Stdlib impl handles this fine
    # except for the case where header is an email address, in
    # which case it encodes the entire value, both the user's
    # name and their address.  Postfix, however, blows up if
    # the address itself (which is required to be 7bit) is
    # encoded.  So we need to do an end run around the standard
    # library and encode only the name portions of any email
    # addresses that might be in this header.
    if name.lower() in ('to', 'from', 'reply-to', 'cc', 'bcc'):
        addrs = []
        for addr in value.split(','):
            addr = addr.strip()
            lt_index = addr.find('<')
            if lt_index != -1:
                user = addr[:lt_index].strip()
                addr = addr[lt_index:]
                addr = '%s %s' % (
                    str(Header(user)), addr.encode('ascii')
                )
            else:
                addr = addr.encode('ascii')
            addrs.append(addr)
        value = ', '.join(addrs)

    # Non address field, do simple encoding
    else:
        value = str(Header(value))

    return value

def decode_header(value):
    if value is None:
        return None

    parts = []
    for part, encoding in stdlib_decode_header(value):
        if encoding is not None:
            part = part.decode(encoding)
        else:
            part = unicode(part)
        parts.append(part)
    return ' '.join(parts)