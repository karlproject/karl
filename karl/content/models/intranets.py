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


from zope.interface import alsoProvides
from zope.interface import implements

from repoze.lemonade.content import create_content
from repoze.folder import Folder

from karl.models.interfaces import IToolFactory
from karl.models.tool import ToolFactory

from karl.models.interfaces import IIntranets
from karl.content.interfaces import IIntranetsTool

class IntranetsFolder(Folder):
    implements(IIntranetsTool)
    title = u'Intranets'

class IntranetsToolFactory(ToolFactory):
    implements(IToolFactory)
    name = 'intranets'
    interfaces = (IIntranetsTool,)
    def add(self, context, request):
        intranets = create_content(IIntranetsTool)
        context['intranets'] = intranets

        # Mark the context (e.g. /osi) as providing IIntranets
        alsoProvides(context, IIntranets)

    def remove(self, context, request):
        del context['intranets']
        
intranets_tool_factory = IntranetsToolFactory()
