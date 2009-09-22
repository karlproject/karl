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

from repoze.bfg.chameleon_zpt import get_template


class Navigation(object):
    '''
    Encapsulate the logic for building the navigation above each calendar.
    '''
    def __init__(self, calendar_presenter):
        self._presenter = calendar_presenter
        
        self._init_left_side()
        self._init_right_side()

        self._init_template()
    
    def _init_left_side(self):
        ''' [ Today ]  [ < ]  [ > ] '''

        if self._is_today_shown():
            self.today_button_img = 'today_disabled.png'
        else:
            self.today_button_img = 'today.png'

        self.today_href = ''
        self.next_href  = ''
        self.prev_href  = ''

    def _init_right_side(self):
        ''' [ Day ]  [ Week ]  [ Month ]  [ List ] '''
        format = '%s?year=%d&month=%d&day=%d' 

        for view_name in ('day', 'week', 'month', 'list'):
            url = self._presenter.url_for('new%s.html' % view_name)
            sub = (url, self._presenter.focus_datetime.year, 
                        self._presenter.focus_datetime.month, 
                        self._presenter.focus_datetime.day)
            setattr(self, '%s_button_href' % view_name, 
                    format % sub)
            setattr(self, '%s_button_img' % view_name, 
                    '%s_up.png' % view_name)
            
        # Depress active button
        setattr(self, '%s_button_img' % self._presenter.name, 
                      '%s_down.png'   % self._presenter.name)
    
    def _is_today_shown(self):
        now_at   = self._presenter.now_datetime

        within_start = (now_at >= self._presenter.first_moment)
        within_end   = (now_at <= self._presenter.last_moment)

        return (within_start and within_end)

    def _init_template(self):
        path = '../views/templates/newcalendar_navigation.pt'
        self._template = get_template(path)

    @property
    def macros(self):
        return self._template.macros
