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

"""Spelling check view used by TinyMCE editor"""

from karl.utilities.interfaces import ISpellChecker
from karl.utilities.spelling import SpellChecker
from karl.utilities.spelling import SpellCheckError
from karl.utils import get_setting
from simplejson import JSONEncoder
from simplejson import JSONDecoder
from webob.exc import HTTPBadRequest
from webob.exc import HTTPMethodNotAllowed
from webob.exc import HTTPServiceUnavailable
from webob import Response
from zope.component import queryUtility

def tinymce_spellcheck_view(context, request):
    methodcall, language, words = _parse_tinymce_request(request)
    
    # get aspell settings
    settings = _get_aspell_settings(context)
    if language not in settings['languages']:
        return _make_tinymce_response(error="Language is not supported")
                                    
    # initialize spellchecker
    klass = queryUtility(ISpellChecker, default=SpellChecker)
    try:                                            
        spellchecker = klass(settings['executable'], language)
    except SpellCheckError, why:
        return _make_tinymce_response(error=why[0])

    # handle tinymce rpc spelling request    
    if methodcall == 'checkWords':
        misspellings = spellchecker.find_misspelled_words(words, 
                        max_words=settings['max_words'])
        response = _make_tinymce_response(misspellings)        

    elif methodcall == 'getSuggestions':
        suggestions = spellchecker.suggestions_for_word(words[0],
                        max_suggestions=10) # keeps ui pretty
        response = _make_tinymce_response(suggestions)        

    del spellchecker # ensure close
    return response


def _parse_tinymce_request(request):
    if request.method != 'POST':
       raise HTTPMethodNotAllowed('Expected POST')

    try:                                             
        from_json = JSONDecoder().decode(request.body)
        methodcall = from_json['method']
        lang, words = from_json['params']
        if not isinstance(words, list):
            words = [ words ]
    except (KeyError, ValueError):
        raise HTTPBadRequest('Invalid JSON payload')
    
    if methodcall not in ('checkWords', 'getSuggestions'):
        raise HTTPBadRequest('Unknown RPC method')
    
    return methodcall, lang, words 


def _make_tinymce_response(result=[], id=None, error=None): 
    D = {'id':id, 'error':error, 'result':result}
    json = JSONEncoder().encode(D)
    return Response(json, content_type='application/x-json')
    

def _get_aspell_settings(context):
    D = {}
    D['executable'] = get_setting(context, 'aspell_executable', 'aspell')
    D['max_words'] = int(get_setting(context, 'aspell_max_words', 5000))
    langs_csv = get_setting(context, 'aspell_languages', 'en')  
    D['languages'] = [x.strip() for x in langs_csv.split(',')]
    return D
 