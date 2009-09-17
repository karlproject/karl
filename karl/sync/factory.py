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

import copy
import inspect
from zope.interface import directlyProvides
from zope.component import getAdapter
from zope.component import queryAdapter
from repoze.lemonade.interfaces import IContentFactory
from karl.sync.interfaces import IGenericContentFactory

class provides:
    """
    Hack stolen from Chris McDonough to work around issue that ZCA wants you
    to have an instance when doing adaptation.  Creates a dummy instance that
    provides the desired interface.
    """
    def __init__(self, iface):
        directlyProvides(self, iface)

def _signature(factory):
    if isinstance(factory, type):
        # If factory is a class, getargspec blows up because it isn't a
        # function, even though it is a callable.  We need to grab its
        # __init__ method, if defined.
        try:
            args, _, _, defaults = inspect.getargspec(factory.__init__)
        except TypeError:
            # If __init__ method isn't actually defined, it shows up as a
            # 'wrapper_desriptor' which will cause getargspec to fail with a
            # type error.  This really means there is no constructor defined
            # for this type so we have a no arg factory signature.
            return tuple(), tuple()
    else:
        args, _, _, defaults = inspect.getargspec(factory)

    args, kwargs = args[:len(defaults)], args[len(defaults):]
    return args, kwargs

def create_generic_content(iface, attrs):
    """
    Creates instance of a content type from dictionary of attributes.  ``iface``
    is the content type and ``attrs`` is the dictionary of attributes to use.
    If there is an implementation of IGenericContentFactory registered for the
    given type, that factory is used.  Otherwise an attempt is made to
    construct an instance by introspecting the IContentFactory registered
    with repoze.lemonade for the given type.  Arguments will be filled in with
    attributes of the same name from ``attrs``.  If not all of the attributes
    are used by the factory, each remaining attribute will be set via
    ``setattr`` after the content object has been constructed.
    """
    # Try registered generic factory
    generic_factory = queryAdapter(provides(iface), IGenericContentFactory)
    if generic_factory is not None:
        return generic_factory(attrs)

    # Didn't work, let's introspect repoze.lemonade factory
    attrs = copy.copy(attrs)
    factory = getAdapter(provides(iface), IContentFactory)
    args, kwargs = _signature(factory)
    argvalues, kwvalues = [], {}
    for name in args:
        argvalues.append(attrs.pop(name))
    for name in kwargs:
        if name in attrs:
            kwvalues[name] = attrs.pop(name)
    obj = factory(*argvalues, **kwvalues)

    # Set any attributes that didn't get passed to the factory
    for name, value in attrs.items():
        setattr(obj, name, value)

    return obj
