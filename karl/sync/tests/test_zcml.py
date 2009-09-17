import unittest
from zope.testing.cleanup import cleanUp

class TestGenericContentDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from karl.sync.zcml import generic_content
        return generic_content(*arg, **kw)

    def test_not_an_interface(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,None, None)

    def test_it(self):
        class Foo:
            def __init__(self, **kw):
                self.kw = kw

        from zope.interface import Interface
        from repoze.lemonade.interfaces import IContent
        from karl.sync.interfaces import IGenericContentFactory
        from karl.sync.zcml import addbase

        class IFoo(Interface):
            pass

        context = DummyContext()

        from karl.sync.zcml import handler

        self._callFUT(context, Foo, IFoo)

        self.assertEqual(len(context.actions), 2)

        provide = context.actions[0]
        self.assertEqual(provide['discriminator'],
                         ('content', IFoo, IContent))
        self.assertEqual(provide['callable'], addbase)
        self.assertEqual(provide['args'], (IFoo, IContent))

        register = context.actions[1]
        self.assertEqual(register['discriminator'],
                         ('content', Foo, IFoo, IGenericContentFactory))
        self.assertEqual(register['callable'], handler)
        self.assertEqual(register['args'][0], 'registerAdapter')
        self.assertEqual(register['args'][1].factory, Foo)
        self.assertEqual(register['args'][2], (IFoo,))
        self.assertEqual(register['args'][3], IGenericContentFactory)
        self.assertEqual(register['args'][4], '')
        self.assertEqual(register['args'][5], context.info)

class TestAddBase(unittest.TestCase):
    def _callFUT(self, I1, I2):
        from karl.sync.zcml import addbase
        return addbase(I1, I2)

    def test_already_in_iro(self):
        from repoze.lemonade.interfaces import IContent
        class IFoo(IContent):
            pass
        result = self._callFUT(IFoo, IContent)
        self.assertEqual(result, False)

    def test_not_in_iro(self):
        from zope.interface import Interface
        from repoze.lemonade.interfaces import IContent
        class IFoo(Interface):
            pass
        result = self._callFUT(IFoo, IContent)
        self.assertEqual(result, True)
        self.failUnless(IContent in IFoo.__bases__)
        self.failUnless(IContent in IFoo.__iro__)

class DummyContext:
    info = None
    def __init__(self):
        self.actions = []

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )
