/*
 * multiupload unit tests
 */
(function($) {

module("karl: multiupload");

// init

test('init() hides stub', function() {
  equals("block", $(".muf-stub").css("display"));

  $('.muf-widget').karlmultiupload({});
  equals("none", $(".muf-stub").css("display"));
});

test('init() removes name attribute from stub input', function() {
  equals("attachment", $(".muf-stub input").attr("name"));

  $('.muf-widget').karlmultiupload({});
  equals("", $(".muf-stub input").attr("name"));
});


// add

test('clicking add button adds new stub', function() {
  $('.muf-widget').karlmultiupload({});
  equals(0, $(".muf-widget input[name='attachment0']").length)
  equals(0, $(".muf-widget input[name='attachment1']").length)

  $('.muf-addbutton').simulate('click');
  equals(1, $(".muf-widget input[name='attachment0']").length)

  $('.muf-addbutton').simulate('click');
  equals(1, $(".muf-widget input[name='attachment1']").length)
});


// close

test('clicking add button adds new stub', function() {
  $('.muf-widget').karlmultiupload({});
  $('.muf-addbutton').simulate('click');
  equals(1, $(".muf-widget input[name='attachment0']").length)

  $(".muf-closebutton").simulate('click');
  equals(0, $(".muf-widget input[name='attachment0']").length)
});


})(jQuery);