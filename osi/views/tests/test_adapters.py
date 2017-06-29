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

from zope.interface import implements
from zope.interface import alsoProvides

from pyramid import testing

from karl.models.interfaces import ISite

from karl.content.interfaces import ICommunityFolder
from karl.models.interfaces import IIntranets
from karl.content.interfaces import IIntranetFolder

import karl.testing


class TestFolderCustomizer(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from osi.views.adapters import FolderCustomizer
        return FolderCustomizer

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IFolderCustomizer(self):
        from zope.interface.verify import verifyClass
        from karl.content.views.interfaces import IFolderCustomizer
        verifyClass(IFolderCustomizer, self._getTargetClass())

    def test_markers_default(self):
        context = DummyFolder()
        request = testing.DummyRequest()
        adapter = self._makeOne(context, request)
        self.assertEqual(adapter.markers, [])

    def test_markers_intranetfolder(self):
        intranets = DummyIntranets()
        context = DummyFolder()
        intranets['folder'] = context
        request = testing.DummyRequest()
        adapter = self._makeOne(context, request)
        self.assertEqual(adapter.markers, [IIntranetFolder])


class TestShowSendalert(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from osi.views.adapters import ShowSendalert
        return ShowSendalert

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IShowSendalert(self):
        from zope.interface.verify import verifyClass
        from karl.content.views.interfaces import IShowSendalert
        verifyClass(IShowSendalert, self._getTargetClass())

    def test_not_intranet(self):
        context = DummyFolder()
        request = testing.DummyRequest()
        adapter = self._makeOne(context, request)
        self.assertEqual(adapter.show_sendalert, True)

    def test_intranet(self):
        intranets = DummyIntranets()
        context = DummyFolder()
        intranets['folder'] = context
        request = testing.DummyRequest()
        adapter = self._makeOne(context, request)
        self.assertEqual(adapter.show_sendalert, False)


class TestInvitationBoilerplate(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from osi.views.adapters import InvitationBoilerplate
        return InvitationBoilerplate

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IInvitationBoilerplate(self):
        from zope.interface.verify import verifyClass
        from karl.views.interfaces import IInvitationBoilerplate
        verifyClass(IInvitationBoilerplate, self._getTargetClass())

    def test_terms_and_conditions(self):
        from karl.views.interfaces import IInvitationBoilerplate
        context = DummyFolder()
        alsoProvides(context, IInvitationBoilerplate)
        request = testing.DummyRequest()
        adapter = self._makeOne(context, request)
        self.assertEqual(adapter.terms_and_conditions[0:7], '<p>No t')

    def test_privacy_statement(self):
        from karl.views.interfaces import IInvitationBoilerplate
        context = DummyFolder()
        alsoProvides(context, IInvitationBoilerplate)
        request = testing.DummyRequest()
        adapter = self._makeOne(context, request)
        self.assertEqual(adapter.privacy_statement[0:7], '<p>No p')

class TestOSIFooter(unittest.TestCase):

    def _getTargetClass(self):
        from osi.views.adapters import OSIFooter
        return OSIFooter

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = testing.DummyModel()
        if request is None:
            request = testing.DummyRequest()
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IFooter(self):
        from zope.interface.verify import verifyClass
        from karl.views.interfaces import IFooter
        verifyClass(IFooter, self._getTargetClass())

    def test_instance_conforms_to_IFooter(self):
        from zope.interface.verify import verifyObject
        from karl.views.interfaces import IFooter
        verifyObject(IFooter, self._makeOne())

    def test_it(self):
        renderer = karl.testing.registerDummyRenderer('templates/footer.pt')
        footer = self._makeOne()
        api = object()
        response = footer(api)
        self.failUnless(renderer.api is api)


class DummySearchAdapter:
    def __init__(self, context):
        self.context = context

    def __call__(self, **kw):
        return 0, [], None

class DummySite(testing.DummyModel):
    title = 'dummysite'
    implements(ISite)

class DummyIntranets(testing.DummyModel):
    title = 'dummyintranets'
    implements(IIntranets)

class DummyFolder(testing.DummyModel):
    title = 'dummyfolder'
    implements(ICommunityFolder)

class DummyToolFactory:
    def __init__(self, present=False):
        self.present = present

    def add(self, context, request):
        self.added = True

    def remove(self, context, request):
        self.removed = True

    def is_present(self, context, request):
        return self.present

