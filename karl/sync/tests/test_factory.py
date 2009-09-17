import unittest
from zope.testing.cleanup import cleanUp
from repoze.bfg import testing

def FactoryFactory(factory):
    def wrapper(object):
        return factory
    return wrapper

class TestCreateGenericContent(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

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

    def test_introspection_no_args(self):
        class Foo(object):
            pass

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Foo, IFoo)

        o = self._call_it(IFoo, {})
        self.failUnless(isinstance(o, Foo), repr(o))

    def test_introspection_no_args_extra_attrs(self):
        class Foo(object):
            pass

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Foo, IFoo)

        attrs = dict(a='a', b='b', c='c')
        o = self._call_it(IFoo, attrs)
        self.failUnless(isinstance(o, Foo), repr(o))
        self.assertEqual(o.a, 'a')
        self.assertEqual(o.b, 'b')
        self.assertEqual(o.c, 'c')

    def test_instrospection_args(self):
        class Foo(object):
            def __init__(self, a, b, c):
                self._a = a
                self._b = b
                self._c = c

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Foo, IFoo)

        attrs = dict(a='a', b='b', c='c')
        o = self._call_it(IFoo, attrs)
        self.failUnless(isinstance(o, Foo), repr(o))
        self.assertEqual(o._a, 'a')
        self.assertEqual(o._b, 'b')
        self.assertEqual(o._c, 'c')
