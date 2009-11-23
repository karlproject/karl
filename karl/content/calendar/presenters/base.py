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


class BasePresenter(object):
    '''
    A calendar presenter encapsulates the complex presentation logic required
    for rendering a calendar.  It aggregates data from the model and view,
    manipulates that data solely for presentation, and exposes properties that
    are used by the template.

    Constructor Arguments
    
    ``focus_datetime``

       A ``datetime`` containing the moment in time that the 
       calendar will focus around.

    ``now_datetime``
    
       A ``datetime`` containing the moment of "now".  
     
    ``url_for``
       
       A function wrapping ``repoze.bfg.url.model_url``, where the current 
       context and request are already set.  A presenter often needs to
       generate URLs, but the context and request are not its concern.
    '''

    name = 'abstract'
    title = ''
    
    def __init__(self, focus_datetime, now_datetime, url_for):
        self.focus_datetime = focus_datetime
        self.now_datetime   = now_datetime

        self.url_for        = url_for
        self.add_event_url  = self.url_for('add_calendarevent.html')
        
        self._initialize()

    def _initialize(self):
        '''
        Hook after ``__init__`` has finished that contains initialization
        of the presenter.  This is used to set up the calendar canvas.
        '''
        pass

    def paint_events(self, events):
        '''
        Paint events list (ICalendarEvent) on this calendar's canvas.  This
        is typically where the most logic in the presenter will be needed.
        '''
        raise NotImplementedError

    @property
    def first_moment(self):
        '''
        A ``datetime`` containing the first moment in time that this
        presenter will present.  It is the presenter's responsibility to
        compute what it will present before and after the ``focus_datetime``.
        '''
        raise NotImplementedError

    @property
    def last_moment(self):
        '''
        A ``datetime`` containing the last moment in time that this
        presenter will present.
        '''
        raise NotImplementedError

    @property
    def template_filename(self):
        '''
        The template containing markup for this presenter.  Each concrete
        presenter is coupled to a specific template and exposes properties
        specific to that template.
        '''
        raise NotImplementedError


class BaseEvent(object):
    def __init__(self, day, catalog_event, 
                 show_url='#', edit_url='#', delete_url='#'):

        self._day = day # DayOnListView                               
        self._catalog_event = catalog_event # ICalendarEvent                               

        self.color = catalog_event._v_layer_color 
        self.layer = catalog_event._v_layer_title 

        self.show_url = show_url
        self.edit_url = edit_url
        self.delete_url = delete_url

        self._init_properties()
        self._init_first_moment()
        self._init_last_moment()

    def _init_properties(self):
        self.title       = self._catalog_event.title
        self.location    = self._catalog_event.location
        self.description = self._catalog_event.description
    
    def _init_first_moment(self):
        if self._catalog_event.startDate < self._day.first_moment:
            self.first_moment = self._day.first_moment
        else:
            self.first_moment = self._catalog_event.startDate

    def _init_last_moment(self):
        if self._catalog_event.endDate > self._day.last_moment:
            self.last_moment = self._day.last_moment
        else:
            self.last_moment = self._catalog_event.endDate

    @property
    def time_in_words(self):
        same_first = (self.first_moment == self._day.first_moment)
        same_last  = (self.last_moment  == self._day.last_moment)
        if same_first and same_last: 
            return 'all-day'

        starts = self._format_time_of_day(self.first_moment)
        ends   = self._format_time_of_day(self.last_moment)
        return '%s - %s' % (starts, ends) #=> "3pm - 3:30pm"
   
    def _format_time_of_day(self, dt):
        ''' Format a time like "2pm" or "3:15pm". '''
        fmt = dt.strftime('%l:%M%p').lstrip(' ')
        time, ampm = fmt[:-2], fmt[-2:].lower()
        if time.endswith(':00'):
            time = time[:-3]
        return time + ampm
