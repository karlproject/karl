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

from email.message import Message
import string
import warnings
import time
import datetime

from pyramid.interfaces import IDebugLogger
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.traversal import find_interface
from pyramid.traversal import find_resource
from pyramid.traversal import resource_path
from pyramid.url import resource_url
from repoze.lemonade.listitem import get_listitems
from repoze.sendmail.interfaces import IMailDelivery
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements

from karl.adapters.interfaces import IMailinHandler
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IComment
from karl.models.interfaces import ICommunities
from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import IContextualSummarizer
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import ILetterManager
from karl.models.interfaces import IPeopleReportCategoryFilter
from karl.models.interfaces import IPeopleReportFilter
from karl.models.interfaces import IPeopleReportGroupFilter
from karl.models.interfaces import IProfiles
from karl.models.interfaces import ITagQuery
from karl.models.interfaces import IToolFactory
from karl.models.site import get_weighted_textrepr

from karl.utils import find_catalog
from karl.utils import find_peopledirectory_catalog
from karl.utils import find_profiles
from karl.utils import find_tags
from karl.utils import get_content_type_name
from karl.utils import get_setting

TIMEAGO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class CatalogSearch(object):
    """ Centralize policies about searching """
    implements(ICatalogSearch)
    def __init__(self, context, request=None):
        # XXX request argument is not used, is left in for backwards
        #     compatability.  Should be phased out.
        self.context = context
        self.catalog = find_catalog(self.context)
        if request is not None:
            warnings.warn('Creating CatalogSearch with request is deprecated.',
                          DeprecationWarning, stacklevel=2)

    def __call__(self, **kw):
        num, docids = self.catalog.search(**kw)
        address = self.catalog.document_map.address_for_docid
        logger = queryUtility(IDebugLogger)
        def resolver(docid):
            path = address(docid)
            if path is None:
                return None
            try:
                return find_resource(self.context, path)
            except KeyError:
                logger and logger.warn('Model missing: %s' % path)
                return None
        return num, docids, resolver


class PeopleDirectoryCatalogSearch(CatalogSearch):
    """ Catalog search from the PeopleDirectory catalog """
    def __init__(self, context, request=None):
        # XXX request argument is not used, is left in for backwards
        #     compatability.  Should be phased out.
        self.context = context
        self.catalog = find_peopledirectory_catalog(context)


class GridEntryInfo(object):
    implements(IGridEntryInfo)
    _type = None
    _url = None
    _modified = None
    _modified_ago = None
    _created = None
    _creator_title = None
    _creator_url = None
    _profiles = None
    _profile = None  # profile of creator
    _modified_by_profile = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def title(self):
        return self.context.title

    @property
    def url(self):
        if self._url is None:
            if IComment.providedBy(self.context):
                # show the comment in context of its grandparent.
                # (its parent is a comments folder.)
                parent = self.context.__parent__.__parent__
                self._url = '%s#comment-%s' % (
                    resource_url(parent, self.request), self.context.__name__)
            else:
                self._url = resource_url(self.context, self.request)
        return self._url

    @property
    def type(self):
        if self._type is None:
            self._type = get_content_type_name(self.context)
        return self._type

    @property
    def modified(self):
        if self._modified is None:
            self._modified = self.context.modified.strftime("%m/%d/%Y")
        return self._modified

    @property
    def modified_ago(self):
        if self._modified_ago is None:
            # timeago expects utc time
            utc_seconds = time.mktime(self.context.modified.timetuple())
            utc_date = datetime.datetime.utcfromtimestamp(utc_seconds)
            self._modified_ago = utc_date.strftime(TIMEAGO_FORMAT)
        return self._modified_ago

    @property
    def created(self):
        if self._created is None:
            self._created = self.context.created.strftime("%m/%d/%Y")
        return self._created

    @property
    def creator_title(self):
        if self._profiles is None:
            self._profiles = find_profiles(self.context)
        if self._profile is None:
            self._profile = self._profiles.get(self.context.creator, None)
        if self._creator_title is None:
            self._creator_title = getattr(self._profile, "title",
                                          "no profile title")
        return self._creator_title

    @property
    def creator_url(self):
        if self._profiles is None:
            self._profiles = find_profiles(self.context)
        if self._profile is None:
            self._profile = self._profiles.get(self.context.creator, None)
        if self._creator_url is None:
            self._creator_url = resource_url(self._profile, self.request)
        return self._creator_url

    @property
    def modified_by_profile(self):
        if self._modified_by_profile is None:
            modified_by = getattr(self.context, 'modified_by', None)
            if modified_by is None:
                modified_by = self.context.creator
            if self._profiles is None:
                self._profiles = find_profiles(self.context)
            self._modified_by_profile = self._profiles.get(modified_by, None)
        return self._modified_by_profile

    @property
    def modified_by_title(self):
        return getattr(self.modified_by_profile, 'title', 'no profile title')

    @property
    def modified_by_url(self):
        return resource_url(self.modified_by_profile, self.request)


