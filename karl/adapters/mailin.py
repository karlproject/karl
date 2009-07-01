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

    def crackHeaders(self, message):
        """ See IMailinDispatcher.
        """
        info = {'bounce': True,
                'tool': self.default_tool,
                'in_reply_to': None,
               }

        to = self.getAddrList(message, 'To')
        if not to:
            info['reason'] = 'missing To:'
            return info

        info['to'] = to

        fromaddrs = self.getAddrList(message, 'From')
        if len(fromaddrs) == 0:
            info['reason'] = 'missing From:'
            return info

        if len(fromaddrs) > 1:
            info['reason'] = 'multiple From:'
            return info

        info['from'] = fromaddrs

        subject = message['Subject']
        if not subject:
            info['reason'] = 'missing Subject:'
            return info

        info['subject'] = subject

        subject_lower = subject.lower()
        if 'autoreply' in subject_lower or 'out of office' in subject_lower:
            info['reason'] = 'vacation message'
            return info

        realname, email = fromaddrs[0]

        author = self.getAuthor(email)
        if not author:
            info['reason'] = 'author not found'
            return info

        info['author'] = author

        cc = self.getAddrList(message, 'Cc')
        for realname, email in to + cc:

            match = REPLY_REGX.search(email)
            if match:
                community = info['community'] = match.group('community')
                info['tool'] = match.group('tool')
                info['in_reply_to'] = match.group('reply')
                if not self.isCommunity(community):
                    info['reason'] = 'invalid community: %s' % community
                else:
                    info['bounce'] = False
                return info

            match = TOOL_REGX.search(email)
            if match:
                community = info['community'] = match.group('community')
                info['tool'] = match.group('tool')
                if not self.isCommunity(community):
                    info['reason'] = 'invalid community: %s' % community
                # XXX ACL check
                else:
                    info['bounce'] = False

                return info

            community = info['community'] = self.getCommunityId(email)
            if community is not None:  # validity checked in 'getCommunityId'
                # XXX ACL check
                info['bounce'] = False
                return info

        info['reason'] =  'no community'
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
                data = data.decode(charset)
            if filename is not None:
                attachments.append((filename, mimetype, data))
            elif text is None and mimetype.startswith('text/plain'):
                text = data
                text_mimetype = mimetype

        if text is not None and self.text_scrubber is not None:
            scrubber = getUtility(IMailinTextScrubber, self.text_scrubber)
            text = scrubber(text, text_mimetype)
        return text, attachments
