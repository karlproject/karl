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

from zope.component.event import objectEventNotify
from zope.interface import implements
from repoze.lemonade.content import create_content

from karl.cico.interfaces import IContentIn
from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent
from karl.models.interfaces import IProfile
from karl.models.peopledirectory import PeopleCategory
from karl.models.peopledirectory import PeopleCategoryItem
from karl.views.utils import make_name
from karl.utils import find_site
from karl.utils import find_users


class UserProfileImporter(object):
    implements(IContentIn)

    NAMESPACE = 'http://xml.karlproject.org/people/userprofile'
    NS_PREFIX = '{%s}' % NAMESPACE

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
        self.element = element

    def create(self, profiles):
        element = self.element
        username = _element_value(self, element, 'username')
        password = _element_value(self, element, 'sha_password')
        groups = self._groups(element)

        users = find_users(profiles)
        users.add(username, username, password, groups, encrypted=True)

        profile = create_content(IProfile)
        profiles[username] = profile
        self._populate(profile)

        profile.created_by = profile.modified_by = username
        profile.created = profile.modified = datetime.datetime.now()

    def update(self, profile):
        objectEventNotify(ObjectWillBeModifiedEvent(profile))

        element = self.element
        username = _element_value(self, element, 'username')
        password = _element_value(self, element, 'sha_password')
        groups = self._groups(element)

        users = find_users(profile)
        users.remove(username)
        users.add(username, username, password, groups, encrypted=True)

        self._populate(profile)

        objectEventNotify(ObjectModifiedEvent(profile))

    def _populate(self, profile):
        # Root element must be in correct namespace
        if not self.element.tag.startswith(self.NS_PREFIX):
            raise ValueError("Wrong namespace, expecting: %s" % self.NAMESPACE)

        # Iterate over each child node in root element, calling appropriate
        # handlers.
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
        if not hasattr(profile, 'categories'):
            profile.categories = {}
        categories = [item.text.strip() for item in
                      element.iterchildren(self.NS_PREFIX + 'item')]
        root = find_site(profile)
        category_group = root['people']['categories'][section]
        category_names = dict([(c.sync_id, c.__name__) for c in
                               category_group.values()])
        profile.categories[section] = [category_names[id] for id in categories]


    def _element_value(self, root, name):
        element = root.find(self.NS_PREFIX + name)
        return element.text.strip()


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

    def __init__(self, element):
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

