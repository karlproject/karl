from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.interface import providedBy

from zope.component import getSiteManager

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import GlobalInterface

from zope.schema import TextLine

from repoze.lemonade.interfaces import IContent
from karl.sync.interfaces import IGenericContentFactory

def handler(methodName, *args, **kwargs):
    method = getattr(getSiteManager(), methodName)
    method(*args, **kwargs)

def addbase(iface1, iface2):
    if not iface2 in iface1.__iro__:
        iface1.__bases__ += (iface2,)
        return True
    return False

class HammerFactoryFactory(object):
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, other):
        return self.factory

class IGenericContentDirective(Interface):
    factory = GlobalObject(
        title=u"The generic factory that will create the content.",
        required=True
        )

    type = GlobalInterface(
        title=u"The type (an interface) that will be created by the factory",
        required=True)

def generic_content(_context, factory, type):

    if not IInterface.providedBy(type):
        raise ConfigurationError(
            'The provided "type" argument (%r) is not an '
            'interface object (it does not inherit from '
            'zope.interface.Interface' % type)

    _context.action(
        discriminator = ('content', type, IContent),
        callable = addbase,
        args = (type, IContent),
        )

    hammer = HammerFactoryFactory(factory)

    _context.action(
        discriminator = ('content', factory, type, IGenericContentFactory),
        callable = handler,
        args = ('registerAdapter',
                hammer, (type,), IGenericContentFactory, '', _context.info),
        )
