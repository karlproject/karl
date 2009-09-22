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
from __future__ import with_statement

from email import Encoders
from email.message import Message
from email.mime.multipart import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from lxml import etree
from lxml.html import document_fromstring
import math

from zope.component import getUtility
from zope.interface import implements

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.traversal import find_interface
from repoze.bfg.url import model_url

from karl.utilities.interfaces import IAlert
from karl.utilities.interfaces import IKarlDates
from karl.utilities.interfaces import IMimeInfo
from karl.models.interfaces import IComment
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import IWikiPage
from karl.content.interfaces import ICommunityFile
from karl.content.views.interfaces import IFileInfo
from karl.content.views.interfaces import IBylineInfo

from karl.utils import docid_to_hex
from karl.utils import get_setting
from karl.utils import find_community
from karl.utils import find_profiles
from karl.utilities.interfaces import IKarlDates

MAX_ATTACHMENT_SIZE = (1<<20) * 5  # 5 megabytes

class FileInfo(object):
    """ Adapter for showing file entry data in views """
    implements(IFileInfo)
    _url = None
    _modified = None
    _mimeinfo = None
    _size = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def name(self):
        return self.context.__name__

    @property
    def title(self):
        return self.context.title

    @property
    def modified(self):
        if self._modified is None:
            self._modified = self.context.modified.strftime("%m/%d/%Y")
        return self._modified

    @property
    def url(self):
        if self._url is None:
            self._url = model_url(self.context, self.request)
        return self._url

    @property
    def mimeinfo(self):
        if self._mimeinfo is None:
            mimetype = getattr(self.context, 'mimetype', None)
            if mimetype is None:
                self._mimeinfo = {'small_icon_name':'files_folder_small.png',
                                  'title':'Folder'}
            else:
                mimeutil = getUtility(IMimeInfo)
                self._mimeinfo =  mimeutil(mimetype)
        return self._mimeinfo

    @property
    def size(self):
        if self._size is None:
            powers = ["bytes", "KB", "MB", "GB", "TB"] # Future proof ;)
            size = self.context.size
            if size > 0:
                power = int(math.log(size, 1024))
                assert power < len(powers), "File is larger than 999 TB"
            else:
                power = 0

            if power == 0:
                self._size = "%d %s" % (size, powers[0])

            else:
                size = float(size) / (1 << (10 * power))
                self._size = "%0.1f %s" % (size, powers[power])

        return self._size

class CalendarEventFileInfo(FileInfo):
    @property
    def mimeinfo(self):
        return {
            "small_icon_name": "files_event_small.png",
            "title": "Event"
        }

class PageFileInfo(FileInfo):
    @property
    def mimeinfo(self):
        return {
            "small_icon_name": "files_page_small.png",
            "title": "Page"
        }

class ReferenceManualFileInfo(FileInfo):
    @property
    def mimeinfo(self):
        return {
            "small_icon_name": "files_manual_small.png",
            "title": "Reference Manual"
        }

class ReferenceSectionFileInfo(FileInfo):
    @property
    def mimeinfo(self):
        return {
            "small_icon_name": "files_manual_small.png",
            "title": "Reference Section"
        }


class BylineInfo(object):
    """ Adapter to grab resource info for the byline in ZPT """
    implements(IBylineInfo)
    _author_url = None
    _author_name = None
    _posted_date = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.profile = find_profiles(context).get(context.creator)

    @property
    def author_url(self):
        if self._author_url is None:
            self._author_url = model_url(self.profile, self.request)
        return self._author_url


    @property
    def author_name(self):
        if self._author_name is None:
            if self.profile:
                self._author_name = self.profile.title
            else:
                self._author_name = None
        return self._author_name

    @property
    def posted_date(self):
        if self._posted_date is None:
            kd = getUtility(IKarlDates)
            self._posted_date = kd(self.context.created, 'longform')
        return self._posted_date

class Alert(object):
    """Base adapter class for generating emails from alerts.
    """
    implements(IAlert)

    mfrom = None
    message = None
    digest = False

    def __init__(self, context, profile, request):
        self.context = context
        self.profile = profile
        self.request = request

        self.profiles = profiles = find_profiles(context)
        self.creator = profiles[context.creator]

    @property
    def mto(self):
        return [self.profile.email,]

