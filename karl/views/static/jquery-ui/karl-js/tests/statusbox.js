/*
 * statusbox unit tests
 */
(function($) {

module("karl: statusbox");

// defaults

test('uses custom class for item base on defaults', function() {
  $('.statusbox').karlstatusbox({clsItem: 'special-class'});

  $('.statusbox').karlstatusbox('append', '1st message!');
  ok( $(".statusbox .special-class").length, "box uses custom class name");
});

test('adds close button when defaults to hasCloseButton = true', function() {
  $('.statusbox').karlstatusbox({hasCloseButton: true});

  $('.statusbox').karlstatusbox('append', '1st message!');
  ok( $(".statusbox .statusbox-closebutton").length, "close button exists" );
});

test('does not add close button when defaults to hasCloseButton = false', function() {
  $('.statusbox').karlstatusbox({hasCloseButton: false});

  $('.statusbox').karlstatusbox('append', '1st message!');
  ok(!$(".statusbox .statusbox-closebutton").length, "close button does't exist" );
});


// append

test('append() without category adds items to queue', function() {
  $('.statusbox').karlstatusbox({});

  $('.statusbox').karlstatusbox('append', '1st message!');
  $('.statusbox').karlstatusbox('append', '2nd message!');

  // messages were appended
  equals(2, $('.statusbox div.statusbox-item .message').length);
  equals("1st message!", $('.statusbox .message').html());
});

test('append() with category adds items to queue', function() {
  $('.statusbox').karlstatusbox({});

  $('.statusbox').karlstatusbox('append', '1st message!', 'login');
  $('.statusbox').karlstatusbox('append', '2nd message!', 'register');

  // messages were appended
  equals(2, $('.statusbox div.statusbox-item .message').length);
  equals("1st message!", $('.statusbox .message').html());
});


// clear

test('clear() without category empties queue', function() {
  $('.statusbox').karlstatusbox({});

  // seed messages to test that they are cleared
  $('.statusbox').karlstatusbox('append', '1st message!');
  $('.statusbox').karlstatusbox('append', '2nd message!');
  equals(2, $('.statusbox .message').length);

  $('.statusbox').karlstatusbox('clear');
  equals(0, $('.statusbox .message').length);
});

test('clear() with category empties items in category', function() {
  $('.statusbox').karlstatusbox({});

  // seed messages to test that they are cleared
  $('.statusbox').karlstatusbox('append', '1st message!', 'login');
  $('.statusbox').karlstatusbox('append', '2nd message!', 'register');
  equals(2, $('.statusbox .message').length);

  $('.statusbox').karlstatusbox('clear', 'login');
  equals(1, $('.statusbox .message').length);
});


// clearAndAppend

test('clearAndAppend() with category empties category and appends to queue', function() {
  $('.statusbox').karlstatusbox({});

  // seed messages to test that they are cleared
  $('.statusbox').karlstatusbox('append', '1st message!', 'login');
  $('.statusbox').karlstatusbox('append', '2nd message!', 'register');
  equals(2, $('.statusbox .message').length)
  equals("1st message!", $('.statusbox .message').html());

  $('.statusbox').karlstatusbox('clearAndAppend', '3rd message!', 'login');
  equals(2, $('.statusbox .message').length);
  equals("2nd message!", $('.statusbox .message').html());
});

test('clearAndAppend() without category empties queue and appends to queue', function() {
  $('.statusbox').karlstatusbox({});
  
  // seed messages to test that they are cleared
  $('.statusbox').karlstatusbox('append', '1st message!');
  $('.statusbox').karlstatusbox('append', '2nd message!');
  equals(2, $('.statusbox .message').length)

  $('.statusbox').karlstatusbox('clearAndAppend', '3rd message!');
  equals(1, $('.statusbox .message').length);
  equals("3rd message!", $('.statusbox .message').html());
});


})(jQuery);