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
import sys
import datetime
import time
import calendar
from repoze.bfg import testing


class BasePresenterTests(unittest.TestCase):     
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    # default properties

    def test_has_a_name_of_abstract(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.name, 'abstract')

    def test_has_an_empty_title(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.title, '')

    def test_has_an_add_event_url(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        expected = presenter.url_for('add_calendarevent.html')
        self.assertEqual(presenter.add_event_url, expected)

    # constructor

    def test_ctor_assigns_url_for(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertTrue(presenter.url_for is dummy_url_for)

    def test_ctor_assigns_date_properties(self):
        focus_at = datetime.datetime(2009, 8, 26)
        now_at   = datetime.datetime.now()

        presenter = self._makeOne(focus_at, now_at, dummy_url_for)
        self.assertEqual(presenter.focus_datetime, focus_at)
        self.assertEqual(presenter.now_datetime, now_at)

    # helpers

    def _makeOne(self, *args, **kargs):
        from karl.content.calendar.presenters.base import BasePresenter
        return BasePresenter(*args, **kargs)


class BaseEventTests(unittest.TestCase):
    def setUp(self):
        calendar.setfirstweekday(calendar.SUNDAY)

    # title

    def test_has_title_location_description_from_catalog_event(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        catalog_event = DummyCatalogEvent(
                            title='foo', 
                            description='bar',
                            location='baz'
                        )

        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEquals(event.title,       catalog_event.title)
        self.assertEquals(event.location,    catalog_event.location)
        self.assertEquals(event.description, catalog_event.description)

    # show_url
    
    def test_show_url_defaults_to_pound(self):
        day_on_listview = self._makeDay(2009, 9, 7) 
        catalog_event = DummyCatalogEvent()
        
        first_moment = datetime.datetime(2009, 9, 7)
        last_moment  = datetime.datetime(2009, 9, 7)

        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEquals(event.show_url, '#')

    def test_show_url_can_be_assigned(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        catalog_event = DummyCatalogEvent() 

        event = self._makeEvent(day_on_listview, catalog_event,
                                show_url='http://somewhere'  
                               )
        self.assertEquals(event.show_url, 'http://somewhere')
    
    # edit_url
    
    def test_edit_url_defaults_to_pound(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        catalog_event = DummyCatalogEvent()

        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEquals(event.edit_url, '#')

    def test_edit_url_can_be_assigned(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        catalog_event = DummyCatalogEvent()
        
        event = self._makeEvent(day_on_listview, catalog_event, 
                                edit_url='http://somewhere'  
                               )
        self.assertEquals(event.edit_url, 'http://somewhere')
        
    # delete_url
    
    def test_delete_url_defaults_to_pound(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        catalog_event = DummyCatalogEvent()

        event = self._makeEvent(day_on_listview, catalog_event) 
        self.assertEquals(event.delete_url, '#')

    def test_delete_url_can_be_assigned(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        catalog_event = DummyCatalogEvent()

        event = self._makeEvent(day_on_listview, catalog_event, 
                                delete_url='http://somewhere'  
                               )
        self.assertEquals(event.delete_url, 'http://somewhere')
        
    # first and last moment
    
    def test_assigns_constrains_catalog_event_first_moment_within_day(self):
        day_on_listview = self._makeDay(2009, 9, 7)                
        
        starts_before_day = datetime.datetime(2009, 9, 5)
        catalog_event = DummyCatalogEvent(startDate=starts_before_day)
        
        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEqual(event.first_moment, day_on_listview.first_moment)

    def test_assigns_constrains_catalog_event_last_moment_within_day(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        
        ends_after_day = datetime.datetime(2009, 9, 9)
        catalog_event = DummyCatalogEvent(endDate=ends_after_day)

        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEqual(event.last_moment, day_on_listview.last_moment)

    # time_in_words

    def test_time_in_words_shows_all_day_for_events_over_entire_day(self):
        day_on_list = self._makeDay(2009, 9, 7)                
        catalog_event = DummyCatalogEvent(startDate=day_on_list.first_moment,
                                          endDate=day_on_list.last_moment)
        
        event = self._makeEvent(day_on_list, catalog_event)
        self.assertEqual(event.time_in_words, 'all-day')
    
    def test_time_in_words_shows_start_end_times_with_hh_colon_mm(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        starts_at = datetime.datetime(2009, 9, 7, 15, 15, 0) # 3:15pm
        ends_at   = datetime.datetime(2009, 9, 7, 15, 30, 0) # 3:30pm
                        
        catalog_event = DummyCatalogEvent(startDate=starts_at,
                                          endDate=ends_at)
        
        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEqual(event.time_in_words, '3:15pm - 3:30pm')

    
    def test_time_in_words_shows_times_ending_in_00_without_00(self):
        day_on_listview = self._makeDay(2009, 9, 7)
        starts_at = datetime.datetime(2009, 9, 7, 15, 00, 0) # 3:00pm
        ends_at   = datetime.datetime(2009, 9, 7, 16, 00, 0) # 4:00pm
                        
        catalog_event = DummyCatalogEvent(startDate=starts_at,
                                          endDate=ends_at)
        
        event = self._makeEvent(day_on_listview, catalog_event)
        self.assertEqual(event.time_in_words, '3pm - 4pm')
    
    # helpers
    
    def _makeEvent(self, *args, **kargs):
        from karl.content.calendar.presenters.base import BaseEvent
        return BaseEvent(*args, **kargs)

    def _makeDay(self, *args, **kargs):
        from karl.content.calendar.presenters.month import DayOnMonthView
        return DayOnMonthView(*args, **kargs)


def dummy_url_for(*args, **kargs):
    context = testing.DummyModel()
    request = testing.DummyRequest()
    from repoze.bfg.url import model_url
    return model_url(context, request, *args, **kargs)


class DummyDayWithEvents(object):
    def __init__(self):
        self.event_slots = [None]*5


class DummyCatalogEvent(object):
    def __init__(self, title='', location='', description='',
                 startDate=None, endDate=None):

        self.title = title
        self.location = location
        self.description = description
        
        if startDate is None:
            startDate = datetime.datetime.now()
        self.startDate = startDate

        if endDate is None:       
            endDate = datetime.datetime.now()
        self.endDate = endDate
        
        self._v_layer_color = 'blue'
        self._v_layer_title = 'Vacation'
            