class TagQuery(object):
    implements(ITagQuery)
    _docid = None
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.username = authenticated_userid(request)
        self.path = resource_path(context)
        self.catalog = find_catalog(context)
        self.tags = find_tags(context)

    @property
    def docid(self):
        if self._docid is None:
            self._docid = self.catalog.document_map.docid_for_address(
                                                                self.path)
        return self._docid

    @property
    def usertags(self):
        return self.tags.getTags(users=(self.username,), items=(self.docid,))

    @property
    def tagswithcounts(self):
        """Return tags on a resource, including people and counts"""

        # To draw the tagbox on a resource, we need to know all the
        # tags.  For each tag, the count of people that tagged the
        # resource and if the current user was a tagger.
        tagObjects = self.tags.getTagObjects(items=(self.docid,))
        tagObjects = sorted(tagObjects, key=lambda x: (x.name, x.user))
        alltaginfo = []
        count = 0
        current = None
        current_users = []
        for tagObj in tagObjects:
            if tagObj.name != current:
                if current is not None:
                    alltaginfo.append({
                            'tag': current,
                            'count': len(current_users),
                            'snippet': (self.username not in current_users
                                            and 'nondeleteable' or ''),
                            })
                current = tagObj.name
                count = 1
                current_users = [tagObj.user]
            else:
                count += 1
                current_users.append(tagObj.user)
        if current is not None:
            alltaginfo.append({
                    'tag': current,
                    'count': len(current_users),
                    'snippet': (self.username not in current_users
                                    and 'nondeleteable' or ''),
                    })

        # Sort the tags alphabetically
        return sorted(alltaginfo, key=lambda r: r['tag'])

    @property
    def tagusers(self):
        taginfo = " ".join(self.usertags)
        return taginfo

    def tags_with_prefix(self, prefix):
        return self.tags.getTagsWithPrefix(prefix)


class CommunityInfo(object):
    implements(ICommunityInfo)
    _url = None
    _tabs = None
    _content_modified = None
    _number_of_members = None
    _tags = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = self.context.__name__
        self.title = self.context.title
        self.description = self.context.description

    @property
    def tags(self):
        if self._tags is None:
            self._tags = find_tags(self.context)
        return self._tags

    @property
    def number_of_members(self):
        if self._number_of_members is None:
            self._number_of_members = self.context.number_of_members
        return self._number_of_members

    @property
    def url(self):
        if self._url is None:
            self._url = resource_url(self.context, self.request)
        return self._url

    @property
    def last_activity_date(self):
        if self._content_modified is None:
            # we avoid use of strftime here to banish it from profiler
            # output (for /communities), although this is probably no
            # faster IRL
            m = self.context.content_modified
            self._content_modified = '%02d/%02d/%s' % (m.month, m.day, m.year)
        return self._content_modified

    @property
    def tabs(self):
        if self._tabs is None:

            found_current = False

            overview_css_class = ''

            if ( ICommunity.providedBy(self.request.context) and
                 self.request.view_name in ['','view.html'] ):
                overview_css_class = 'curr'
                found_current = True

            tabs = [
                {'url':resource_url(self.context, self.request, 'view.html'),
                 'css_class':overview_css_class,
                 'name':'OVERVIEW'}
                ]

            for toolinfo in get_listitems(IToolFactory):
                toolfactory = toolinfo['component']
                if toolfactory.is_present(self.context, self.request):
                    info = {}
                    info['url'] = toolfactory.tab_url(self.context,
                                                      self.request)
                    info['css_class'] = ''
                    if not found_current:
                        if toolfactory.is_current(self.context, self.request):
                            info['css_class'] = 'curr'
                            found_current = True
                    info['name'] = toolinfo['title'].upper()
                    tabs.append(info)

            self._tabs = tabs

        return self._tabs

    @property
    def member(self):
        principals = set(effective_principals(self.request))
        members = set(self.context.member_names)
        return bool(principals & members)

    @property
    def moderator(self):
        username = authenticated_userid(self.request)
        return username in self.context.moderator_names

    @property
    def public(self):
        return getattr(self.context, 'security_state', 'inherits') == 'public'


