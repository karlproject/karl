from karl.webtests.base import Base

# Help on the 72 char limit
dc = '/communities/default'

class TestCommunitiesView(Base):

    def test_it(self):

        # login
        self.login()
        self.assertTrue('Active KARL Communities')

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

        # blog_view
        response = self.app.get(dc + '/blog')
        self.assertTrue('Add Blog Entry' in response)

        # blogentry_add

        # blogentry_edit

        # blogentry_view

        # attachment_download
        # attachment_edit
        # attachment_view
        # attachments_widget

        # calendar_listview
        # calendar_setup
        # calendar_view
        # calendarentry_add
        # calendarentry_edit
        # calendarentry_ics
        # calendarentry_view
        # chatter_discover
        # chatter_following
        # chatter_messages
        # chatter_posts
        # chatter_pushdown
        # chatter_topics
        # comment_edit
        # comments_widget
        # communities_view, active vs. all
        response = self.app.get('/communities/active_communities.html')
        self.assertTrue('KARL Communities' in response)
        response = self.app.get('/communities/all_communities.html')
        self.assertTrue('KARL Communities' in response)

        # community_add
        # community_edit
        # community_join
        # community_overview
        # community_searchresults
        # community_tagcloud
        # community_taglisting
        # file_add
        # file_download
        # file_edit
        # file_view
        # folder_add
        # folder_edit
        # folder_view
        # forum_add
        # forum_edit
        # forum_view
        # forums_allforums
        # forumtopic_add
        # forumtopic_edit
        # forumtopic_view
        # atom
        # contact
        # error_forbidden
        # error_general
        # error_notfound
        # legal
        # resource_advanced
        # resource_delete
        # history_preview
        # history_restore
        # history_view
        # intranet_networkevents
        # intranet_networknews
        # intranet_view
        # members_acceptinvitation
        # members_addexisting
        # members_invitenew
        # members_manage
        # members_picturesview
        # members_tableview
        # networknews_view
        # newsitem_add
        # newsitem_edit
        # newsitem_view
        # page_title
        # profile_adminedit
        # profile_edit
        # profile_managecommunities
        # profile_managetags
        # profile_view
        # trash_deletepermanently
        # trash_restore
        # trash_view
        # wiki_index
        response = self.app.get(dc + '/wiki/wikitoc.html')
        self.assertTrue('Wiki Index' in response)

        # wikipage_edit
        # wikipage_view

        # logout
