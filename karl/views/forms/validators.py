import re

from lxml.html.clean import clean_html
from validatish import validate
from validatish.validator import Validator
from validatish.error import Invalid
from zope.component import getAdapter
from repoze.bfg.traversal import find_model
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_site
from karl.views.utils import make_name

class FolderNameAvailable(Validator):
    def __init__(self, container, exceptions=()):
        self.container = container
        self.exceptions = exceptions

    def __call__(self, v):
        if v in self.exceptions:
            return
        try:
            make_name(self.container, v)
        except ValueError, why:
            raise Invalid(why[0])
    
class NotOneOf(Validator):
    """ Checks whether value is not one of a supplied list of values"""
    def __init__(self, set_of_values):
        self.set_of_values = set_of_values

    def __call__(self, v):
        if v in set(self.set_of_values):
            raise Invalid('%s already exists' % v, validator=self)

class RegularExpression(Validator):
    """ Checks whether the value matches a regular expression """
    def __init__(self, regex, msg='Invalid'):
        self.expr = re.compile(regex)
        self.msg = msg

    def __call__(self, v):
        if v is not None:
            if not self.expr.match(v):
                raise Invalid(self.msg)

class PathExists(Validator):
    """ Ensures that a model object exists at the specified path,
    and that the model object is not the site root. """
    def __init__(self, context):
        self.context = context

    def __call__(self, v):
        if not v:
            return
        site = find_site(self.context)
        try:
            target = find_model(site, v)
        except KeyError, e:
            raise Invalid("Path not found: %s" % v)
        else:
            if target is site:
                raise Invalid("Path must not point to the site root")

class PasswordChecker(Validator):
    def __init__(self, min_pw_length):
        self.min_pw_length = min_pw_length
        
    def __call__(self, v):
        if v and len(v) < int(self.min_pw_length):
            fmt = "Password must be at least %s characters"
            msg = fmt % self.min_pw_length
            raise Invalid(msg, v)

class UniqueEmail(Validator):
    def __init__(self, context):
        self.context = context

    def __call__(self, v):
        if v:
            context = self.context
            # Let's not find conflicts with our own selves
            prev = getattr(context, 'email', None)
            if prev == v:
                # Nothing's changed, no need to check
                return

            search = getAdapter(context, ICatalogSearch)
            result = search(interfaces=[IProfile], email=[v.lower()],
                            limit=1)
            n = result[0]
            if n:
                raise Invalid(
                    'Email address is already in use by another user.')

class HTML(Validator):
    def __call__(self, v):
        if v:
            try:
                clean = clean_html(v)
            except:
                raise Invalid('Unable to parse the provided HTML')

class WebURL(Validator):
    """Custom web URL validation.  Value must either be empty or start
    with 'http://', 'https://', or 'www.'"""
    def __call__(self, v):
        if v:
            if v.startswith('www.'):
                v = 'http://%s' % v
            try:
                validate.is_url(v, with_scheme=True)
            except Invalid, e:
                msg = u"Must start with 'http://', 'https://', or 'www.'"
                raise Invalid(msg, validator=self)
