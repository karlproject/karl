/* jshint expr: true */

describe.only('karl-contentfeeds plugin', function () {

  var _time, _now_saved, _save_timeago, server;

  // This test has been migrated from QUnit, and uses the old QUnit assertions.
  // If you write new tests, use Chai instead! http://chaijs.com/api/bdd/

  function set_time(d) {
    _time = d;
  }

  function result_ok(items, comment) {
    var result = [];
    $('#feedlist').children().each(function() {
      var txt = $(this).find('.firstline')
        .text().split(/ +/).join(' ');
      // remove leading/trailing space in favor of IE
      txt =txt.replace(/^ /, '');
      txt =txt.replace(/ $/, '');
      result.push(txt);
    });
    deepequals(result, items, comment);
  }

  //
  // Actual mock response can be produced here.
  //
  function handle_ajax(request, ajax_heartbeat) {
    if (request.urlParts.file == 'feed.json') {
      request.setResponseHeader("Content-Type", "application/json; charset=UTF-8");
      if (ajax_heartbeat === 0) {
        // Full record set captured from real example
        request.receive(200, '[0, 54, 0, 35, [' +
          '{"flavor": "added_edited_other", "context_url": "/offices", "description": "This is a test under selenium for add forum", "title": "selenium_test1", "url": "/offices/forums/selenium_test", "tags": [], "userid": "jpglenn09", "comment_count": 0, "author": "System User", "content_type": "Forum", "short_description": "This is a test under selenium for add forum", "context_name": "OSI", "operation": "edited", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:26:01Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/offices", "description": "This is a test under selenium for add forum", "title": "selenium_test", "url": "/offices/forums/selenium_test", "tags": [], "userid": "jpglenn09", "comment_count": 0, "author": "System User", "content_type": "Forum", "short_description": "This is a test under selenium for add forum", "context_name": "OSI", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:25:41Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "selenium", "url": "/communities/selenium_test/wiki/selenium", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Wiki Page", "short_description": "", "context_name": "selenium_test", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:25:09Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "This is the front page. This page is edited by selenium", "title": "Second Page", "url": "/communities/selenium_test/wiki/front_page", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Wiki Page", "short_description": "This is the front page. This page is edited by selenium", "context_name": "selenium_test", "operation": "edited", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:24:53Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "test folder", "url": "/communities/selenium_test/files/test-folder", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Folder", "short_description": "", "context_name": "selenium_test", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:24:01Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "calendar_event_234", "url": "/communities/selenium_test/calendar/calendar_test_event_123", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Event", "short_description": "", "context_name": "selenium_test", "operation": "edited", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:23:10Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "calendar_test_event_123", "url": "/communities/selenium_test/calendar/calendar_test_event_123", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Event", "short_description": "", "context_name": "selenium_test", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:22:39Z"}, '+
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "selenium_test_blog", "url": "/communities/selenium_test/blog/selenium_test_blog", "tags": [], "userid": "jpglenn09", "comment_count": 1, "author": "System User", "content_type": "Blog Entry", "short_description": "", "context_name": "selenium_test", "operation": "edited", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:21:53Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "Re: selenium_test_blog", "url": "/communities/selenium_test/blog/selenium_test_blog/comments/001", "tags": [], "userid": "jpglenn09", "comment_count": 0, "author": "System User", "content_type": "Comment", "short_description": "", "context_name": "selenium_test", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:21:28Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/communities/selenium_test", "description": "", "title": "selenium_test_blog", "url": "/communities/selenium_test/blog/selenium_test_blog", "tags": [], "userid": "jpglenn09", "comment_count": 0, "author": "System User", "content_type": "Blog Entry", "short_description": "", "context_name": "selenium_test", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:21:22Z"}, ' +
          '{"flavor": "joined_left", "context_url": "/communities/selenium_test", "description": "This is a test of Karl Under Selenium.", "title": "selenium_test", "url": "/communities/selenium_test", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Community", "short_description": "This is a test of Karl Under Selenium.", "context_name": "selenium_test", "operation": "joined", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:20:49Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/communities/selenium_test", "description": "This is a test of Karl Under Selenium.", "title": "selenium_test", "url": "/communities/selenium_test", "tags": [], "userid": "jpglenn09", "comment_count": false, "author": "System User", "content_type": "Community", "short_description": "This is a test of Karl Under Selenium.", "context_name": "selenium_test", "operation": "added", "thumbnail": "/profiles/jpglenn09/profile_thumbnail", "profile_url": "/profiles/jpglenn09", "timeago": "2010-07-28T19:20:48Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/offices", "description": "Privacy Policy Open Society Institute (\\" OSI ,\\" \\" we ,\\" \\" us \\") cares about privacy issues and wants you to be familiar with how we collect, use and disclose your Personally Identifiable Information (as defined below). This Privacy Policy (the \\" Policy \\") describes our practices in connection...", "title": "privacy_statement", "url": "/offices/files/privacy_statement", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Page", "short_description": "Privacy Policy Open Society Institute (\\" OSI ,\\" \\" we ,\\" \\" us \\") cares about priv...", "context_name": "OSI", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_other", "context_url": "/offices", "description": "Terms of Service LAST UPDATED: June 1, 2007 This Terms of Service Agreement (the \\"Agreement\\") is between you (\\"you\\") and Open Society Institute (\\"OSI,\\" \\"we,\\" \\"us\\") concerning your use of the KARL network (together with all Services (as defined below), the \\"Site\\"). This Terms of Service Agreement (the \\" Agreement...", "title": "terms_and_conditions", "url": "/offices/files/terms_and_conditions", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Page", "short_description": "Terms of Service LAST UPDATED: June 1, 2007 This Terms of Service Agreement (the...", "context_name": "OSI", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/offices/washington", "description": "", "title": "washington", "url": "/offices/washington", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Community", "short_description": "", "context_name": "washington", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/offices/paris", "description": "", "title": "paris", "url": "/offices/paris", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Community", "short_description": "", "context_name": "paris", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/offices/national-foundation", "description": "", "title": "national-foundation", "url": "/offices/national-foundation", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Community", "short_description": "", "context_name": "national-foundation", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/offices/london", "description": "", "title": "london", "url": "/offices/london", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Community", "short_description": "", "context_name": "london", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/offices/brussels", "description": "", "title": "brussels", "url": "/offices/brussels", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Community", "short_description": "", "context_name": "brussels", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}, ' +
          '{"flavor": "added_edited_community", "context_url": "/offices/budapest", "description": "", "title": "budapest", "url": "/offices/budapest", "tags": [], "userid": "admin", "comment_count": false, "author": "Ad Min", "content_type": "Community", "short_description": "", "context_name": "budapest", "operation": "added", "thumbnail": "/profiles/admin/profile_thumbnail", "profile_url": "/profiles/admin", "timeago": "2010-07-28T18:34:21Z"}]]'
        );
      } else if (ajax_heartbeat == 1) {
        // Example 1
        request.receive(200, JSON.stringify([0, 54, 0, 35, [{
            flavor: "added_edited_other",
            context_url: "/offices",
            description: "This is a test under selenium for add forum",
            title: "selenium_test1",
            url: "/offices/forums/selenium_test",
            tags: [],
            userid: "jpglenn09",
            comment_count: 0,
            author: "System User",
            content_type: "Forum",
            short_description: "This is a test under selenium for add forum",
            context_name: "OSI",
            operation: "edited",
            thumbnail: "/profiles/jpglenn09/profile_thumbnail",
            profile_url: "/profiles/jpglenn09",
            timeago: "2010-07-28T19:26:01Z"
          }, {
            flavor: "joined_left",
            context_url: "/communities/selenium_test",
            description: "This is a test of Karl Under Selenium.",
            title: "selenium_test",
            url: "/communities/selenium_test",
            tags: [],
            userid: "jpglenn09",
            comment_count: false,
            author: "System User",
            content_type: "Community",
            short_description: "This is a test of Karl Under Selenium.",
            context_name: "selenium_test",
            operation: "joined",
            thumbnail: "/profiles/jpglenn09/profile_thumbnail",
            profile_url: "/profiles/jpglenn09",
            timeago: "2010-07-28T19:20:49Z"
          }, {
            flavor: "added_edited_community",
            context_url: "/communities/selenium_test",
            description: "This is a test of Karl Under Selenium.",
            title: "selenium_test",
            url: "/communities/selenium_test",
            tags: [],
            userid: "jpglenn09",
            comment_count: false,
            author: "System User",
            content_type: "Community",
            short_description: "This is a test of Karl Under Selenium.",
            context_name: "selenium_test",
            operation: "added",
            thumbnail: "/profiles/jpglenn09/profile_thumbnail",
            profile_url: "/profiles/jpglenn09",
            timeago: "2010-07-28T19:20:48Z"
          }, {
            flavor: "added_edited_other",
            context_url: "/offices",
            description: "Privacy Policy Open Society Institute (\" OSI ,\" \" we ,\" \" us \") cares about privacy issues and wants you to be familiar with how we collect, use and disclose your Personally Identifiable Information (as defined below). This Privacy Policy (the \" Policy \") describes our practices in connection...",
            title: "privacy_statement",
            url: "/offices/files/privacy_statement",
            tags: [],
            userid: "admin",
            comment_count: false,
            author: "Ad Min",
            content_type: "Page",
            short_description: "Privacy Policy Open Society Institute (\" OSI ,\" \" we ,\" \" us \") cares about priv...",
            context_name: "OSI",
            operation: "added",
            thumbnail: "/profiles/admin/profile_thumbnail",
            profile_url: "/profiles/admin",
            timeago: "2010-07-28T18:34:21Z"
        }]]));
      } else if (ajax_heartbeat == 2) {
        // empty record set, means no recent changes
        request.receive(200, JSON.stringify([0, 54, 0, 35, []]));
      } else if (ajax_heartbeat == 3) {
        // Example 2
        request.receive(200, JSON.stringify([0, 54, 0, 35, [{
            flavor: "added_edited_other",
            context_url: "/offices",
            description: "Test example 2 row 1",
            title: "selenium_test1",
            url: "/offices/forums/selenium_test",
            tags: [],
            userid: "jpglenn09",
            comment_count: 0,
            author: "System User",
            content_type: "Forum",
            short_description: "Test example 2 row 1",
            context_name: "TEST2",
            operation: "edited",
            thumbnail: "/profiles/jpglenn09/profile_thumbnail",
            profile_url: "/profiles/jpglenn09",
            timeago: "2010-07-28T19:26:01Z"
          }, {
            flavor: "added_edited_other",
            context_url: "/offices",
            description: "Test example 2 row 2",
            title: "privacy_statement",
            url: "/offices/files/privacy_statement",
            tags: [],
            userid: "admin",
            comment_count: false,
            author: "Ad Min",
            content_type: "Page",
            short_description: "Test example 2 row 2",
            context_name: "TEST2",
            operation: "added",
            thumbnail: "/profiles/admin/profile_thumbnail",
            profile_url: "/profiles/admin",
            timeago: "2010-07-28T18:34:21Z"
        }]]));
      } else if (ajax_heartbeat == 4) {
        // simulate an error
        request.receive(500, 'Error');
      }
    } else {
      request.receive(404, 'Not Found in Mock Server');
    }
  }

  beforeEach(function () {
    $('head').append(__html__['karl/views/static/karl-plugins/karl-contentfeeds/karl-contentfeeds-templates-fixture.html']);
    $('body').html(__html__['karl/views/static/karl-plugins/karl-contentfeeds/karl-contentfeeds-fixture.html']);

    // Mock the time
    _time = 'Thu Aug 05 2010 17:29:36 GMT+0200 (CET)';
    _now_saved = $.karl.karlcontentfeeds.prototype._now;
    $.karl.karlcontentfeeds.prototype._now = function() {
      return self._time;
    };

    // Mock the timeago iterator
    _save_timeago = $.fn.timeago;
    $.fn.timeago = function() {
      $(this).text($(this).attr('title'));
    };

    // Create a mock server for testing ajax.
    server = new MoreMockHttpServer(handle_ajax);

    // Start the server
    server.start();

    $('#feedlist').empty();

  });

  afterEach(function () {
    $('head').empty();
    $('body').empty();

    // Stop the server
    server.stop();

    // Restore the timeago iterator
    $.fn.timeago = _save_timeago;

    // restore the time
    $.karl.karlcontentfeeds.prototype._now = _now_saved;

  });
/*
  test("Create and destroy", function() {

    $('#feedlist').karlcontentfeeds({
    });

    $('#feedlist').karlcontentfeeds('destroy');

  });
*/
  test("Can receive full record set", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    $('#feedlist').karlcontentfeeds('get_items');

    equals($('#feedlist').children().length, 20);

    $('#feedlist').karlcontentfeeds('destroy');
  });
