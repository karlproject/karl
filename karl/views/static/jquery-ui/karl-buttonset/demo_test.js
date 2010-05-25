
module('Buttonset');

test("Create / destroy", function() {

    $('#template1').karlbuttonset();

    ok($('#template1').data('karlbuttonset'), 'instance bound');
    ok($('#template1').parent().data('karlbuttonset'), 'instance bound to wrapper');

    $('#template1').karlbuttonset('destroy');

    ok(! $('#template1').data('karlbuttonset'), 'instance not bound');
    ok(! $('#template1').hasClass('ui-helper-hidden'), 'original node not hidden');

    // let's try with ui-helper-hidden initially
    $('#template1').addClass('ui-helper-hidden');
    $('#template1').karlbuttonset();
    $('#template1').karlbuttonset('destroy');
    ok($('#template1').hasClass('ui-helper-hidden'), 'original hidden node remains hidden');

});

test("Basic", function() {

    $('#template1').karlbuttonset();

    var wrapper = $('#template1').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    ok(wrapper.hasClass('fg-buttonset'), 'wrapper class ');
    ok(wrapper.hasClass('ui-helper-clearfix'), 'wrapper class, clearfix');

    ok(! wrapper.hasClass('fg-buttonset-single'), 'wrapper class, not single (compact)');

    equals(buttons.length, 3, 'nr buttons created');
    equals(buttons.eq(0).find('a').attr('title'), 'Delete', 'title 0');
    equals(buttons.eq(1).find('a').attr('title'), 'Save', 'title 1');
    equals(buttons.eq(2).find('a').attr('title'), 'Open', 'title 2');
    ok(buttons.eq(0).find('span').hasClass('ui-icon-trash'), 'icon 0');
    ok(buttons.eq(1).find('span').hasClass('ui-icon-disk'), 'icon 1');
    ok(buttons.eq(2).find('span').hasClass('ui-icon-folder-open'), 'icon 2');
    ok(buttons.eq(0).text(), 'Delete', 'no spaces in label 0');
    ok(buttons.eq(1).text(), 'Save', 'no spaces in label 1');
    ok(buttons.eq(2).text(), 'Open', 'no spaces in label 2');
    buttons.each(function(i) {
        ok($(this).hasClass('fg-button'), 'buttonclass ' + i);
        ok(! $(this).hasClass('fg-button-icon-solo'), 'buttonclass, no soloicons ' + i);
        ok($(this).hasClass('ui-corner-all'), 'buttonclass, corner ' + i);
        ok($(this).find('span').hasClass('ui-icon'), 'iconclass ' + i);
    });


    $('#template1').karlbuttonset('destroy');
});

test("Singleselect", function() {

    $('#template2').karlbuttonset();

    var wrapper = $('#template2').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    ok(wrapper.hasClass('fg-buttonset'), 'wrapper class ');
    ok(wrapper.hasClass('ui-helper-clearfix'), 'wrapper class, clearfix');

    ok(! wrapper.hasClass('fg-buttonset-single'), 'wrapper class, not single (compact)');

    equals(buttons.length, 3, 'nr buttons created');
    equals(buttons.eq(0).find('a').attr('title'), 'Delete', 'title 0');
    equals(buttons.eq(1).find('a').attr('title'), 'Save', 'title 1');
    equals(buttons.eq(2).find('a').attr('title'), 'Open', 'title 2');
    ok(buttons.eq(0).find('span').hasClass('ui-icon-trash'), 'icon 0');
    ok(buttons.eq(1).find('span').hasClass('ui-icon-disk'), 'icon 1');
    ok(buttons.eq(2).find('span').hasClass('ui-icon-folder-open'), 'icon 2');
    buttons.each(function(i) {
        ok($(this).hasClass('fg-button'), 'buttonclass ' + i);
        ok(! $(this).hasClass('fg-button-icon-solo'), 'buttonclass, no soloicons ' + i);
        ok($(this).hasClass('ui-corner-all'), 'buttonclass, corner ' + i);
        ok($(this).find('span').hasClass('ui-icon'), 'iconclass ' + i);
    });

    // check selections
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');

    $('#template2').karlbuttonset('destroy');
});

