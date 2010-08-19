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

import os
import signal
import subprocess
import re
from zope.interface import implements
from karl.utilities.interfaces import ISpellChecker

class SpellChecker:
    implements(ISpellChecker)

    _UNKNOWN = re.compile(r'^& (.*?) \d* \d*: (.*)$', re.U)
    _UNKNOWN_NO_REPLACEMENT = re.compile(r'^\# (.*?) \d*.*$', re.U)

    _subprocess = None

    def __init__(self, aspell_executable, language='en'):
        self._spawn_aspell(aspell_executable, language)

        # first line will either be version info or an error
        # such as the language file cannot be loaded
        msg = self._subprocess.stdout.readline()

    def _spawn_aspell(self, aspell_executable, language):
        args = [aspell_executable, 
                '--encoding=UTF-8',
                '--lang=%s' % language,
                '--pipe']

        try:
            self._subprocess = subprocess.Popen(args=args,
                                                shell=False,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                               )
        except OSError:            
            msg = 'Spell checker could not be started'
            raise SpellCheckError(msg)
        
    def __del__(self):
        if self._subprocess:
            self.kill()

    def find_misspelled_words(self, list_of_words, max_words=None):
        ''' Check a list of words for misspellings and return a list
        of possible misspelled words.  If max_words is not None, no
        more than max_words will be given to aspell.
        '''
        result = self.find_words_and_suggestions(list_of_words, max_words)
        misspellings = result.keys()
        return misspellings
    
    def suggestions_for_word(self, word, max_suggestions=None):
        ''' Check spelling of a single word and return a list of
        possible suggestions for the word.  If max_suggestions is not
        None, at most max_suggestions will be returned.
        '''
        result = self.find_words_and_suggestions([word])
        suggestions = result.get(word, [])
        if max_suggestions is not None:
            suggestions = suggestions[:max_suggestions]
        return suggestions

    def find_words_and_suggestions(self, list_of_words, max_words=None):
        ''' Check a list of words for misspellings and return a dict where
        the keys are the possibly misspelled words and the values are lists
        of suggestions.  If max_words is not None, no more than max_words
        will be given to aspell.
        
        Part of this routine was derived from Kupu, which can be found at 
        http://plone.org/products/kupu under BSD license.  Copyright (c) 
        2003-2005, Kupu Contributors, All Rights Reserved.
        '''
        result = {}

        if max_words is not None:
            list_of_words = list_of_words[:max_words]
        
        words = [word.strip() for word in list_of_words]
        if '' in list_of_words:    
            list_of_words.remove('')

        if not list_of_words:
            return result # nothing to do

        line = ' '.join(set(list_of_words))
        
        try:
            self._writeline(line)
            while True:
                resline = self._subprocess.stdout.readline()
                if not resline.strip():
                    break
                if resline.strip() != '*':
                    match = self._UNKNOWN.match(resline)
                    have_replacement = True
                    if not match:
                        match = self._UNKNOWN_NO_REPLACEMENT.match(resline)
                        have_replacement = False
                    assert match, 'Unknown formatted line: %s' % resline
                    word = match.group(1)
                    if result.has_key(word):
                        continue
                    replacements = []
                    if have_replacement:
                        replacements = match.group(2).split(', ')
                    result[word] = replacements
        except IOError:
            pass

        return result
     
    def _writeline(self, chars):
        if isinstance(chars, unicode):
            chars = chars.encode('utf-8')
        self._subprocess.stdin.write(chars)
        self._subprocess.stdin.write('\n')
        self._subprocess.stdin.flush()
    
    def kill(self):
        os.kill(self._subprocess.pid, signal.SIGTERM)


class SpellCheckError(Exception):
    pass
    