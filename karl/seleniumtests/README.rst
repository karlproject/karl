========================
Selenium2 Tests for KARL
========================

KARL had a pile of Twill and Selenium1 tests. This directory contains
the start of a move to Selenium2, with tests written in Python.

Additionally, this document contains a listing of every "screen" in
KARL. The listing will be removed as the Selenium2 tests get filled in,
making the Selenium2 tests the official listing of KARL "screens". (The
reflect a priority on test writing, 1 being highest and 5 being lowest.)

Usage
=====

#. Download from ``selenium-server-standalone-2.15.0.jar`` from
   ``http://code.google.com/p/selenium/downloads/list``

#. Run ``java -jar ./selenium-server-standalone-2.15.0.jar``

#. In a virtualenv,  easy_install ``selenium`` and ``nose``

#. ``/path/to/virtualenv/bin/nosetests ./test_karl.py``

blog
====

- (1) show_blog

- (4) show_mailin_trace

- (4) redirect_to_add_form

- (1) show_blogentry

commenting
==========

- (3) redirect_comments

- (4) show_comment


calendar
========

- (1) show_view

- (4) redirect_to_add_form

- (1) show_week

- (1) show_month

- (1) show_day

- (1) show_list

- (2) calendar_setup

- (2) calendar_setup_categories

- (2) calendar_setup_layers

- (1) show_calendarevent

- (3) show_calendarevent_ics

files
=====

- (1) communityroot.show_folder

- (1) communityfolder.show_folder

- (4) redirect_to_add_form

- (1) show_file

- (2) preview_file

- (2) download_file_preview

- (1) download_file

- (2) thumbnail

- (1) jquery_grid_folder

- (3) NetworkNewsView

- (3) NetworkEventsView

- (3) ajax_file_reorganize_delete

- (3) ajax_file_reorganize_moveto

- (2) ajax_file_upload

- (2) new_ajax_file_upload

- (2) new_ajax_file_query

references
==========

- (2) reference_outline

- (2) reference_viewall

forum
=====

- (2) show_forums

- (2) show_forum

- (2) show_forum_topic

resource
========

- (3) delete_resource

- (3) delete_folder

page
====

- (1) show_page

- (1) show_folder

wiki
====

- (2) redirect_to_front_page

- (3) redirect_to_add_form

- (1) show_wikipage

- (3) preview_wikipage

- (2) show_wikitoc

- (4) unlock_wiki

newsitem
========

- (3) show_newsitem

- (4) newsitem_photo_filestore

atom
====

- (3) blog_atom

- (3) calendar_atom

- (3) wiki_atom

- (3) community_files_atom

intranets
=========

- (4) show_intranets

admin
=============

- (5) show_zodbinfo

- (1) ok.ok

- (4) stats

- (5) edit_acl

- (5) acl_tree

- (4) admin_view

- (4) delete_content

- (4) move_content

- (4) site_announcement

- (4) EmailUsersView

- (4) syslog_view

- (4) logs_view

- (4) statistics_view

- (4) statistics_csv_view

- (4) UploadUsersView

- (1) error_monitor_view

- (3) error_monitor_subsystem_view

- (3) error_monitor_status_view

- (4) postoffice_quarantine_view

- (4) postoffice_quarantine_status_view

- (4) rename_or_merge_user_view

- (4) postoffice_quarantined_message

imagedrawer
===========

- (3) drawer_dialog_view

- (3) drawer_data_view

- (3) drawer_upload_view

contentfeeds
============

- (2) show_feeds_view

- (4) profile_feed_view

- (4) community_feed_view

- (1) newest_feed_items

- (5) older_feed_items

site
====

- (3) versioning_static

- (1) site_view

- (1) login

- (1) logout

- (4) resetpassword.reset_sent

search
======

- (2) searchresults

- (3) calendar_searchresults

- (3) jquery_liveseach

tags
====

- (3) showtag

- (3) community_showtag

- (3) profile_showtag

- (3) tag_cloud

- (3) community_tag_cloud

- (3) tag_listing

- (3) community_tag_listing

- (3) profile_tag_listing

- (3) tag_users (profile, site)

- (3) community_tag_users

- (4) manage_tags

- (3) jquery_tag_search

- (3) jquery_tag_add

- (3) jquery_tag_del


communities
===========

- (1) show_communities

- (1) show_active_communities

- (2) show_all_communities

- (3) jquery_set_preferred

- (3) jquery_clear_preferred

- (3) jquery_list_preferred

- (3) jquery_edit_preferred

- (3) jquery_list_my_communities

community
=========

- (1) redirect_community

- (1) show_community

- (3) community_recent_items_ajax

- (3) community_members_ajax

- (4) related_communities_ajax

- (4) community_atom

- (5) delete_community

- (3) searchresults

- (3) calendar_searchresults

- (3) join_community

people
======

- (3) edit_profile_filestore_photo

- (3) add_user_filestore_photo

- (2) recent_content

- (3) manage_communities

- (1) show_profile

- (1) profile_thumbnail

- (4) deactivate_profile

- (4) reactivate_profile

- (3) delete_resource

members
=======

- (3) show_profiles

- (3) show_members

- (3) jquery_member_search

- (4) accept_invitation_photo


other
=====

- (4) tinymce_spellcheck_view

- (1) redirect_up

- (1) redirect_favicon

- (4) redirect_rss_view

- (1) raise_error

- (1) forbidden

- (3) retail_view

- (3) kaltura_create_session

versions
========

- (3) show_history

- (3) revert

- (3) show_trash

- (3) undelete

peopledirectory
===============

- (1) view

- (3) download_peopledirectory

- (3) upload_peopledirectory

- (5) admin_contents, moveup, movedown
  - directory, categories, category, categoryitem, peoplesection, ...
  - peoplesectioncolumn, peoplereportgroup, peoplereport, ...
  - peoplereportfilter
  - peoplereportmailinglist

- (5) edit_categories

- (2) section_view

- (2) section_column_view

- (2) redirector_view

- (5) redirector_admin_view

- (3) report_view

- (3) jquery_grid_view

- (3) picture_view

- (4) csv_view

- (3) print_view

- (5) opensearch_view

karl.external_link_ticket
=========================

- wrap_external_link

- authenticate_ticket

osi
===

- show_forums

- peopledirectory_view

- peopledirectory.report_view

- peopledirectory.picture_view

- edit_profile

- forumsfolder.all_forums

- people.layouts_redirect

- people.searches_redirect_view

Other
=====

- ux2.switch_ui