class LetterManager(object): # abstract adapter class, requires iface attr
    implements(ILetterManager)

    def __init__(self, context):
        self.context = context

    def delta(self, delta):
        value = getattr(self.context, 'title', None)
        if not value:
            return False
        firstletter = value[0].upper()
        storage = find_interface(self.context, self.iface)
        if storage is None:
            return False
        if getattr(storage, 'alpha', None) is None:
            storage.alpha = {}
        num = storage.alpha.setdefault(firstletter, 0)
        new = num + delta
        if new < 0:
            new = 0
        storage.alpha[firstletter] = new
        storage._p_changed = True
        return new

    def get_info(self, request):
        """Generate a sequence for the letter box, highlighting current"""

        # Get the letterbox data.  If the use has clicked on a letter, get
        # it from the URL and pass it into the function to get the data
        # for the letterbox macro, so we don't underline the current
        # letter.

        storage = find_interface(self.context, self.iface)
        current = request.params.get('titlestartswith', None)
        fmt = request.path_url + "?titlestartswith=%s"
        letters = []

        for letter in string.uppercase:
            if getattr(storage, 'alpha', None) and storage.alpha.get(letter):
                href = fmt % letter
            else:
                href = None
            if letter == current:
                css_class = 'current'
            else:
                css_class = 'notcurrent'
            letters.append({'name': letter,
                            'href': href,
                            'css_class': css_class,
                            'is_current': letter == current,
                           })
        letters.append({'name': 'Any',
                        'href': current is not None and
                                    request.path_url or None,
                        'css_class': current is None and
                                        'current' or 'notcurrent',
                        'is_current': current is None,
                       })
        return letters


class CommunityLetterManager(LetterManager):
    iface = ICommunities


class ProfileLetterManager(LetterManager):
    iface = IProfiles


class PeopleReportLetterManager(object):
    implements(ILetterManager)

    def __init__(self, context):
        self.context = context

    def get_active_letters(self):
        report = self.context
        catalog = find_peopledirectory_catalog(report)

        # Use the lastnamestartswith index directly for speed.
        index = catalog['lastnamestartswith']
        filters = [(name, obj) for name, obj in report.items()
                        if IPeopleReportFilter.providedBy(obj)]
        if not filters:
            # Any letter in the index will suffice.  This is a fast
            # common case.
            # XXX using undocumented _fwd_index attribute
            return set(index._fwd_index.keys())

        # Perform a catalog search, but don't resolve any paths.
        kw = {}
        for catid, filter in filters:
            if IPeopleReportCategoryFilter.providedBy(filter):
                kw['category_%s' % str(catid)] = {'query': filter.values,
                                                  'operator': 'or',
                                                 }
            elif IPeopleReportGroupFilter.providedBy(filter):
                kw['groups'] =  {'query': filter.values,
                                 'operator': 'or',
                                }
        total, docids = catalog.search(**kw)

        # Intersect the search result docids with the docid set
        # for each letter.
        docid_set = index.family.IF.Set(docids)
        active = set()
        intersection = index.family.IF.intersection
        for letter in string.uppercase:
            # XXX using undocumented _fwd_index attribute
            letter_set = index._fwd_index.get(letter)
            if not letter_set:
                continue
            if intersection(letter_set, docid_set):
                active.add(letter)
        return active

    def get_info(self, request):
        current = request.params.get('lastnamestartswith', None)
        fmt = request.path_url + "?lastnamestartswith=%s"
        letters = []
        active = self.get_active_letters()

        for letter in string.uppercase:
            if letter in active:
                href = fmt % letter
            else:
                href = None
            if letter == current:
                css_class = 'current'
            else:
                css_class = 'notcurrent'
            letters.append({
                'name': letter,
                'href': href,
                'css_class': css_class,
                'is_current': letter == current,
                })
        letters.append({'name': 'Any',
                        'href': current is not None and
                                    request.path_url or None,
                        'css_class': current is None and
                                        'current' or 'notcurrent',
                        'is_current': current is None,
                       })

        return letters


