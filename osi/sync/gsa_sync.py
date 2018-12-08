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

import base64
import datetime
import logging
import lxml.etree
import pkg_resources
import random
import string
import socket
import time
import urllib
import urllib2

from persistent.dict import PersistentDict
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow
from zope.event import notify
from zope.component.event import objectEventNotify

from pyramid.threadlocal import get_current_request

from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent
from karl.models.interfaces import IProfile
from karl.models.peopledirectory import PeopleCategory
from karl.models.peopledirectory import PeopleCategoryItem
from karl.models.peopledirectory import PeopleDirectorySchemaChanged
from karl.security.workflow import reset_security_workflow
from karl.views.resetpassword import request_password_reset
from karl.views.utils import make_name
from karl.utils import find_peopledirectory
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_users
from karl.utils import get_settings

from osi.utilities.former_staff import make_non_staff

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
RETRIES = 5
RETRY_SLEEP = 60 # One minute

log = logging.getLogger(__name__)


def get_last_sync(root, url):
    last_gsa_sync = getattr(root, 'last_gsa_sync', {})
    return last_gsa_sync.get(url, None)

def get_random_password():
    password = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits)
        for _ in range(32))
    return password


class GsaSync(object):
    """
    Provides a means of importing user, profile and category data from an
    external, OSI managed, data source.
    """

    def __init__(self,
                 context,
                 url,
                 username=None,
                 password=None,
                 timeout=None,
                 last_sync=None):
        # Context is assumed to be site root
        self.context = context
        self.url = url

        if timeout is None:
            timeout = socket.getdefaulttimeout()

        url_query = url
        is_http = url.startswith('http')
        if is_http:
            # Add date to query string
            if last_sync is None:
                last_sync = get_last_sync(context, url)

            if last_sync:
                if isinstance(last_sync, datetime.datetime):
                    modified = last_sync.strftime(DATETIME_FORMAT)
                else:
                    modified = last_sync
                params = {
                    'timestamp': modified,
                    }
                url_query = url + '?' + urllib.urlencode(params)

        log.debug("Running GSA sync with url: %s", url_query)

        # XML data to import
        if is_http and username is not None and password is not None:
            request = urllib2.Request(url_query)
            basic_auth = base64.b64encode('%s:%s' % (username, password))
            request.add_header('Authorization', 'Basic %s' % basic_auth)
        else:
            request = url_query

        tries = 0
        while True:
            try:
                resource = urllib2.urlopen(request, timeout=timeout)
            except urllib2.HTTPError, e:
                if e.code != 500 or tries >= RETRIES:
                    raise
                tries += 1
                time.sleep(RETRY_SLEEP)
            else:
                break

        doc = lxml.etree.parse(resource)

        # Remember timestamp for when we last did this
        self.modified = datetime.datetime.strptime(
            doc.getroot().get('timestamp'), DATETIME_FORMAT)

        # XSLT template to transform from gsa to our format
        xslt_doc = lxml.etree.parse(pkg_resources.resource_stream(
            'osi.sync', 'gsa_to_karl.xsl'))
        transformer = lxml.etree.XSLT(xslt_doc)

        self.doc = transformer(doc)

    def __call__(self):

        # One pass for each namespace we're looking for
        namespaces = [
            ('categories', NS_CATEGORY_PREFIX, self._handle_category),
            ('profiles', NS_PROFILE_PREFIX, self._handle_profile),
            ]

        for label, ns_prefix, handle in namespaces:
            count = 0
            for child in self.doc.getroot().iterchildren():
                if child.tag.startswith(ns_prefix):
                    handle(child)
                    count += 1
            log.info("Updated %s: %d", label, count)

        # Now that we have done everything, "remember" this as the
        # last successful modification
        context = self.context
        if not hasattr(context, 'last_gsa_sync'):
            context.last_gsa_sync = PersistentDict()
        context.last_gsa_sync[self.url] = self.modified


    def _handle_profile(self, element):
        username = _element_value(element, NS_PROFILE_PREFIX + 'username')
        inactive = _pop_element_value(element, NS_PROFILE_PREFIX + 'inactive')
        if inactive:
            active = not bool(int(inactive))
        else:
            active = True
        profiles = find_profiles(self.context)
        importer = UserProfileImporter(element)
        groups = self._get_groups(element)
        if username not in profiles:
            username = username.replace(' ', '')
        if username in profiles:
            profile = profiles[username]
            users = find_users(self.context)
            if (users.member_of_group(username, 'group.KarlStaff') or
                  'group.KarlStaff' in groups):
                if active and profile.security_state == 'inactive':
                    log.info("Reactivating profile: %s", username)
                    self._reactivate(profile)

                log.info("Updating profile: %s", username)
                importer.update(profile)

                if profile.security_state == 'active' and not active:
                    log.info("Deactivating profile: %s", username)
                    self._deactivate(profile)

                if active and 'group.KarlStaff' not in groups:
                    make_non_staff(profile)

        elif 'group.KarlStaff' in groups:
            log.info("Creating profile: %s", username)
            importer.create(profiles)
            if not active:
                self._deactivate(profiles[username])

    def _deactivate(self, profile):
        users = find_users(profile)
        username = profile.__name__
        users.remove(username)
        workflow = get_workflow(IProfile, 'security', profile)
        workflow.transition_to_state(profile, None, 'inactive')

    def _reactivate(self, profile):
        workflow = get_workflow(IProfile, 'security', profile)
        workflow.transition_to_state(profile, None, 'active')

    def _handle_category(self, element):
        sync_id = element.get('id')
        importer = PeopleCategoryImporter(element)

        category_element = element.find(NS_CATEGORY_PREFIX + 'category')
        category_id = category_element.get('id')
        categories = self.context['people']['categories']
        category = categories.get(category_id, None)
        title = _element_value(element, NS_CATEGORY_PREFIX + 'title')

        updated = False
        if category is not None:
            for category_item in category.values():
                if category_item.sync_id == sync_id:
                    log.info("Updating category: %s", title)
                    importer.update(category_item)
                    updated = True
                    break

        if not updated:
            log.info("Creating category: %s", title)
            importer.create(categories)

    def _get_groups(self, root):
        element = root.find(NS_PROFILE_PREFIX + 'groups')
        if element is not None:
            return set([child.text.strip() for child in
                        element.iterchildren(NS_PROFILE_PREFIX + 'item')])
        return set()


