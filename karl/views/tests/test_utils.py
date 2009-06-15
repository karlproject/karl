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
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

class TestClientJsonData(unittest.TestCase):
    
    def test_client_json_data(self):
        from karl.views.utils import convert_to_script
        client_json_data = {}
        injection = convert_to_script(client_json_data)
        self.assertEqual(injection, '')
        client_json_data = {
            'widget1': {'aa':1, 'bb': [2, 3]},
            'widget2': ['cc', 'dd', {'ee': 4, 'ff':5}],
            }
        injection = convert_to_script(client_json_data)
        from textwrap import dedent
        self.assertEqual(injection, dedent("""\
            <script type="text/javascript">
            window.karl_client_data = {"widget2": ["cc", "dd", {"ee": 4, "ff": 5}], "widget1": {"aa": 1, "bb": [2, 3]}};
            </script>"""))

class TestDebugSearch(unittest.TestCase):
    def _callFUT(self, context, **kw):
        from karl.utils import debugsearch
        return debugsearch(context, **kw)

    def test_it(self):
        context = testing.DummyModel()
        context.catalog = DummyCatalog()
        result = self._callFUT(context)
        self.assertEqual(result, (1, [1]))

class TestGetSession(unittest.TestCase):
    def _callFUT(self, context, request):
        from karl.utils import get_session
        return get_session(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        context.sessions = testing.DummyModel()
        foo = testing.DummyModel()
        context.sessions['foo'] = foo
        request.environ = {'repoze.browserid':'foo'}
        result = self._callFUT(context, request)
        self.assertEqual(result, foo)

class TestMakeName(unittest.TestCase):
    def test_make_name(self):
        from karl.views.utils import make_name
        context = {}
        self.assertEqual(make_name(context, "foo.bar"), "foo.bar")
        self.assertEqual(make_name(context, "Harry 'Bigfoot' Henderson"), 
                         "harry-bigfoot-henderson")
        self.assertEqual(make_name(context, "Which one?"), "which-one")
        self.assertEqual(make_name(context, "One/Two/Three"), "one-two-three")
        self.assertEqual(make_name(context, "Genesis 1:1"), "genesis-1-1")
        self.assertEqual(make_name(context, "'My Life'"), "-my-life-")

    def test_make_name_without_error(self):
        from karl.views.utils import make_name
        context = testing.DummyModel()
        context['foo.bar'] = testing.DummyModel()
        try:
            self.assertEqual(make_name(context, "foo.bar"), 'foo.bar')
        except ValueError:
            pass
        else:
            self.fail("Expected a ValueError")
        self.assertEqual(make_name(context, "Test 1", raise_error=False), 'test-1')

    def test_empty_name(self):
        from karl.views.utils import make_name
        context = {}
        self.assertRaises(ValueError, make_name, context, '$@?%')

    def test_unicode(self):
        from karl.views.utils import make_name
        context = {}
        self.assertEqual(make_name(context, u'what?'), "what")
        self.assertEqual(make_name(context, u"\u0fff"), "-fff-")
        self.assertEqual(make_name(context, u"\u0081\u0082"), "-81-82-")
        self.assertEqual(make_name(context, u'foo\u008ab\u00c3ll'), "foosball")

class TestGetUserHome(unittest.TestCase):
    def setUp(self):
        cleanUp()
        
    def tearDown(self):
        cleanUp()
        
    def test_not_logged_in(self):
        from karl.views.utils import get_user_home
        testing.registerDummySecurityPolicy()
        context = testing.DummyModel()
        communities = context["communities"] = testing.DummyModel()
        request = testing.DummyRequest()
        target, extra_path = get_user_home(context, request)
        self.failUnless(target is communities)
        self.assertEqual(extra_path, [])
        
    def test_no_communities(self):
        from karl.views.utils import get_user_home
        from karl.testing import DummyUsers
        from karl.testing import DummyProfile
        testing.registerDummySecurityPolicy("userid")
        context = testing.DummyModel()
        communities = context["communities"] = testing.DummyModel()
        profiles = context["profiles"] = testing.DummyModel()
        profile = profiles["userid"] = DummyProfile()        
        users = context.users = DummyUsers()
        users.add("userid", "userid", "password", [])
        request = testing.DummyRequest()
        target, extra_path = get_user_home(context, request)
        self.failUnless(target is communities)
        self.assertEqual(extra_path, [])
        
    def test_one_community(self):
        from karl.views.utils import get_user_home
        from karl.testing import DummyUsers
        from karl.testing import DummyProfile
        testing.registerDummySecurityPolicy("userid")
        context = testing.DummyModel()
        communities = context["communities"] = testing.DummyModel()
        community = communities["community"] = testing.DummyModel()
        profiles = context["profiles"] = testing.DummyModel()
        profile = profiles["userid"] = DummyProfile()        
        users = context.users = DummyUsers()
        users.add("userid", "userid", "password", 
                  ["group.community:community:members",])
        request = testing.DummyRequest()
        target, extra_path = get_user_home(context, request)
        self.failUnless(target is community)
        self.assertEqual(extra_path, [])
        
    def test_many_communities(self):
        from karl.views.utils import get_user_home
        from karl.testing import DummyUsers
        from karl.testing import DummyProfile
        testing.registerDummySecurityPolicy("userid")
        context = testing.DummyModel()
        communities = context["communities"] = testing.DummyModel()
        profiles = context["profiles"] = testing.DummyModel()
        profile = profiles["userid"] = DummyProfile()
        users = context.users = DummyUsers()
        users.add("userid", "userid", "password", 
                  ["group.community:community:members",
                   "group.community:community2:members"])
        request = testing.DummyRequest()
        target, extra_path = get_user_home(context, request)
        self.failUnless(target is communities)
        self.assertEqual(extra_path, [])
        
    def test_user_home_path(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import ITraverserFactory
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        testing.registerDummySecurityPolicy("userid")
        c = DummyCommunity()
        site = c.__parent__.__parent__
        directlyProvides(site, Interface)
        c["foo"] = foo = testing.DummyModel()
        site["profiles"] = profiles = testing.DummyModel()
        profiles["userid"] = profile = DummyProfile()
        profile.home_path = "/communities/community/foo"
        testing.registerAdapter(
            dummy_traverser_factory, Interface, ITraverserFactory
        )
        
        from karl.views.utils import get_user_home
        request = testing.DummyRequest()
        
        # Test from site root
        target, extra_path = get_user_home(site, request)
        self.failUnless(foo is target)
        self.assertEqual([], extra_path)
        
        # Test from arbitrary point in tree
        target, extra_path = get_user_home(c, request)
        self.failUnless(foo is target)
        self.assertEqual([], extra_path)
        
    def test_user_home_path_w_view(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import ITraverserFactory
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        testing.registerDummySecurityPolicy("userid")
        c = DummyCommunity()
        site = c.__parent__.__parent__
        directlyProvides(site, Interface)
        c["foo"] = foo = testing.DummyModel()
        site["profiles"] = profiles = testing.DummyModel()
        profiles["userid"] = profile = DummyProfile()
        profile.home_path = "/communities/community/foo/view.html"
        testing.registerAdapter(
            dummy_traverser_factory, Interface, ITraverserFactory
        )
        
        from karl.views.utils import get_user_home
        request = testing.DummyRequest()
        
        # Test from site root
        target, extra_path = get_user_home(site, request)
        self.failUnless(foo is target)
        self.assertEqual(['view.html'], extra_path)
        
        # Test from arbitrary point in tree
        target, extra_path = get_user_home(c, request)
        self.failUnless(foo is target)
        self.assertEqual(['view.html'], extra_path)

    def test_space_as_home_path(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import ITraverserFactory
        from karl.views.utils import get_user_home
        from karl.testing import DummyUsers
        from karl.testing import DummyProfile
        testing.registerDummySecurityPolicy("userid")
        context = testing.DummyModel()
        communities = context["communities"] = testing.DummyModel()
        community = communities["community"] = testing.DummyModel()
        profiles = context["profiles"] = testing.DummyModel()
        profile = profiles["userid"] = DummyProfile()
        profile.home_path = ' '
        testing.registerAdapter(
            dummy_traverser_factory, Interface, ITraverserFactory
        )

        users = context.users = DummyUsers()
        users.add("userid", "userid", "password", 
                  ["group.community:community:members",])
        request = testing.DummyRequest()
        target, extra_path = get_user_home(context, request)
        self.failUnless(target is community)
        self.assertEqual(extra_path, [])

class DummyCatalog:
    def _search(self, **kw):
        return 1, [1], lambda x: x
    
def dummy_traverser_factory(root):
    def traverser(environ):
        parts = environ["PATH_INFO"][1:].split("/")
        node = root
        name = None
        left_over = []
        for i in xrange(len(parts)):
            part = parts.pop(0)
            if part in node:
                node = node[part]
            else:
                name = part
                left_over = parts
                break
        return {'context':node, 'view_name':name, 'subpath':left_over}
    return traverser
