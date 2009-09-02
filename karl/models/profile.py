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

from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree
from zope.interface import implementer
from zope.interface import implements
from zope.component import adapter

from repoze.folder import Folder
from karl.models.interfaces import IProfile
from karl.models.interfaces import IProfiles
from karl.models.interfaces import ITextIndexData
from karl.models.image import extensions as image_extensions

class Profile(Folder):

    implements(IProfile)

    alert_attachments = 'link'

    def __init__(self,
                 firstname = '',
                 lastname = '',
                 email = '',
                 phone = '',
                 extension = '',
                 department = '',
                 position = '',
                 organization = '',
                 location = '',
                 country = '',
                 website = '',
                 languages = '',
                 office='',
                 room_no='',
                 biography='',
                 data=None,
                 home_path=None,
                ):
        super(Profile, self).__init__(data)
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.extension = extension
        self.department = department
        self.position = position
        self.organization = organization
        self.location = location
        self.country = country
        self.website = website
        self.languages = languages
        self.office = office
        self.room_no = room_no
        self.biography = biography
        self.home_path = home_path
        self._alert_prefs = PersistentMapping()
        self._pending_alerts = PersistentList()
        self.categories = PersistentMapping()
        self.password_reset_key = None
        self.password_reset_time = None

    @property
    def creator(self):
        return self.__name__

    @property
    def title(self):
        return unicode(
            '%s %s' % (self.firstname.strip(), self.lastname.strip())
            )

    def get_photo(self):
        for ext in image_extensions.values():
            name = "photo." + ext
            if name in self:
                return self[name]
        return None

    def get_alerts_preference(self, community_name):
        return self._alert_prefs.get(community_name,
                                     IProfile.ALERT_IMMEDIATELY)

    def set_alerts_preference(self, community_name, preference):
        if preference not in (
            IProfile.ALERT_IMMEDIATELY,
            IProfile.ALERT_DIGEST,
            IProfile.ALERT_NEVER):
            raise ValueError("Invalid preference.")

        self._alert_prefs[community_name] = preference

class CaseInsensitiveOOBTree(OOBTree):
    def __getitem__(self, name):
        return super(CaseInsensitiveOOBTree, self).__getitem__(name.lower())

    def __setitem__(self, name, value):
        return super(CaseInsensitiveOOBTree, self).__setitem__(name.lower(),
                                                               value)
    def get(self, name, default=None):
        return super(CaseInsensitiveOOBTree, self).get(name.lower(), default)

class ProfilesFolder(Folder):

    implements(IProfiles)

    def __init__(self, data=None):
        super(ProfilesFolder, self).__init__(data)
        self.email_to_name = CaseInsensitiveOOBTree()

    def getProfileByEmail(self, email):
        name = self.email_to_name.get(email)
        if name is not None:
            return self[name]

@implementer(ITextIndexData)
@adapter(IProfile)
def profile_textindexdata(profile):
    """Provides info for the text index"""
    text = []
    for attr in (
        '__name__',
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
        ):
        v = getattr(profile, attr, None)
        if v:
            text.append(unicode(v))
    text = '\n'.join(text)
    return lambda: text
