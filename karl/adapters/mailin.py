# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
import datetime
import time
from email.utils import getaddresses
from email.utils import parsedate

import re

from repoze.bfg.security import has_permission
from repoze.bfg.traversal import find_model
from repoze.postoffice.message import decode_header
from zope.component import getUtility
from zope.interface import implements
import webob

from karl.adapters.interfaces import IMailinDispatcher
from karl.utilities.interfaces import IMailinTextScrubber
from karl.utils import find_communities
from karl.utils import find_peopledirectory
from karl.utils import find_profiles
from karl.utils import find_root
from karl.utils import find_users
from karl.utils import get_setting

REPORT_REPLY_REGX = re.compile(r'peopledir-'
                                '(?P<report>\w+(\+\w+)*)'
                                '-(?P<reply>\w+)@')

REPORT_REGX = re.compile(r'peopledir-'
                          '(?P<report>\w+(\+\w+)*)')

REPLY_REGX = re.compile(r'(?P<community>[^+]+)\+(?P<tool>\w+)'
                         '-(?P<reply>\w+)@')

TOOL_REGX = re.compile(r'(?P<community>[^+]+)\+(?P<tool>\w+)@')

ALIAS_REGX = None
def _get_ALIAS_REGX(context):
    global ALIAS_REGX
    if ALIAS_REGX is None:
        subdomain = get_setting(context, "system_list_subdomain", None)
        if subdomain is not None:
            ALIAS_REGX = re.compile(r'(?P<alias>.*)@%s' % subdomain)
        else:
            ALIAS_REGX = re.compile(r'(?P<alias>.*)@')
    return ALIAS_REGX

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
        addrs = map(decode_header, addrs)
        return getaddresses(addrs)

    def isCommunity(self, name):
        """ See IMailinDispatcher.
        """
        return name in find_communities(self.context)

    def isReport(self, name):
        """ See IMailinDispatcher.
        """
        root = find_root(self.context)
        if name in root.list_aliases:
            return True
        pd = find_peopledirectory(self.context)
        tokens = name.split('+')
        try:
            find_model(pd, tokens)
        except KeyError:
            return False
        return True

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

    def getMessageTargets(self, message):
        """Return a mapping describing the target(s) of a message.

        The mapping will contain 'targets', which in turn is a sequence of
        target mappings containing 'report', 'community', 'tool',
        'in_reply_to'. Each target mapping will also contain 'to' for
        debugging purposes and will contain 'error' if the to address lookied
        like it should have matched but a target couldn't be found.  The top
        level mapping will contain 'error' if no targets could be found.
        """
        targets = []
        to = self.getAddrList(message, 'To')
        to = to + self.getAddrList(message, 'Cc')
        info = {
            'to': to,
            'targets': targets,
        }

        for realname, email in to:
            target = {
                'report': None,
                'community': None,
                'tool': self.default_tool,
                'in_reply_to': None,
                'to': (realname, email),
            }

            match = REPORT_REPLY_REGX.search(email)
            if match:
                report = match.group('report')
                target['report'] = report
                target['in_reply_to'] = match.group('reply')
                if not self.isReport(report):
                    target['error'] = 'invalid report: %s' % report
                targets.append(target)
                continue

            match = REPORT_REGX.search(email)
            if match:
                report = match.group('report')
                target['report'] = report
                if not self.isReport(report):
                    target['error'] = 'invalid report: %s' % report
                targets.append(target)
                continue

            match = _get_ALIAS_REGX(self.context).search(email)
            if match:
                alias = match.group('alias')
                path = self.context.list_aliases.get(alias)
                if path is not None:
                    elements = path.split('/')
                    if elements[0:2] == ['', 'people']:
                        target['report'] = '+'.join(elements[2:])
                        targets.append(target)
                        continue

            match = REPLY_REGX.search(email)
            if match:
                community = match.group('community')
                target['community'] = community
                target['tool'] = match.group('tool')
                target['in_reply_to'] = match.group('reply')
                if not self.isCommunity(community):
                    target['error'] = 'invalid community: %s' % community
                targets.append(target)
                continue

            match = TOOL_REGX.search(email)
            if match:
                community = match.group('community')
                target['community'] = community
                target['tool'] = match.group('tool')
                if not self.isCommunity(community):
                    target['error'] = 'invalid community: %s' % community
                targets.append(target)
                continue

            community = self.getCommunityId(email)
            if community is not None:
                target['community'] = community
                targets.append(target)
                continue

        good_targets = [target for target in targets if 'error' not in target]
        if not good_targets:
            info['error'] = 'no community or distribution list specified'
        return info

    def getMessageAuthorAndSubject(self, message):
        """ Return a mapping describing the author and subject of a message.

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

        subject = decode_header(message['Subject'])
        if not subject:
            info['error'] = 'missing Subject:'
            return info

        info['subject'] = subject

        return info

    def getAutomationIndicators(self, message):
        """ Look for headers that indicate automated email.

        If the message appears to be automated rather than written
        by a person, this method returns a mapping containing 'error'.
        Otherwise an empty mapping is returned.
        """
        info = {}
        # Like Mailman, if a message has "Precedence: bulk|junk|list",
        # discard it.  The Precedence header is non-standard, yet
        # widely supported.
        precedence = decode_header(message.get('Precedence', '')).lower()
        if precedence in ('bulk', 'junk', 'list'):
            info['error'] = 'Precedence: %s' % precedence
            return info

        # rfc3834 is the standard way to discard automated responses, but
        # it is not yet widely supported.
        auto_submitted = decode_header(
            message.get('Auto-Submitted', '')).lower()
        if auto_submitted.startswith('auto'):
            info['error'] = 'Auto-Submitted: %s' % auto_submitted
            return info

        subject_lower = decode_header(message.get('Subject', '')).lower()
        if 'autoreply' in subject_lower or 'out of office' in subject_lower:
            info['error'] = 'vacation message'
            return info

        return info

    def checkPermission(self, info):
        """ Does user have permission to author content in the given context?

        Uses ACL security policy to test.
        """
        users = find_users(self.context)
        for target in info['targets']:
            if 'error' in target:
                continue
            report_name = target.get('report')
            if report_name is not None:
                pd = find_peopledirectory(self.context)
                context = find_model(pd, report_name.split('+'))
                permission = "email"
            else:
                communities = find_communities(self.context)
                community = communities[target['community']]
                context = community[target['tool']]
                permission = "create"   # XXX In theory could depend on target
            user = users.get_by_id(info['author'])
            if user is not None:
                user = dict(user)
                user['repoze.who.userid'] = info['author']

            # BFG Security API always assumes http request, so we fabricate a
            # fake request.
            request = webob.Request.blank('/')
            request.environ['repoze.who.identity'] = user

            if not has_permission(permission, context, request):
                target['error'] = 'Permission Denied'

    def crackHeaders(self, message):
        """ See IMailinDispatcher.
        """
        info = {}

        # Crack the date
        datestr = message['Date']
        if datestr:
            # Per usual, the email module is broken. The documentation asserts
            # that the tuple returned by parsedate is suitable for passing to
            # time.mktime, but parsedate returns a time in GMT and time.mktime
            # assumes a local time. There is no GMT equivalent to time.mktime
            # in the time module, so we just manually subtract the timezone
            # offset from the result of time.mktime.
            timestamp = time.mktime(parsedate(datestr)) - time.timezone
            timetuple = time.localtime(timestamp)
            info['date'] = datetime.datetime(*timetuple[:6])
        else:
            info['date'] = datetime.datetime.now()

        # Get all necessary info for addressing a community. This is important
        # for allowing moderators to see all email addressed to their
        # community, even if some email can't be posted for other reasons.
        info.update(self.getMessageTargets(message))
        if info.get('error'):
            return info

        # Next, add the necessary info for creating an object from the
        # message.
        info.update(self.getMessageAuthorAndSubject(message))
        if info.get('error'):
            return info

        # Check that author has permission to create content in the target
        self.checkPermission(info)
        good_targets = [t for t in info['targets'] if 'error' not in t]
        if not good_targets:
            return info

        # Look for issues that a moderator can choose to ignore.
        info.update(self.getAutomationIndicators(message))

        return info

    def crackPayload(self, message):
        """ See IMailinDispatcher.
        """
        texts = []
        attachments = []

        for part in message.walk():
            filename = part.get_filename()
            mimetype = part.get_content_type()
            data = part.get_payload(decode=1)
            if not data:
                # Parts with no payload are containers, for example, the
                # message part of a forwarded message, which in turn contains
                # text parts and possibly its own attachments.
                continue

            if mimetype.startswith('text/'):
                charset = part.get_content_charset() or 'utf-8'
                data = self._decode_messsage_body(data, charset)
            if filename is not None:
                attachments.append((filename, mimetype, data))
            elif mimetype.startswith('text/plain'):
                texts.append(data)
                text_mimetype = mimetype

        if texts:
            text = '\n\n'.join(texts)
            if self.text_scrubber is not None:
                scrubber = getUtility(IMailinTextScrubber, self.text_scrubber)
                is_reply = not not message.get('In-Reply-To')
                text = scrubber(text, 'text/plain', is_reply)

        else:
            text = ("Message body not found.  Incoming email message must "
                    "contain a plain text representation.  HTML-only email "
                    "is not supported.")

        return text, attachments

    def _decode_messsage_body(self, body, charset):
        try:
            return body.decode(charset)
        except (LookupError, UnicodeDecodeError):
            pass

        # We know of at least one case where a mail client is sending us
        # messages using the 'windows-874' encoding which is not in Python's
        # database of character encodings. Some research, however, shows that
        # 'windows-874' is the same encoding as 'cp874', which is an encoding
        # that Python knows about. Here, since we know we don't know the
        # character encoding, we attempt to apply a general rule where
        # 'windows-XXX' is turned into 'cpXXX'. Although we don't know that
        # every windows-XXX encoding is exactly equivalent to it's 'cpXXX'
        # counterpart, it's likely they will be very close and will translate
        # almost every character correctly. To the extent that their may be
        # mistranslations, the end result will still probably be readable and
        # is better than simply throwing the message away as undecodable.
        if charset.startswith('windows-'):
            charset = charset.replace('windows-', 'cp')
            try:
                return body.decode(charset)
            except (LookupError, UnicodeDecodeError):
                pass


        # Try UTF-8 if we haven't already
        if charset.lower().replace('-', '') != 'utf8':
            try:
                return body.decode('UTF-8')
            except UnicodeDecodeError:
                pass

        # As a last resort, decode as 'latin-1'.  This guarantees that every
        # character will be translated as something.  Characters outside of the
        # ASCII range may wind up getting mistranslated, but it is better to
        # show the user something than to fail altogether.  Since content in
        # all known instances of Karl is in English, and since this method will
        # correctly translate all characters in the ASCII range, this should
        # yield readable results for the vast majority of user content.
        return body.decode('latin1')
