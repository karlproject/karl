"""Base class for KARL3 forms.
"""

from lxml.html import document_fromstring
from lxml.html import tostring
from lxml.html.clean import clean_html
from formencode import Schema
from formencode import Invalid
from formencode import ForEach
from formencode import validators
from copy import deepcopy
import re
import time
import datetime
from karl.models.image import mimetypes as image_mimetypes

from zope.component import getAdapter
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile

valid_username_re = re.compile(r'[\w-]+$')

_ = validators._

class HTMLValidator(validators.UnicodeString):
    """ Parse and return a string of html """

    def _to_python(self, value, state):
        try:
            clean = clean_html(value)
        except:
            msg = 'Unable to parse the provided HTML'
            raise Invalid(msg, value, state)
        return clean

# Simulate getting some vocabularies
class UsernameLookup(validators.UnicodeString):

    def _to_python(self, value, state):
        if re.search('\s', value):
            msg = 'Username must not contain spaces'
            raise Invalid(msg, value, state)
        if not valid_username_re.match(value):
            msg = 'Username must contain only letters, numbers, and dashes'
            raise Invalid(msg, value, state)
        profiles = state.profiles
        if value in profiles:
            msg = 'Username %s already exists' % value
            raise Invalid(msg, value, state)
        return value

class CountriesLookup(validators.UnicodeString):

    def _to_python(self, value, state):
        vocabularies = state.vocabularies
        countries = vocabularies['countries']
        country_ids = [i[0] for i in countries]
        if value not in country_ids:
            msg = 'Unknown country code of %s' % value
            raise Invalid(msg, value, state)
        return value

class TextAreaToList(validators.UnicodeString):

    def _to_python(self, value, state):
        strip_option = getattr(self, 'strip', False)
        split_values = []
        for v in value.strip().splitlines():
            if strip_option:
                v2 = v.strip()
            else:
                v2 = v
            if v is not '':
                split_values.append(v2)

        return split_values

    def _from_python(self, value, state):
        return "\n".join(value)
    
class UserProfileLookup(validators.UnicodeString):

    def _to_python(self, value, state):
        strip_option = getattr(self, 'strip', False)
        split_values = []
        profiles = state.profiles

        # The username values are in the hidden fields for the
        # bubbles, not the single input that is this fieldname
        for v in state.usernames:
            if strip_option:
                v2 = v.strip()
            else:
                v2 = v
            # Lookup profiles
            profile = profiles.get(v2, False)
            if profile is False:
                msg = 'Username %s does not exist' % v
                raise Invalid(msg, value, state)
            split_values.append(profile)

        return split_values

class NotOneOf(validators.UnicodeString):

    messages = {
        'known_value': 'Value %(value)s matches existing value',
        }

    def validate_python(self, value, state):
        if value in self.known_values:
            msg = self.message('known_value', state, value=value)
            raise Invalid(msg, value, state)
        return value

class TextAreaToEmails(validators.UnicodeString):

    def _to_python(self, value, state):
        v1 = TextAreaToList(strip=True, not_empty=True)
        lines = v1.to_python(value, state)
        v2 = ForEach(validators.Email(), NotOneOf(known_values=state.emails))
        return v2.to_python(lines)

class Taglist(validators.FancyValidator):
    """ Converter to return sequence of strings for each tagbox tag """

    def _to_python(self, value, state):
        # For now we just return the contents from the state.  But
        # later we might do some processing, e.g. sorting or reducing
        # duplicates.
        return state.tags_list

class PasswordChecker(validators.UnicodeString):

    def _to_python(self, value, state):
        # Check password length against the site configuration policy
        if len(value) < state.min_pw_length:
            fmt = "Password must be at least %s characters"
            msg = fmt % state.min_pw_length
            raise Invalid(msg, value, state)
        return value

class Photo(validators.FieldStorageUploadConverter):
    invalid_message = u"Image file must be jpeg, gif or png"
    def _to_python(self, value, state):
        if value.type not in image_mimetypes:
            raise Invalid(self.invalid_message, value, state)

        return super(Photo, self)._to_python(value, state)
        
class DateTime(validators.FancyValidator):
    """Convert dates"""
    datetime_format = '%m/%d/%Y %H:%M'
    round_minutes = 15
    
    messages = {
        'invalid': _("Invalid date. Date must have a format mm/dd/yyyy, HH:MM." \
                     "<br>Example: 3/21/2009 18:30"),
        }

    def _to_python(self, value, state):
        try:
            # convert from string to timetuple
            timetuple = time.strptime(value, self.datetime_format)
        except ValueError, exc:
            raise Invalid(self.message('invalid', state),
                    value, state)
        ts = datetime.datetime(*timetuple[0:5])
        # round the resulting timestamp
        ts = self._round_datetime(ts)
        return ts

    def _from_python(self, value, state):
        # round the timestamp
        ts = self._round_datetime(value)
        # convert from timestamp to string
        return ts.strftime(self.datetime_format)

    def _round_datetime(self, ts=None):
        """Round the datetime to quarters of hours"""
        round_minutes = self.round_minutes
        rounded_ts = ts.replace(
            minute = ts.minute / round_minutes * round_minutes,
            second = 0,
            microsecond = 0,
            )
        return rounded_ts