class BlogAlert(Alert):
    """Adapter for generating an email from a blog entry alert.
    """
    _mfrom = None
    _message = None
    _template = None
    _subject = None

    def __init__(self, context, profile, request):
        super(BlogAlert, self).__init__(context, profile, request)
        self._community = find_community(context)
        self._blogentry = find_interface(context, IBlogEntry)

    @property
    def mfrom(self):
        if self._mfrom is not None:
            return self._mfrom

        system_email_domain = get_setting(self.context, "system_email_domain")
        mfrom = "%s@%s" % (self._community.__name__,
                                   system_email_domain)
        self._mfrom = mfrom
        return mfrom

    @property
    def message(self):
        if self._message is not None:
            return self._message

        community = self._community
        request = self.request
        profile = self.profile
        blogentry = self._blogentry

        community_href = model_url(community, request)
        blogentry_href = model_url(blogentry, request)
        manage_preferences_href = model_url(profile, request)
        system_name = get_setting(self.context, "system_name", "KARL")
        system_email_domain = get_setting(self.context, "system_email_domain")

        reply_to = "%s <%s+blog-%s@%s>" % (community.title,
                                           community.__name__,
                                           docid_to_hex(blogentry.docid),
                                           system_email_domain)

        attachments = []
        attachment_links = []
        attachment_hrefs = {}
        for name,model in self._attachments.items():
            assert name == model.title
            if profile.alert_attachments == 'link':
                attachment_links.append(name)
                attachment_hrefs[name] = model_url(model, request)

            elif profile.alert_attachments == 'attach':
                with model.blobfile.open() as f:
                    f.seek(0, 2)
                    size = f.tell()
                    if size > MAX_ATTACHMENT_SIZE:
                        attachment_links.append(name)
                        attachment_hrefs[name] = model_url(model, request)

                    else:
                        f.seek(0, 0)
                        data = f.read()
                        type, subtype = model.mimetype.split('/', 1)
                        attachment = MIMEBase(type, subtype)
                        attachment.set_payload(data)
                        Encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            'attachment; filename="%s"' % model.filename)
                        attachments.append(attachment)

        body_template = get_template(self._template)
        from_name = "%s | %s" % (self.creator.title, system_name)
        msg = MIMEMultipart() if attachments else Message()
        msg["From"] = "%s <%s>" % (from_name, self.mfrom)
        msg["To"] = "%s <%s>" % (profile.title, profile.email)
        msg["Reply-to"] = reply_to
        msg["Subject"] = self._subject
        body_text = body_template(
            context=self.context,
            community=community,
            community_href=community_href,
            blogentry=blogentry,
            blogentry_href=blogentry_href,
            attachments=attachment_links,
            attachment_hrefs=attachment_hrefs,
            manage_preferences_href=manage_preferences_href,
            profile=profile,
            profiles=self.profiles,
            creator=self.creator,
            digest=self.digest,
            alert=self,
            history=self._history,
        )

        if self.digest:
            # Only interested in body for digest
            html = document_fromstring(body_text)
            body_element = html.cssselect('body')[0]
            span = etree.Element("span", nsmap=body_element.nsmap)
            span[:] = body_element[:] # Copy all body elements to an empty span
            body_text = etree.tostring(span, pretty_print=True)

        if isinstance(body_text, unicode):
            body_text = body_text.encode('utf-8')

        if attachments:
            body = MIMEText(body_text, 'html', 'utf-8')
            msg.attach(body)
            for attachment in attachments:
                msg.attach(attachment)
        else:
            msg.set_payload(body_text, 'utf-8')
            msg.set_type("text/html")

        self._message = msg

        return self._message

    @property
    def _attachments(self):
        return self._blogentry['attachments']

    @property
    def _history(self):
        """
        Return a tuple, (messages, n), where messages is a list of at most
        three preceding messages considered relevant to the current message. n
        is the total number of messages in the 'thread' for some definition of
        'thread'.
        """
        return ([], 0)

class BlogEntryAlert(BlogAlert):
    _template = "templates/email_blog_entry_alert.pt"

    def __init__(self, context, profile, request):
        super(BlogEntryAlert, self).__init__(context, profile, request)
        assert IBlogEntry.providedBy(context)

    @property
    def _subject(self):
        return "[%s] %s" % (self._community.title, self._blogentry.title)

