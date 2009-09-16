import unittest
from repoze.bfg import testing

def FactoryFactory(factory):
    def wrapper(object):
        return factory
    return wrapper

class TestCreateGenericContent(unittest.TestCase):
    def _call_it(self, iface, attrs):
        from karl.sync.factory import create_generic_content
        return create_generic_content(iface, attrs)

    def test_generic_factory(self):
        class GenericContent(object):
            def __init__(self, attrs):
                self.attrs = attrs

        from karl.sync.interfaces import IGenericContentFactory
        from zope.interface import Interface
        testing.registerAdapter(
            FactoryFactory(GenericContent), Interface, IGenericContentFactory)
        attrs = object()
        obj = self._call_it(Interface, attrs)
        self.failUnless(obj.attrs is attrs)