class StartEndFields(validators.FormValidator):
    """
    """

    start_field = None
    end_field = None
    __unpackargs__ = ('start_field', 'end_field')

    messages = {
        'invalid': _("End date must follow start date."),
        }
    
    def validate_python(self, field_dict, state):
        start = field_dict[self.start_field]
        end = field_dict[self.end_field]
        errors = {}
        if end < start:
            errors[self.end_field] = self.message('invalid', state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict, state,
                          error_dict=errors)

class UniqueEmail(validators.Email):
    """ Performs email validation, also insuring email address does not
    conflict with another user's email address.
    """
    
    def validate_python(self, value, state):
        super(UniqueEmail, self).validate_python(value, state)

        context = getattr(state, "context", None)
        if value and context:
            # Let's not find conflicts with our own selves
            prev = getattr(context, "email", None)
            if prev == value:
                # Nothing's changed, no need to check
                return
                
            # Search catalog for matching emails
            search = getAdapter(context, ICatalogSearch)
            result = search(interfaces=[IProfile], email=[value.lower()], 
                            limit=1)
            n = result[0]
            if n:
                raise Invalid(
                    "Email address is already in use by another user.",
                     value, state)

# Make some re-usable fields
login = validators.UnicodeString(not_empty=True, strip=True)
username = UsernameLookup(not_empty=True, strip=True)
old_password = validators.UnicodeString(not_empty=True, strip=True)
password = PasswordChecker(not_empty=True, strip=True)
password_confirm = validators.UnicodeString(not_empty=True, strip=True)
chained_validators = [validators.FieldsMatch(
        'password', 'password_confirm')]
title = validators.UnicodeString(not_empty=True, strip=True)
firstname = validators.UnicodeString(not_empty=True, strip=True)
lastname = validators.UnicodeString(not_empty=True, strip=True)
phone = validators.UnicodeString(strip=True)
extension = validators.UnicodeString(strip=True)
organization = validators.UnicodeString(strip=True)
location = validators.UnicodeString(strip=True)
country = CountriesLookup(strip=True)
department = validators.UnicodeString(strip=True)
position = validators.UnicodeString(strip=True)
website = validators.URL(strip=True)
languages = validators.UnicodeString(strip=True)
room_no = validators.UnicodeString(strip=True)
office = validators.UnicodeString(strip=True)
biography = validators.UnicodeString(strip=True)
photo = Photo()
caption = validators.UnicodeString(strip=True)
photo_delete = validators.Bool(if_missing=False, default=False)
terms_and_conditions = validators.StringBool(not_empty=True)
accept_privacy_policy = validators.StringBool(not_empty=True)
users = UserProfileLookup(not_empty=True, strip=True)
text = validators.UnicodeString(strip=True)
email = UniqueEmail(not_empty=True, resolve_domain=False)
email_addresses = TextAreaToEmails(not_empty=True, strip=True)
profile_id = validators.UnicodeString(not_empty=True)
is_moderator = validators.Bool(if_missing=False)
resend_info = validators.Bool(if_missing=False)
remove_entry = validators.Bool(if_missing=False)
add_comment = validators.UnicodeString(strip=True)
tags = Taglist(if_missing=[])
sendalert = validators.StringBool(if_missing=False)
# attachment is not validated through the form
description = validators.UnicodeString(not_empty=True, max=500)
overview = validators.UnicodeString(strip=True)
sharing = validators.StringBool(not_empty=True)
start_date = DateTime()
end_date = DateTime()
publication_date = DateTime()

start_end_constraints =  [StartEndFields(
                          start_field='startDate', end_field='endDate')]

class AppState(object):
    """ Provide keyword-based initialization of FormEncode app state"""

    def __init__(self, *args, **kw):
        for key in kw:
            setattr(self, key, kw[key])

class BaseForm(Schema):

    allow_extra_fields = True
    filter_extra_fields = True
    is_valid = None

    def __init__(self, formdata, submit='form.submitted', 
                 cancel='form.cancel'):
        Schema.__init__(self)
        self.defaults = {}
        for name, value in self.fields.items():
            default = getattr(value, 'default', None)
            if default is not None:
                self.defaults[name] = value.default
        self.formdata = formdata
        self.submit = submit
        self.cancel = cancel

        # Merge field defaults with any request.POST data passed in
        self.fieldvalues = deepcopy(self.defaults)
        for key, value in self.formdata.items():
            self.fieldvalues[key] = value

    def merge(self, htmlstring, fieldvalues):
        # Merge in field values, either from the default or from what
        # they typed in.

        # If there are no values to merge or if the htmlstring is
        # empty (for unit testing), return the string
        if not fieldvalues or not htmlstring:
            return htmlstring

        form_tree = document_fromstring(htmlstring)
        form = form_tree.forms[0]

        schema_field_names = self.fields.keys()
        for field_name, field_value in fieldvalues.items():
            fv = field_value
            if isinstance(fv, str):
                # Reverse the encoding performed by UnicodeString.
                # XXX This is an ugly workaround. UnicodeString encodes
                # the field value and then the code below immediately
                # decodes it again. We don't want UnicodeString to
                # encode the string at all. Unfortauntely, FormEncode
                # 1.0.1 doesn't provide a way to turn off the encoding.
                # Only the FormEncode trunk (>1.2.2) has the needed
                # feature.
                ufv = fv.decode('utf-8')
            else:
                ufv = unicode(fv)
            field_false = (ufv == u'') or (fv is False) or (fv is None)
            if not field_false and field_name in schema_field_names:
                form.fields[field_name] = ufv

        merged_form_html = tostring(form)

        return merged_form_html
