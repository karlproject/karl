# -*- coding: iso-8859-15 -*-
"""test FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload

from funkload.utils import Data
from funkloadcommands import *

class karltest(FunkLoadTestCase):

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

    def test(self):
       server_url = self.server_url
       user_login = self.cred_admin[0]

        # Logs in
       login(self,*self.cred_admin)

        # Makes a community if necessary
       comm_url = make_community(self, "bob")

       # Do whatever testing we want 

       self.get(server_url + "/communities/bob/blog",
           description="Get /communities/bob/blog")

       self.get(server_url + "/communities/bob/blog/add_blogentry.html",
           description="Get /communities/bob/blog/add_blogentry.html")

       self.post(server_url + "/communities/bob/blog/add_blogentry.html", params=[
           ['title', 'test blog entry 1'],
           ['text_text_format', 'text/html'],
           ['text', '<p>testing the new scripts</p>'],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/bob/blog/add_blogentry.html")

       self.post(server_url + "/communities/bob/blog/test-blog-entry-1/comments/add_comment.html", params=[
           ['add_comment_text_format', 'text/html'],
           ['add_comment', '<p>test comment 1</p>\r\n<p>&#160;</p>'],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/bob/bl...ts/add_comment.html")

       self.get(server_url + "/communities/bob/wiki",
           description="Get /communities/bob/wiki")

       self.get(server_url + "/communities/bob/wiki/front_page/edit.html",
           description="Get /communities/bob/wiki/front_page/edit.html")

       self.post(server_url + "/communities/bob/wiki/front_page/edit.html", params=[
           ['title', 'Front Page'],
           ['text_text_format', 'text/html'],
           ['text', '<p>This is the front page of your wiki.</p>\r\n<p>written in ((funkload))</p>'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/bob/wiki/front_page/edit.html")

       self.get(server_url + "/communities/bob/wiki/add_wikipage.html?title=funkload",
           description="Get /communities/bob/wiki/add_wikipage.html")

       self.post(server_url + "/communities/bob/wiki/add_wikipage.html?title=funkload", params=[
           ['title', 'funkload'],
           ['text_text_format', 'text/html'],
           ['text', '<p>this is the funkload test</p>'],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/bob/wiki/add_wikipage.html")

       self.get(server_url + "/communities/bob/wiki/",
           description="Get /communities/bob/wiki/")

       self.get(server_url + "/communities/bob/calendar",
           description="Get /communities/bob/calendar")

       self.get(server_url + "/communities/bob/calendar/add_calendarevent.html",
           description="Get /communities/bob/ca..._calendarevent.html")

       self.post(server_url + "/communities/bob/calendar/add_calendarevent.html", params=[
           ['title', 'test event 1'],
           ['virtual_calendar', ''],
           ['startDate', '10/19/2009 16:00'],
           ['endDate', '10/19/2009 17:00'],
           ['location', ''],
           ['text_text_format', 'text/html'],
           ['text', '<p>test event</p>'],
           ['attendees', ''],
           ['contact_name', ''],
           ['contact_email', ''],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/bob/ca..._calendarevent.html")

       self.get(server_url + "/communities/bob/calendar/",
           description="Get /communities/bob/calendar/")

       self.get(server_url + "/communities/bob/files",
           description="Get /communities/bob/files")

       self.get(server_url + "/communities/bob/files/add_file.html",
           description="Get /communities/bob/files/add_file.html")

       self.post(server_url + "/communities/bob/files/add_file.html", params=[
           ['title', 'Test File'],
           ['file', Upload("Photo 10.jpg")],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/bob/files/add_file.html")

       self.get(server_url + "/communities/",
           description="Get /communities/")

        # Logout
       logout(self)



    def tearDown(self):
       """Tears down the test."""
       self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
