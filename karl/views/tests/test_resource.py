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
from zope.interface import Interface

from repoze.bfg import testing


class TestDeleteResourceView(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.resource import delete_resource_view
        return delete_resource_view(context, request)

    def test_noconfirm(self):
        from karl.testing import registerLayoutProvider
        registerLayoutProvider()

        context = testing.DummyModel()
        context.title = 'Context'
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/delete_resource.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')

    def test_confirm(self):
        parent = testing.DummyModel()
        context = testing.DummyModel()
        context.title = 'Child'
        parent['child'] = context
        request = testing.DummyRequest(params={'confirm':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, 
                         'http://example.com/?status_message=Deleted+Child')
        self.failIf('child' in parent)
        
        

