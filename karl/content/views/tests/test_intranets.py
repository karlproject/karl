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
from repoze.bfg.testing import cleanUp

from repoze.bfg import testing
from karl.testing import DummySessions
from karl.testing import DummyUsers

class TestShowIntranetsView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.content.views.intranets import show_intranets_view
        return show_intranets_view(context, request)

    def test_it(self):
        from zope.interface import directlyProvides
        from zope.interface import alsoProvides
        from karl.models.interfaces import ISite
        from karl.models.interfaces import IIntranets
        renderer = testing.registerDummyRenderer('templates/show_intranets.pt')
        context = testing.DummyModel(title='Intranets')
        directlyProvides(context, IIntranets)
        alsoProvides(context, ISite)
        request = testing.DummyRequest()
        self._callFUT(context, request)
        self.assertEqual(len(renderer.actions), 1)

class AddIntranetFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        context = testing.DummyModel(sessions=DummySessions())
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.intranets import AddIntranetFormController
        return AddIntranetFormController(context, request)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failUnless('name' in fields)
        self.failUnless('address' in fields)
        self.failUnless('city' in fields)
        self.failUnless('state' in fields)
        self.failUnless('country' in fields)
        self.failUnless('zipcode' in fields)
        self.failUnless('telephone' in fields)
        self.failUnless('navigation' in fields)
        self.failUnless('middle_portlets' in fields)
        self.failUnless('right_portlets' in fields)

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('navigation' in widgets)
        self.failUnless('middle_portlets' in widgets)
        self.failUnless('right_portlets' in widgets)

    def test_handle_cancel(self):
        controller = self._makeOne(self.context, self.request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        context = self.context
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICommunity
        directlyProvides(context, ICommunity)
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyCommunity, ICommunity)
        context.users = DummyUsers({})
        controller = self._makeOne(context, self.request)
        # first time fill out all the fields
        converted = {'title': 'Intranet Title',
                     'name': 'url_name',
                     'address': 'address',
                     'city': 'city',
                     'state': 'state',
                     'country': 'country',
                     'zipcode': 'zipcode',
                     'telephone': 'telephone',
                     'navigation': '<ul><li>something</li>',
                     'middle_portlets': 'one\ntwo\nthree',
                     'right_portlets': 'four\nfive\nsix',
                     }
        response = controller.handle_submit(converted)
        self.failUnless('url_name' in context)
        intranet = context['url_name']
        self.assertEqual(intranet.title, 'Intranet Title')
        self.assertEqual(intranet.address, 'address')
        self.assertEqual(intranet.city, 'city')
        self.assertEqual(intranet.state, 'state')
        self.assertEqual(intranet.country, 'country')
        self.assertEqual(intranet.zipcode, 'zipcode')
        self.assertEqual(intranet.telephone, 'telephone')
        self.assertEqual(intranet.navigation, '<ul><li>something</li></ul>')
        self.assertEqual(intranet.middle_portlets, ['one', 'two', 'three'])
        self.assertEqual(intranet.right_portlets, ['four', 'five', 'six'])
        self.failUnless('?status_message=Intranet%20added' in response.location)

        # now try again, same values, make sure it fails on name check
        from repoze.bfg.formish import ValidationError
        self.assertRaises(ValidationError,
                          controller.handle_submit, converted)

        # this time no name, nav, or portlet values to make sure the
        # auto-fill stuff works correctly
        converted['title'] = 'Another Title'
        converted['name'] = None
        converted['navigation'] = None
        converted['middle_portlets'] = None
        converted['right_portlets'] = None
        response = controller.handle_submit(converted)
        self.failUnless('another-title' in context)
        intranet = context['another-title']
        self.assertEqual(intranet.title, 'Another Title')
        from karl.content.views.intranets import sample_navigation
        from karl.content.views.intranets import sample_middle_portlets
        from karl.content.views.intranets import sample_right_portlets
        from lxml.html.clean import clean_html
        self.assertEqual(clean_html(intranet.navigation),
                         clean_html(sample_navigation.strip()))
        self.assertEqual(intranet.middle_portlets, sample_middle_portlets)
        self.assertEqual(intranet.right_portlets, sample_right_portlets)

class EditIntranetFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        container = testing.DummyModel(sessions=DummySessions())
        container['intranets'] = testing.DummyModel()
        context = DummyCommunity('Intranet', 'description', 'text',
                                 'creator')
        container['intranet'] = context
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.intranets import EditIntranetFormController
        return EditIntranetFormController(context, request)

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = dict(controller.form_fields())
        self.failUnless('title' in fields)
        self.failIf('name' in fields)
        self.failUnless('address' in fields)
        self.failUnless('city' in fields)
        self.failUnless('state' in fields)
        self.failUnless('country' in fields)
        self.failUnless('zipcode' in fields)
        self.failUnless('telephone' in fields)
        self.failUnless('navigation' in fields)
        self.failUnless('middle_portlets' in fields)
        self.failUnless('right_portlets' in fields)

    def test_form_defaults(self):
        context = self.context
        context.address = 'address'
        context.city = 'city'
        context.state = 'state'
        context.country = 'country'
        context.zipcode = 'zipcode'
        context.telephone = 'telephone'
        context.navigation = '<ul><li>navigation</ul>'
        context.middle_portlets = ['one', 'two']
        context.right_portlets = ['three', 'four']
        controller = self._makeOne(context, self.request)
        defaults = controller.form_defaults()
        self.assertEqual(defaults['title'], 'Intranet')
        self.assertEqual(defaults['address'], 'address')
        self.assertEqual(defaults['city'], 'city')
        self.assertEqual(defaults['state'], 'state')
        self.assertEqual(defaults['country'], 'country')
        self.assertEqual(defaults['zipcode'], 'zipcode')
        self.assertEqual(defaults['telephone'], 'telephone')
        self.assertEqual(defaults['navigation'], '<ul><li>navigation</ul>')
        self.assertEqual(defaults['middle_portlets'], 'one\ntwo')
        self.assertEqual(defaults['right_portlets'], 'three\nfour')

    def test_handle_submit(self):
        converted = {'title': 'New Title',
                     'address': 'address',
                     'city': 'city',
                     'state': 'state',
                     'country': 'country',
                     'zipcode': 'zipcode',
                     'telephone': 'telephone',
                     'navigation': '<ul><li>navigation</ul>',
                     'middle_portlets': 'one\ntwo',
                     'right_portlets': 'three\nfour',
                     }
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller.handle_submit(converted)
        self.assertEqual(context.title, 'New Title')
        self.assertEqual(context.address, 'address')
        self.assertEqual(context.city, 'city')
        self.assertEqual(context.state, 'state')
        self.assertEqual(context.country, 'country')
        self.assertEqual(context.zipcode, 'zipcode')
        self.assertEqual(context.telephone, 'telephone')
        self.assertEqual(context.navigation, '<ul><li>navigation</li></ul>')
        self.assertEqual(context.middle_portlets, ['one', 'two'])
        self.assertEqual(context.right_portlets, ['three', 'four'])

class EditIntranetRootFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()
        from karl.testing import registerTagbox
        registerTagbox()
        container = testing.DummyModel(sessions=DummySessions())
        context = DummyCommunity('Intranets', 'description', 'text',
                                 'creator')
        container['intranets'] = context
        self.context = context
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        self.request = request

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.content.views.intranets import EditIntranetRootFormController
        return EditIntranetRootFormController(context, request)

    def _registerDummyWorkflow(self):
        from repoze.workflow.testing import registerDummyWorkflow
        wf = DummyWorkflow(
            [{'transitions':['private'],'name': 'public', 'title':'Public'},
             {'transitions':['public'], 'name': 'private', 'title':'Private'}])
        workflow = registerDummyWorkflow('security', wf)
        return workflow

    def _registerAddables(self, addables):
        from karl.views.interfaces import IToolAddables
        from zope.interface import Interface
        def tool_adapter(context, request):
            def adapter():
                return addables
            return adapter
        testing.registerAdapter(tool_adapter, (Interface, Interface),
                                IToolAddables)

    def test_form_defaults(self):
        context = self.context
        context.feature = '<p>Boo!</p>'
        controller = self._makeOne(self.context, self.request)
        defaults = controller.form_defaults()
        self.failUnless('feature' in defaults)
        self.assertEqual(defaults['feature'], '<p>Boo!</p>')

    def test_form_fields(self):
        controller = self._makeOne(self.context, self.request)
        fields = controller.form_fields()
        self.assertEqual(fields[4][0], 'feature')

    def test_form_widgets(self):
        controller = self._makeOne(self.context, self.request)
        widgets = controller.form_widgets({})
        self.failUnless('feature' in widgets)

    def test___call__(self):
        context = self.context
        controller = self._makeOne(context, self.request)
        response = controller()
        self.failUnless('api' in response)
        self.assertEqual(response['api'].page_title, 'Edit Intranets')

    def test_handle_submit(self):
        converted = {'title': 'New Title',
                     'description': 'new description',
                     'text': 'new text',
                     'feature': 'feature',
                     'tags': ['foo', 'bar'],
                     'security_state': 'public',
                     'tools': ['hammer', 'screwdriver', 'drill'],
                     'default_tool': 'drill',
                     }
        context = self.context
        context.workflow = self._registerDummyWorkflow()
        hammer_factory = DummyToolFactory()
        screwdriver_factory = DummyToolFactory(present=True)
        drill_factory = DummyToolFactory()
        wrench_factory = DummyToolFactory(present=True)
        saw_factory = DummyToolFactory()
        laser_factory = DummyToolFactory(present=True)
        self._registerAddables([{'name': 'hammer', 'title': 'hammer',
                                 'component': hammer_factory},
                                {'name': 'screwdriver', 'title': 'screwdriver',
                                 'component': screwdriver_factory},
                                {'name': 'drill', 'title': 'drill',
                                 'component': drill_factory},
                                {'name': 'wrench', 'title': 'wrench',
                                 'component': wrench_factory},
                                {'name': 'saw', 'title': 'saw',
                                 'component': saw_factory},
                                {'name': 'laser', 'title': 'laser',
                                 'component': laser_factory},
                                ])
        context.default_tool = 'hammer'
        controller = self._makeOne(context, self.request)
        controller.handle_submit(converted)
        self.assertEqual(context.title, 'New Title')
        self.assertEqual(context.description, 'new description')
        self.assertEqual(context.text, 'new text')
        self.assertEqual(context.feature, '<p>feature</p>')
        self.assertEqual(context.workflow.transitioned[0]['to_state'],
                         'public')
        self.failUnless(hammer_factory.added)
        self.failIf(getattr(screwdriver_factory, 'removed', False))
        self.failUnless(drill_factory.added)
        self.failUnless(wrench_factory.removed)
        self.failIf(getattr(saw_factory, 'added', False))
        self.failUnless(laser_factory.removed)
        self.assertEqual(context.default_tool, 'drill')

class DummyAdapter:
    url = 'someurl'
    title = 'sometitle'
    tabs = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyFilesTool:
    title = 'Dummy Files Tool'


class DummyCommunity:
    def __init__(self, title, description, text, creator):
        self.title = title
        self.description = description
        self.text = text
        self.creator = creator
        self.members_group_name = 'members'
        self.moderators_group_name = 'moderators'
        self.files = DummyFilesTool()

    def get(self, key, default):
        return getattr(self, key)

class DummyToolFactory:
    def __init__(self, present=False):
        self.present = present

    def add(self, context, request):
        self.added = True

    def remove(self, context, request):
        self.removed = True

    def is_present(self, context, request):
        return self.present

class DummyToolAddables(DummyAdapter):
    def __call__(self):
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.listitem import get_listitems
        return get_listitems(IToolFactory)

class DummyWorkflow:
    state_attr = 'security_state'
    initial_state = 'initial'
    def __init__(self, state_info=[
        {'name':'public', 'transitions':['private']},
        {'name':'private', 'transitions':['public']},
        ]):
        self.transitioned = []
        self._state_info = state_info

    def state_info(self, context, request):
        return self._state_info

    def initialize(self, content):
        self.initialized = True

    def transition_to_state(self, content, request, to_state, context=None,
                            guards=(), skip_same=True):
        self.transitioned.append({'to_state':to_state, 'content':content,
                                  'request':request, 'guards':guards,
                                  'context':context, 'skip_same':skip_same})

    def state_of(self, content):
        return getattr(content, self.state_attr, None)
