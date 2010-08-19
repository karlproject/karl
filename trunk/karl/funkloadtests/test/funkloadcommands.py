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

"""Extend funkload with commands unique to KARL tests

"""

__all__ = ['login',
           'logout',
           'set_random_word',
           'make_community',
           'remove_community'
           ]

DEBUG=True
import unittest
import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data

def login(self, login, pwd):
    # although I can get login to work, there seems to be a problem with
    # webunit re-submitting cookies on any follow up request
    # therefore, I'm skipping login and using BasicAuth
    #    params = [["login", login],
    #              ["password", pwd],
    #              ['max_age', '315360000'],
    #              ['came_from',self.server_url],
    #              ['form.submitted', '1'],
    #              ["submit", "Login"]]
    #    print self.post('%s/login' % self.server_url, params,
    #               description="Post /login")
    self.setBasicAuth(login,pwd)
    self.get("%s/"% self.server_url)
    self.logd("Logged in as %s" % login)
    self.assert_('My Profile' in self.getBody(),
                 "Invalid credential %s:%s" % (login, pwd))
    self._karl_login = login

def logout(self):
   self.get('%s/logout' % self.server_url,
            description="logout %s" % self._karl_login)

def set_random_word(varname):
    """Create a random word based by adding an int to varname """

    randint = str(random.randint(100000, 999999))
    return (varname + randint)

def make_community(self, community):
    # return the doc_url
    community_url = "%s/communities/%s" % (self.server_url, community)
    comm_text = "This community was made by funkload testing tool."
    response = self.get(community_url,ok_codes=[200,301,302,404])
    if response.code != 404:
        self.get("%s/delete.html?confirm=1" % community_url)
        print "Deleted community first: %s" % community
    self.post( "http://localhost:6543/communities/add_community.html", params=[
        ['title', community],
        ['description', comm_text],
        ['text_text_format', 'text/html'],
        ['text', comm_text],
        ['security_state', 'public'],
        ['blog', 'Blog'],
        ['wiki', 'Wiki'],
        ['calendar', 'Calendar'],
        ['files', 'Files'],
        ['forums', 'Forums'],
        ['form.submitted', '']],
        description="Post /communities/add_community.html",ok_codes=[200,301,302])
    self.assert_("Add Existing" in self.getBody(),
                     "Error in creating community")
    print "Community created: %s" % community
    return community_url

def remove_community(self, community):
    # return the doc_url
    community_url = "%s/communities/%s" % (self.server_url, community)
    response = self.get(community_url,ok_codes=[200,301,302,404])
    if response.code != 404:
        self.get("%s/delete.html?confirm=1" % community_url)
        print "Deleted community: %s" % community

