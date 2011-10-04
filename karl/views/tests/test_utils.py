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

import karl.testing

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
            window._karl_client_data = {"widget2": ["cc", "dd", {"ee": 4, "ff": 5}], "widget1": {"aa": 1, "bb": [2, 3]}};
            </script>"""))
        injection = convert_to_script(client_json_data, 'karl_client_data')
        from textwrap import dedent
        self.assertEqual(injection, dedent("""\
            <script type="text/javascript">
            window.karl_client_data = {"widget2": ["cc", "dd", {"ee": 4, "ff": 5}], "widget1": {"aa": 1, "bb": [2, 3]}};
            </script>"""))


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

class TestMakeUniqueName(unittest.TestCase):

    def _make_context(self):
        class C(dict):
            # ... this is actually only used by the code for exception formatting ...
            __name__ = 'thename'
        return C()

    def test_make_name(self):
        from karl.views.utils import make_unique_name
        context = self._make_context()
        self.assertEqual(make_unique_name(context, "foo.bar"), "foo.bar")
        self.assertEqual(make_unique_name(context, "Harry 'Bigfoot' Henderson"),
                         "harry-bigfoot-henderson")
        self.assertEqual(make_unique_name(context, "Which one?"), "which-one")
        self.assertEqual(make_unique_name(context, "One/Two/Three"), "one-two-three")
        self.assertEqual(make_unique_name(context, "Genesis 1:1"), "genesis-1-1")
        self.assertEqual(make_unique_name(context, "'My Life'"), "-my-life-")

    def test_empty_name(self):
        from karl.views.utils import make_unique_name
        context = self._make_context()
        self.assertEqual(make_unique_name(context, '$@?%'), '-1')

        name = make_unique_name(context, '$@?%')
        self.assertEqual(name, '-1')
        for i in range(2, 101):
            context[name] = testing.DummyModel()
            name = make_unique_name(context, '$@?%')
            self.assertEqual(name, '-%i' % (i, ))

    def test_unicode(self):
        from karl.views.utils import make_unique_name
        context = self._make_context()
        self.assertEqual(make_unique_name(context, u'what?'), "what")
        self.assertEqual(make_unique_name(context, u"\u0fff"), "-fff-")
        self.assertEqual(make_unique_name(context, u"\u0081\u0082"), "-81-82-")
        self.assertEqual(make_unique_name(context, u'foo\u008ab\u00c3ll'), "foosball")
        
    def test_make_unique_name(self):
        from karl.views.utils import make_unique_name
        context = self._make_context()
        name = make_unique_name(context, 'foo.bar')
        self.assertEqual(name, 'foo.bar')
        for i in range(1, 20):
            context[name] = testing.DummyModel()
            name = make_unique_name(context, 'foo.bar')
            self.assertEqual(name, 'foo-%i.bar' % (i, ))

        name = make_unique_name(context, 'something.else.bar')
        self.assertEqual(name, 'something.else.bar')
        for i in range(1, 20):
            context[name] = testing.DummyModel()
            name = make_unique_name(context, 'something.else.bar')
            self.assertEqual(name, 'something.else-%i.bar' % (i, ))

    def test_make_unique_name_noextension(self):
        from karl.views.utils import make_unique_name
        context = self._make_context()
        name = make_unique_name(context, 'opensociety')
        self.assertEqual(name, 'opensociety')
        for i in range(1, 20):
            context[name] = testing.DummyModel()
            name = make_unique_name(context, 'opensociety')
            self.assertEqual(name, 'opensociety-%i' % (i, ))

    def test_make_unique_name_numbers(self):
        from karl.views.utils import make_unique_name
        context = self._make_context()
        name = make_unique_name(context, '123-456.78')
        self.assertEqual(name, '123-456.78')
        for i in range(1, 20):
            context[name] = testing.DummyModel()
            name = make_unique_name(context, '123-456.78')
            self.assertEqual(name, '123-456-%i.78' % (i, ))
  
    def test_make_unique_name_and_postfix(self):
        from karl.views.utils import make_unique_name_and_postfix
        context = self._make_context()
        name, postfix = make_unique_name_and_postfix(context, 'foo.bar')
        self.assertEqual(name, 'foo.bar')
        self.assertEqual(postfix, '')
        for i in range(1, 20):
            context[name] = testing.DummyModel()
            name, postfix = make_unique_name_and_postfix(context, 'foo.bar')
            self.assertEqual(name, 'foo-%i.bar' % (i, ))
            self.assertEqual(postfix, '%i' % (i, ))


class TestBasenameOfFilepath(unittest.TestCase):
    def test_it(self):
        from karl.views.utils import basename_of_filepath
        self.assertEqual(basename_of_filepath('c:\\dos\\autorun.bat'),
            'autorun.bat')
        self.assertEqual(basename_of_filepath('/home/user/myimage.jpg'),
            'myimage.jpg')


class TestGetUserHome(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def test_not_logged_in(self):
        from karl.views.utils import get_user_home
        karl.testing.registerDummySecurityPolicy()
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
        karl.testing.registerDummySecurityPolicy("userid")
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
        karl.testing.registerDummySecurityPolicy("userid")
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
        karl.testing.registerDummySecurityPolicy("userid")
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
        from pyramid.interfaces import ITraverserFactory
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        karl.testing.registerDummySecurityPolicy("userid")
        c = DummyCommunity()
        site = c.__parent__.__parent__
        directlyProvides(site, Interface)
        c["foo"] = foo = testing.DummyModel()
        site["profiles"] = profiles = testing.DummyModel()
        profiles["userid"] = profile = DummyProfile()
        profile.home_path = "/communities/community/foo"
        karl.testing.registerAdapter(
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
        from pyramid.interfaces import ITraverserFactory
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        karl.testing.registerDummySecurityPolicy("userid")
        c = DummyCommunity()
        site = c.__parent__.__parent__
        directlyProvides(site, Interface)
        c["foo"] = foo = testing.DummyModel()
        site["profiles"] = profiles = testing.DummyModel()
        profiles["userid"] = profile = DummyProfile()
        profile.home_path = "/communities/community/foo/view.html"
        karl.testing.registerAdapter(
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

    def test_user_home_path_w_subpath(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from pyramid.interfaces import ITraverserFactory
        from karl.testing import DummyCommunity
        from karl.testing import DummyProfile
        karl.testing.registerDummySecurityPolicy("userid")
        c = DummyCommunity()
        site = c.__parent__.__parent__
        directlyProvides(site, Interface)
        c["foo"] = foo = testing.DummyModel()
        site["profiles"] = profiles = testing.DummyModel()
        profiles["userid"] = profile = DummyProfile()
        profile.home_path = "/communities/community/foo/bar/baz"
        karl.testing.registerAdapter(
            dummy_traverser_factory, Interface, ITraverserFactory
        )

        from karl.views.utils import get_user_home
        request = testing.DummyRequest()

        # Test from site root
        target, extra_path = get_user_home(site, request)
        self.failUnless(foo is target)
        self.assertEqual(['bar', 'baz'], extra_path)

        # Test from arbitrary point in tree
        target, extra_path = get_user_home(c, request)
        self.failUnless(foo is target)
        self.assertEqual(['bar', 'baz'], extra_path)

    def test_space_as_home_path(self):
        from zope.interface import Interface
        from pyramid.interfaces import ITraverserFactory
        from karl.views.utils import get_user_home
        from karl.testing import DummyUsers
        from karl.testing import DummyProfile
        karl.testing.registerDummySecurityPolicy("userid")
        context = testing.DummyModel()
        communities = context["communities"] = testing.DummyModel()
        community = communities["community"] = testing.DummyModel()
        profiles = context["profiles"] = testing.DummyModel()
        profile = profiles["userid"] = DummyProfile()
        profile.home_path = ' '
        karl.testing.registerAdapter(
            dummy_traverser_factory, Interface, ITraverserFactory
        )

        users = context.users = DummyUsers()
        users.add("userid", "userid", "password",
                  ["group.community:community:members",])
        request = testing.DummyRequest()
        target, extra_path = get_user_home(context, request)
        self.failUnless(target is community)
        self.assertEqual(extra_path, [])

class TestHandlePhotoUpload(unittest.TestCase):
    def tearDown(self):
        # call to transaction.get().doom() might leave transaction manager
        # in doomed state for next test if we don't abort.
        import transaction
        transaction.abort()

    def _callFUT(self, context, form):
        from karl.views.utils import handle_photo_upload
        return handle_photo_upload(context, form)

    def test_upload_photo(self):
        from cStringIO import StringIO
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        karl.testing.registerDummySecurityPolicy("userid")
        def make_image(title, stream, mimetype, filename, creator):
            res = testing.DummyModel()
            res.title = title
            res.mimetype = mimetype
            res.data = stream.read()
            res.filename = filename
            res.creator = creator
            res.is_image = True
            return res
        registerContentFactory(make_image, ICommunityFile)

        context = testing.DummyModel()
        context.title = 'Howdy Doody'
        context.__name__ = 'howdydoody'
        form = {'photo': DummyUpload(StringIO(one_pixel_jpeg), 'image/jpeg')}
        self._callFUT(context, form)
        self.assertTrue('photo' in context)
        photo = context['photo']
        self.assertEqual(photo.title, 'Photo of Howdy Doody')
        self.assertEqual(photo.mimetype, 'image/jpeg')
        self.assertEqual(photo.data, one_pixel_jpeg)
        self.assertEqual(photo.filename, 'test.dat')
        self.assertEqual(photo.creator, 'userid')

    def test_replace_photo(self):
        from cStringIO import StringIO
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        karl.testing.registerDummySecurityPolicy("userid")
        def make_image(title, stream, mimetype, filename, creator):
            res = testing.DummyModel()
            res.title = title
            res.mimetype = mimetype
            res.data = stream.read()
            res.filename = filename
            res.creator = creator
            res.is_image = True
            return res
        registerContentFactory(make_image, ICommunityFile)

        class DummyModel(testing.DummyModel):
            # Simulate repoze.folder behavior of refusing to overwrite
            # existing keys without an explicit removal.
            def __setitem__(self, name, value):
                if name in self:
                    raise KeyError(u'An object named %s already exists' % name)
                return testing.DummyModel.__setitem__(self, name, value)

        context = DummyModel()
        context.title = 'Howdy Doody'
        context.__name__ = 'howdydoody'
        context['photo'] = testing.DummyModel()
        form = {'photo': DummyUpload(StringIO(one_pixel_jpeg), 'image/jpeg')}
        self._callFUT(context, form)
        self.assertTrue('photo' in context)
        photo = context['photo']
        self.assertEqual(photo.title, 'Photo of Howdy Doody')
        self.assertEqual(photo.mimetype, 'image/jpeg')
        self.assertEqual(photo.data, one_pixel_jpeg)
        self.assertEqual(photo.filename, 'test.dat')
        self.assertEqual(photo.creator, 'userid')

    def test_invalid_image(self):
        from cStringIO import StringIO
        from karl.views.utils import Invalid
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        def make_image(title, stream, mimetype, filename, creator):
            res = testing.DummyModel()
            res.title = title
            res.mimetype = mimetype
            res.data = stream.read()
            res.filename = filename
            res.creator = creator
            res.is_image = False
            return res
        registerContentFactory(make_image, ICommunityFile)

        context = testing.DummyModel()
        context.title = 'Howdy Doody'
        context.__name__ = 'howdydoody'
        form = {'photo': DummyUpload(StringIO(one_pixel_jpeg), 'image/jpeg')}
        self.assertRaises(Invalid, self._callFUT, context, form)
        self.assertTrue('photo' not in context)


    def test_delete_photo(self):
        context = testing.DummyModel()
        context['photo'] = testing.DummyModel()
        form = {'photo_delete': 'yes'}
        self.assertTrue('photo' in context)
        self._callFUT(context, form)
        self.assertFalse('photo' in context)

    def test_upload_has_mimetype_instead_of_type(self):
        from cStringIO import StringIO
        from karl.content.interfaces import ICommunityFile
        from repoze.lemonade.testing import registerContentFactory
        karl.testing.registerDummySecurityPolicy("userid")
        def make_image(title, stream, mimetype, filename, creator):
            res = testing.DummyModel()
            res.title = title
            res.mimetype = mimetype
            res.data = stream.read()
            res.filename = filename
            res.creator = creator
            res.is_image = True
            return res
        registerContentFactory(make_image, ICommunityFile)

        context = testing.DummyModel()
        context.title = 'Howdy Doody'
        context.__name__ = 'howdydoody'
        dummy_upload = DummyUpload(StringIO(one_pixel_jpeg), 'image/jpeg')
        dummy_upload.mimetype = dummy_upload.type
        del dummy_upload.type

        form = {'photo': dummy_upload}
        self._callFUT(context, form)
        self.assertTrue('photo' in context)
        photo = context['photo']
        self.assertEqual(photo.title, 'Photo of Howdy Doody')
        self.assertEqual(photo.mimetype, 'image/jpeg')
        self.assertEqual(photo.data, one_pixel_jpeg)
        self.assertEqual(photo.filename, 'test.dat')
        self.assertEqual(photo.creator, 'userid')

class TestConvertEntities(unittest.TestCase):
    def _callFUT(self, s):
        from karl.views.utils import convert_entities
        return convert_entities(s)

    def test_convert_entities(self):
        expected = "You &#38; are &#160; my sunshine."
        outcome = self._callFUT("You &amp; are &nbsp; my sunshine.")
        self.assertEqual(outcome, expected)

    def test_bad_entity(self):
        expected = "I have &foobar; for breakfast."
        outcome = self._callFUT(expected)
        self.assertEqual(outcome, expected)

    def test_numeric_entity(self):
        expected = "I have &#38; for breakfast."
        outcome = self._callFUT(expected)
        self.assertEqual(outcome, expected)

    def test_non_entities(self):
        expected = "I have &; &&; &#; for breakfast."
        outcome = self._callFUT(expected)
        self.assertEqual(outcome, expected)

class DummyUpload:
    filename = 'test.dat'
    def __init__(self, file, type):
        self.file = file
        self.type = type

def dummy_traverser_factory(root):
    def traverser(request):
        parts = request.environ["PATH_INFO"][1:].split("/")
        node = root
        name = None
        left_over = ()
        for i in xrange(len(parts)):
            part = parts.pop(0)
            if part in node:
                node = node[part]
            else:
                name = part
                left_over = tuple(parts)
                break
        return {'context':node, 'view_name':name, 'subpath':left_over}
    return traverser

one_pixel_jpeg = [
0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01,
0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xff, 0xdb, 0x00, 0x43, 0x00, 0x05,
0x03, 0x04, 0x04, 0x04, 0x03, 0x05, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x06,
0x07, 0x0c, 0x08, 0x07, 0x07, 0x07, 0x07, 0x0f, 0x0b, 0x0b, 0x09, 0x0c, 0x11,
0x0f, 0x12, 0x12, 0x11, 0x0f, 0x11, 0x11, 0x13, 0x16, 0x1c, 0x17, 0x13, 0x14,
0x1a, 0x15, 0x11, 0x11, 0x18, 0x21, 0x18, 0x1a, 0x1d, 0x1d, 0x1f, 0x1f, 0x1f,
0x13, 0x17, 0x22, 0x24, 0x22, 0x1e, 0x24, 0x1c, 0x1e, 0x1f, 0x1e, 0xff, 0xdb,
0x00, 0x43, 0x01, 0x05, 0x05, 0x05, 0x07, 0x06, 0x07, 0x0e, 0x08, 0x08, 0x0e,
0x1e, 0x14, 0x11, 0x14, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e, 0x1e,
0x1e, 0x1e, 0xff, 0xc0, 0x00, 0x11, 0x08, 0x00, 0x01, 0x00, 0x01, 0x03, 0x01,
0x22, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01, 0xff, 0xc4, 0x00, 0x15, 0x00,
0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x08, 0xff, 0xc4, 0x00, 0x14, 0x10, 0x01, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0xff, 0xc4, 0x00, 0x14, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xc4, 0x00,
0x14, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xda, 0x00, 0x0c, 0x03, 0x01, 0x00,
0x02, 0x11, 0x03, 0x11, 0x00, 0x3f, 0x00, 0xb2, 0xc0, 0x07, 0xff, 0xd9
]

one_pixel_jpeg = ''.join([chr(x) for x in one_pixel_jpeg])