test("Multiselect", function() {

    $('#template3').karlbuttonset();

    var wrapper = $('#template3').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    ok(wrapper.hasClass('fg-buttonset'), 'wrapper class ');
    ok(wrapper.hasClass('ui-helper-clearfix'), 'wrapper class, clearfix');

    ok(! wrapper.hasClass('fg-buttonset-single'), 'wrapper class, not single (compact)');

    equals(buttons.length, 3, 'nr buttons created');
    equals(buttons.eq(0).find('a').attr('title'), 'Delete', 'title 0');
    equals(buttons.eq(1).find('a').attr('title'), 'Save', 'title 1');
    equals(buttons.eq(2).find('a').attr('title'), 'Open', 'title 2');
    ok(buttons.eq(0).find('span').hasClass('ui-icon-trash'), 'icon 0');
    ok(buttons.eq(1).find('span').hasClass('ui-icon-disk'), 'icon 1');
    ok(buttons.eq(2).find('span').hasClass('ui-icon-folder-open'), 'icon 2');
    buttons.each(function(i) {
        ok($(this).hasClass('fg-button'), 'buttonclass ' + i);
        ok(! $(this).hasClass('fg-button-icon-solo'), 'buttonclass, no soloicons ' + i);
        ok($(this).hasClass('ui-corner-all'), 'buttonclass, corner ' + i);
        ok($(this).find('span').hasClass('ui-icon'), 'iconclass ' + i);
    });

    // check selections
    ok(buttons.eq(0).hasClass('ui-state-active'), 'selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(buttons.eq(2).hasClass('ui-state-active'), 'selected 2');

    $('#template2').karlbuttonset('destroy');
});


test("Icons only", function() {

    // mark as icons only
    $('#template1').addClass('icons-only');

    $('#template1').karlbuttonset();

    var wrapper = $('#template1').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    equals(buttons.length, 3, 'nr buttons created');
    buttons.each(function(i) {
        ok($(this).hasClass('fg-button-icon-solo'), 'buttonclass, solo icons ' + i);
    });

    $('#template1').karlbuttonset('destroy');
});

test("Icons + text", function() {

    // default is icons + text
    // remove 2nd icon
    $('#template1').children().eq(1).removeClass('ui-icon-disk')

    $('#template1').karlbuttonset();

    var wrapper = $('#template1').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    equals(buttons.length, 3, 'nr buttons created');

    // check text + icon markup
    ok(buttons.eq(0).hasClass('fg-button-icon-right'), 'buttonclass, right icon 0');
    ok(buttons.eq(0).find('span').hasClass('ui-icon-trash'), 'icon 0');
    ok(! buttons.eq(1).hasClass('fg-button-icon-right'), 'buttonclass, no right icon 1');
    ok(buttons.eq(1).find('span').length == 0, 'no icon 1');
    ok(buttons.eq(2).hasClass('fg-button-icon-right'), 'buttonclass, right icon 2');
    ok(buttons.eq(2).find('span').hasClass('ui-icon-folder-open'), 'icon 2');

    $('#template1').karlbuttonset('destroy');
});

test("Compact", function() {

    // mark as compact
    $('#template1').addClass('compact');

    $('#template1').karlbuttonset();

    var wrapper = $('#template1').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    ok(wrapper.hasClass('fg-buttonset'), 'wrapper class ');
    ok(wrapper.hasClass('ui-helper-clearfix'), 'wrapper class, clearfix');
    ok(wrapper.hasClass('fg-buttonset-single'), 'wrapper class, single (compact)');

    equals(buttons.length, 3, 'nr buttons created');
    buttons.each(function(i) {
        ok($(this).hasClass('fg-button'), 'buttonclass ' + i);
        ok(! $(this).hasClass('ui-corner-all'), 'buttonclass, no corner-all  ' + i);
    });
    ok(buttons.eq(0).hasClass('ui-corner-left'), 'buttonclass left rounding');
    ok(buttons.eq(2).hasClass('ui-corner-right'), 'buttonclass right rounding');

    $('#template1').karlbuttonset('destroy');
});


test("Actions, noselection", function() {

    $('#template1').karlbuttonset();

    var wrapper = $('#template1').parent();
    var buttons = wrapper.find('.fg-button');

    // test if events arrive both to wrapper and original element
    var res = [];
    wrapper
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res.push([button_index, value]);
        });
    var res2 = [];
    $('#template1').data('karlbuttonset').element
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res2.push([button_index, value]);
        });

    buttons.each(function(i) {
        ok(! $(this).hasClass('ui-state-active'), 'before, not selected ' + i);
    });

    buttons.eq(0).click();
    buttons.eq(2).click();
    buttons.eq(1).click();
    buttons.eq(2).click();

    same(res, [
        [0, true],
        [2, true],
        [1, true],
        [2, true]
    ], 'event sequence wrapper');
    same(res2, [
        [0, true],
        [2, true],
        [1, true],
        [2, true]
    ], 'event sequence original element');

    buttons.each(function(i) {
        ok(! $(this).hasClass('ui-state-active'), 'after, not selected ' + i);
    });

    $('#template1').karlbuttonset('destroy');
});

