
/* jshint expr: true */

describe('karl-contentfeeds-info plugin', function () {

  beforeEach(function () {
    $('head').append(__html__['karl/views/static/karl-plugins/karl-contentfeeds/karl-contentfeeds-templates-fixture.html']);
    $('body').html(__html__['karl/views/static/karl-plugins/karl-contentfeeds/karl-contentfeeds-fixture.html']);
  });

  afterEach(function () {
    $('head').empty();
    $('body').empty();
  });

  // This test has been migrated from QUnit, and uses the old QUnit assertions.
  // If you write new tests, use Chai instead! http://chaijs.com/api/bdd/

  test("Create and destroy", function() {

    $('#feedinfo').karlcontentfeeds_info({
    });

    $('#feedinfo').karlcontentfeeds_info('destroy');

  });

  test("Update", function() {

    $('#feedinfo').karlcontentfeeds_info({
    });

    $('#feedinfo').karlcontentfeeds_info('update', {
      last_update: 'Thu Aug 05 2010 17:29:36 GMT+0200 (CET)',
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      feed_url: '/json_newest_feed_items.json?newer_than=0:54&filter=None'
    });

    equals($('#feedinfo .last-update').text(), 'Thu Aug 05 2010 17:29:36 GMT+0200 (CET)');
    equals($('#feedinfo .last-gen').text(), '0');
    equals($('#feedinfo .last-index').text(), '54');
    equals($('#feedinfo .feed-url').text(), '/json_newest_feed_items.json?newer_than=0:54&filter=None');
    equals($('#feedinfo .feed-url').attr('href'), '/json_newest_feed_items.json?newer_than=0:54&filter=None');

    $('#feedinfo').karlcontentfeeds_info('destroy');

  });

  test("Select options work", function() {

    $('#feedinfo2').karlcontentfeeds_info({
      selectLastUpdate: '.mark1',
      selectLastGen: '.mark2',
      selectLastIndex: '.mark3',
      selectFeedUrl: '.mark4'
    });

    $('#feedinfo2').karlcontentfeeds_info('update', {
      last_update: 'Thu Aug 05 2010 17:29:36 GMT+0200 (CET)',
      last_gen: 0,
      last_index: 54,
      earliest_gen: 0,
      earliest_index: 35,
      feed_url: '/json_newest_feed_items.json?newer_than=0:54&filter=None'
    });

    equals($('#feedinfo2 .mark1').text(), 'Thu Aug 05 2010 17:29:36 GMT+0200 (CET)');
    equals($('#feedinfo2 .mark2').text(), '0');
    equals($('#feedinfo2 .mark3').text(), '54');
    equals($('#feedinfo2 .mark4').text(), '/json_newest_feed_items.json?newer_than=0:54&filter=None');
    equals($('#feedinfo2 .mark4').attr('href'), '/json_newest_feed_items.json?newer_than=0:54&filter=None');

    $('#feedinfo2').karlcontentfeeds_info('destroy');

  });

});
