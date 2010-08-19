# -*- coding: iso-8859-15 -*-
"""test FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload

from funkload.utils import Data
from funkloadcommands import *

class Community(FunkLoadTestCase):

    def setUp(self):
       """Setting up test."""
       self.logd("setUp")
       self.server_url = self.conf_get('main', 'url')
       credential_host = self.conf_get('credential', 'host')
       credential_port = self.conf_getInt('credential', 'port')
       self.credential_host = credential_host
       self.credential_port = credential_port
       self.cred_admin = ("admin","admin")
       self.cred_member = ("staff1","staff1")

    def test_10_create_comm(self):
        server_url = self.server_url
        user_login = self.cred_admin[0]
        login(self,*self.cred_admin)
        make_community(self,"jbglenn")
        logout(self)

    def test_10_test_blog(self):
        server_url = self.server_url
        user_login = self.cred_admin[0]
        login(self,*self.cred_admin)
        comm_url = make_community(self, "test_blog")
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
        logout(self)


    def test_11_delete_comm(self):
        server_url = self.server_url
        user_login = self.cred_admin[0]
        login(self,*self.cred_admin)
        remove_community(self,"jbglenn")
        logout(self)


    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
