import unittest
import schemaish
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

class TestTagsWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from karl.views.forms.widgets import TagsWidget
        return TagsWidget(**kw)

    def test_json_taginfo(self):
        widget = self._makeOne(tagdata={'records':[{'tag':'a'}]})
        result = widget.json_taginfo(['a', 'b'])
        self.assertEqual(
            result,
            '{"records": [{"tag": "a"}, '
            '{"count": 1, "snippet": "", "tag": "b"}]}')

    def test_to_request_data(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.to_request_data(field, 'a')
        self.assertEqual(result, ['a'])

    def test_from_request_data(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.from_request_data(field, ['a', '', 'b'])
        self.assertEqual(result, ['a', 'b'])

class TestUserProfileLookupWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from karl.views.forms.widgets import UserProfileLookupWidget
        return UserProfileLookupWidget(**kw)

    def test_it(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.from_request_data(field, ['a', '', 'b'])
        self.assertEqual(result, ['a', 'b'])

class TestFolderNameAvailableValidator(unittest.TestCase):
    def _makeOne(self, container, exceptions=()):
        from karl.views.forms.validators import FolderNameAvailable
        return FolderNameAvailable(container, exceptions)

    def test_fail(self):
        from validatish.error import Invalid
        container = testing.DummyModel()
        container['foo'] = testing.DummyModel()
        validator = self._makeOne(container)
        self.assertRaises(Invalid, validator, 'foo')

    def test_exception_success(self):
        container = testing.DummyModel()
        container['foo'] = testing.DummyModel()
        validator = self._makeOne(container, exceptions=('foo',))
        self.assertEqual(validator('foo'), None)

class TestNotOneOfValidator(unittest.TestCase):
    def _makeOne(self, set_of_values):
        from karl.views.forms.validators import NotOneOf
        return NotOneOf(set_of_values)

    def test_fail(self):
        from validatish.error import Invalid
        container = testing.DummyModel()
        validator = self._makeOne(('a', 'b'))
        self.assertRaises(Invalid, validator, 'a')

class TestRegularExpressionValidator(unittest.TestCase):
    def _makeOne(self, regex, msg):
        from karl.views.forms.validators import RegularExpression
        return RegularExpression(regex, msg)

    def test_fail(self):
        from validatish.error import Invalid
        validator = self._makeOne('a', 'not valid')
        self.assertRaises(Invalid, validator, 'b')

    def test_nofail(self):
        validator = self._makeOne('a', 'not valid')
        self.assertEqual(validator('a'), None)

class TestPathExistsValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()
        site = self.site = testing.DummyModel()
        context = self.context = testing.DummyModel()
        site['context'] = context

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context):
        from karl.views.forms.validators import PathExists
        return PathExists(context)

    def test_found(self):
        validator = self._makeOne(self.site)
        self.assertEqual(validator('/context'), None)

    def test_notfound(self):
        from validatish.error import Invalid
        validator = self._makeOne(self.site)
        self.assertRaises(Invalid, validator, '/doesnotexist')

    def test_foundsite(self):
        from validatish.error import Invalid
        validator = self._makeOne(self.site)
        self.assertRaises(Invalid, validator, '/')

class TestPasswordCheckerValidator(unittest.TestCase):
    def _makeOne(self, min_pw_length):
        from karl.views.forms.validators import PasswordChecker
        return PasswordChecker(min_pw_length)

    def test_fail(self):
        from validatish.error import Invalid
        validator = self._makeOne(6)
        self.assertRaises(Invalid, validator, 'secre')

    def test_nofail(self):
        validator = self._makeOne(6)
        self.assertEqual(validator('secret'), None)

class TestUniqueEmailValidator(unittest.TestCase):
    def setUp(self):
        cleanUp()
        self.context = testing.DummyModel()
        from karl.testing import registerCatalogSearch
        registerCatalogSearch()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context):
        from karl.views.forms.validators import UniqueEmail
        return UniqueEmail(context)

    def test_fail(self):
        from validatish.error import Invalid
        validator = self._makeOne(self.context)
        self.assertRaises(Invalid, validator, 'match@x.org')

    def test_nofail(self):
        validator = self._makeOne(self.context)
        self.assertEqual(validator('nomatch@x.org'), None)

    def test_nofail_on_self_match(self):
        email = 'match@x.org'
        self.context.email = email
        validator = self._makeOne(self.context)
        self.assertEqual(validator(email), None)

class TestHTMLValidator(unittest.TestCase):
    def _makeOne(self):
        from karl.views.forms.validators import HTML
        return HTML()

    def test_fail(self):
        from validatish.error import Invalid
        validator = self._makeOne()
        bad_html = "</failure>"
        self.assertRaises(Invalid, validator, bad_html)

    def test_nofail(self):
        validator = self._makeOne()
        good_html = "<html><body> is well formed </body></html>"
        self.assertEqual(validator(good_html), None)

class TestWebURLValidator(unittest.TestCase):
    def _makeOne(self):
        from karl.views.forms.validators import WebURL
        return WebURL()

    def test_fail(self):
        from validatish.error import Invalid
        validator = self._makeOne()
        self.assertRaises(Invalid, validator, 'http:/something.com')
        self.assertRaises(Invalid, validator, 'something.com')
        self.assertRaises(Invalid, validator, 'http://')

    def test_nofail(self):
        validator = self._makeOne()
        self.assertEqual(validator('http://s'), None)
        self.assertEqual(validator('https://s'), None)
        self.assertEqual(validator('http://something.com'), None)
        self.assertEqual(validator('www.fooo.com'), None)
        # empty is okay too
        self.assertEqual(validator(''), None)

class TestAcceptFieldWidget(unittest.TestCase):
    def _makeOne(self, text, description, **kw):
        from karl.views.forms.widgets import AcceptFieldWidget
        return AcceptFieldWidget(text, description, **kw)

    def test_it(self):
        widget = self._makeOne('text', 'description')
        self.assertEqual(widget.text, 'text')
        self.assertEqual(widget.description, 'description')

class TestZODBFileStore(unittest.TestCase):
    def _makeOne(self, mapping):
        from karl.views.forms.filestore import ZODBFileStore
        return ZODBFileStore(mapping)

    def test_get_present(self):
        mapping = {'a':([], '', DummyBlob())}
        filestore = self._makeOne(mapping)
        result = filestore.get('a')
        self.assertEqual(result, ('', [], True))

    def test_get_absent(self):
        mapping = {}
        filestore = self._makeOne(mapping)
        result = filestore.get('a')
        self.assertEqual(result, (None, [], None))

    def test_put_no_headers(self):
        from StringIO import StringIO
        io = StringIO('the data')
        mapping = {}
        filestore = self._makeOne(mapping)
        filestore.put('a', io, 'tag')
        headers, cache_tag, blobfile = mapping['a']
        self.assertEqual(headers, ())
        self.assertEqual(cache_tag, 'tag')
        self.assertEqual(blobfile.open('r').read(), 'the data')

    def test_put_with_headers(self):
        from StringIO import StringIO
        io = StringIO('the data')
        mapping = {}
        filestore = self._makeOne(mapping)
        filestore.put('a', io, 'tag', [('a', '1')])
        headers, cache_tag, blobfile = mapping['a']
        self.assertEqual(headers, [('a', '1')])
        self.assertEqual(cache_tag, 'tag')
        self.assertEqual(blobfile.open('r').read(), 'the data')

    def test_delete_exists(self):
        mapping = {'a':1}
        filestore = self._makeOne(mapping)
        filestore.delete('a')
        self.failIf('a' in mapping)

    def test_delete_missing(self):
        mapping = {}
        filestore = self._makeOne(mapping)
        self.assertRaises(KeyError, filestore.delete, 'a')

class TestFileUpload2(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from karl.views.forms.widgets import FileUpload2
        return FileUpload2(*arg, **kw)

    def test_ctor(self):
        filestore = 'abc'
        widget = self._makeOne(filestore)
        self.assertEqual(widget.filestore, 'abc')

    def test_from_request_data_no_name(self):
        from schemaish.type import File as SchemaFile
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        field = DummyField()
        result = widget.from_request_data(field, {'name':[''], 'remove':[True]})
        self.assertEqual(result.__class__, SchemaFile)
        self.assertEqual(result.metadata, {'default': None, 'name': '',
                                           'remove': True})

    def test_from_request_data_name_equals_default(self):
        from schemaish.type import File as SchemaFile
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        field = DummyField()
        result = widget.from_request_data(field,
                                          {'name':['abc'], 'default':['abc']})
        self.assertEqual(result.__class__, SchemaFile)
        self.assertEqual(result.metadata, {})
        self.assertEqual(result.filename, None)

    def test_from_request_data_name_equals_default_with_upload(self):
        from schemaish.type import File as SchemaFile
        filestore = DummyFileStore()
        filestore['abc'] = ('tag', [('Filename', 'abc'), ('Content-Type',
                                     'content-type')], 'file')
        widget = self._makeOne(filestore)
        field = DummyField()
        storage = DummyFieldStorage()
        result = widget.from_request_data(field,
                                          {'name':['abc'], 'default':['abc'],
                                           'file': [storage]})
        self.assertEqual(result.__class__, SchemaFile)
        self.assertEqual(result.metadata, {})
        self.assertEqual(result.filename, 'abc')

    def test_from_request_data_name_notequal_default_missing(self):
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        field = DummyField()
        result = widget.from_request_data(field,
                                          {'name':['abc'], 'default':['def']})
        self.assertEqual(result, None)

    def test_from_request_data_name_notequal_default(self):
        from schemaish.type import File as SchemaFile
        filestore = DummyFileStore()
        filestore['abc'] = ('tag', [('Filename', 'filename'), ('Content-Type',
                                     'content-type')], 'file')
        widget = self._makeOne(filestore)
        field = DummyField()
        result = widget.from_request_data(field,
                                          {'name':['abc'], 'default':['def']})
        self.assertEqual(result.__class__, SchemaFile)
        self.assertEqual(result.file, 'file')
        self.assertEqual(result.filename, 'filename')
        self.assertEqual(result.mimetype, 'content-type')

    def test_pre_parse_incoming_request_data_None(self):
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        field = DummyField()
        result = widget.pre_parse_incoming_request_data(field, None)
        self.assertEqual(result, {})
        
    def test_pre_parse_incoming_request_data_remove(self):
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        field = DummyField()
        data = {'remove':[True]}
        result = widget.pre_parse_incoming_request_data(field, data)
        self.assertEqual(result['name'], [''])
        self.assertEqual(result['mimetype'], [''])

    def test_pre_parse_incoming_request_data_with_file(self):
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        field = DummyField()
        storage = DummyFieldStorage()
        data = {'file':[storage]}
        result = widget.pre_parse_incoming_request_data(field, data)
        self.assertEqual(result['name'], ['bar.txt'])
        self.assertEqual(result['mimetype'], ['type'])

    def test_to_request_data_with_schemafile(self):
        from schemaish.type import File as SchemaFile
        field = DummyField()
        f = SchemaFile('1', '2', '3')
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        result = widget.to_request_data(field, f)
        self.assertEqual(result['name'], ['2'])
        self.assertEqual(result['default'], ['2'])
        self.assertEqual(result['mimetype'], ['3'])
        
    def test_to_request_data_with_none_schemafile(self):
        field = DummyField()
        f = None
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        result = widget.to_request_data(field, f)
        self.assertEqual(result['name'], [''])
        self.assertEqual(result['default'], [''])
        self.assertEqual(result['mimetype'], [''])

    def test_urlfactory_with_data(self):
        data = 'b/d'
        filestore = DummyFileStore()
        widget = self._makeOne(filestore)
        result = widget.urlfactory(data)
        self.assertEqual(result, '/filehandler/b/d')
        
    def test_urlfactory_with_no_data(self):
        filestore = DummyFileStore()
        widget = self._makeOne(filestore, image_thumbnail_default='1')
        result = widget.urlfactory(None)
        self.assertEqual(result, '1')

class Test_get_filestore(unittest.TestCase):
    def _callFUT(self, context, request, form_id):
        from karl.views.forms.filestore import get_filestore
        return get_filestore(context, request, form_id)

    def test_it_present(self):
        from karl.views.forms.filestore import ZODBFileStore
        sessions = DummySessions()
        sessions['1'] = {'formid':{'a':1}}
        context = testing.DummyModel(sessions=sessions)
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        result = self._callFUT(context, request, 'formid')
        self.assertEqual(result.__class__, ZODBFileStore)
        self.assertEqual(result.persistent_map, {'a':1})

    def test_it_missing(self):
        from karl.views.forms.filestore import ZODBFileStore
        from persistent.mapping import PersistentMapping
        sessions = DummySessions()
        context = testing.DummyModel(sessions=sessions)
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        result = self._callFUT(context, request, 'formid')
        self.assertEqual(result.__class__, ZODBFileStore)
        self.assertEqual(result.persistent_map.__class__, PersistentMapping)

class Test_KarlDateTime(unittest.TestCase):
    def test_can_create(self):
        from karl.views.forms.attr import KarlDateTime
        kdt = KarlDateTime()
        self.assertEqual(kdt.type, 'KarlDateTime')

class Test_KarlDateTimeToStringConverter(unittest.TestCase):
    def _makeOne(self):
        from karl.views.forms.convert import KarlDateTimeToStringConverter
        return KarlDateTimeToStringConverter('KarlDateTime')

    def test_from_type(self):
        from datetime import datetime
        converter = self._makeOne()
        dt = datetime(2010, 3, 14, 1, 59, 26)
        converted = converter.from_type(dt)
        self.assertEqual(converted, '03/14/2010 01:45')

    def test_to_type(self):
        from datetime import datetime
        converter = self._makeOne()
        converted = converter.to_type('03/14/2010 01:45')
        self.assertEqual(converted, datetime(2010, 3, 14, 1, 45, 0, 0))
        from convertish.convert import ConvertError
        self.assertRaises(ConvertError, converter.to_type, 'bo/gus/val')
        self.assertRaises(ConvertError, converter.to_type, '12/12')
        self.assertRaises(ConvertError, converter.to_type, '12/21/2012 1212')

class DummyAttr:
    def __init__(self):
        self.attr = schemaish.String()

class DummyField:
    def __init__(self):
        self.attr = DummyAttr()
        
class DummyBlob:
    def open(self, mode):
        return True
    
class DummyFileStore(dict):
    def put(self, key, value, name, headers=()):
        self[key] = (value, name, headers)
        
class DummyFieldStorage(object):
    filename = 'c:\\fuz\\foo\\bar.txt'
    file = 'file'
    type = 'type'
    
class DummySessions(dict):
    def get(self, name, default=None):
        if not name in self:
            self[name] = {}
        return self[name]
    
