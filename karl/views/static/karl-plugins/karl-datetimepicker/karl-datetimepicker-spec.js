
/* jshint expr: true */

describe('karl-buttonset plugin', function () {

  beforeEach(function () {
    $('body').html(__html__['karl/views/static/karl-plugins/karl-datetimepicker/karl-datetimepicker-fixture.html']);
  });
  afterEach(function () {
    $('body').empty();
  });

  it('can be created and destroyed', function() {
    $('#datetime1').karldatetimepicker({
    });
    $('#datetime1').karldatetimepicker('destroy');
  });

});

