# -*- coding: iso-8859-15 -*-
"""test FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload

from funkload.utils import Data

class CommunityTestCase(FunkLoadTestCase):
    """XXX

    This test use a configuration file Community.conf.
    """
    def karlLogin(self, login, pwd):
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

    def karlLogout(self):
        self.get('%s/logout' % self.server_url,
                 description="logout %s" % self._karl_login)


    def karlCreateCommunity(self, community):
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

    def karlRemoveCommunity(self, community):
        # return the doc_url
        community_url = "%s/communities/%s" % (self.server_url, community)
        response = self.get(community_url,ok_codes=[200,301,302,404])
        if response.code != 404:
            self.get("%s/delete.html?confirm=1" % community_url)
            print "Deleted community: %s" % community


class Community(CommunityTestCase):

    def setUp(self):
       """Setting up test."""
       self.logd("setUp")
       self.server_url = self.conf_get('main', 'url')
       credential_host = self.conf_get('credential', 'host')
       credential_port = self.conf_getInt('credential', 'port')
       self.credential_host = credential_host
       self.credential_port = credential_port
       self.cred_admin = ("admin","admin")
       self.cred_member = ("admin","admin")

    def test_10_create_comm(self):
        server_url = self.server_url
        login = self.cred_admin[0]
        self.karlLogin(*self.cred_admin)
        self.karlCreateCommunity("jbglenn")
        self.karlLogout()

    def test_10_test_blog(self):
        server_url = self.server_url
        login = self.cred_admin[0]
        self.karlLogin(*self.cred_admin)
        comm_url = self.karlCreateCommunity("test_blog")
        self.get("%s/blog" % comm_url)
        self.assert_("Add Blog Entry" in self.getBody(),
                         "Error in finding blog")
        self.post("http://localhost:6543/communities/test_blog/blog/add_blogentry.html", params=[
                            ['title', 'test title'],
                            ['text_text_format', 'text/html'],
                            ['text', '<p>test text in blog entry</p>'],
                            ['sendalert', 'true'],
                            ['security_state', 'inherits'],
                            ['form.submitted', '']],
                            description="Post /communities/test_b.../add_blogentry.html")
        self.karlLogout()


    def test_11_delete_comm(self):
        server_url = self.server_url
        login = self.cred_admin[0]
        self.karlLogin(*self.cred_admin)
        self.karlRemoveCommunity("jbglenn")
        self.karlLogout()


    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
