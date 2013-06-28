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

import unittest
from pyramid import testing
from karl import testing as karltesting
from zope.interface import implements
from karl.utilities.interfaces import ISpellChecker

class TinyMceSpellCheckViewTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        karltesting.registerUtility(DummySpellChecker, iface=ISpellChecker)

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.spellcheck import tinymce_spellcheck_view
        return tinymce_spellcheck_view(context, request)

    def test_renders_error_response_for_unsupported_language(self):
        from simplejson import JSONEncoder
        rpc_request = {'id':None, 'method':'checkWords', 
                       'params':['za',['foo','bar']]}
        json = JSONEncoder().encode(rpc_request)

        request = testing.DummyRequest(method='POST', body=json)
        data = self._callFUT(testing.DummyModel(), request)
        self.assertEquals(data['id'], None)
        self.assertEquals(data['result'], [])
        self.assertEquals(data['error'], 'Language is not supported')
    
    def test_renders_misspelled_words_for_checkWords_request(self):
        from simplejson import JSONEncoder
        rpc_request = {'id':None, 'method':'checkWords', 
                       'params':['en',['foo','bar']]}
        json = JSONEncoder().encode(rpc_request)

        request = testing.DummyRequest(method='POST', body=json)
        data = self._callFUT(testing.DummyModel(), request)
        self.assertEquals(data['id'], None)
        self.assertEquals(data['result'], ['foo', 'bar'])
        self.assertEquals(data['error'], None)
        
    def test_renders_suggestions_for_getSuggestions_request(self):
        from simplejson import JSONEncoder
        rpc_request = {'id':None, 'method':'getSuggestions', 
                       'params':['en','foo']}
        json = JSONEncoder().encode(rpc_request)

        request = testing.DummyRequest(method='POST', body=json)
        data = self._callFUT(testing.DummyModel(), request)
        self.assertEquals(data['id'], None)
        self.assertEquals(data['result'], ['foo','foo','foo'])
        self.assertEquals(data['error'], None)


class DummySpellChecker:
    implements(ISpellChecker)

    def __init__(self, executable, language):
        pass
        
    def find_misspelled_words(self, list_of_words, max_words=None):
        return list_of_words        

    def suggestions_for_word(self, word, max_suggestions=None):
        return [word, word, word]
        
    
class TinyMceRequestParsingTests(unittest.TestCase):
    def _callFUT(self, request):
        from karl.views.spellcheck import _parse_tinymce_request
        return _parse_tinymce_request(request)
           
    def test_raises_bad_method_when_not_POST(self):
        from pyramid.httpexceptions import HTTPMethodNotAllowed
        
        request = testing.DummyRequest(method='GET')
        self.assertRaises(HTTPMethodNotAllowed,
            self._callFUT, request
        )

    def test_raises_bad_request_when_not_json_encoded(self):
        from pyramid.httpexceptions import HTTPBadRequest

        request = testing.DummyRequest(method='POST', body='not json')
        self.assertRaises(HTTPBadRequest,
            self._callFUT, request
        )

    def test_raises_bad_request_when_json_contents_are_invalid(self):
        from simplejson import JSONEncoder
        from pyramid.httpexceptions import HTTPBadRequest
        
        rpc_request = {'invalid':'contents'}
        json = JSONEncoder().encode(rpc_request)

        request = testing.DummyRequest(method='POST', 
                    body=json, content_type='application/x-json')
        self.assertRaises(HTTPBadRequest,
            self._callFUT, request
        )
        
    def test_raises_bad_request_when_rpc_method_is_invalid(self):
        from simplejson import JSONEncoder
        from pyramid.httpexceptions import HTTPBadRequest

        rpc_request = {'method': 'invalid', 'params': ['en', ['foo']]}
        json = JSONEncoder().encode(rpc_request)
        
        request = testing.DummyRequest(method='POST', 
                    body=json, content_type='application/x-json')
        self.assertRaises(HTTPBadRequest,
            self._callFUT, request
        )

    def test_raises_bad_request_when_rpc_params_are_invalid(self):
        from simplejson import JSONEncoder
        from pyramid.httpexceptions import HTTPBadRequest

        rpc_request = {'method': 'checkWords', 'params': ['en']}
        json = JSONEncoder().encode(rpc_request)
        
        request = testing.DummyRequest(method='POST', 
                    body=json, content_type='application/x-json')
        self.assertRaises(HTTPBadRequest,
            self._callFUT, request
        )

    def test_parses_valid_checkWords_request(self):
        from simplejson import JSONEncoder

        rpc_request = {'method': 'checkWords', 
                       'params': ['en', ['hello', 'there']]}
        json = JSONEncoder().encode(rpc_request)

        request = testing.DummyRequest(method='POST', 
                    body=json, content_type='application/x-json')

        methodcall, lang, words = self._callFUT(request)
        self.assertEqual(methodcall, 'checkWords')
        self.assertEqual(lang, 'en')
        self.assertEqual(words, ['hello', 'there'])
    
    def test_parses_valid_getSuggestions_request(self):
        from simplejson import JSONEncoder

        rpc_request = {'method': 'getSuggestions', 
                       'params': ['en', 'hello']}
        json = JSONEncoder().encode(rpc_request)

        request = testing.DummyRequest(method='POST', 
                    body=json, content_type='application/x-json')

        methodcall, lang, words = self._callFUT(request)        
        self.assertEqual(methodcall, 'getSuggestions')
        self.assertEqual(lang, 'en')
        self.assertEqual(words, ['hello'])


class TinyMceResponseBuildingTests(unittest.TestCase):
    def _callFUT(self, **kargs):
        from karl.views.spellcheck import _make_tinymce_response
        return _make_tinymce_response(**kargs)

    def test_no_kargs_builds_a_valid_but_empty_response(self):
        data = self._callFUT()
        expected = {'id': None, 'error': None, 'result': []}
        self.assertEqual(data, expected)

    def test_passes_id_to_response(self):
        data = self._callFUT(id='foo')
        expected = {'id': 'foo', 'error': None, 'result': []}
        self.assertEqual(data, expected)

    def test_passes_error_to_response(self):
        data = self._callFUT(error='broken')
        expected = {'id': None, 'error': 'broken', 'result': []}
        self.assertEqual(data, expected)

    def test_passes_result_to_response(self):
        data = self._callFUT(result=['foo','bar'])
        expected = {'id': None, 'error': None, 'result': ['foo','bar']}
        self.assertEqual(data, expected)
