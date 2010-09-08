
(function($){

module("karl-slider");

var inside = function(el, xmulti, ymulti) {
    el = $(el);
    var offset = el.offset();
    return {
        x: Math.floor(offset.left + el.outerWidth() * xmulti),
        y: Math.floor(offset.top + el.outerHeight() * ymulti)
    };
};

var simulateDrag = function(el, from, to) {
    el = $(el);
    var d = $(document);
    // as seen in simulate
    // that starts drtagging at the middle of the drag target.
    // ... but we need a specific drag position, 
    // because we want to test if a drag fails correctly.
    var coord = {clientX: from.x, clientY: from.y};
    el.simulate("mousedown", coord);
    coord = {clientX: from.x + 1, clientY: from.y + 1};
    d.simulate("mousemove", coord);
    coord = {clientX: to.x, clientY: to.y};
    d.simulate("mousemove", coord);
    d.simulate("mousemove", coord);
    el.simulate("mouseup", coord);
};

test("create and destroy with enableClickJump=true", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true
    });

    equals(el.karlslider('value'), 0, 'Created OK');
    equals(el.karlslider('option', 'enableClickJump'), true, 'Option OK');

    el.karlslider('destroy');

});

test("jump click", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 1, 'at first increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after first increment');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 2, 'at second increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after second increment');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 3, 'at third increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after third increment');

    el.simulate('mousedown', {clientX: 0,  clientY: p.y});
    el.simulate('mouseup', {clientX: 0,  clientY: p.y});
    equals(el.karlslider('value'), 2, 'back at second increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after decrement');

    el.simulate('mousedown', {clientX: 0,  clientY: p.y});
    el.simulate('mouseup', {clientX: 0,  clientY: p.y});
    equals(el.karlslider('value'), 1, 'back at first increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated in the end');

    el.karlslider('destroy');

});

test("sanity check", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: false     // not enabled 
    });
    
    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    ok(el.karlslider('value') > 50, 'jumped to click position');

    el.karlslider('destroy');

});

test("click on the handle", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        value: 50
    });

    var handle = el.find('.ui-slider-handle');
    
    equals(el.karlslider('value'), 50, 'at the center');

    var p = inside(handle, 0.50, 0.50);

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x, clientY: p.y});
    equals(el.karlslider('value'), 50, 'still at the center');

    el.karlslider('destroy');

});

test("jump click with drag", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        value: 50
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 50, 'at the center');

    var p_left = inside(el, 0.25, 0.50);
    var p_right = inside(el, 0.75, 0.50);

    simulateDrag(el, {x: p_right.x, y: p_right.y}, 
                     {x: p_right.x + 20, y: p_right.y});
    equals(el.karlslider('value'), 51, 'drag 1 failed and did jump');

    simulateDrag(el, {x: p_right.x, y: p_right.y}, 
                     {x: p_right.x + 20, y: p_right.y});
    equals(el.karlslider('value'), 52, 'drag 2 failed and did jump');

    simulateDrag(el, {x: p_left.x, y: p_left.x}, 
                     {x: p_left.x - 20, y: p_right.y});
    equals(el.karlslider('value'), 51, 'drag 3 failed and did jump');

    simulateDrag(el, {x: p_left.x, y: p_left.x}, 
                     {x: p_left.x - 20, y: p_right.y});
    equals(el.karlslider('value'), 50, 'drag 4 failed and did jump');

    el.karlslider('destroy');
});

test("sanity check with drag", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: false,     // not enabled 
        value: 50
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 50, 'at the center');

    var p_left = inside(el, 0.25, 0.50);
    var p_right = inside(el, 0.75, 0.50);

    simulateDrag(el, {x: p_right.x, y: p_right.y}, 
                     {x: p_right.x + 1, y: p_right.y});
    equals(el.karlslider('value'), 75, 'drag 1 succeeded');

    simulateDrag(el, {x: p_left.x, y: p_left.y}, 
                     {x: p_left.x - 1, y: p_left.y});
    equals(el.karlslider('value'), 25, 'drag 2 succeeded');

    el.karlslider('destroy');
});

test("dragging the handle still works", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        value: 50
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 50, 'at the center');

    var p = inside(handle, 0.50, 0.50);
    var p_left = inside(el, 0, 0.50);
    var p_right = inside(el, 0.99, 0.50);

    simulateDrag(el, {x: p.x, y: p.x}, 
                     {x: p_right.x, y: p_right.y});
    equals(el.karlslider('value'), 99, 'drag 1 worked');

    simulateDrag(el, {x: p_right.x, y: p_right.x}, 
                     {x: p.x, y: p.y});
    equals(el.karlslider('value'), 50, 'drag 2 worked');

    el.karlslider('destroy');
});