def _element_value(ancestor, name):
    return ancestor.find(name).text.strip()

def _pop_element_value(ancestor, name):
    element = ancestor.find(name)
    if element is None:
        return
    if element.text is not None:
        value = element.text.strip()
    else:
        value = ''
    element.getparent().remove(element)
    return value

class Importer(object):
    def __init__(self, element):
        # Validate xml against RNG Schema
        # XXX Memoize schema?
        schema_doc = lxml.etree.parse(pkg_resources.resource_stream(
            __name__, self.SCHEMA))
        schema = lxml.etree.RelaxNG(schema_doc)
#        schema.assertValid(element)
        self.element = element

    def _element_value(self, root, name):
        element = root.find(self.NS_PREFIX + name)
        if element is not None:
            value = element.text
            if value:
                value = value.strip()
            return value
        return None

class UserProfileImporter(Importer):
    NAMESPACE = 'http://xml.karlproject.org/people/userprofile'
    NS_PREFIX = '{%s}' % NAMESPACE
    SCHEMA = 'userprofile.rng'

    _simple_attributes = [
        "firstname",
        "lastname",
        "email",
        "phone",
        "extension",
        "department",
        "position",
        "organization",
        "board",
        "location",
        "country",
        "languages",
        "office",
        "room_no",
        "biography",
        "home_path",
        "auth_method",
        "sso_id",
        ]

    def create(self, profiles):
        element = self.element
        login = self._element_value(element, 'username')
        username = login.replace(' ', '')
        password = get_random_password()
        groups = self._groups(element)

        users = find_users(profiles)
        users.add(username, login, password, groups, encrypted=False)

        profile = create_content(IProfile)
        profiles[username] = profile
        self._populate(profile)

        workflow = get_workflow(IProfile, 'security', profile)
        if workflow is not None:
            workflow.initialize(profile)

        profile.created_by = profile.modified_by = username
        profile.created = profile.modified = datetime.datetime.now()

        # Profile was indexed before workflow was initialized, so there is a
        # a bogus value for the 'allowed' index.  Unfortunately, we can't just
        # add the profile to the profiles folder (which triggers indexing)
        # after the workflow is initialized, because the workflow
        # initialization code for profiles requires that the profile already
        # be in the content tree since a call to 'find_users' is made.  The
        # work around is to just remove the profile and add it back again to
        # trigger reindexing.
        del profiles[username]
        profiles[username] = profile

    def update(self, profile):
        objectEventNotify(ObjectWillBeModifiedEvent(profile))

        if profile.security_state == 'active':
            element = self.element
            login = self._element_value(element, 'username')
            username = profile.__name__
            groups = self._groups(element)

            # Don't clobber user's community memberships
            users = find_users(profile)
            info = users.get_by_id(username)
            if info is not None:
                prev_groups = info['groups']
                community_groups = [g for g in prev_groups if
                                    g.startswith('group.community')]
                groups = groups | set(community_groups)

            if info is not None:
                # keep old password
                password = info['password']
                users.remove(username)
                users.add(username, login, password, groups, encrypted=True)
            else:
                # can it be that we have a new user here?
                password = get_random_password()
                users.add(username, login, password, groups, encrypted=False)
                user = users.get_by_id(username)
                request = get_current_request()
                settings = get_settings()
                app_url = settings.get('script_app_url')
                request_password_reset(user, profile, request, app_url=app_url)

        self._populate(profile)
        reset_security_workflow(profile)

        objectEventNotify(ObjectModifiedEvent(profile))

    def _populate(self, profile):
        # Iterate over each child node in root element, calling appropriate
        # handlers.
        profile.categories = {}
        for element in self.element.iterchildren():
            tag = element.tag
            if not tag.startswith(self.NS_PREFIX):
                # Ignore foreign name spaces
                continue

            attr = tag[len(self.NS_PREFIX):]
            if attr in self._simple_attributes:
                self._pop_simple_attribute(profile, element, attr)

            elif attr == 'website':
                value = element.text
                if value is None:
                    value = ''
                websites = value.strip().split()
                for i in xrange(len(websites)):
                    if websites[i].startswith('www.'):
                        websites[i] = 'http://' + websites[i]
                profile.websites = tuple(websites)

            elif attr in ('offices', 'entities', 'departments', 'boards'):
                self._pop_category_section(profile, element, attr)

    def _pop_simple_attribute(self, profile, element, attr):
        value = element.text
        if value:
            value = value.strip()
        setattr(profile, attr, value)

    def _pop_category_section(self, profile, element, section):
        categories = [item.text.strip() for item in
                      element.iterchildren(self.NS_PREFIX + 'item')]
        root = find_site(profile)
        category_group = root['people']['categories'][section]
        category_names = dict([(v.sync_id, k) for k,v in
                               category_group.items()])
        profile.categories[section] = [category_names[id] for id in categories]


    def _groups(self, root):
        element = root.find(self.NS_PREFIX + 'groups')
        if element is not None:
            return set([child.text.strip() for child in
                        element.iterchildren(self.NS_PREFIX + 'item')])
        return set()

