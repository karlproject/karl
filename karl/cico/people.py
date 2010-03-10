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
import lxml.etree
import pkg_resources
import sys

from zope.event import notify
from zope.component.event import objectEventNotify
from zope.interface import implements
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow

from karl.cico.interfaces import IContentIn
from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent
from karl.models.interfaces import IProfile
from karl.models.peopledirectory import PeopleCategory
from karl.models.peopledirectory import PeopleCategoryItem
from karl.models.peopledirectory import PeopleDirectorySchemaChanged
from karl.security.workflow import reset_security_workflow
from karl.views.utils import make_name
from karl.utils import find_peopledirectory
from karl.utils import find_site
from karl.utils import find_users


class UserProfileImporter(object):
    implements(IContentIn)

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
        "location",
        "country",
        "website",
        "languages",
        "office",
        "room_no",
        "biography",
        "home_path",
        ]

    def __init__(self, element):
        # Validate xml against RNG Schema
        # XXX Memoize schema?
        try:
            schema_doc = lxml.etree.parse(pkg_resources.resource_stream(
                __name__, 'schemas/%s' % self.SCHEMA))
            schema = lxml.etree.RelaxNG(schema_doc)
            schema.assertValid(element)
        except lxml.etree.DocumentInvalid:
            print lxml.etree.tostring(element, pretty_print=True)
            raise

        self.element = element

    def create(self, profiles):
        element = self.element
        login = _element_value(self, element, 'username')
        username = login.replace(' ', '')
        password = _element_value(self, element, 'sha_password')
        groups = self._groups(element)

        users = find_users(profiles)
        users.add(username, login, password, groups, encrypted=True)

        profile = create_content(IProfile)
        profiles[username] = profile
        self._populate(profile)

        workflow = get_workflow(IProfile, 'security', profile)
        if workflow is not None:
            workflow.initialize(profile)

        profile.created_by = profile.modified_by = username
        profile.created = profile.modified = datetime.datetime.now()

    def update(self, profile):
        objectEventNotify(ObjectWillBeModifiedEvent(profile))

        element = self.element
        login = _element_value(self, element, 'username')
        username = profile.__name__
        password = _element_value(self, element, 'sha_password')
        groups = self._groups(element)

        users = find_users(profile)

        # Don't clobber user's community memberships
        prev_groups = users.get_by_id(username)['groups']
        community_groups = [g for g in prev_groups if
                            g.startswith('group.community')]
        groups = groups | set(community_groups)

        users.remove(username)
        users.add(username, login, password, groups, encrypted=True)

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

            elif attr in ('offices', 'entities', 'departments'):
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
        category_group = root['people'].categories[section]
        category_names = dict([(v.sync_id, k) for k,v in
                               category_group.items()])
        profile.categories[section] = [category_names[id] for id in categories]


    def _groups(self, root):
        element = root.find(self.NS_PREFIX + 'groups')
        if element is not None:
            return set([child.text.strip() for child in
                        element.iterchildren(self.NS_PREFIX + 'item')])
        return set()


class PeopleCategoryImporter(object):
    implements(IContentIn)

    NAMESPACE = 'http://xml.karlproject.org/people/category'
    NS_PREFIX = '{%s}' % NAMESPACE
    SCHEMA = 'peoplecategory.rng'

    def __init__(self, element):
        # Validate xml against RNG Schema
        # XXX Memoize schema?
        schema_doc = lxml.etree.parse(pkg_resources.resource_stream(
            __name__, 'schemas/%s' % self.SCHEMA))
        schema = lxml.etree.RelaxNG(schema_doc)
        try:
            schema.assertValid(element)
        except:
            print sys.stderr, lxml.etree.tostring(element)
            raise

        self.element = element

    def create(self, container):
        """
        container is root['people'].categories, or moral equivalent.
        """
        title = _element_value(self, self.element, 'title')
        sync_id = self.element.get('id')
        name = make_name(container, title)
        description = _element_value(self, self.element, 'description')

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

        category[name] = category_item

    def update(self, item):
        objectEventNotify(ObjectWillBeModifiedEvent(item))

        item.title = _element_value(self, self.element, 'title')
        item.description = _element_value(self, self.element, 'description')

        objectEventNotify(ObjectModifiedEvent(item))


def _element_value(self, root, name):
    element = root.find(self.NS_PREFIX + name)
    if element is not None:
        value = element.text
        if value:
            value = value.strip()
        return value
    return None

