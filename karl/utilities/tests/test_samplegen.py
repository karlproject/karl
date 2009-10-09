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
from zope.testing.cleanup import cleanUp
import karl.testing

class SampleGenTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_get_sample_filename(self):
        import os
        from karl.utilities.samplegen import get_sample_filename
        fn = get_sample_filename()
        self.assert_(os.path.isfile(fn))

    def test_get_sample_text(self):
        from karl.utilities.samplegen import get_sample_text
        text = get_sample_text()
        self.assert_(isinstance(text, basestring))
        self.assert_(text)

    def test_get_sample_html(self):
        from karl.utilities.samplegen import get_sample_html
        html = get_sample_html()
        self.assert_(isinstance(html, basestring))

    def test_generate_title(self):
        from karl.utilities.samplegen import generate_title
        title = generate_title("SampleT")
        self.assert_(title.startswith("(SampleT"))
        self.assert_(len(title.split()) >= 2)

    def test_add_community(self):
        karl.testing.registerTagbox()

        from zope.interface import Interface
        from karl.views.interfaces import IToolAddables
        testing.registerAdapter(DummyToolAddables, (Interface, Interface),
                                IToolAddables)

        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import ICommunity
        registerContentFactory(DummyCommunity, ICommunity)

        site = testing.DummyModel()
        site['communities'] = testing.DummyModel()
        site.users = karl.testing.DummyUsers()
        site.catalog = karl.testing.DummyCatalog()

        from karl.utilities.samplegen import add_sample_community
        obj = add_sample_community(site, add_content=False)
        self.assert_('SampleC' in obj.title)

    def test_add_blog_entry(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IBlogEntry
        registerContentFactory(DummyBlogEntry, IBlogEntry)

        site = testing.DummyModel()
        site.catalog = karl.testing.DummyCatalog()
        community = testing.DummyModel()
        site['community'] = community
        community['blog'] = testing.DummyModel()

        from karl.utilities.samplegen import add_sample_blog_entry
        obj = add_sample_blog_entry(community)
        self.assert_('SampleB' in obj.title)

    def test_add_wiki_page(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import IWikiPage
        registerContentFactory(DummyWikiPage, IWikiPage)

        site = testing.DummyModel()
        site.catalog = karl.testing.DummyCatalog()
        community = testing.DummyModel()
        site['community'] = community
        community['wiki'] = testing.DummyModel()
        community['wiki']['front_page'] = DummyWikiPage(
            'Front Page', '', '', '')

        from karl.utilities.samplegen import add_sample_wiki_page
        obj = add_sample_wiki_page(community)
        self.assert_('SampleW' in obj.title)

    def test_add_calendar_event(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICalendarEvent
        registerContentFactory(DummyCalendarEvent, ICalendarEvent)

        site = testing.DummyModel()
        site.catalog = karl.testing.DummyCatalog()
        community = testing.DummyModel()
        site['community'] = community
        community['calendar'] = testing.DummyModel()

        from karl.utilities.samplegen import add_sample_calendar_event
        obj = add_sample_calendar_event(community)
        self.assert_('SampleE' in obj.title)

    def test_add_file(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.content.interfaces import ICommunityFile
        registerContentFactory(DummyCommunityFile, ICommunityFile)

        site = testing.DummyModel()
        site.catalog = karl.testing.DummyCatalog()
        community = testing.DummyModel()
        site['community'] = community
        community['files'] = testing.DummyModel()

        from karl.utilities.samplegen import add_sample_file
        obj = add_sample_file(community, 1)
        self.assert_('SampleF' in obj.title)


class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyToolAddables(DummyAdapter):
    def __call__(self):
        from karl.models.interfaces import IToolFactory
        from repoze.lemonade.listitem import get_listitems
        return get_listitems(IToolFactory)

class DummyCommunity(testing.DummyModel):
    def __init__(self, title, description, text, creator):
        testing.DummyModel.__init__(self)
        self.title = title
        self.description = description
        self.text = text
        self.creator = creator
        self.members_group_name = 'members'
        self.moderators_group_name = 'moderators'

class DummyBlogEntry(testing.DummyModel):
    def __init__(self, title, text, description, creator):
        testing.DummyModel.__init__(self)
        self.title = title
        self.text = text
        self.description = description
        self.creator = creator
        self['comments'] = testing.DummyModel()
        self['attachments'] = testing.DummyModel()
        from datetime import datetime
        self.created = datetime.now()

class DummyWikiPage:
    def __init__(self, title, text, description, creator):
        self.title = title
        self.text = text
        self.description = description
        self.creator = creator

class DummyCalendarEvent(testing.DummyModel):

    def __init__(self, title='', startDate=None, endDate=None, creator=0,
                 text='', location='', attendees=[], contact_name='',
                 contact_email='', virtual_calendar=''):
        testing.DummyModel.__init__(self)
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
        self.creator = creator
        self.text = text
        self.location = location
        self.attendees = attendees
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.virtual_calendar = virtual_calendar
        self.__parent__ = testing.DummyModel()
        self.__name__ = 'calendarevent'
        self['attachments'] = testing.DummyModel()
        from datetime import datetime
        self.created = datetime.now()

class DummyCommunityFile(testing.DummyModel):
    size = 3