class PeopleCategoryImporter(Importer):
    NAMESPACE = 'http://xml.karlproject.org/people/category'
    NS_PREFIX = '{%s}' % NAMESPACE
    SCHEMA = 'peoplecategory.rng'

    def create(self, container):
        """
        container is root['people']['categories'], or moral equivalent.
        """
        title = self._element_value(self.element, 'title')
        sync_id = self.element.get('id')
        name = make_name(container, title)
        description = self._element_value(self.element, 'description')

        category_element = self.element.find(self.NS_PREFIX + 'category')
        category_id = category_element.get('id')
        category = container.get(category_id, None)
        if category is None:
            category = PeopleCategory(category_element.text.strip())
            container[category_id] = category
            peopledir = find_peopledirectory(container)
            notify(PeopleDirectorySchemaChanged(peopledir))

        category_item = PeopleCategoryItem(title, description)
        if sync_id is not None:
            category_item.sync_id = sync_id # OSI artifact

        if name in category:
            del category[name]
        category[name] = category_item

    def update(self, item):
        objectEventNotify(ObjectWillBeModifiedEvent(item))

        item.title = self._element_value(self.element, 'title')
        item.description = self._element_value(self.element, 'description')

        objectEventNotify(ObjectModifiedEvent(item))

PROFILE_NAMESPACE = UserProfileImporter.NAMESPACE
NS_PROFILE_PREFIX = UserProfileImporter.NS_PREFIX

CATEGORY_NAMESPACE = PeopleCategoryImporter.NAMESPACE
NS_CATEGORY_PREFIX = PeopleCategoryImporter.NS_PREFIX