/*
  test("Can receive example record set", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');

    equals($('#feedlist').children().length, 4);

    $('#feedlist').karlcontentfeeds('destroy');

  });

  test("Can receive empty record set", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(2);
    $('#feedlist').karlcontentfeeds('get_items');

    equals($('#feedlist').children().length, 0);

    $('#feedlist').karlcontentfeeds('destroy');

  });

  test("Incremental queries", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 8);

    server.set_server_state(2);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 8);

    server.set_server_state(2);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 8);

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 12);

    $('#feedlist').karlcontentfeeds('destroy');
  });

  test("Order of insertion", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);

    result_ok([
      'System User edited a Forum selenium_test1 in OSI.',
      'System User joined Community selenium_test.',
      'System User added Community selenium_test.',
      'Ad Min added a Page privacy_statement in OSI.'
    ]);

    server.set_server_state(3);

    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 6);

    result_ok([
      'System User edited a Forum selenium_test1 in TEST2.',
      'Ad Min added a Page privacy_statement in TEST2.',
      //
      'System User edited a Forum selenium_test1 in OSI.',
      'System User joined Community selenium_test.',
      'System User added Community selenium_test.',
      'Ad Min added a Page privacy_statement in OSI.'
    ]);

    $('#feedlist').karlcontentfeeds('destroy');
  });

  test("summary_info getter", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    deepequals($('#feedlist').karlcontentfeeds('summary_info'), {
      feed_url: "/feed.json"
    });

    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);

    deepequals($('#feedlist').karlcontentfeeds('summary_info'), {
       last_gen: 0,
       last_index: 54,
       earliest_gen: 0,
       earliest_index: 35,
       last_update: _time,
       feed_url: "/feed.json?newer_than=0%3A54"
    });

    $('#feedlist').karlcontentfeeds('destroy');

  });

  test("changed event", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    var events_caught = [];
    $('#feedlist').bind('changed.karlcontentfeeds', function(evt, summary_info) {
      events_caught.push(summary_info);
    });

    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('get_items');
    equals(events_caught.length, 1);
    deepequals(events_caught[0], {
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      last_update: "Thu Aug 05 2010 17:29:36 GMT+0200 (CET)",
      feed_url: "/feed.json?newer_than=0%3A54"
    });


    $('#feedlist').karlcontentfeeds('get_items');
    equals(events_caught.length, 2);
    deepequals(events_caught[1], {
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      last_update: "Thu Aug 05 2010 17:29:36 GMT+0200 (CET)",
      feed_url: "/feed.json?newer_than=0%3A54"
    });

    $('#feedlist').karlcontentfeeds('get_items');
    equals(events_caught.length, 3);
    deepequals(events_caught[2], {
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      last_update: "Thu Aug 05 2010 17:29:36 GMT+0200 (CET)",
      feed_url: "/feed.json?newer_than=0%3A54"
    });


    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("ajaxstatechanged event", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    var events_caught = [];
    $('#feedlist').bind('ajaxstatechanged.karlcontentfeeds', function(evt, state, errormsg) {
      events_caught.push([state, errormsg]);
    });

    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('get_items');
    equals(events_caught.length, 2);
    deepequals(events_caught[0], ['polling', undefined]);
    deepequals(events_caught[1], ['on', undefined]);


    $('#feedlist').karlcontentfeeds('get_items');
    equals(events_caught.length, 4);
    deepequals(events_caught[2], ['polling', undefined]);
    deepequals(events_caught[3], ['on', undefined]);

    // error simulation
    server.set_server_state(4);

    $('#feedlist').karlcontentfeeds('get_items');
    equals(events_caught.length, 6);
    deepequals(events_caught[4], ['polling', undefined]);
    deepequals(events_caught[5], ['error', "error: error"]);

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("get_items ignores states", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('setAjaxState', 'off');
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);

    $('#feedlist').karlcontentfeeds('setAjaxState', 'polling');
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);

    $('#feedlist').karlcontentfeeds('setAjaxState', 'error');
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("state manually switched 'off' while polling", function() {
    // for example, someone pushes the polling state button
    // during a slow request is polling

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    var events_caught = [];
    $('#feedlist').bind('ajaxstatechanged.karlcontentfeeds', function(evt, state, errormsg) {
      events_caught.push([state, errormsg]);
    });

    server.set_server_state(1);

    // time the next response.
    server.set_timed_responses(true);

    $('#feedlist').karlcontentfeeds('get_items');

    // nothing happened yet, since the response is in limbo.
    equals(server.length, 1);
    equals(events_caught.length, 1);
    deepequals(events_caught[0], ['polling', undefined]);

    // Someone switches the state 'off', before the response arrives.
    $('#feedlist').karlcontentfeeds('setAjaxState', 'off');

    // Response arrives now.
    server.execute(0);

    equals(events_caught.length, 1, 'there is no "on" state change event');

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("manual polling is possible while in 'off' state", function() {
    // for example, someone changes the filter while in "off" state

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    var events_caught = [];
    $('#feedlist').bind('ajaxstatechanged.karlcontentfeeds', function(evt, state, errormsg) {
      events_caught.push([state, errormsg]);
    });

    // set the state to 'off'
    $('#feedlist').karlcontentfeeds('setAjaxState', 'off');
    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('get_items', {force: true});
    equals(events_caught.length, 2, 'manual polling should happen despite the "off" state, when forced');
    deepequals(events_caught[0], ['polling', undefined]);
    deepequals(events_caught[1], ['off', undefined]);

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("get_items ignores states 'error', 'polling' even when forced", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('setAjaxState', 'polling');
    $('#feedlist').karlcontentfeeds('get_items', {force: true});
    equals($('#feedlist').children().length, 0);

    $('#feedlist').karlcontentfeeds('setAjaxState', 'error');
    $('#feedlist').karlcontentfeeds('get_items', {force: true});
    equals($('#feedlist').children().length, 0);

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("setFilter works", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);
    result_ok([
      'System User edited a Forum selenium_test1 in OSI.',
      'System User joined Community selenium_test.',
      'System User added Community selenium_test.',
      'Ad Min added a Page privacy_statement in OSI.'
    ]);

    var events_caught = [];
    $('#feedlist').bind('changed.karlcontentfeeds', function(evt, summary_info) {
      events_caught.push(summary_info);
    });

    server.set_server_state(3);

    // Set the filter now.
    $('#feedlist').karlcontentfeeds('setFilter', 'myfilter');

    equals($('#feedlist').karlcontentfeeds('option', 'filter'), 'myfilter', 'correctly set in options');
    equals(events_caught.length, 2, 'threw events');
    deepequals(events_caught[0], {
      feed_url: "/feed.json?filter=myfilter" // notice how newer_than is missing here
    });
    deepequals(events_caught[1], {
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      last_update: "Thu Aug 05 2010 17:29:36 GMT+0200 (CET)",
      feed_url: "/feed.json?newer_than=0%3A54&filter=myfilter"
    });
    equals($('#feedlist').children().length, 2, 'different result set here');
    result_ok([
      'System User edited a Forum selenium_test1 in TEST2.',
      'Ad Min added a Page privacy_statement in TEST2.'
    ], 'the filter change has deleted the previous items.');

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("setFilter works in offline mode", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);
    result_ok([
      'System User edited a Forum selenium_test1 in OSI.',
      'System User joined Community selenium_test.',
      'System User added Community selenium_test.',
      'Ad Min added a Page privacy_statement in OSI.'
    ]);

    var events_caught = [];
    $('#feedlist').bind('changed.karlcontentfeeds', function(evt, summary_info) {
      events_caught.push(summary_info);
    });

    server.set_server_state(3);
    // Set offline mode.
    $('#feedlist').karlcontentfeeds('setAjaxState', 'off');

    // Set the filter now.
    $('#feedlist').karlcontentfeeds('setFilter', 'myfilter');

    equals($('#feedlist').karlcontentfeeds('option', 'filter'), 'myfilter', 'correctly set in options');
    equals(events_caught.length, 2, 'threw events');
    deepequals(events_caught[0], {
      feed_url: "/feed.json?filter=myfilter" // notice how newer_than is missing here
    });
    deepequals(events_caught[1], {
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      last_update: "Thu Aug 05 2010 17:29:36 GMT+0200 (CET)",
      feed_url: "/feed.json?newer_than=0%3A54&filter=myfilter"
    });
    equals($('#feedlist').children().length, 2, 'different result set here');
    result_ok([
      'System User edited a Forum selenium_test1 in TEST2.',
      'Ad Min added a Page privacy_statement in TEST2.'
    ], 'the filter change has deleted the previous items.');

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("start over", function() {
    // for example, someone changes the filter

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);
    result_ok([
      'System User edited a Forum selenium_test1 in OSI.',
      'System User joined Community selenium_test.',
      'System User added Community selenium_test.',
      'Ad Min added a Page privacy_statement in OSI.'
    ]);

    var events_caught = [];
    $('#feedlist').bind('changed.karlcontentfeeds', function(evt, summary_info) {
      events_caught.push(summary_info);
    });

    // Start over.
    $('#feedlist').karlcontentfeeds('start_over');

    equals($('#feedlist').children().length, 0, 'purged previous items');

    equals(events_caught.length, 1, 'threw change event');
    deepequals(events_caught[0], {
      feed_url: "/feed.json"    // note how newer_than is missing here.
    });

    $('#feedlist').karlcontentfeeds('destroy');
  });


  test("active requests get dumped on start_over", function() {

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    var events_caught = [];
    $('#feedlist').bind('ajaxstatechanged.karlcontentfeeds', function(evt, state, errormsg) {
      events_caught.push([state, errormsg]);
    });

    // time responses manually
    server.set_timed_responses(true);

    server.set_server_state(3);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);

    equals(server.length, 1);

    equals(events_caught.length, 1);
    deepequals(events_caught[0], ['polling', undefined]);

    // following requests go out at once
    server.set_timed_responses(false);

    server.set_server_state(1);
    // Start over.
    $('#feedlist').karlcontentfeeds('start_over');

    ///equals(events_caught.length, 2);
    deepequals(events_caught[events_caught.length - 1], ['on', undefined]);

    // there goes another request
    server.set_server_state(1);
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 4);

    //equals(events_caught.length, 4);
    deepequals(events_caught[events_caught.length - 2], ['polling', undefined]);
    deepequals(events_caught[events_caught.length - 1], ['on', undefined]);

    // make the stuck request arrive now
    server.execute(0);

    // the stuck request is discarded.
    equals($('#feedlist').children().length, 4, 'Stuck request was discarded.');
    // and no more events
    //equals(events_caught.length, 4);

    $('#feedlist').karlcontentfeeds('destroy');
  });

  test("start_over...and over...and over", function() {
    // for example, someone starts to press on a filter
    // button repetitively like crazy, fast enough to
    // push before any request can arrive. - The reason
    // to test this is IE seems to have
    // javascript error in connection with jquery,
    // in connection with abort.
    // XXX Unfortunately this does not catch the problem
    // on IE, because the problem lies in IE's internal
    // code, which we cannot test this way.

    $('#feedlist').karlcontentfeeds({
      ajax_url: '/feed.json'
    });

    // time responses manually
    server.set_timed_responses(true);
    server.set_server_state(1);

    $('#feedlist').karlcontentfeeds('start_over');
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);
    equals(server.length, 1);

    $('#feedlist').karlcontentfeeds('start_over');
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);
    equals(server.length, 2);

    $('#feedlist').karlcontentfeeds('start_over');
    $('#feedlist').karlcontentfeeds('get_items');
    equals($('#feedlist').children().length, 0);
    equals(server.length, 3);

    // the first two request are already aborted,
    // irrelevant if they arrive or not
    server.execute(0);
    server.execute(1);
    equals($('#feedlist').children().length, 0);

    // the last response arrives really
    server.execute(2);
    equals($('#feedlist').children().length, 4);

    $('#feedlist').karlcontentfeeds('destroy');
  });
*/
});
