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


class TestDeleteResourceView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request, num_children=0):
        from karl.views.resource import delete_resource_view
        return delete_resource_view(context, request, num_children)

    def _registerLayoutProvider(self, **kw):
        from pyramid.testing import registerAdapter
        from zope.interface import Interface
        from karl.views.interfaces import ILayoutProvider
        registerAdapter(DummyLayoutProvider,
                        (Interface, Interface),
                        ILayoutProvider)

    def test_noconfirm_non_community(self):
        self._registerLayoutProvider()
        context = testing.DummyModel(title='Context')
        request = testing.DummyRequest()

        info = self._callFUT(context, request)

        self.assertEqual(info['api'].page_title, 'Delete Context')
        self.assertEqual(info['layout'].name, 'generic')
        self.assertEqual(info['num_children'], 0)

    def test_noconfirm_community(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        self._registerLayoutProvider()
        community = testing.DummyModel()
        directlyProvides(community, ICommunity)
        context = community['context'] = testing.DummyModel(title='Context')
        request = testing.DummyRequest()

        info = self._callFUT(context, request)

        self.assertEqual(info['api'].page_title, 'Delete Context')
        self.assertEqual(info['layout'].name, 'community')
        self.assertEqual(info['num_children'], 0)

    def test_warn_for_folder_containing_children(self):
        self._registerLayoutProvider()
        parent = testing.DummyModel(title='Parent')
        child = parent['child'] = testing.DummyModel()
        request = testing.DummyRequest()

        info = self._callFUT(parent, request, len(parent))

        self.assertEqual(info['num_children'], 1)

    def test_confirm(self):
        parent = testing.DummyModel()
        context = parent['child'] = testing.DummyModel(title='Child')
        request = testing.DummyRequest(params={'confirm':'1'})

        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Deleted+Child')
        self.failIf('child' in parent)


class DummyLayout(object):
    def __init__(self, name):
        self.name = name


class DummyLayoutProvider(object):
    community_layout = DummyLayout('community')
    generic_layout = DummyLayout('generic')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, default):
        return getattr(self, '%s_layout' % default)
