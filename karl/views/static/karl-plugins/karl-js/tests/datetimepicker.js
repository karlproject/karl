/*
 * datetimepicker unit tests
 */
(function($) {

module("karl: datetimepicker");


// init

test('init() hides input', function() {


  $('#startDate').karldatetimepicker({})
      .bind('change.karldatetimepicker', function() {
          $('#endDate').karldatetimepicker('limitMinMax',
            // add one hour
            new Date($(this).karldatetimepicker('getAsDate').valueOf() + 3600000),
          null);
      });
});

test('init() creates container', function() {

});

test('init() creates date input', function() {

});

test('init() creates hour select options', function() {

});

test('init() creates colon span', function() {

});

test('init() creates minute select options', function() {

});


// set


// setDate


// setHour


// setMinute


// getAsDate


// setAsDate


// limitMinMax



})(jQuery);