class PeopleReportMailinHandler(object):
    implements(IMailinHandler)

    def __init__(self, context):
        self.context = context

    def handle(self, message, info, text, attachments):
        """ See IMailinHandler.
        """
        """ Later on, we might want to archive messages, something like::

        entry = create_content(
            IListMessage,
            title=info['subject'],
            creator=info['author'],
            text=text,
            description=extract_description(text),
            )

        if attachments:
            if 'attachments' not in entry:
                # XXX Not a likely code path, left here for safety
                entry['attachments'] = att_folder = AttachmentsFolder()
                att_folder.title = 'Attachments'
                att_folder.creator = info['author']
            else:
                att_folder = entry['attachments']
            _addAttachments(att_folder, info, attachments)

        entry_id = make_unique_name(self.context, entry.title)
        self.context[entry_id] = entry

        workflow = get_workflow(IBlogEntry, 'security', self.context)
        if workflow is not None:
            workflow.initialize(entry)

        alerts = queryUtility(IAlerts, default=Alerts())
        alerts.emit(entry, offline_request)
        """
        mailinglist = self.context.get('mailinglist')
        if mailinglist is not None:
            system_email_domain = get_setting(self.context,
                                                "system_email_domain")
            system_list_subdomain = get_setting(self.context,
                                                "system_list_subdomain",
                                                system_email_domain)
            reply_to = "%s@%s" % (mailinglist.short_address,
                                  system_list_subdomain)
            clone = self._cloneMessage(message)
            clone['Reply-To'] = reply_to
            mailer = getUtility(IMailDelivery)
            for address in self._reportAddresses(self.context):
                mailer.send([address], clone)

    def _cloneMessage(self, message):
        clone = Message()
        for key, value in message.items():
            if key.lower() != 'message-id':
                clone[key] = value
        clone.set_payload(message.get_payload())
        return clone

    def _reportAddresses(self, report):
        query = report.getQuery()
        searcher = ICatalogSearch(report)
        total, docids, resolver = searcher(**query)

        for docid in docids:
            profile = resolver(docid)
            security_state = getattr(profile, 'security_state')
            if profile is not None and security_state != 'inactive':
                yield profile.email


# Dodge to allow developer builds that don't require Postgres
try:
    from repoze.pgtextindex.index import PGTextIndex
except ImportError:
    class PGTextIndex(object):
        pass


class PGTextIndexContextualSummarizer(object):
    implements(IContextualSummarizer)

    get_textrepr = staticmethod(get_weighted_textrepr)

    def __init__(self, index):
        self.index = index

    def __call__(self, document, query):
        doc_text = self.get_textrepr(document, [])
        if type(doc_text) in (list, tuple):
            doc_text = ' '.join(doc_text)
        summary = self.index.get_contextual_summary(
            doc_text, query, MaxFragments=3)
        pieces = [summary]
        if summary[:10] != doc_text[:10]:
            pieces.insert(0, '...')
        if summary[-10:] != doc_text[-10:]:
            pieces.append('...')
        return ' '.join(pieces)

class ZopeTextIndexContextualSummarizer(object):
    implements(IContextualSummarizer)

    def __init__(self, index):
        self.index = index

    def __call__(self, document, query):
        try:
            return getattr(document, 'description')
        except AttributeError:
            return ''

