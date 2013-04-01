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


class Test_retail_view(unittest.TestCase):
    def setUp(self):
        from pyramid.testing import cleanUp
        cleanUp()

    def tearDown(self):
        from pyramid.testing import cleanUp
        cleanUp()
        
    def _callFUT(self, context, request):
        from karl.views.retail import retail_view
        return retail_view(context, request)

    def test_it(self):
        import mock
        from zope.interface import Interface
        from zope.interface import alsoProvides
        from pyramid.testing import DummyModel
        from pyramid.testing import DummyRequest
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import ISite
        from karl.models.interfaces import IIntranet
        from karl.models.interfaces import IIntranets
        from karl.views.interfaces import IIntranetPortlet
        from karl.testing import registerAdapter
        from karl.testing import registerDummyRenderer
        ANY = (Interface, Interface)
        WELL = u'<h1>WELL</h1>'
        BODY = u'<h1>BODY</h1>'
        FEATURE = u'<p>FEATURE</p>'
        root = DummyModel()
        alsoProvides(root, ISite)
        offices = root['offices'] = DummyModel()
        alsoProvides(offices, IIntranets)
        offices.feature = FEATURE
        context = offices['nice'] = DummyModel(title='nice office')
        context['foo'] = DummyModel()
        context['bar'] = DummyModel()
        context['spam'] = DummyModel()
        alsoProvides(context, ICommunity)
        alsoProvides(context, IIntranet)
        context.middle_portlets = ['foo', 'bar|baz']
        context.right_portlets = ['spam|qux']
        request = DummyRequest()
        request.layout_manager = mock.Mock()

        class _Portlet(object):
            def __init__(self, text):
                self._text = text
            @property
            def asHTML(self):
                return self._text

        _nameless_contexts = []
        NAMELESS = '<p>NAMELESS</p>'
        def _nameless(context, req):
            assert req is request
            _nameless_contexts.append(context)
            return _Portlet(NAMELESS)
        registerAdapter(_nameless, ANY, IIntranetPortlet)

        _baz_contexts = []
        BAZ = '<p>BAZ</p>'
        def _baz(context, req):
            assert req is request
            _baz_contexts.append(context)
            return _Portlet(BAZ)
        registerAdapter(_baz, ANY, IIntranetPortlet, name='baz')

        _qux_contexts = []
        QUX = '<p>QUX</p>'
        def _qux(context, req):
            assert req is request
            _qux_contexts.append(context)
            return _Portlet(QUX)
        registerAdapter(_qux, ANY, IIntranetPortlet, name='qux')

        _ihb_data = []
        def _IHB(data, _):
            _ihb_data.append(data)
            return WELL
        registerDummyRenderer(
            'karl.views:templates/intranethome_body.pt', _IHB)

        _ihp_data = []
        def _IHP(data, _):
            _ihp_data.append(data)
            return BODY
        registerDummyRenderer(
            'karl.views:templates/intranet_homepage.pt', _IHP)

        response = self._callFUT(context, request)
        self.assertEqual(response.body, BODY)
        self.assertEqual(len(_ihp_data), 1)
        self.assertEqual(_ihp_data[0]['body'], WELL)
        self.assertEqual(len(_ihb_data), 1)
        self.assertTrue(_ihb_data[0]['current_intranet'] is context)
        self.assertEqual(_ihb_data[0]['feature'], FEATURE)
        self.assertEqual(_ihb_data[0]['middle_portlet_html'], NAMELESS + BAZ)
        self.assertEqual(_ihb_data[0]['right_portlet_html'], QUX)
