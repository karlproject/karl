/* jshint expr: true */

describe('karl-buttonset plugin', function () {

  beforeEach(function () {
    $('body').html(__html__['frontend-test/unit/karl-js-fixture.html']);
  });
  afterEach(function () {
    $('body').empty();
  });

  // This test has been migrated from QUnit, and uses the old QUnit assertions.
  // If you write new tests, use Chai instead! http://chaijs.com/api/bdd/

  // init

  test('init adds dropdown indicator', function() {
    equals(0, $(".karldropdown .karldropdown-indicator").length);

    $('.karldropdown').karldropdown({});

    equals(1, $(".karldropdown .karldropdown-indicator").length);
  });

  test('init hides menu', function() {
    equals("block", $(".karldropdown-menu").css("display"));

    $('.karldropdown').karldropdown({});
    equals("none", $(".karldropdown-menu").css("display"));
  });


  // show

  test('show() changes menu position', function() {
    $('.karldropdown').karldropdown({});
    equals("static", $(".karldropdown-menu").css("position"));

    $('.karldropdown').karldropdown('show');
    equals("absolute", $(".karldropdown-menu").css("position"));
  });

  function expectTransparent(rule) {
    expect(rule == 'transparent' || rule == 'rgba(0, 0, 0, 0)').is.ok;
  }

  test('show() resets items', function() {
    $('.karldropdown').karldropdown({});

    expectTransparent($(".karldropdown-menu li").css("background-color"));

    $('.karldropdown').karldropdown('show');
    equals("rgb(102, 102, 102)", $(".karldropdown-menu li").css("background-color"));
  });

  test('show() shows dropdown menu', function() {
    $('.karldropdown').karldropdown({});
    equals("none", $(".karldropdown-menu").css("display"));

    $('.karldropdown').karldropdown('show');
    equals("block", $(".karldropdown-menu").css("display"));
  });

  function expectFuzzyEqual(value, number, limit) {
    value = parseInt(value, 10); // this will get rid of 'px'
    expect(value).is.most(number + limit);
    expect(value).is.least(number - limit);
  }

  test('show() adjusts max width', function() {
    $('.karldropdown').karldropdown({});
    equals("0px", $(".karldropdown-menu li").css("width"));

    $('.karldropdown').karldropdown('show');
    // fuzzy check
    expectFuzzyEqual($(".karldropdown-menu li").css("width"), 42, 10);

  });


  // hide

  test('hide() hides dropdown menu', function(done) {
    $('.karldropdown').karldropdown({});
    $('.karldropdown').karldropdown('show');
    setTimeout(function() {
      equals("block", $(".karldropdown-menu").css("display"));
      $('.karldropdown').karldropdown('hide');
      setTimeout(function() {
      expect($(".karldropdown-menu").css("display")).equals('none');
      done();
      }, 100);
    }, 100);
  });


  // resetAllItems

  test('resetItem() resets css values', function() {
    $('.karldropdown').karldropdown({});

    var item = $(".karldropdown-menu li:first");

    expectTransparent(item.css("background-color"));

    $('.karldropdown').karldropdown('show');
    $('.karldropdown').karldropdown('resetItem', item[0]);
    equals("rgb(102, 102, 102)", item.css("background-color"));
  });

  // hoverItem
  test('hoverItem() animates background', function(done) {
    $('.karldropdown').karldropdown({});
    $('.karldropdown').karldropdown('show');
    setTimeout(function() {
      var item = $(".karldropdown-menu li:first");
      equals("rgb(102, 102, 102)", item.css("background-color"));
      $('.karldropdown').karldropdown('hoverItem', item);
      setTimeout(function() {
        equals("rgb(206, 206, 206)", item.css("background-color"));
        done();
      }, 150);
    }, 150);
  });

  test('hoverItem() animates padding', function(done) {
    $('.karldropdown').karldropdown({});
    $('.karldropdown').karldropdown('show');
    setTimeout(function() {
      var item = $(".karldropdown-menu li:first");
      var paddingLeft = item.css("padding-left");
      // Fuzzy check
      expectFuzzyEqual(paddingLeft, 15, 10);
      $('.karldropdown').karldropdown('hoverItem', item);
      setTimeout(function() {
        // changed from previous value
        ok(paddingLeft != item.css("padding-left"));
        done();
      }, 200);
    }, 200);
  });

  // leaveItem

  test('leaveItem() resets background', function(done) {
    $('.karldropdown').karldropdown({});
    setTimeout(function() {
      var item = $(".karldropdown-menu li:first");
      $('.karldropdown').karldropdown('leaveItem', item);
      setTimeout(function() {
        equals('rgb(102, 102, 102)', item.css("background-color"));
        done();
      }, 70);
    }, 70);
  });

  test('leaveItem() resets padding', function(done) {
    $('.karldropdown').karldropdown({});
    var item = $(".karldropdown-menu li:first");
    setTimeout(function() {
      $('.karldropdown').karldropdown('leaveItem', item);
      setTimeout(function() {
        equals('0px', item.css("padding-left"));
        done();
      }, 70);
    }, 70);
  });


});
