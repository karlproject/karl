
/* jshint expr: true */

describe('karl-contentfeeds-polling plugin', function () {

  beforeEach(function () {
    $('head').html(__html__['karl/views/static/karl-plugins/karl-contentfeeds/karl-contentfeeds-fixture-templates.html']);
    $('body').html(__html__['karl/views/static/karl-plugins/karl-contentfeeds/karl-contentfeeds-fixture.html']);
  });

  afterEach(function () {
    $('head').empty();
    $('body').empty();
  });

  // This test has been migrated from QUnit, and uses the old QUnit assertions.
  // If you write new tests, use Chai instead! http://chaijs.com/api/bdd/

  test("Create and destroy", function() {

    $('#feed-polling').karlcontentfeeds_polling({
    });

    $('#feed-polling').karlcontentfeeds_polling('destroy');

  });


  test("Select options work", function() {

    $('#feed-polling2').karlcontentfeeds_polling({
      selectInfoButton: '.MARK1',
      selectDetailsInfo: '.MARK2',
      selectError: '.MARK3',
      selectErrorDetails: '.MARK4',
      selectCloseButton: '.MARK5',
      selectIndicator: '.MARK6'
    });

    $('#feed-polling2').karlcontentfeeds_polling('destroy');

  });

  test("Feed options closable by clicking close", function() {

    $('#feed-polling2').karlcontentfeeds_polling({
      selectInfoButton: '.MARK1',
      selectDetailsInfo: '.MARK2',
      selectError: '.MARK3',
      selectErrorDetails: '.MARK4',
      selectCloseButton: '.MARK5',
      selectIndicator: '.MARK6'
    });

    var info_active = function() {
      return $('#feed-polling2').data('karlcontentfeeds_polling').info_active;
    };

    ok(! info_active(), 'initially hidden');

    // click on info button
    $('#feed-polling2 .MARK1').simulate('click');
    // opened
    ok(info_active(), 'opened up');

    // click on close button
    $('#feed-polling2 .MARK2 .MARK5').simulate('click');
    // closed
    ok(! info_active(), 'closed');

    $('#feed-polling2').karlcontentfeeds_polling('destroy');

  });

  test("Feed options closable by clicking outside", function() {

    $('#feed-polling2').karlcontentfeeds_polling({
      selectInfoButton: '.MARK1',
      selectDetailsInfo: '.MARK2',
      selectError: '.MARK3',
      selectErrorDetails: '.MARK4',
      selectCloseButton: '.MARK5',
      selectIndicator: '.MARK6'
    });


    var info_active = function() {
      return $('#feed-polling2').data('karlcontentfeeds_polling').info_active;
    };

    ok(! info_active(), 'initially hidden');

    // click on info button
    $('#feed-polling2 .MARK1').simulate('click');
    // opened
    ok(info_active(), 'opened up');

    // click outside
    $('#main').simulate('click');
    // closed
    ok(! info_active(), 'closed');

    $('#feed-polling2').karlcontentfeeds_polling('destroy');

  });

  test("Feed options does not close by clicking inside", function() {

    $('#feed-polling2').karlcontentfeeds_polling({
      selectInfoButton: '.MARK1',
      selectDetailsInfo: '.MARK2',
      selectError: '.MARK3',
      selectErrorDetails: '.MARK4',
      selectCloseButton: '.MARK5',
      selectIndicator: '.MARK6'
    });


    var info_active = function() {
      return $('#feed-polling2').data('karlcontentfeeds_polling').info_active;
    };

    ok(! info_active(), 'initially hidden');

    // click on info button
    $('#feed-polling2 .MARK1').simulate('click');
    // opened
    ok(info_active(), 'opened up');

    // click outside
    $('#feed-polling2 .MARK2').simulate('click');
    ok(info_active(), 'not closed');

    ok($('#feed-polling2 .MARK2 p').length > 0, 'reality check');
    $('#feed-polling2 .MARK2 p').simulate('click');
    ok(info_active(), 'not closed');

    $('#feed-polling2').karlcontentfeeds_polling('destroy');

  });

});
