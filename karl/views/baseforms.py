"""Base class for KARL3 forms.
"""

from lxml.html import document_fromstring
from lxml.html import tostring
from lxml.html.clean import clean_html
from formencode import Schema
from formencode import Invalid
from formencode import validators
from copy import deepcopy
import time
import datetime
from zope.component import getAdapter
from karl.consts import countries
from karl.models.image import mimetypes as image_mimetypes
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_site
from repoze.bfg.traversal import find_model

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

class CountriesLookup(validators.UnicodeString):

    def _to_python(self, value, state):
        if value not in countries.as_dict:
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

class Taglist(validators.FancyValidator):
    """ Converter to return sequence of strings for each tagbox tag """
    # XXX This validator probably shouldn't exist
    def _from_python(self, value, state):
        return ' '.join(state.tags_list)

    def _to_python(self, value, state):
        # For now we just return the contents from the state.  But
        # later we might do some processing, e.g. sorting or reducing
        # duplicates.
        return state.tags_list

class PasswordChecker(validators.UnicodeString):

    def _to_python(self, value, state):
        # Check password length against the site configuration policy
        if value and len(value) < int(state.min_pw_length):
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
        try:
            # round the timestamp
            ts = self._round_datetime(value)
            # convert from timestamp to string
            return ts.strftime(self.datetime_format)
        except (AttributeError, ValueError):
            return None

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
    all_day_field = None
    __unpackargs__ = ('start_field', 'end_field', 'all_day_field')

    messages = {
        'invalid': _("End date must follow start date."),
        'invalid_duration': _("Event duration must be at least one minute"),
        }

    def validate_python(self, field_dict, state):
        start = field_dict[self.start_field]
        end = field_dict[self.end_field]
        errors = {}

        # can't end before start
        if end < start:
            errors[self.end_field] = self.message('invalid', state)

        # adjust for datetimes for all-day event
        elif field_dict[self.all_day_field] is True:
            field_dict[self.start_field] = datetime.datetime(
                start.year, start.month, start.day,
                0, 0, 0
            )
            
            field_dict[self.end_field] = datetime.datetime(
                end.year, end.month, end.day,
                0, 0, 0
            ) + datetime.timedelta(days=1) 
        
        # event must have some duration
        elif (end - start) < datetime.timedelta(minutes=1):
            errors[self.end_field] = self.message('invalid_duration', state)
            
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

class HomePath(validators.UnicodeString):
    """Validates a home path field value
    """

    def validate_python(self, value, state):
        super(HomePath, self).validate_python(value, state)

        context = getattr(state, "context", None)
        if value and context:
            site = find_site(context)
            try:
                target = find_model(site, value)
            except KeyError, e:
                raise Invalid(
                    "Path not found: %s" % value,
                    value, state)
            else:
                if target is site:
                    raise Invalid(
                        "Home path must not point to the site root",
                        value, state)

# Make some re-usable fields
login = validators.UnicodeString(not_empty=True, strip=True)
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
text = validators.UnicodeString(strip=True)
email = UniqueEmail(not_empty=True, resolve_domain=False)
add_comment = validators.UnicodeString(strip=True)
tags = Taglist(if_missing=[])
sendalert = validators.StringBool(if_missing=False)
# attachment is not validated through the form
description = validators.UnicodeString(not_empty=True, max=500)
overview = validators.UnicodeString(strip=True)
start_date = DateTime()
end_date = DateTime()
publication_date = DateTime()
security_state = validators.UnicodeString(strip=True)

start_end_constraints =  [StartEndFields(
                          start_field='startDate', end_field='endDate',
                          all_day_field='allDay')]

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

    def merge(self, htmlstring, fieldvalues, checkboxes=()):
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
            if field_name in checkboxes:
                form.fields[field_name] = bool(field_value)
                continue

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

