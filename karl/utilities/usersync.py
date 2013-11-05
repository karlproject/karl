"""
=========================
Karl user synchronization
=========================

This document specifies a means of synchronizing users to Karl from an external
data source.  The external data source will make user data available in JSON
format at a particular URL.  The Karl user sync script will be download JSON
data from the external URL and use that data to: create new users, update
existing users, deactivate or reactivate existing users.  Note there is no
facility to delete a user from Karl.  This is a limitation of Karl and not of
the user sync facility.

JSON file format
----------------

The top level of the JSON data used by sync is a mapping with one required key
and two optional keys::

    {
        "timestamp": "2010-05-12T02:42:00",
        "deactivate_missing": false,
        "users": [
            ...
         ]
     }

The `timestamp` key is optional.  If provided it will be used on subsequent
requests to construct a query string appended to the URL used to download data.
If the URL where user data is provided is "http://example.com/users/", then the
first time user sync is done that URL will be called as-is.  If the
JSON data returned contains a `timestamp` key, the value of that key will be
used to construct a new URL:
"http://example.com/users/?timestamp=2010-05-12T2:42:00".

The format of the timestamp value is not important to Karl.  It will simply be
returned verbatim to the user data source.  It doesn't even technically have to
be a timestamp.  It could be a serial transaction id or anything else useful to
the user data source for knowing which data the Karl system has already seen.
It is the responsibility of the user data source to interpret the timestamp
such that only user data which has changed since the time indicated by the
timestamp is retunred to the Karl system.

Use of the timestamp is entirely optional for the user data source.

The `deactivate_missing` key, if provided and `true`, will cause Karl to
deactivate any users missing from the user data upload that are managed by the
user sync facility.  Karl keeps track of which users are managed by
the sync facility.  If a user is added to Karl by another avenue
and does not subsequently appear in any sync data, that user will not
be deactivated by the sync facility.

The `deactivate_missing` should not be set to `true` if the timestamp facility
is used.  Since use of the timestamp facility implies only a subset of user data
may be sent at any one time, then presence or absence of a user record can't be
used as a means of driving a decision to deactivate.  In this case, the
preferred method of deactivating a user using the sync facility is to set the
`active` key of the user record to `false`.

The `users` key is required and contains a sequence of user records.

User Records
------------

Each user record is a mapping.  Which keys are required depend on whether the
user is already in the sysem.  If a user is already in the system, only the
`username` key is required.  If a user is being added to the system, the
`first_name`, `last_name`, `email`, and `password` keys are also required.  Any
key missing from a record will not be changed by the sync facility.

The following keys may appear in a user record:

o `username` This key is always required.  The unique identifier for this user
  in the system.

o `firstname` The user's given name.  Required for new users.

o `lastname` The user's surname.  Required for new users.

o `email` The user's email address.  Required for new users.

o `password` This key is required only for new users.  Passwords must be SHA1
  hashed.  Required for new users or for reactivating a user.

o `login` This is the name used by users to login to Karl at the login page.
  It is presumed to be `username` if not specified.  This will not be remembered
  if the user is deactivated and later reactivated, so it will need to be sent
  again upon reactivation if it differs from `username`.

o `groups` This is a list of groups the user should be added to in Karl.  Valid
  groups are: `group.KarlAdmin`, `group.KarlStaff`, `group.KarlUserAdmin`,
  `group.KarlCommunications`.  These will not be remembered if the user is
  deactivated and later reactivated, so they will need to be sent again up
  reactivation if user is in any groups.

o `active` Whether or not the user is active in the system.  Presumed `true`
  if not provided.  Set this to `false` to deactivate a user.

o `phone` The user's phone number.

o `extension` The user's phone extension.

o `fax` The user's fax number.

o `department` The user's department.

o `position` The user's professional title.

o `organization` The user's organization.

o `location` The user's location.

o `country` The user's country.

o `websites` List of the user's websites.

o `languages` List of languages the user speaks.

o `office` The user's office.

o `room_no` The user's room number.

o `biography` Long form text about the user.

o `date_format` The user's preferred date format.  Use `en-US` for United States
  date format, or `en-GB` for European date format.  If all users use the same
  date format, the default can be specified globally for the entire Karl
  instance, rather than per user in the sync.

o `home_path` The path in Karl to the user's 'home'.  Should usually not be
  specified.

The following is an example of JSON data that could be returned from the user
data source.  Note that `wilma` and `dino` must already be Karl users::

    {
        "timestamp": "348ea92",
        "users": [
            {
                "username": "fred",
                "password": "SHA1:d033e22ae348aeb5660fc2140aec35850c4da997",
                "first_name": "Fred",
                "last_name": "Flintstone",
                "email": "fred@bedrock.town"
            },
            {
                "username": "barney",
                "password": "SHA1:d033e22ae348aeb5660fc2140aec35850c4da997",
                "first_name": "Barney",
                "last_name": "Rubble",
                "email": "barney@bedrock.town"
            },
            {
                "username": "wilma",
                "last_name": "Flintstone"
            },
            {
                "username": "dino",
                "active": false
            }
        ],
        "deactivate_missing": false
    }
"""
import base64
import hashlib
import json
import logging
import urllib
import urllib2