test("jump click with jumpStep", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        jumpStep: 5
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 5, 'at first increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after first increment');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 10, 'at second increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after second increment');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 15, 'at third increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after third increment');

    el.simulate('mousedown', {clientX: 0,  clientY: p.y});
    el.simulate('mouseup', {clientX: 0,  clientY: p.y});
    equals(el.karlslider('value'), 10, 'back at second increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated after decrement');

    el.simulate('mousedown', {clientX: 0,  clientY: p.y});
    el.simulate('mouseup', {clientX: 0,  clientY: p.y});
    equals(el.karlslider('value'), 5, 'back at first increment');
    ok(! handle.is('.ui-state-active'), 'capture terminated in the end');

    el.karlslider('destroy');

});

test("cannot jump beyond the edges", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        jumpStep: 200,
        slide: function(event, ui) {
            // XXX must check this value for overflow as well
            // because, if the limitation is done at the wrong
            // place, this may overflow without value() overflowing.
            ui_value = ui.value;
        }
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.50, 0.50);

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 100, 'at right side');
    equals(ui_value, 100, 'ui.value did not overflow on the right');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 0, 'at left side');
    equals(ui_value, 0, 'ui.value did not overflow on the left');

    el.karlslider('destroy');

});

test("jumpStep is modded by step", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        step: 3,
        jumpStep: 7
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 9, 'at first increment');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 18, 'at second increment');

    el.simulate('mousedown', {clientX: p.x,  clientY: p.y});
    el.simulate('mouseup', {clientX: p.x,  clientY: p.y});
    equals(el.karlslider('value'), 27, 'at third increment');

    el.simulate('mousedown', {clientX: 0,  clientY: p.y});
    el.simulate('mouseup', {clientX: 0,  clientY: p.y});
    equals(el.karlslider('value'), 18, 'back at second increment');

    el.simulate('mousedown', {clientX: 0,  clientY: p.y});
    el.simulate('mouseup', {clientX: 0,  clientY: p.y});
    equals(el.karlslider('value'), 9, 'back at first increment');

    el.karlslider('destroy');

});

test("enableKeyJump works", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        enableKeyJump: true,
        jumpStep: 5
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 5, 'at first increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 10, 'at second increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 15, 'at third increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.LEFT});
    equals(el.karlslider('value'), 10, 'back at second increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.LEFT});
    equals(el.karlslider('value'), 5, 'back at first increment');

    el.karlslider('destroy');

});

test("sanity check for enableKeyJump", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        enableKeyJump: false,            // not enabled
        jumpStep: 5
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 1, 'at first increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 2, 'at second increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 3, 'at third increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.LEFT});
    equals(el.karlslider('value'), 2, 'back at second increment');

    handle.simulate("keydown", {keyCode: $.ui.keyCode.LEFT});
    equals(el.karlslider('value'), 1, 'back at first increment');

    el.karlslider('destroy');

});

test("cannot jump out with keys", function() {

    var el = $('#slider1');

    var ui_value;
    el.karlslider({
        enableClickJump: true,
        enableKeyJump: true,
        jumpStep: 20,
        slide: function(event, ui) {
            // XXX must check this value for overflow as well
            // because, if the limitation is done at the wrong
            // place, this may overflow without value() overflowing.
            ui_value = ui.value;
        }
    });
    
    var handle = el.find('.ui-slider-handle');

    el.karlslider('value', 98);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 100, 'at the right, did not jump out');
    equals(ui_value, 100, 'ui.value did not overflow on the right');

    el.karlslider('value', 2);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.LEFT});
    equals(el.karlslider('value'), 0, 'at the left, did not jump out');
    equals(ui_value, 0, 'ui.value did not overflow on the left');

    el.karlslider('destroy');

});

test("setting jumpStep option works", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        enableKeyJump: true,
        jumpStep: 5
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 5, 'at first increment');

    el.karlslider('option', 'jumpStep', 10);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 15, 'jumpStep in effect');

    el.karlslider('destroy');

    // But, if keyjumps are not enabled:
    //
    var el = $('#slider2');

    el.karlslider({
        enableClickJump: true,
        enableKeyJump: false,    //
        jumpStep: 5
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 1, 'at first increment');

    el.karlslider('option', 'jumpStep', 10);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 2, 'jumpStep not in effect');

    el.karlslider('destroy');

});

test("setting step option works", function() {

    var el = $('#slider1');

    el.karlslider({
        enableClickJump: true,
        enableKeyJump: true,
        jumpStep: 10
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 10, 'at first increment');

    el.karlslider('option', 'step', 10);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 20, 'step not in effect');

    el.karlslider('destroy');

    // But, if keyjumps are not enabled:
    //
    var el = $('#slider2');

    el.karlslider({
        enableClickJump: true,
        enableKeyJump: false,    //
        jumpStep: 10 
    });
    
    var handle = el.find('.ui-slider-handle');

    equals(el.karlslider('value'), 0, 'at the left');

    var p = inside(el, 0.75, 0.50);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 1, 'at first increment');

    el.karlslider('option', 'step', 5);

    handle.simulate("keydown", {keyCode: $.ui.keyCode.RIGHT});
    equals(el.karlslider('value'), 6, 'step in effect');

    el.karlslider('destroy');

});



})(jQuery);

