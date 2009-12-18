import re

from validatish.validator import Validator
from validatish.error import Invalid
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
