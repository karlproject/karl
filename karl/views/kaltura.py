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

from simplejson import JSONEncoder
from pyramid.response import Response
import transaction

from karl.views.api import TemplateAPI
from karl.utilities.kaltura_kcl_py.kaltura_client import KalturaConfiguration 
from karl.utilities.kaltura_kcl_py.kaltura_client import KalturaClient 
from karl.utilities.kaltura_kcl_py.kaltura_client import KalturaSessionUser 

# a somewhat useful decorator
class jsonview(object):
    def __init__(self, content_type="application/x-json"):
        self.content_type = content_type

    def __call__(self, inner):
        def wrapped(*arg, **kw):
            payload = inner(*arg, **kw)
            if 'error' in payload:
                transaction.doom()
            result = JSONEncoder().encode(payload)
            return Response(result, content_type=self.content_type)
        return wrapped

def xmltodict(node):
    'Convert the xml to a python-friendly dict.'
    #return dict([(key, value._text) for (key, value) in node._childrenByName.iteritems()])
    result = {}
    for key, value in node._childrenByName.iteritems():
        try:
            result[key] = value._text
        except KeyError:
            result[key] = xmltodict(value)
    return result


@jsonview()
def create_session(context, request):
    """Create a kaltura session.
    """
    api = TemplateAPI(context, request)
    kaltura_info = api.kaltura_info
    kc = KalturaConfiguration(kaltura_info['partner_id'], kaltura_info['sub_partner_id'])
    client = KalturaClient(kc)
    user = KalturaSessionUser(kaltura_info['local_user'])
    session = client.startSession(user, kaltura_info['admin_secret'], admin=2)
    result = xmltodict(session)
    if not result['error']:
        # error key causes a server error in jsonview, so if error={}, delete it
        del result['error']
    return result
