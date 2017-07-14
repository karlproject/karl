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

from appendonly import Accumulator
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree
from zope.interface import implementer
from zope.interface import implements
from zope.component import adapter

from repoze.folder import Folder
from karl.consts import countries
from karl.consts import cultures
from karl.models.interfaces import IProfile
from karl.models.interfaces import IProfiles
from karl.models.interfaces import ITextIndexData
from karl.utils import find_profiles


class Profile(Folder):

    implements(IProfile)

    alert_attachments = 'link'
    fax = '' # BBB
    _websites = ()
    last_login_time = None # BBB
    date_format = None # BBB
    password_expiration_date = None # BBB
    last_passwords = None # BBB
    active_device = None #BBB
    auth_method = 'password'  # BBB
    _sso_id = None

    def _get_website(self):
        old_ws = self.__dict__.get('website')
        if old_ws is not None:
            return old_ws
        return self._websites and self._websites[0] or ''

    website = property(_get_website,)

    def _get_websites(self):
        self._p_activate()
        if '_websites' in self.__dict__:
            return self._websites
        old_ws = self.__dict__.get('website')
        if old_ws is not None:
            return (old_ws,)
        return ()

    def _set_websites(self, value):
        self._websites = value # coerce / normalize?
        if 'website' in self.__dict__:
            del self.__dict__['website']

    websites = property(_get_websites, _set_websites)

    def __init__(self,
                 firstname='',
                 lastname='',
                 email='',
                 phone='',
                 extension='',
                 fax='',
                 department='',
                 position='',
                 organization='',
                 location='',
                 country='',
                 websites=None,
                 languages='',
                 office='',
                 room_no='',
                 biography='',
                 date_format=None,
                 data=None,
                 home_path=None,
                 preferred_communities=None,
                 ):
        super(Profile, self).__init__(data)
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.fax = fax
        self.extension = extension
        self.department = department
        self.position = position
        self.organization = organization
        self.location = location
        if country not in countries.as_dict:
            country = 'XX'
        self.country = country
        if websites is not None:
            self.websites = websites
        self.languages = languages
        self.office = office
        self.room_no = room_no
        self.biography = biography
        if date_format not in cultures.as_dict:
            date_format = None
        self.date_format = date_format
        self.home_path = home_path
        self._alert_prefs = PersistentMapping()
        self._pending_alerts = Accumulator()
        self.categories = PersistentMapping()
        self.password_reset_key = None
        self.password_reset_time = None
        self.preferred_communities = preferred_communities
        self.last_login_time = None
        self.password_expiration_date = None
        self.last_passwords = None
        self.active_device = None

    @property
    def creator(self):
        return self.__name__

    @property
    def title(self):
        title = [self.firstname.strip(), self.lastname.strip()]
        if getattr(self, 'security_state', None) == 'inactive':
            title += ['(Inactive)',]
        return unicode(' '.join(title))

    def get_alerts_preference(self, community_name):
        return self._alert_prefs.get(community_name,
                                     IProfile.ALERT_IMMEDIATELY)

    def set_alerts_preference(self, community_name, preference):
        if preference not in (
            IProfile.ALERT_IMMEDIATELY,
            IProfile.ALERT_DAILY_DIGEST,
            IProfile.ALERT_NEVER,
            IProfile.ALERT_WEEKLY_DIGEST,
            IProfile.ALERT_BIWEEKLY_DIGEST,
            ):
            raise ValueError("Invalid preference.")

        self._alert_prefs[community_name] = preference

    @apply
    def sso_id():
        def getter(self):
            return self._sso_id

        def setter(self, value):
            if value is not None:
                profiles = find_profiles(self)
                if profiles:
                    profiles.ssoid_to_name[value] = self.__name__
            self._sso_id = value

        return property(getter, setter)


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
        self.ssoid_to_name = CaseInsensitiveOOBTree()

    def getProfileByEmail(self, email):
        name = self.email_to_name.get(email)
        if name is not None:
            return self[name]

    def getProfileBySSOID(self, sso_id):
        name = self.ssoid_to_name.get(sso_id)
        if name is not None:
            # XXX Might have stale entries.  Do we care?
            return self.get(name)


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
            if isinstance(v, str):
                try:
                    v = v.decode('UTF8')
                except UnicodeDecodeError:
                    v = v.decode('latin1')
            text.append(unicode(v))
    text = '\n'.join(text)
    return lambda: (profile.title, text)
