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
       new_word = set_random_word('test_com')
       comm_url = make_community(self, new_word)

       # Do whatever testing we want 


       self.get(server_url + "/communities/" + new_word + "/blog",
           description="Get /communities/" + new_word + "/blog")

       self.get(server_url + "/communities/" + new_word + "/blog/add_blogentry.html",
           description="Get /communities/bob/blog/add_blogentry.html")

       self.post(server_url + "/communities/" + new_word + "/blog/add_blogentry.html", params=[
           ['title', 'test blog entry 1'],
           ['text_text_format', 'text/html'],
           ['text', '<p>testing the new scripts</p>'],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/" + new_word + "/blog/add_blogentry.html")

       self.post(server_url + "/communities/" + new_word + "/blog/test-blog-entry-1/comments/add_comment.html", params=[
           ['add_comment_text_format', 'text/html'],
           ['add_comment', '<p>test comment 1</p>\r\n<p>&#160;</p>'],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/" + new_word + "/bl...ts/add_comment.html")

       self.get(server_url + "/communities/" + new_word + "/wiki",
           description="Get /communities/" + new_word + "/wiki")

       self.get(server_url + "/communities/" + new_word + "/wiki/front_page/edit.html",
           description="Get /communities/" + new_word + "/wiki/front_page/edit.html")

       self.post(server_url + "/communities/" + new_word + "/wiki/front_page/edit.html", params=[
           ['title', 'Front Page'],
           ['text_text_format', 'text/html'],
           ['text', '<p>This is the front page of your wiki.</p>\r\n<p>written in ((funkload))</p>'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/" + new_word + "/wiki/front_page/edit.html")

       self.get(server_url + "/communities/" + new_word + "/wiki/add_wikipage.html?title=funkload",
           description="Get /communities/" + new_word + "/wiki/add_wikipage.html")

       self.post(server_url + "/communities/" + new_word + "/wiki/add_wikipage.html?title=funkload", params=[
           ['title', 'funkload'],
           ['text_text_format', 'text/html'],
           ['text', '<p>this is the funkload test</p>'],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/" + new_word + "/wiki/add_wikipage.html")

       self.get(server_url + "/communities/" + new_word + "/wiki/",
           description="Get /communities/" + new_word + "/wiki/")

       self.get(server_url + "/communities/" + new_word + "/calendar",
           description="Get /communities/" + new_word + "/calendar")

       self.get(server_url + "/communities/" + new_word + "/calendar/add_calendarevent.html",
           description="Get /communities/" + new_word + "/ca..._calendarevent.html")

       self.post(server_url + "/communities/" + new_word + "/calendar/add_calendarevent.html", params=[
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
           description="Post /communities/"+ new_word +"/ca..._calendarevent.html")

       self.get(server_url + "/communities/" + new_word + "/calendar/",
           description="Get /communities/" + new_word + "/calendar/")

       self.get(server_url + "/communities/" + new_word + "/files",
           description="Get /communities/" + new_word + "/files")

       self.get(server_url + "/communities/" + new_word + "/files/add_file.html",
           description="Get /communities/" + new_word + "/files/add_file.html")

       self.post(server_url + "/communities/" + new_word + "/files/add_file.html", params=[
           ['title', 'Test File'],
           ['file', Upload("Photo 10.jpg")],
           ['sendalert', 'true'],
           ['security_state', 'inherits'],
           ['form.submitted', '']],
           description="Post /communities/" + new_word + "/files/add_file.html")

       self.get(server_url + "/communities/" + new_word + "/delete.html?confirm=1",
           description="Delete test community")

        # Logout
       logout(self)



    def tearDown(self):
       """Tears down the test."""
       self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
