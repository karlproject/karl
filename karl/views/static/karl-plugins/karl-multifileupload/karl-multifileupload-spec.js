
/* jshint expr: true */

describe('KARL Multi File Upload', function() {

  beforeEach(function() {
    $('body').html(__html__['karl/views/static/karl-plugins/karl-multifileupload/karl-multifileupload-fixture.html']);
  });
  afterEach(function() {
    $('body').empty();
  });

  it('can create and destroy', function() {
    $('#template1').karlbuttonset();
    // instance bound
    expect($('#template1').data('karlbuttonset')).not.to.be.empty;
    // instance bound to wrapper
    expect($('#template1').parent().data('karlbuttonset')).to.be.ok;
    $('#template1').karlbuttonset('destroy');
    // instance not bound
    expect($('#template1').data('karlbuttonset')).not.to.be.ok;
    // original node not hidden
    expect($('#template1').hasClass('ui-helper-hidden')).to.be.false;

    // let's try with ui-helper-hidden initially
    $('#template1').addClass('ui-helper-hidden');
    $('#template1').karlbuttonset();
    $('#template1').karlbuttonset('destroy');
    // original hidden node remains hidden
    expect($('#template1').hasClass('ui-helper-hidden')).to.be.true;
  });

});