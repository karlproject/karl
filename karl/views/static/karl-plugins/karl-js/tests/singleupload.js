/*
 * singleupload unit tests
 */
(function($) {

module("karl: singleupload");

// init

test('init() hides stub', function() {
  equals("block", $(".sif-stub").css("display"));

  $('.sif-widget').karlsingleupload({});
  equals("none", $(".sif-stub").css("display"));
});

test('init() removes name attribute from stub input', function() {
  equals("file", $(".sif-stub input").attr("name"));

  $('.sif-widget').karlsingleupload({});
  equals("", $(".sif-stub input").attr("name"));
});


// add 

test('clicking upload adds new stub', function() {
  $('.sif-widget').karlsingleupload({});
  equals(0, $(".sif-widget input[name='file']").length);

  $('.sif-upload').simulate('click');
  equals(1, $(".sif-widget input[name='file']").length);
});


// del

test('_del() removes stub', function() {
  $('.sif-widget').karlsingleupload({});

  $('.sif-upload').simulate('click');
  equals(1, $(".sif-widget input[name='file']").length);

  $('.sif-nochange').simulate('click');
  equals(0, $(".sif-widget input[name='file']").length);
});


})(jQuery);