from email.utils import getaddresses
import re
from zope.interface import implements
from zope.component import getUtility
from karl.adapters.interfaces import IMailinDispatcher
from karl.utilities.interfaces import IMailinTextScrubber
from karl.utils import find_communities
from karl.utils import find_profiles

REPLY_REGX = re.compile(r'(?P<community>\w+(-\w+)*)\+(?P<tool>\w+)'
                         '-(?P<reply>\w+)@')
TOOL_REGX = re.compile(r'(?P<community>\w+(-\w+)*)\+(?P<tool>\w+)@')

class MailinDispatcher(object):
    implements(IMailinDispatcher)
    default_tool = None
    text_scrubber = None

    def __init__(self, context):
        self.context = context

    def getAddrList(self, message, name):
        """ See IMailinDispatcher.
        """
        addrs = message.get_all(name)
        if addrs is None:
            return []
        return getaddresses(addrs)

    def isCommunity(self, name):
        """ See IMailinDispatcher.
        """
        return name in find_communities(self.context)

    def getCommunityId(self, email):
        """ See IMailinDispatcher.
        """
        community_id = email.split('@',1)[0]
        if self.isCommunity(community_id):
            return community_id

    def getAuthor(self, email):
        """ See IMailinDispatcher.
        """
        profiles = find_profiles(self.context)
        profile = profiles.getProfileByEmail(email)
        if profile is not None:
            return profile.__name__

    def getMessageTarget(self, message):
        """Return a mapping describing the target of a message.

        The mapping will contain 'community', 'tool', and 'in_reply_to'.
        It will also contain 'to' for debugging purposes.  It will
        contain 'error' if the target can not be identified.
        """
        info = {
            'community': None,
            'tool': self.default_tool,
            'in_reply_to': None,
            }

        to = self.getAddrList(message, 'To')
        info['to'] = to
        cc = self.getAddrList(message, 'Cc')

        for realname, email in to + cc:

            match = REPLY_REGX.search(email)
            if match:
                community = match.group('community')
                info['community'] = community
                info['tool'] = match.group('tool')
                info['in_reply_to'] = match.group('reply')
                if not self.isCommunity(community):
                    info['error'] = 'invalid community: %s' % community
                return info

            match = TOOL_REGX.search(email)
            if match:
                community = match.group('community')
                info['community'] = community
                info['tool'] = match.group('tool')
                if not self.isCommunity(community):
                    info['error'] = 'invalid community: %s' % community
                return info

            community = self.getCommunityId(email)
            if community is not None:
                info['community'] = community
                return info

        info['error'] = 'no community specified'
        return info

    def getMessageAuthorAndSubject(self, message):
        """Return a mapping describing the author and subject of a message.

        If there is no error, the mapping will contain 'author' (a
        profile ID) and 'subject'.  It will also contain 'from' for
        debugging purposes.

        If an error occurs, the mapping will contain 'error' and
        may contain 'from', 'author', and 'subject'.
        """
        info = {}

        fromaddrs = self.getAddrList(message, 'From')
        if len(fromaddrs) == 0:
            info['error'] = 'missing From:'
            return info

        if len(fromaddrs) > 1:
            info['error'] = 'multiple From:'
            return info

        info['from'] = fromaddrs

        realname, email = fromaddrs[0]

        author = self.getAuthor(email)
        if not author:
            info['error'] = 'author not found'
            return info

        info['author'] = author

        subject = message['Subject']
        if not subject:
            info['error'] = 'missing Subject:'
            return info

        info['subject'] = subject

        return info

    def getAutomationIndicators(self, message):
        """Look for headers that indicate automated email.

        If the message appears to be automated rather than written
        by a person, this method returns a mapping containing 'error'.
        Otherwise an empty mapping is returned.
        """
        info = {}
        # Like Mailman, if a message has "Precedence: bulk|junk|list",
        # discard it.  The Precedence header is non-standard, yet
        # widely supported.
        precedence = message.get('Precedence', '').lower()
        if precedence in ('bulk', 'junk', 'list'):
            info['error'] = 'Precedence: %s' % precedence
            return info

        # rfc3834 is the standard way to discard automated responses, but
        # it is not yet widely supported.
        auto_submitted = message.get('Auto-Submitted', '').lower()
        if auto_submitted.startswith('auto'):
            info['error'] = 'Auto-Submitted: %s' % auto_submitted
            return info

        subject_lower = message.get('Subject', '').lower()
        if 'autoreply' in subject_lower or 'out of office' in subject_lower:
            info['error'] = 'vacation message'
            return info

        return info

    def crackHeaders(self, message):
        """ See IMailinDispatcher.
        """
        # First, get all necessary info for addressing a community.
        # This is important for allowing moderators to see all email
        # addressed to their community, even if some email can't be
        # posted for other reasons.
        info = self.getMessageTarget(message)
        if info.get('error'):
            return info

        # Next, add the necessary info for creating an object from the
        # message.
        info.update(self.getMessageAuthorAndSubject(message))
        if info.get('error'):
            return info

        # Finally, look for issues that a moderator can choose to ignore.
        info.update(self.getAutomationIndicators(message))

        return info

    def crackPayload(self, message):
        """ See IMailinDispatcher.
        """
        text = None
        text_mimetype = None
        attachments = []

        for part in message.walk():
            filename = part.get_filename()
            mimetype = part.get_content_type()
            data = part.get_payload(decode=1)
            if mimetype.startswith('text/'):
                charset = part.get_content_charset() or 'utf-8'
                try:
                    data = data.decode(charset)
                except UnicodeDecodeError:
                    # At this point we've run out of options in terms of
                    # determining what the character encoding of this text
                    # might be.  We will decode as though it is latin-1--if
                    # the character encoding is not actually latin-1, some of
                    # the characters will be mistranslated, but we at least
                    # avoid a show-stopping UnicodeDecodeError.
                    data = data.decode('latin-1')

            if filename is not None:
                attachments.append((filename, mimetype, data))
            elif text is None and mimetype.startswith('text/plain'):
                text = data
                text_mimetype = mimetype

        if text is not None and self.text_scrubber is not None:
            scrubber = getUtility(IMailinTextScrubber, self.text_scrubber)
            text = scrubber(text, text_mimetype)

        if text is None:
            text = ("Message body not found.  Incoming email message must "
                    "contain a plain text representation.  HTML-only email "
                    "is not supported.")

        return text, attachments