test("Actions, single selection", function() {

    $('#template2').karlbuttonset();

    var select = $('#template2');
    var wrapper = $('#template2').parent();
    var buttons = wrapper.find('.fg-button');

    // test if events arrive both to wrapper and original element
    var res = [];
    wrapper
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res.push([button_index, value]);
        });
    var res2 = [];
    $('#template2').data('karlbuttonset').element
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res2.push([button_index, value]);
        });


    // initial selection
    ok(!buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Save');
    
    buttons.eq(0).click();
    ok(buttons.eq(0).hasClass('ui-state-active'), 'selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Delete');
    buttons.eq(2).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(buttons.eq(2).hasClass('ui-state-active'), 'selected 2');
    same(select.val(), 'Open');
    buttons.eq(1).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Save');
    buttons.eq(2).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(buttons.eq(2).hasClass('ui-state-active'), 'selected 2');
    same(select.val(), 'Open');

    // sequence of events
    same(res, [
        [1, false],
        [0, true],
        [0, false],
        [2, true],
        [2, false],
        [1, true],
        [1, false],
        [2, true]
    ], 'event sequence wrapper');
    same(res2, [
        [1, false],
        [0, true],
        [0, false],
        [2, true],
        [2, false],
        [1, true],
        [1, false],
        [2, true]
    ], 'event sequence original element');

    $('#template2').karlbuttonset('destroy');
});

test("Actions, multiple selection", function() {

    $('#template3').karlbuttonset();

    var select = $('#template3');
    var wrapper = $('#template3').parent();
    var buttons = wrapper.find('.fg-button');

    // test if events arrive both to wrapper and original element
    var res = [];
    wrapper
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res.push([button_index, value]);
        });
    var res2 = [];
    $('#template3').data('karlbuttonset').element
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res2.push([button_index, value]);
        });

    // initial selection
    ok(buttons.eq(0).hasClass('ui-state-active'), 'selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(buttons.eq(2).hasClass('ui-state-active'), 'selected 2');
    same(select.val(), ['Delete', 'Open']);

    buttons.eq(0).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(buttons.eq(2).hasClass('ui-state-active'), 'selected 2');
    same(select.val(), ['Open']);
    buttons.eq(2).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), null);
    buttons.eq(1).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), ['Save']);
    buttons.eq(2).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(buttons.eq(2).hasClass('ui-state-active'), 'selected 2');
    same(select.val(), ['Save', 'Open']);

    // sequence of events
    same(res, [
        [0, false],
        [2, false],
        [1, true],
        [2, true]
    ], 'event sequence wrapper');
    same(res2, [
        [0, false],
        [2, false],
        [1, true],
        [2, true]
    ], 'event sequence original element');

    $('#template3').karlbuttonset('destroy');
});

test("Extra container class", function() {

    $('#template1').karlbuttonset({
        clsContainer: 'MARKER1 MARKER2'
    });

    var wrapper = $('#template1').parent();
    var buttons = wrapper.find('.fg-button');

    // check markup
    //
    ok(wrapper.hasClass('fg-buttonset'), 'wrapper class ');
    ok(wrapper.hasClass('ui-helper-clearfix'), 'wrapper class, clearfix');
    ok(wrapper.hasClass('MARKER1'), 'wrapper class, marker1 ok');
    ok(wrapper.hasClass('MARKER2'), 'wrapper class, marker2 ok');

    $('#template1').karlbuttonset('destroy');
});

test("Disables work with noselection", function() {

    $('#template4').karlbuttonset();

    var wrapper = $('#template4').parent();
    var buttons = wrapper.find('.fg-button');

    // test if events arrive both to wrapper and original element
    var res = [];
    wrapper
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res.push([button_index, value]);
        });
    var res2 = [];
    $('#template4').data('karlbuttonset').element
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res2.push([button_index, value]);
        });

    // initial markup
    ok(buttons.eq(0).hasClass('ui-state-default'), 'default ok 0');
    ok(buttons.eq(1).hasClass('ui-state-default'), 'default ok 1');
    ok(buttons.eq(2).hasClass('ui-state-default'), 'default ok 2');
    ok(! buttons.eq(0).hasClass('ui-state-disabled'), 'not disabled 0');
    ok(! buttons.eq(1).hasClass('ui-state-disabled'), 'not disabled 1');
    ok(buttons.eq(2).hasClass('ui-state-disabled'), 'disabled 2');

    buttons.eq(0).click();
    buttons.eq(2).click();
    buttons.eq(1).click();
    buttons.eq(2).click();

    // sequence of events
    same(res, [
        [0, true],
        [1, true],
    ], 'event sequence wrapper');
    same(res2, [
        [0, true],
        [1, true],
    ], 'event sequence original element');

    $('#template4').karlbuttonset('destroy');

});