from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent
from karl.models.interfaces import IProfile
from karl.utils import find_profiles
from karl.utils import find_users
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow
from zope.component.event import objectEventNotify

DUPLICATE = object()
log = logging.getLogger(__name__)


class Empty(set):
    pass


class UserSync(object):
    profile_keys = [
        'firstname',
        'lastname',
        'email',
        'phone',
        'extension',
        'fax',
        'department',
        'position',
        'organization',
        'location',
        'country',
        'websites',
        'languages',
        'office',
        'room_no',
        'biography',
        'date_format',
        'home_path',
    ]
    required_keys = ['username']
    required_newuser_keys = ['firstname', 'lastname', 'email', 'password']

    def __init__(self, context):
        self.context = context

    def __call__(self, url, username=None, password=None):
        data = self.download_userdata(url, username, password)
        if data is not DUPLICATE:
            self.sync(data)
        else:
            log.info("User data has not changed.  No action required.")

    def download_userdata(self, url, username=None, password=None):
        timestamp = getattr(self.context, 'usersync_timestamp', None)
        if timestamp:
            url += '?' + urllib.urlencode({'timestamp': timestamp})
        if username:
            request = urllib2.Request(url)
            basic_auth = base64.encodestring('%s:%s' % (username, password))
            request.add_header('Authorization', 'Basic %s' % basic_auth)
        else:
            request = url
        data = urllib2.urlopen(request).read()
        digest = hashlib.sha1(data).digest()
        if getattr(self.context, 'usersync_sha1', None) == digest:
            return DUPLICATE
        return json.loads(data)

    def sync(self, data):
        context = self.context
        timestamp = data.pop('timestamp', None)
        if timestamp:
            context.usersync_timestamp = timestamp
        elif hasattr(context, 'usersync_timestamp'):
            del context.usersync_timestamp

        deactivate_missing = data.pop('deactivate_missing', False)
        if deactivate_missing:
            profiles = find_profiles(self.context)
            missing = set([p.__name__ for p in profiles.values()
                           if p.security_state == 'active' and
                              getattr(p, 'usersync_managed', False)])
        else:
            missing = Empty()

        users = data.pop('users')
        for user in users:
            self.syncuser(user, missing)
        if data:
            raise ValueError("Unrecognized keys in user sync data: %s" %
                             data.keys())

        if missing:
            users = find_users(self.context)
            for username in missing:
                profile = profiles[username]
                workflow = get_workflow(IProfile, 'security', profile)
                workflow.transition_to_state(profile, None, 'inactive')
                users.remove(username)

    def syncuser(self, data, missing):
        for key in self.required_keys:
            if not data.get(key):
                raise ValueError(
                    "Invalid user data: '%s' key is required" % key)
        users = find_users(self.context)
        profiles = find_profiles(self.context)
        username = data.pop("username")
        profile = profiles.get(username)
        active = profile and profile.security_state == 'active'
        if username in missing:
            missing.remove(username)
        if not profile:
            profile = self.createuser(data)
            self.update(profile, data)
            profiles[username] = profile
            activate = data.pop('active', 'true')
            security_state = 'active' if activate else 'inactive'
            log.info('Created user: %s', username)
        else:
            objectEventNotify(ObjectWillBeModifiedEvent(profile))
            self.update(profile, data)
            objectEventNotify(ObjectModifiedEvent(profile))
            activate = data.pop('active', None)
            if activate is not None:
                security_state = 'active' if activate else 'inactive'
            else:
                security_state = profile.security_state
                activate = active
            if type(missing) is Empty:
                log.info("Updated user: %s", username)
        profile.usersync_managed = True

        if active:
            info = users.get(username)
            password = data.pop('password', info['password'])
            groups = data.pop('groups', info['groups'])
            login = data.pop('login', info['login'])
            users.remove(username)

        elif activate:  # reactivate
            log.info("Reactivating user: %s", username)
            login = data.pop('login', username)
            password = data.pop('password', None)
            groups = data.pop('groups', [])
            if not password:
                raise ValueError(
                    "Invalid user data: 'password' key is required to "
                    "reactivate user")

        if activate:
            users.add(username, login, password, groups, encrypted=True)

        if security_state != getattr(profile, 'security_state', None):
            workflow = get_workflow(IProfile, 'security', profile)
            workflow.transition_to_state(profile, None, security_state)
            if security_state == 'inactive':
                log.info("Deactivated user: %s", username)

        if data:
            raise ValueError("Unrecognized keys in sync data for user: %s: %s" %
                             (username, data.keys()))

    def createuser(self, data):
        for key in ('firstname', 'lastname', 'email', 'password'):
            if not data.get(key):
                raise ValueError(
                    "Invalid user data: '%s' is required for new users" % key)
        return create_content(IProfile)

    def update(self, profile, data):
        for key in self.profile_keys:
            setattr(profile, key, data.pop(key, getattr(profile, key, None)))

