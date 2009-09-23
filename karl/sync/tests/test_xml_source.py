import unittest

class XMLContentSourceTests(unittest.TestCase):
    def _target_class(self):
        from karl.sync.xml_source import XMLContentSource
        return XMLContentSource

    def _make_one(self, test_file='test_xml_source_1.xml'):
        import pkg_resources
        stream = pkg_resources.resource_stream(__name__, test_file)
        assert stream is not None
        return self._target_class()(stream)

    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.sync.interfaces import IContentSource
        verifyClass(IContentSource, self._target_class())

    def test_instance_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.sync.interfaces import IContentSource
        verifyObject(IContentSource, self._make_one())

    def test_import(self):
        from karl.sync.xml_source import XMLContentSource

    def test_location(self):
        o = self._make_one()
        self.assertEqual(o.location, 'http://foo.com/bar')

    def test_incremental(self):
        o = self._make_one()
        self.assertTrue(o.incremental)

    def test_content(self):
        o = self._make_one()
        self.assertEqual(2, len(list(o.content)))

    def test_deleted_content(self):
        o = self._make_one()
        self.assertEqual(o.deleted_content,
                         ['64071160-f25e-4221-a2d7-cd85b76395fb',
                          'a66af600-718c-4f60-ad78-63dc7018de78'])

    def test_relaxng_validates(self):
        import lxml.etree
        import pkg_resources

        schema = lxml.etree.RelaxNG(lxml.etree.parse(
            pkg_resources.resource_stream(__name__, 'karl_export.rng')
            ))

        doc = lxml.etree.parse(
            pkg_resources.resource_stream(__name__, 'test_xml_source_1.xml')
            )

        self.failUnless(schema.validate(doc))

    def test_nodes(self):
        o = self._make_one()
        self.assertEqual(1, len(list(o.nodes)))

class XMLContentItemTests(unittest.TestCase):
    def _make_some(self, test_file='test_xml_source_1.xml'):
        import pkg_resources
        stream = pkg_resources.resource_stream(__name__, test_file)
        assert stream is not None

        from karl.sync.xml_source import XMLContentSource
        return XMLContentSource(stream).content


    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.sync.interfaces import IContentItem
        from karl.sync.xml_source import XMLContentItem
        verifyClass(IContentItem, XMLContentItem)

    def test_instance_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.sync.interfaces import IContentItem
        verifyObject(IContentItem, self._make_some().next())

    def test_id(self):
        o = self._make_some().next()
        self.assertEqual(o.id, '765b078b-ccd7-4bb0-a197-ec23d03be430')

    def test_name(self):
        o = self._make_some().next()
        self.assertEqual(o.name, 'why-radio-is-awesome')

    def test_type(self):
        o = self._make_some().next()
        from karl.models.interfaces import IProfile
        self.assertEqual(o.type, IProfile)

    def test_type_no_sys_modules(self):
        from karl.models.interfaces import IProfile
        o = self._make_some().next()

        import sys
        save_modules = sys.modules
        sys.modules = {}
        try:
            self.assertEqual(o.type, IProfile)
        finally:
            sys.modules = save_modules

    def test_workflow_state(self):
        o = self._make_some().next()
        self.assertEqual(o.workflow_state, 'inherit')

    def test_created(self):
        import datetime
        import pytz
        o = self._make_some().next()
        expected = datetime.datetime(2009, 9, 9, 18, 28, 3,
                                     tzinfo=pytz.FixedOffset(-300))
        self.assertEqual(o.created, expected)

    def test_created_not_specified(self):
        import datetime
        now = datetime.datetime.now()
        window = datetime.timedelta(seconds=2)
        o = list(self._make_some())[1]
        self.failUnless(o.created - now < window)

    def test_created_by(self):
        o = self._make_some().next()
        self.assertEqual(o.created_by, 'crossi')

    def test_modified(self):
        import datetime
        import pytz
        o = self._make_some().next()
        expected = datetime.datetime(2009, 9, 9, 18, 28, 3,
                                     tzinfo=pytz.FixedOffset(-300))
        self.assertEqual(o.modified, expected)

    def test_modified_not_specified(self):
        import datetime
        now = datetime.datetime.now()
        window = datetime.timedelta(seconds=2)
        o = list(self._make_some())[1]
        self.failUnless(o.modified - now < window)

    def test_modified_by(self):
        o = self._make_some().next()
        self.assertEqual(o.modified_by, 'crossi')

    def test_attributes(self):
        o = self._make_some().next()
        attrs = o.attributes
        self.assertEqual(attrs['title'], u'Why Radio is Awesome')
        self.assertEqual(attrs['text'],
                         u'La radio \xe8 straordinaria perch\xe9 ...')
        self.assertEqual(attrs['description'], None)
        self.assertEqual(attrs['colors'], [u'Red', u'Green', u'Blue'])
        self.assertEqual(attrs['animals'], {
            'Clio': u'cat',
            'Ginger': u'cat',
            'Elsa': u'dog',
            })

    def test_children(self):
        o = list(self._make_some())[1]
        children = list(o.children)
        self.assertEqual(len(children), 1)
        child = children[0]
        self.assertEqual(child.id, '234jjlkj3423')
        self.assertEqual(child.name, 'some-doc-in-folder')

    def test_deleted_children(self):
        o = list(self._make_some())[1]
        self.assertEqual(o.deleted_children, ['abc123'])

class XMLContentNodeTests(unittest.TestCase):
    def setUp(self):
        import pkg_resources
        from karl.sync.xml_source import XMLContentSource
        test_file = 'test_xml_source_1.xml'
        stream = pkg_resources.resource_stream(__name__, test_file)
        self.source =  XMLContentSource(stream)

    def test_class_conforms_to_interface(self):
        from zope.interface.verify import verifyClass
        from karl.sync.interfaces import IContentNode
        from karl.sync.xml_source import XMLContentNode
        verifyClass(IContentNode, XMLContentNode)

    def test_instance_conforms_to_interface(self):
        from zope.interface.verify import verifyObject
        from karl.sync.interfaces import IContentNode
        verifyObject(IContentNode, list(self.source.nodes)[0])

    def test_name(self):
        node = list(self.source.nodes)[0]
        self.assertEqual(node.name, 'foo')

    def test_nodes(self):
        node = list(self.source.nodes)[0]
        nodes = list(node.nodes)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, 'bar')

    def test_content(self):
        node = list(self.source.nodes)[0]
        content = list(node.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].name, 'some-folder')

    def test_deleted_content(self):
        node = list(self.source.nodes)[0]
        self.assertEqual(node.deleted_content, ['abc123'])

class MemoizeTests(unittest.TestCase):
    def test_it(self):
        from karl.sync.xml_source import memoize

        class Foo(object):
            count = 0

            @property
            @memoize
            def f(self):
                self.count += 1
                return self.count

        foo = Foo()
        self.assertEqual(foo.f, 1)
        self.assertEqual(foo.f, 1) # doesn't increment