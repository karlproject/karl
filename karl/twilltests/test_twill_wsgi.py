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

import os
import shutil
import twill
import karl.twillcommands
from cStringIO import StringIO
from repoze.bfg.paster import get_app

def _rm(path):
    """ grrr. """
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

class TestKarlTwill:
    '''Uses wsgiproxy to proxy requests to let twill run tests\

    Runs with "nosetests"
    You can use Twill commands including commands written for karl that are in
    karl.twillcommands by:
    twill.execute_string("valid twill statement")
    or you can run a twill file which is mostly what has been done in this class by
    twill.execute_string("runfile '${test_path}/path/to/twill_file.twill')'''

    def setUp(self):
        '''Create the app'''
        test_path =  os.path.abspath(os.path.dirname(__file__))
        testpath_command = "setglobal test_path " + test_path
        twill.execute_string(testpath_command)

        fixtures = os.path.join(test_path, 'fixtures')
        for to_delete in [fname for fname in os.listdir(fixtures)
                          if fname.startswith('Data.fs') or fname in ['blobs']]:
            _rm(os.path.join(fixtures, to_delete))
        os.mkdir(os.path.join(fixtures, 'blobs'))
        wsgi_app = get_app(os.path.join(test_path, 'fixtures', 'karl.ini'), 'main')

        def build_app():
            return wsgi_app

        twill.add_wsgi_intercept('localhost', 6543, build_app)
        twill.execute_string("extend_with karl.twillcommands")

        # mostly the same as karl3.conf without extending with flunc
        # and few other adjustments.

        twill.execute_string("runfile '" +
                             os.path.abspath(os.path.dirname(__file__)) +
                             "/test_twill_wsgi_karl3.conf'")

        # while we're at it, stop twill from running off at the mouth...
        # Comment out for debugging.
        # XXX How do we suppress the annoying "AT LINE: " output?
        outp = StringIO()
        twill.set_output(outp)

    def tearDown(self):
        # remove intercept
        twill.remove_wsgi_intercept('localhost', 6543)

        test_path =  os.path.abspath(os.path.dirname(__file__))
        fixtures = os.path.join(test_path, 'fixtures')
        for to_delete in [fname for fname in os.listdir(fixtures)
                          if fname.startswith('Data.fs') or fname in
                          ['blobs', 'mail_queue']]:
            _rm(os.path.join(fixtures, to_delete))

    def blog_tes(self):
        ''' Blog tests:'''

        # copied from twilltests/blog/blog-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # run blog tests
                      "runfile '${test_path}/blog/blog_view.twill'",
                      "runfile '${test_path}/blog/blogentry_aved.twill'",
                      "runfile '${test_path}/blog/blog_index.twill'",
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)

    def calendar_tes(self):
        ''' Calendar tests:'''

        # copied from twilltests/calendar/calendar-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # run calendar tests
                      "runfile '${test_path}/calendar/calendar-view.twill'",
                      "runfile '${test_path}/calendar/create-event.twill'",
                      "runfile '${test_path}/calendar/calendar-aved.twill'",
                      "runfile '${test_path}/calendar/calendar-index.twill'"
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)


    def community_tes(self):
        ''' Community tests:'''

        # copied from twilltests/community/community-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # Make community
                      "runfile '${test_path}/community/make_community.twill'",

                      # optional tests which we run to test functionality of new community.
                      # you can comment out if needed
                      "runfile '${test_path}/community/blog_initialize.twill'",
                      "runfile '${test_path}/community/calendar_initialize.twill'",
                      "runfile '${test_path}/community/files_initialize.twill'",
                      "runfile '${test_path}/community/wiki_initialize.twill'"
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)

    def files_tes(self):
        ''' Files tests:'''

        # copied from twilltests/files/files-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # Tests for files suite

                      "runfile '${test_path}/files/files_view.twill'",
                      "runfile '${test_path}/files/files_aved.twill'",
                      "runfile '${test_path}/files/files_index.twill'"
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)

    def profiles_tes(self):
        ''' Profiles tests:'''

        # copied from twilltests/profiles/profiles-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # Profile tests

                      # Test to see what profiles we can see
                      #user_view

                      # Login as admin before add/edit/delete user
                      "login 'admin'",

                      # Add, edit, and delete user account
                      "runfile '${test_path}/profiles/user_add.twill'",
                      #user_edit
                      "runfile '${test_path}/profiles/user_delete.twill'"
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)

    def search_tes(self):
        ''' Search tests:'''

        # copied from twilltests/files/files-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # Search tests

                      # Test searching for a blog entry
                      "runfile '${test_path}/search/search_blog_entry.twill'",

                      # Test searching for a calendar entry
                      "runfile '${test_path}/search/search_calendar_entry.twill'",

                      # Test searching for a community
                      "runfile '${test_path}/search/search_community.twill'",

                      # Test searching for a file
                      "runfile '${test_path}/search/search_file.twill'",

                      # Test searching for a user
                      "runfile '${test_path}/search/search_user.twill'",

                      # Test searching for wiki
                      "runfile '${test_path}/search/search_wiki_entry.twill'",

                      # Check the advanced search page
                      "runfile '${test_path}/search/advanced_search.twill'",
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)

    def tagging_tes(self):
        ''' Tagging tests:'''

        # copied from twilltests/files/files-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # Tag suite

                      # tag a community
                      "runfile '${test_path}/tagging/tag_community.twill'",

                      # tag a blog entry
                      #"runfile '${test_path}/tagging/tag_blog_entry.twill'",

                      # tag a calendar entry
                      "runfile '${test_path}/tagging/tag_calendar_entry.twill'",

                      # tag a file
                      "runfile '${test_path}/tagging/tag_file.twill'",

                      # tag a user
                      "runfile '${test_path}/tagging/tag_user.twill'",

                      # tag a wiki
                      "runfile '${test_path}/tagging/tag_wiki_entry.twill'",
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)

    def wiki_tes(self):
        ''' Wiki tests:'''

        # copied from twilltests/wiki/wiki-tests.tsuite
        mytwilltests = [
                      "login 'admin'",

                      # run wiki tests
                      "runfile '${test_path}/wiki/wiki_view.twill'",
                      "runfile '${test_path}/wiki/wikipage_aved.twill'",
                      "runfile '${test_path}/wiki/wiki_index.twill'"
                      ]
        for comm in mytwilltests:
            twill.execute_string(comm)


    def test_twill_all(self):
        ''' test_twill_all is equivalent to "All" tests from twilltests directory'''

        # copied from twilltests/all.tsuite


        # This suite is to test major functionality for this installation of karl.
        #
        # see more options in the README
        print twill.execute_string("go http://localhost:6543")
        twill.execute_string("login 'admin'")
        # check for login accounts
        twill.execute_string("runfile '${test_path}/profiles/user_karl3.twill'")

        # first login
        # changed to admin for this script (different from copy & paste)
        twill.execute_string("login 'admin'")

        # make community to test with
        self.community_tes()

        # run blog tests
        self.blog_tes()

        # run calendar tests
        self.calendar_tes()

        # run files tests
        self.files_tes()

        # run profile tests, then re-login as user vs. admin
        twill.execute_string("runfile '${test_path}/profiles/user_initialize.twill'")
        self.profiles_tes()

        # run search tests
        self.search_tes()

        # run tagging tests
        self.tagging_tes()

        # run wiki tests
        self.wiki_tes()

        # This is copied from all_cleanup.tsuite
        # This is the cleanup routines for the "all" suite
        # To run just the cleanup suite, use the -C flag
        # flunc -C all
        #
        # or to run the "all" suite without running cleanup
        # use the -X flag
        # flunc -X all
        # See README.txt for more

        # Cleanup tests
        twill.execute_string("runfile '${test_path}/community/delete_testing_community.twill'")

        twill.execute_string("logout")
