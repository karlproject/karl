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

from repoze.bfg.url import model_url

class ToolFactory(object):
    name = None
    interfaces = ()
    def add(self, context, request):
        raise NotImplementedError

    def remove(self, context, request):
        raise NotImplementedError

    def is_present(self, context, request):
        if self.name is None:
            raise NotImplementedError
        return self.name in context

    def is_current(self, context, request):
        if not self.interfaces:
            raise NotImplementedError
        for iface in self.interfaces:
            if iface.providedBy(request.context):
                return True
        return False

    def tab_url(self, context, request):
        if not self.name:
            raise NotImplementedError
        return model_url(context, request, self.name)
    
