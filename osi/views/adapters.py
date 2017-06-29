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

from os.path import join

from zope.interface import implements

from pyramid.renderers import render
from pyramid.path import package_path
from pyramid.traversal import find_interface

from karl.views.interfaces import IFooter

from karl.utils import find_community
from karl.utils import find_site

from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import IForum
from karl.models.interfaces import IIntranets
from karl.models.interfaces import IIntranet
from karl.content.interfaces import IIntranetFolder
from karl.content.views.interfaces import IFolderCustomizer
from karl.views.interfaces import IFolderAddables
from karl.views.interfaces import ILayoutProvider
from karl.content.views.interfaces import INetworkEventsMarker
from karl.content.views.interfaces import INetworkNewsMarker
from karl.content.views.interfaces import IShowSendalert
from karl.views.interfaces import IInvitationBoilerplate
from karl.content.interfaces import IReferencesFolder
from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection


class FolderCustomizer(object):
    """ Site-specific policies for folders after creation """
    implements(IFolderCustomizer)

    def __init__(self, context, request):
        assert ICommunityFolder.providedBy(context)
        self.context = context
        self.request = request

    @property
    def markers(self):
        """ Based on policy, return extra markers for new folder """

        _markers = []

        # Most importantly: are we an IntranetFolder?  If so, we need
        # to mark thus, to allow other content types to be added
        # beyond folder and file.
        intranets = find_interface(self.context, IIntranets)
        if intranets:
            _markers.append(IIntranetFolder)

        return _markers

class ShowSendalert(object):
    """ Site-specific policies for showing the alert checkbox """
    implements(IShowSendalert)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def show_sendalert(self):
        """ Return boolean on whether to suppress this field """

        intranets = find_interface(self.context, IIntranets)
        # We don't want to send alerts for content created inside an
        # intranet.
        if intranets:
            return False

        return True


class InvitationBoilerplate(object):
    """ Policy for where to get terms-conditions and privacy statement """
    implements(IInvitationBoilerplate)

    tc_default_text = "<p>No terms and conditions found.</p>"
    ps_default_text = "<p>No privacy statement found.</p>"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def terms_and_conditions(self):
        site = find_site(self.context)
        offices = site.get('offices')
        if not offices:
            return self.tc_default_text
        files = offices.get('files')
        if not files:
            return self.tc_default_text
        tc = files.get('terms_and_conditions', None)
        if tc:
            return tc.text
        else:
            return self.tc_default_text

    @property
    def privacy_statement(self):
        site = find_site(self.context)
        offices = site.get('offices')
        if not offices:
            return self.ps_default_text
        files = offices.get('files', None)
        if not files:
            return self.ps_default_text
        ps = files.get('privacy_statement', None)
        if ps:
            return ps.text
        else:
            return self.ps_default_text


class OSIFooter(object):
    """ Multi-adapter for OSI-specific page footer.
    """
    implements(IFooter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, api):
        return render(
            'templates/footer.pt',
            dict(api=api),
            request=self.request,
            )
