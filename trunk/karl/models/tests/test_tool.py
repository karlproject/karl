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
from repoze.bfg import testing

class TestToolFactory(unittest.TestCase):
    def _makeOne(self):
        from karl.models.tool import ToolFactory
        return ToolFactory()
    
    def test_add(self):
        factory = self._makeOne()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, factory.add, context, request)

    def test_remove(self):
        factory = self._makeOne()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, factory.remove, context, request)

    def test_is_present(self):
        factory = self._makeOne()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, factory.is_present,
                          context, request)
        factory.name = 'thename'
        self.failIf(factory.is_present(context, request))
        context['thename'] = testing.DummyModel
        self.failUnless(factory.is_present(context, request))
        
    def test_is_current(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        factory = self._makeOne()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, factory.is_current,
                          context, request)
        class IDummy(Interface):
            pass
        factory.interfaces = (IDummy,)
        self.failIf(factory.is_current(context, request))
        directlyProvides(context, IDummy)
        request.context = context
        self.failUnless(factory.is_current(context, request))
        
    def test_tab_url(self):
        factory = self._makeOne()
        context = testing.DummyModel()
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, factory.tab_url,
                          context, request)
        factory.name = 'thename'
        self.assertEqual(factory.tab_url(context, request),
                         'http://example.com/thename')
        
        