class BlogCommentAlert(BlogAlert):
    _template = "templates/email_blog_comment_alert.pt"

    def __init__(self, context, profile, request):
        super(BlogCommentAlert, self).__init__(context, profile, request)
        assert IComment.providedBy(context)

    @property
    def _subject(self):
        return "[%s] Re: %s" % (self._community.title, self._blogentry.title)

    @property
    def _attachments(self):
        return self.context

    @property
    def _history(self):
        """ See abstract base class, BlogAlert, above."""
        if self.digest:
            return ([], 0)

        blogentry = self._blogentry
        comments = list(self._blogentry['comments'].values())
        comments = [comment for comment in comments
                    if comment is not self.context]
        comments.sort(key=lambda x: x.created)

        messages = [blogentry] + comments
        n = len(comments) + 1
        return messages, n

class NonBlogAlert(Alert):
    # XXX Are BlogAlert and NonBlogAlert close enough that they could merged
    #     into Alert?
    _mfrom = None
    _message = None
    _template = None
    _subject = None
    _template = None
    _interface = None
    _content_type_name = None

    def __init__(self, context, profile, request):
        Alert.__init__(self, context, profile, request)
        self._community = find_community(context)
        self._model = find_interface(context, self._interface)
        assert self._interface.providedBy(context)

    @property
    def _subject(self):
        return "[%s] %s" % (self._community.title, self.context.title)

    @property
    def mfrom(self):
        if self._mfrom is not None:
            return self._mfrom

        system_email_domain = get_setting(self.context, "system_email_domain")
        mfrom = "%s@%s" % ('alerts', system_email_domain)
        self._mfrom = mfrom
        return mfrom

    @property
    def message(self):
        if self._message is not None:
            return self._message

        community = self._community
        request = self.request
        profile = self.profile
        model = self._model

        community_href = model_url(community, request)
        model_href = model_url(model, request)
        manage_preferences_href = model_url(profile, request)
        system_name = get_setting(self.context, "system_name", "KARL")
        system_email_domain = get_setting(self.context, "system_email_domain")

        body_template = get_template(self._template)
        from_name = "%s | %s" % (self.creator.title, system_name)
        msg = Message()
        msg["From"] = "%s <%s>" % (from_name, self.mfrom)
        msg["To"] = "%s <%s>" % (community.title, profile.email)
        msg["Subject"] = self._subject
        body = body_template(
            context=self.context,
            community=community,
            community_href=community_href,
            model=model,
            model_href=model_href,
            manage_preferences_href=manage_preferences_href,
            profile=profile,
            creator=self.creator,
            content_type=self._content_type_name,
            digest=self.digest,
            alert=self,
        )

        if self.digest:
            # Only interested in body for digest
            html = document_fromstring(body)
            body_element = html.cssselect('body')[0]
            span = etree.Element("span", nsmap=body_element.nsmap)
            span[:] = body_element[:] # Copy all body elements to an empty span
            body = etree.tostring(span, pretty_print=True)

        if isinstance(body, unicode):
            body = body.encode('utf-8')

        msg.set_payload(body, 'utf-8')
        msg.set_type("text/html")
        self._message = msg
        return msg

class WikiPageAlert(NonBlogAlert):
    _template = "templates/email_wikipage_alert.pt"
    _interface = IWikiPage
    _content_type_name = 'Wiki Page'

class CommunityFileAlert(NonBlogAlert):
    _template = "templates/email_community_file_alert.pt"
    _interface = ICommunityFile
    _content_type_name = 'File'

class CalendarEventAlert(NonBlogAlert):
    _template = "templates/email_calendar_event_alert.pt"
    _interface = ICalendarEvent
    _content_type_name = "Event"

    @property
    def startDate(self):
        model = self._model
        if not model.startDate:
            return None
        karldates = getUtility(IKarlDates)
        return karldates(model.startDate, 'longform')

    @property
    def endDate(self):
        model = self._model
        if not model.endDate:
            return None
        karldates = getUtility(IKarlDates)
        return karldates(model.endDate, 'longform')

    @property
    def attendees(self):
        model = self._model
        if not model.attendees:
            return None
        return '; '.join(model.attendees)
