/* jshint node: true, expr: true */

var urls = [
  '/admin.html',

  // Profile stuff
  '/profiles/admin', '/profiles/admin/edit_profile.html',
  '/profiles/admin/admin_edit_profile.html',
  '/profiles/admin/manage_communities.html',
  '/profiles/admin/manage_tags.html', '/profiles/admin/advanced.html',
  '/contentfeeds.html',

  // Search
  '/searchresults.html?body=min',

  // Tag stuff
  '/tagcloud.html', '/taglisting.html',

  // People
  '/people/all/all/', '/people/all/all/picture_view.html',
  '/people/all/all/print.html', '/people/all/all/csv',

  // Communities/Community
  '/communities', '/communities/active_communities.html',
  '/communities/active_communities.html',
  '/communities/add_community.html',
  '/communities/active_communities.html?body=default',
  '/communities/default/view.html',
  '/communities/default/searchresults.html?body=front',
  '/communities/default/members', '/communities/default/tagcloud.html',
  '/communities/default/taglisting.html', '/communities/default/edit.html',
  '/communities/default/delete.html', '/communities/default/advanced.html',

  // Blog
  '/communities/default/blog', '/communities/default/blog/add_blogentry.html',

  // Wiki
  '/communities/default/wiki/front_page/', '/communities/default/wiki/wikitoc.html',
  '/communities/default/wiki/trash', '/communities/default/wiki/front_page/edit.html',
  '/communities/default/wiki/front_page/history.html',
  '/communities/default/wiki/front_page/advanced.html',

  // Calendar
  '/communities/default/calendar/month.html', '/communities/default/calendar/setup.html',
  '/communities/default/calendar/add_calendarevent.html',
  '/communities/default/calendar/list.html?year=2014&month=11&day=5&term=month',
  '/communities/default/calendar/list.html?year=2014&month=11&day=5&term=day',
  '/communities/default/calendar/list.html?year=2014&month=11&day=5&term=week',
  '/communities/default/calendar/list.html?year=2014&month=11&day=5&term=month',
  '/communities/default/calendar/notes.html',

  // Files
  '/communities/default/files', '/communities/default/files/trash',
  '/communities/default/files/add_folder.html',
  '/communities/default/files/add_file.html',
  '/communities/default/files/advanced.html',

  // Offices
  '/offices/nyc/', '/offices', '/offices/intranets',
  '/offices/files/edit_acl.html',
  '/offices/intranets/add_intranet.html', '/offices/baltimore//edit_intranet.html',
  '/offices/files', '/offices/files/network-news/', '/offices/files/network-news/add_newsitem.html',
  '/offices/files/network-events/', '/offices/files/network-events/?past_events=True',
  '/offices/files/network-events/add_calendarevent.html'
];

describe('site walkthrough', function () {

  beforeEach(loginAsAdmin);

  describe('principal urls load without server error', function () {
    urls.forEach(function (url) {
      it(url, function() {
        browser.get(resolve(url));
        expectPageOk();
      });
    });
  });

  it('nonexistent page goes to error page', function () {
    browser.get(resolve('/anything.html'));
    expectPageError();
  });


});
