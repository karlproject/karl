from karl.webtests.base import Base

# Help on the 72 char limit
dc = '/communities/default'

class TestAllScreens(Base):
    """
    Basic smoke test, hits all screens in Karl and makes sure the templates
    render without raising an exception.
    """

    def test_it(self):
        # login
        response = self.login()
        self.assertTrue('Default Community' in response)

        # admin_deletecontent
        response = self.app.get('/delete_content.html')
        self.assertTrue('Admin Section: Delete Content' in response)

        # admin_emailusers
        response = self.app.get('/email_users.html')
        self.assertTrue('Admin Section: Email Users' in response)

        # admin_errormonitor
        response = self.app.get('/error_monitor.html')
        self.assertTrue('Admin Section: Error Monitor' in response)

        # admin_movecontent
        response = self.app.get('/move_content.html')
        self.assertTrue('Admin Section: Move Content' in response)

        # admin_po_quarantine
        response = self.app.get('/po_quarantine.html')
        self.assertTrue('Post Office Quarantine' in response)

        # admin_renameusers
        response = self.app.get('/rename_user.html')
        self.assertTrue('Admin Section: Rename or Merge' in response)

        # admin_siteannouncement
        response = self.app.get('/site_announcement.html')
        self.assertTrue('Admin Section: Site Announcement' in response)

        # admin_uploadusers
        response = self.app.get('/upload_users_csv.html')
        self.assertTrue('Admin Section: Upload Users' in response)

        # admin_view
        response = self.app.get('/admin.html')
        self.assertTrue('Admin Section' in response)

        ##################
        # blog_view
        response = self.app.get(dc + '/blog')
        self.assertTrue('Add Blog Entry' in response)

        # blogentry_add
        response = self.app.get(dc + '/blog/add_blogentry.html')
        self.assertTrue('Add Blog Entry' in response)
        form = response.forms['save']
        form['title'] = 'someblogpost'
        response = form.submit('submit')

        # blogentry_view
        response = self.app.get(dc + '/blog/someblogpost')
        self.assertTrue('someblogpost' in response)

        # blogentry_edit
        response = self.app.get(dc + '/blog/someblogpost/edit.html')
        self.assertTrue('Edit someblogpost' in response)


        # Add a comment, see it in the widget, navigate to it, edit
        response = self.app.get(dc + '/blog/someblogpost')
        form = response.forms['save']
        form['add_comment'] = "someblogcomment"
        response = form.submit('submit')

        # comments_widget
        response = self.app.get(dc + '/blog/someblogpost')
        self.assertTrue('someblogcomment' in response)

        # comment_view
        url = dc + '/blog/someblogpost/comments/001'
        response = self.app.get(url)
        self.assertTrue('someblogcomment' in response)

        # comment_edit
        response = self.app.get(url + '/edit.html')
        self.assertTrue('Edit Re:' in response)


        # attachment_download

        # attachment_edit

        # attachment_view

        # attachments_widget

        # calendar_view
        response = self.app.get(dc + '/calendar/month.html')
        self.assertTrue('Layer:' in response)
        response = self.app.get(dc + '/calendar/week.html')
        self.assertTrue('Layer:' in response)
        response = self.app.get(dc + '/calendar/day.html')
        self.assertTrue('Layer:' in response)

        # calendar_listview
        response = self.app.get(dc + '/calendar/list.html')
        self.assertTrue('Layer:' in response)

        # calendar_setup
        response = self.app.get(dc + '/calendar/setup.html')
        self.assertTrue('Calendar Categories' in response)

        # calendarentry_add
        response = self.app.get(dc + '/calendar/add_calendarevent.html')
        self.assertTrue('Start Date' in response)
        form = response.forms['save']
        form['title'] = "sometitle"
        form['start_date'] = "4/12/2012 11:00"
        form['end_date'] = "4/13/2012 11:00"
        response = form.submit('submit')

        # calendarentry_view
        response = self.app.get(dc + '/calendar/sometitle')
        self.assertTrue('sometitle' in response)

        # calendarentry_edit
        response = self.app.get(dc + '/calendar/sometitle')
        form['title'] = "anothertitle"
        response = form.submit('submit')
        response.follow()
        self.assertTrue('anothertitle' in response)

        # calendarentry_ics
        response = self.app.get(dc + '/calendar/sometitle/@@event.ics')
        self.assertTrue('VCALENDAR' in response)

        # chatter_discover

        # chatter_following

        # chatter_messages

        # chatter_posts

        # chatter_pushdown

        # chatter_topics

        # communities_view, active vs. all
        response = self.app.get('/communities/active_communities.html')
        self.assertTrue('KARL Communities' in response)
        response = self.app.get('/communities/all_communities.html')
        self.assertTrue('KARL Communities' in response)

        # community_add
        response = self.app.get('/communities/add_community.html')
        form = response.forms['save']
        form['title'] = "sometitle"
        form['description'] = "somedescription"
        form.submit('submit')

        # community_edit
        response = self.app.get(dc + '/edit.html')
        self.assertTrue("Edit Default Community" in response)

        # community_join
        response = self.app.get(dc + '/join.html')
        self.assertTrue("Type a message" in response)

        # community_overview
        response = self.app.get(dc + '/view.html')
        self.assertTrue("Overview" in response)

        # community_searchresults
        response = self.app.get(dc + '/searchresults.html?body=Hatter')
        self.assertTrue("Reference Manuals" in response)

        # community_tagcloud
        response = self.app.get(dc + '/tagcloud.html')
        self.assertTrue("a list of tags" in response)

        # community_taglisting
        response = self.app.get(dc + '/taglisting.html')
        self.assertTrue("shows all the tags" in response)

        # file_add
        response = self.app.get(dc + '/files/add_file.html')
        self.assertTrue("Add File</h" in response)

        # file_download
        # file_edit
        # file_view
        # folder_add
        response = self.app.get(dc + '/files/add_folder.html')
        self.assertTrue("Add Folder</h" in response)

        # folder_edit
        # folder_view
        response = self.app.get(dc + '/files/')
        self.assertTrue("Files </h" in response)

        # forum_add
        # forum_edit
        # forum_view
        # forums_allforums
        # forumtopic_add
        # forumtopic_edit
        # forumtopic_view

        # atom
        response = self.app.get(dc + '/atom.xml')
        self.assertTrue("subtitle" in response)


        # error_forbidden
        # error_general
        # error_notfound

        # resource_advanced
        response = self.app.get(dc + '/advanced.html')
        self.assertTrue("Advanced Settings for" in response)

        # resource_delete
        response = self.app.get(dc + '/calendar/sometitle/delete.html')
        self.assertTrue("you really want" in response)

        # intranet_networkevents
        # intranet_networknews
        # intranet_view

        # members_picturesview
        response = self.app.get(dc + '/members')
        self.assertTrue("Community Members" in response)

        # members_tableview
        response = self.app.get(dc + '/members?hide_pictures')
        self.assertTrue("Organization" in response)

        # members_manage
        response = self.app.get(dc + '/members/manage.html')
        self.assertTrue('Manage Community Members' in response)

        # members_addexisting
        response = self.app.get(dc + '/members/add_existing.html')
        self.assertTrue('Add Existing KARL Users' in response)

        # members_invitenew
        response = self.app.get(dc + '/members/invite_new.html')
        self.assertTrue('Invite New KARL Users' in response)
        # Let's make an invitation, find the invitation code,
        # so we can use it at the end after logout
        form = response.forms[1]
        form['email_addresses'] = 'foo@bar.org'
        response = form.submit('submit')
        response = response.follow()
        xp = '//table[@id="members"]/tbody/tr[2]/td[2]/span/@title'
        invitation_key = response.lxml.xpath(xp)[0]


        # networknews_view
        # newsitem_add
        # newsitem_edit
        # newsitem_view

        # profile_adminedit
        # profile_recentcontent
        # profile_edit
        # profile_managecommunities
        # profile_managetags
        # profile_view

        # wiki_index
        response = self.app.get(dc + '/wiki/wikitoc.html')
        self.assertTrue('Wiki Index' in response)

        # wikipage_add
        url = '/wiki/add_wikipage.html?title=yourwiki'
        response = self.app.get(dc + url)
        form = response.forms['save']
        response = form.submit('submit')

        # wikipage_view
        response = self.app.get(dc + '/wiki/yourwiki/')
        self.assertTrue('yourwiki' in response)

        # wikipage_edit
        response = self.app.get(dc + '/wiki/yourwiki/edit.html')
        self.assertTrue('Edit yourwiki' in response)
        form = response.forms['save']
        form['text'] = "<p>editedtext</p>"
        response = form.submit('submit')
        response = self.app.get(dc + '/wiki/yourwiki/')
        self.assertTrue('<p>editedtext</p>' in response)

        # history_view
        response = self.app.get(dc + '/wiki/yourwiki/history.html')
        self.assertTrue('History for yourwiki' in response)

        # history_preview
        url = '/wiki/yourwiki/preview.html?version_num=1'
        response = self.app.get(dc + url)
        self.assertTrue('"author":' in response)


        # history_restore
        url = '/wiki/yourwiki/revert?version_num=1'
        response = self.app.get(dc + url)
        response = self.app.get(dc + '/wiki/yourwiki/')
        self.assertTrue('<p>editedtext</p>' not in response)

        # trash_view
        url = '/wiki/yourwiki/delete.html?confirm=1'
        response = self.app.get(dc + '/trash')
        self.assertTrue('Date Deleted' in response)
        self.assertTrue('yourwiki' in response)

        # global searchresults
        response = self.app.get(dc + '/searchresults.html?body=france')
        self.assertTrue('Reference Manuals' in response)

        # logout
        response = self.app.get('/logout.html')
        response = response.follow()
        self.assertTrue('Login to' in response)

        # members_acceptinvitation
        # We have to be logged out in order to see this
        response = self.app.get(dc + '/members/' + invitation_key)
        self.assertTrue('You have been invited to join' in response)
