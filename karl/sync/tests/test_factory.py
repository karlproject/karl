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

    def test_instrospection_kwargs(self):
        class Foo(object):
            def __init__(self, a=None, b=None, c=None):
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

    def test_instrospection_args_and_kwargs(self):
        class Foo(object):
            def __init__(self, a, b, c, x=None, y=None, z=None):
                self._a = a
                self._b = b
                self._c = c
                self._x = x
                self._y = y
                self._z = z

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Foo, IFoo)

        attrs = dict(a='a', b='b', c='c', x='x', z='z')
        o = self._call_it(IFoo, attrs)
        self.failUnless(isinstance(o, Foo), repr(o))
        self.assertEqual(o._a, 'a')
        self.assertEqual(o._b, 'b')
        self.assertEqual(o._c, 'c')
        self.assertEqual(o._x, 'x')
        self.assertEqual(o._y, None)
        self.assertEqual(o._z, 'z')

    def test_instrospection_args_and_kwargs_w_extra_attrs(self):
        class Foo(object):
            def __init__(self, a, b, c, x=None, y=None, z=None):
                self._a = a
                self._b = b
                self._c = c
                self._x = x
                self._y = y
                self._z = z

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(Foo, IFoo)

        attrs = dict(a='a', b='b', c='c', x='x', z='z', name='chris')
        o = self._call_it(IFoo, attrs)
        self.failUnless(isinstance(o, Foo), repr(o))
        self.assertEqual(o._a, 'a')
        self.assertEqual(o._b, 'b')
        self.assertEqual(o._c, 'c')
        self.assertEqual(o._x, 'x')
        self.assertEqual(o._y, None)
        self.assertEqual(o._z, 'z')
        self.assertEqual(o.name, 'chris')

    def test_introspection_factory_function(self):
        class Foo(object):
            def __init__(self, *args):
                self.args = args

        def factory(a, b, c=None, d=None):
            return Foo(a, b, c, d)

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(factory, IFoo)

        attrs = dict(a='a', b='b', c='c', z='z')
        o = self._call_it(IFoo, attrs)
        self.failUnless(isinstance(o, Foo), repr(o))
        self.assertEqual(o.args[0], 'a')
        self.assertEqual(o.args[1], 'b')
        self.assertEqual(o.args[2], 'c')
        self.assertEqual(o.args[3], None)
        self.assertEqual(o.z, 'z')

    def test_introspection_factory_method(self):
        class Foo(object):
            def __init__(self, *args, **kw):
                self.args = args
                self.kw = kw

        class FactoryFactory(object):
            def factory(self):
                return Foo()

        from zope.interface import Interface
        class IFoo(Interface):
            pass

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(FactoryFactory().factory, IFoo)

        attrs = dict(a='a', b='b', c='c')
        o = self._call_it(IFoo, attrs)
        self.failUnless(isinstance(o, Foo), repr(o))
        self.assertEqual(o.a, 'a')
        self.assertEqual(o.b, 'b')
        self.assertEqual(o.c, 'c')
