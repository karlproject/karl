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

import re

from webob.exc import HTTPFound
from repoze.bfg.chameleon_zpt import render_template_to_response

from karl.security.policy import NO_INHERIT

COMMA_WS = re.compile(r'[\s,]+')

def edit_acl_view(context, request):

    acl = getattr(context, '__acl__', [])
    if acl and acl[-1] == NO_INHERIT:
        acl = acl[:-1]
        epilog = [NO_INHERIT]
    else:
        epilog = []

    if 'form.move_up' in request.POST:
        index = int(request.POST['index'])
        if index > 0:
            new = acl[:]
            new[index-1], new[index] = new[index], new[index-1]
            context.__acl__ = new + epilog

    if 'form.move_down' in request.POST:
        index = int(request.POST['index'])
        if index < len(acl) - 1:
            new = acl[:]
            new[index+1], new[index] = new[index], new[index+1]
            context.__acl__ = new + epilog

    if 'form.remove' in request.POST:
        index = int(request.POST['index'])
        new = acl[:]
        del new[index]
        context.__acl__ = new + epilog

    if 'form.add' in request.POST:
        verb = request.POST['verb']
        principal = request.POST['principal']
        permissions = tuple(filter(None,
                              COMMA_WS.split(request.POST['permissions'])))
        new = acl[:]
        new.append((verb, principal, permissions))
        context.__acl__ = new + epilog

    if 'form.inherit' in request.POST:
        no_inherit = request.POST['inherit'] == 'disabled'
        if no_inherit:
            context.__acl__ = acl + [NO_INHERIT]
        else:
            context.__acl__ = acl

    parent = context.__parent__
    parent_acl = []
    while parent is not None:
        p_acl = getattr(parent, '__acl__', ())
        stop = False
        for ace in p_acl:
            if ace == NO_INHERIT:
                stop = True
            else:
                parent_acl.append(ace)
        if stop:
            break
        parent = parent.__parent__

    local_acl = []
    inheriting = 'enabled'
    l_acl = getattr(context, '__acl__', ())
    for l_ace in l_acl:
        if l_ace == NO_INHERIT:
            inheriting = 'disabled'
            break
        local_acl.append(l_ace)

    return render_template_to_response('templates/edit_acl.pt',
                                       parent_acl=parent_acl or (),
                                       local_acl=local_acl,
                                       inheriting=inheriting,
                                      )
