/*
 * dropdown unit tests
 */
(function($) {

module("karl: dropdown");

// init

test('init adds dropdown indictaor', function() {
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

test('show() resets items', function() {
  $('.karldropdown').karldropdown({});
  equals("transparent", $(".karldropdown-menu li").css("background-color"));

  $('.karldropdown').karldropdown('show');
  equals("rgb(102, 102, 102)", $(".karldropdown-menu li").css("background-color"));
});

test('show() shows dropdown menu', function() {
  $('.karldropdown').karldropdown({});
  equals("none", $(".karldropdown-menu").css("display"));
  
  $('.karldropdown').karldropdown('show');
  equals("block", $(".karldropdown-menu").css("display"));
});

test('show() adjusts max width', function() {
  $('.karldropdown').karldropdown({});
  equals("auto", $(".karldropdown-menu li").css("width"));

  $('.karldropdown').karldropdown('show');
  equals("38px", $(".karldropdown-menu li").css("width"));
});


// hide

test('hide() hides dropdown menu', function() {
  stop();
  $('.karldropdown').karldropdown({});

  $('.karldropdown').karldropdown('show');
  equals("block", $(".karldropdown-menu").css("display"));

  $('.karldropdown').karldropdown('hide');
  setTimeout(function() {
    equals("none", $(".karldropdown-menu").css("display"));
    start();
  }, 100);
});


// resetAllItems

test('resetItem() resets css values', function() {
  $('.karldropdown').karldropdown({});
  
  var item = $(".karldropdown-menu li:first");

  equals("transparent", item.css("background-color"));

  $('.karldropdown').karldropdown('show');
  $('.karldropdown').karldropdown('resetItem', item[0]);
  equals("rgb(102, 102, 102)", item.css("background-color"));
});


// hoverItem

test('hoverItem() animates background', function() {
  stop();
  $('.karldropdown').karldropdown({});
  $('.karldropdown').karldropdown('show');

  var item = $(".karldropdown-menu li:first");
  equals("rgb(102, 102, 102)", item.css("background-color"));
  
  $('.karldropdown').karldropdown('hoverItem', item);

  setTimeout(function() {  
    equals("rgb(206, 206, 206)", item.css("background-color"));
    start();
  }, 150);
});

test('hoverItem() animates padding', function() {
  stop();
  $('.karldropdown').karldropdown({});
  $('.karldropdown').karldropdown('show');

  var item = $(".karldropdown-menu li:first");
  equals("0px", item.css("padding-left"));
  
  $('.karldropdown').karldropdown('hoverItem', item);
  
  setTimeout(function() {    
    ok('0px' != item.css("padding-left"));
    start();
  }, 200);
});


// leaveItem

test('leaveItem() resets background', function() {
  stop();
  $('.karldropdown').karldropdown({});
  var item = $(".karldropdown-menu li:first");

  $('.karldropdown').karldropdown('leaveItem', item);

  setTimeout(function() {    
    equals('rgb(102, 102, 102)', item.css("background-color"));
    start();
  }, 70);
});

test('leaveItem() resets padding', function() {
  stop();
  $('.karldropdown').karldropdown({});
  var item = $(".karldropdown-menu li:first");

  $('.karldropdown').karldropdown('leaveItem', item);

  setTimeout(function() {    
    equals('0px', item.css("padding-left"));
    start();
  }, 70);
});

})(jQuery);