test("Disables work in selects", function() {

    $('#template5').karlbuttonset();

    var select = $('#template5');
    var wrapper = $('#template5').parent();
    var buttons = wrapper.find('.fg-button');

    // test if events arrive both to wrapper and original element
    var res = [];
    wrapper
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res.push([button_index, value]);
        });
    var res2 = [];
    $('#template5').data('karlbuttonset').element
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res2.push([button_index, value]);
        });

    // initial markup
    ok(buttons.eq(0).hasClass('ui-state-default'), 'default ok 0');
    ok(buttons.eq(1).hasClass('ui-state-default'), 'default ok 1');
    ok(buttons.eq(2).hasClass('ui-state-default'), 'default ok 2');
    ok(! buttons.eq(0).hasClass('ui-state-disabled'), 'not disabled 0');
    ok(! buttons.eq(1).hasClass('ui-state-disabled'), 'not disabled 1');
    ok(buttons.eq(2).hasClass('ui-state-disabled'), 'disabled 2');

    // initial selection
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Save');
    
    buttons.eq(0).click();
    ok(buttons.eq(0).hasClass('ui-state-active'), 'selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Delete');
    // this is inactive since it's disabled.
    buttons.eq(2).click();
    ok(buttons.eq(0).hasClass('ui-state-active'), 'selected 0');
    ok(! buttons.eq(1).hasClass('ui-state-active'), 'not selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Delete');
    buttons.eq(1).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Save');
    // this is inactive since it's disabled.
    buttons.eq(2).click();
    ok(! buttons.eq(0).hasClass('ui-state-active'), 'not selected 0');
    ok(buttons.eq(1).hasClass('ui-state-active'), 'selected 1');
    ok(! buttons.eq(2).hasClass('ui-state-active'), 'not selected 2');
    same(select.val(), 'Save');

    // sequence of events
    same(res, [
        [1, false],
        [0, true],
        [0, false],
        [1, true],
    ], 'event sequence wrapper');
    same(res2, [
        [1, false],
        [0, true],
        [0, false],
        [1, true],
    ], 'event sequence original element');

    $('#template5').karlbuttonset('destroy');

});

test("Disables works with the change event", function() {

    // Here we checked that even if the widget starts
    // with some buttons disabled, those buttons will
    // become clickable after they are re-enabled by
    // removing the ui-state-disabled interaction class
    // from them.

    $('#template5').karlbuttonset();

    var select = $('#template5');
    var wrapper = $('#template5').parent();
    var buttons = wrapper.find('.fg-button');

    // test if events arrive both to wrapper and original element
    var res = [];
    wrapper
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res.push([button_index, value]);
        });
    var res2 = [];
    $('#template5').data('karlbuttonset').element
        .bind('change.karlbuttonset', function(event, button_index, value) {
            res2.push([button_index, value]);
        });

    // initial markup
    ok(buttons.eq(0).hasClass('ui-state-default'), 'default ok 0');
    ok(buttons.eq(1).hasClass('ui-state-default'), 'default ok 1');
    ok(buttons.eq(2).hasClass('ui-state-default'), 'default ok 2');
    ok(! buttons.eq(0).hasClass('ui-state-disabled'), 'not disabled 0');
    ok(! buttons.eq(1).hasClass('ui-state-disabled'), 'not disabled 1');
    ok(buttons.eq(2).hasClass('ui-state-disabled'), 'disabled 2');

    // Try to click on the disabled button
    buttons.eq(2).click();

        // It did trigger
    same(res, [
    ], 'no triggering happened');
    same(res2, [
    ], 'no triggering happened');
    
    // Set button 2 to enabled
    buttons.eq(2).removeClass('ui-state-disabled')
    buttons.eq(2).click();

    same(res, [
        [1, false],
        [2, true],
    ], 'triggering ok after re-enabling');
    same(res2, [
        [1, false],
        [2, true],
    ], 'triggering ok after re-enabling');

    $('#template5').karlbuttonset('destroy');

});

test("getButton method returns a button control by its index", function() {

    $('#template5').karlbuttonset();

    var select = $('#template5');
    var wrapper = $('#template5').parent();
    var buttons = wrapper.find('.fg-button');

    // check if the buttons returned by getButton are the real controls 
    // XXX Why the spaces after the label?
    same($('#template5').karlbuttonset('getButton', 0).text(), 'Delete', 'getButton(0) ok');
    same($('#template5').karlbuttonset('getButton', 1).text(), 'Save', 'getButton(1) ok');
    same($('#template5').karlbuttonset('getButton', 2).text(), 'Open', 'getButton(2) ok');

    $('#template5').karlbuttonset('destroy');

});

