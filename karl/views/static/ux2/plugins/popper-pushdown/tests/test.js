/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console setTimeout jQuery module test $ */
/*globals module test start stop expect equal deepEqual ok raises */
/*globals MockHttpServer JSON sinon */


var log = function () {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


// as sinon does not (yet) provide an api call for this,
// we need to define this helper function ourselves.
function parseQuery(url) {
    var result = {};
    var qs = url.split('?', 2)[1];
    var items = qs === undefined ? [] : qs.split('&');
    $.each(items, function (i, v) {
        var pair = v.split('=');
        result[pair[0]] = pair[1];
    });
    return result;
}


// We may have a Mustache library present or not.
// We will patch the library in the tests with a mock,
// which assumes that there is a library to patch.
if (window.Mustache === undefined) {
    window.Mustache = {to_html: function () {}};
}

 
module('popper-pushdowntab', {

    setup: function () {
        var self = this;
        $('#main').append(
            '<div id="the-top-bar">' +
                '<a id="the-link">' +
                    'Pushdown <span class="the-counter">11</span>' +
                '</a>' +
            '</div>'
        );
        // Mock stub for Mustache, which we assume to be tested by itself.

        this.mockMustache = sinon.mock(window.Mustache, "to_html", 
            function (template, data) {
                return template;
            }
        );

        this.clock = sinon.useFakeTimers();

        this.xhr = sinon.useFakeXMLHttpRequest();
        var requests = this.requests = [];
        this.xhr.onCreate = function (xhr) {
            requests.push(xhr);
        };
        // Make sure to deplete microtemplate cache in the head data
        window.head_data = {
        };
    },

    teardown: function () {
        this.clock.restore();
        this.xhr.restore();
        this.mockMustache.verify();
        $('#main').empty();
    }

});


test("Create / destroy", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });

    $('#the-link').pushdowntab('destroy');

    ok(true);
});


test("open it", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    
    this.mockMustache.expects('to_html').once();

    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {}
        })
    );

    // bump the time
    this.clock.tick(400);

    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    $('#the-link').pushdowntab('destroy');
});


test("close it", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    
    // click to open it
    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {}
        })
    );

    // bump the time
    this.clock.tick(400);

    equal($('#popper-pushdown-mypushdown').is(':visible'), true);
    
    // click again to close it
    $('#the-link').simulate('click');

    // bump the time
    this.clock.tick(200);

    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    $('#the-link').pushdowntab('destroy');
});


test("trigger events beforeShow, show, beforeHide, hide", function () {

    var events = [];
    function markEvent(evt) {
        events.push(evt.type);
    }

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter',
        beforeShow: markEvent,
        show: markEvent,
        beforeHide: markEvent,
        hide: markEvent
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    deepEqual(events, []);

    // click to open it
    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        "ts": ""    
    });

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {}
        })
    );

    deepEqual(events, ['pushdowntabbeforeshow']);

    // bump the time
    this.clock.tick(400);

    equal($('#popper-pushdown-mypushdown').is(':visible'), true);
    deepEqual(events, 
        ['pushdowntabbeforeshow', 'pushdowntabshow']);

    // click again to close it
    $('#the-link').simulate('click');
    deepEqual(events,
        ['pushdowntabbeforeshow', 'pushdowntabshow',
        'pushdowntabbeforehide']);

    // bump the time
    this.clock.tick(200);

    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    deepEqual(events,
        ['pushdowntabbeforeshow', 'pushdowntabshow',
        'pushdowntabbeforehide', 'pushdowntabhide']);

    $('#the-link').pushdowntab('destroy');
});


test("getCounter method", function () {
    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });

    equal($('#the-link').pushdowntab('getCounter'), 11);

    $('#the-link .the-counter').text('');
    equal($('#the-link').pushdowntab('getCounter'), 0);

    $('#the-link .the-counter').text('NOTNUMBER');
    equal($('#the-link').pushdowntab('getCounter'), 0);

    $('#the-link .the-counter').text('12.12');
    equal($('#the-link').pushdowntab('getCounter'), 12);

    $('#the-link .the-counter').text('-12');
    equal($('#the-link').pushdowntab('getCounter'), 0);
});


test("setCounter method", function () {
    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });

    // we are closed now
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    $('#the-link').pushdowntab('setCounter', 3);
    equal($('#the-link .the-counter').text(), '3');
    equal($('#the-link .the-counter').is(':visible'), true);

    $('#the-link').pushdowntab('setCounter', 44);
    equal($('#the-link .the-counter').text(), '44');
    equal($('#the-link .the-counter').is(':visible'), true);

    $('#the-link').pushdowntab('setCounter', 0);
    equal($('#the-link .the-counter').text(), '0');
    equal($('#the-link .the-counter').is(':visible'), false,
            'if counter is zero, it is hidden');

    $('#the-link').pushdowntab('setCounter', 2);
    equal($('#the-link .the-counter').text(), '2');
    equal($('#the-link .the-counter').is(':visible'), true);

});


test("listens to notifierUpdate event when panel is closed", function () {
    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });

    // we are closed now
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    // initially we are on 11
    equal($('#the-link').pushdowntab('getCounter'), 11);

    // notifier will trigger this events on document, so this
    // is the deepEqual what we test here.

    $(document).trigger('notifierUpdate', [{
        mypushdown: {cnt: 2, ts: '2012-02-13T20:40:24.771787'},
        // foo is, of course, ignored altogether.
        foo: {cnt: 99, ts: '2012-02-13T20:40:24.771787'}
    }]);
    equal($('#the-link').pushdowntab('getCounter'), 13);

    $(document).trigger('notifierUpdate', [{
        // different isodate format is also ok.
        mypushdown: {cnt: 3, ts: '2012-2-13T20:40:24'}, 
        foo: {cnt: 99, ts: '2012-02-13T20:40:24.771787'}
    }]);
    equal($('#the-link').pushdowntab('getCounter'), 16);

    $(document).trigger('notifierUpdate', [{
        // cnt = 0
        mypushdown: {cnt: 0, ts: '2012-02-13T20:40:24.771787'},
        foo: {cnt: 99, ts: '2012-02-13T20:40:24.771787'}
    }]);
    equal($('#the-link').pushdowntab('getCounter'), 16);

    $(document).trigger('notifierUpdate', [{
        // no section for this pushdown
        foo: {cnt: 99, ts: '2012-02-13T20:40:24.771787'}
    }]);
    equal($('#the-link').pushdowntab('getCounter'), 16);

});


test("listens to notifierUpdate event when panel open", function () {
    
    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });

    // we are closed now
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    // initially we are on 11
    equal($('#the-link').pushdowntab('getCounter'), 11);

    // open it 
    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        "ts": ""
    });

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {}
        })
    );

    // bump the time
    this.clock.tick(400);

    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    // label is zero and hidden now, since we are opened
    equal($('#the-link').pushdowntab('getCounter'), 0);
    equal($('#the-link .the-counter').is(':visible'), false);

    // notifier will trigger this events on document, so this
    // is the deepEqual what we test here.

    $(document).trigger('notifierUpdate', [{
        mypushdown: {cnt: 22, ts: '2012-02-13T20:40:24.771787'},
        // foo is, of course, ignored altogether.
        foo: {cnt: 99, ts: '2012-02-13T20:40:24.771787'}
    }]);

    // however in open state, the counter will always remain intact
    equal($('#the-link').pushdowntab('getCounter'), 0);
    equal($('#the-link .the-counter').is(':visible'), false);
    
    // click again to close it
    $('#the-link').simulate('click');

    // bump the time
    this.clock.tick(200);

    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    $(document).trigger('notifierUpdate', [{
        mypushdown: {cnt: 33, ts: '2012-02-13T20:40:24.771787'},
        // foo is, of course, ignored altogether.
        foo: {cnt: 99, ts: '2012-02-13T20:40:24.771787'}
    }]);

    // counter re-appeared, but we only have the recent items
    // since the panel has been closed.
    equal($('#the-link').pushdowntab('getCounter'), 33);
    equal($('#the-link .the-counter').is(':visible'), true);

    $('#the-link').pushdowntab('destroy');
});


test("ajax data fetch, trigger events ajaxstart, " +
     "ajaxdone, ajaxerror on the panel", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    // Hitch ajax events for checking
    var ajaxEvents = [];
    function collectAjaxEvent() {
        var eventInfo = [arguments[0].type,
            Array.prototype.slice.call(arguments, 1)];
        ajaxEvents.push(eventInfo);
    }
    $('#popper-pushdown-mypushdown').bind({
        'pushdowntabajaxstart': collectAjaxEvent, 
        'pushdowntabajaxdone': collectAjaxEvent, 
        'pushdowntabajaxerror': collectAjaxEvent
    });
    
    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // we have a start event triggered
    equal(ajaxEvents.length, 1);
    deepEqual(ajaxEvents[0], ['pushdowntabajaxstart', []]);

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {}
        })
    );

    // We have a done event triggered
    equal(ajaxEvents.length, 2);
    deepEqual(ajaxEvents[1], ['pushdowntabajaxdone', []]);

    // bump the time
    this.clock.tick(400);

    // yes, succeeded to show it
    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    $('#the-link').pushdowntab('destroy');
});


test("ajax data fetch, error", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter',
        polling: 1   // poll every second
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    
    this.mockMustache.expects('to_html').never();

    // Hitch ajax events for checking
    var ajaxEvents = [];
    function collectAjaxEvent() {
        var eventInfo = [arguments[0].type,
            Array.prototype.slice.call(arguments, 1)];
        ajaxEvents.push(eventInfo);
    }
    $('#popper-pushdown-mypushdown').bind({
        'pushdowntabajaxstart': collectAjaxEvent, 
        'pushdowntabajaxdone': collectAjaxEvent, 
        'pushdowntabajaxerror': collectAjaxEvent
    }); 

    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // we have a start event triggered
    equal(ajaxEvents.length, 1);
    deepEqual(ajaxEvents[0], ['pushdowntabajaxstart', []]);

    // Receive the response
    this.requests[0].respond(505,
        {},
        'ERROR'
    );

    // we have an error event triggered
    equal(ajaxEvents.length, 2);
    deepEqual(ajaxEvents[1], ['pushdowntabajaxerror', []]);

    // Stays closed
    // bump the time, to make sure we don't animate to open...
    this.clock.tick(500);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
});


test("ajax data fetch, explicit error", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter',
        polling: 1   // poll every second
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    
    this.mockMustache.expects('to_html').never();

    // Hitch ajax events for checking
    var ajaxEvents = [];
    function collectAjaxEvent() {
        var eventInfo = [arguments[0].type,
            Array.prototype.slice.call(arguments, 1)];
        ajaxEvents.push(eventInfo);
    }
    $('#popper-pushdown-mypushdown').bind({
        'pushdowntabajaxstart': collectAjaxEvent, 
        'pushdowntabajaxdone': collectAjaxEvent, 
        'pushdowntabajaxerror': collectAjaxEvent
    }); 

    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // we have a start event triggered
    equal(ajaxEvents.length, 1);
    deepEqual(ajaxEvents[0], ['pushdowntabajaxstart', []]);

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            error: 'Explicit error',
            data: {}
        })
    );

    // we have an error event triggered
    equal(ajaxEvents.length, 2);
    deepEqual(ajaxEvents[1], ['pushdowntabajaxerror', []]);

    // Stays closed
    // bump the time, to make sure we don't animate to open...
    this.clock.tick(500);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
});


test("ajax data fetch, repeats polling", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter',
        polling: 1   // poll every second
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    
    this.mockMustache.expects('to_html').once();

    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {},
            ts: 'TS1'
        })
    );

    // bump the time, to let animation have finished
    this.clock.tick(500);

    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    // Now we wait another tick, this ought to trigger the next
    // ajax refresh from the server.
    this.mockMustache.expects('to_html').once();
    this.clock.tick(1000);
    
    // Check what parameters were passed to the request.
    equal(this.requests.length, 2);
    deepEqual(parseQuery(this.requests[1].url), {
        "needsTemplate": "false",
        'ts': 'TS1'
    });

    // Receive the response
    this.requests[1].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            data: {thenewvalue: 'something'},
            ts: 'TS2'
        })
    );

    // Now we wait _yet_ another tick,
    // to make sure that this was not a one time show,
    // and we are repeating properly.
    this.mockMustache.expects('to_html').once();
    this.clock.tick(1000);
    
    // Check what parameters were passed to the request.
    equal(this.requests.length, 3);
    deepEqual(parseQuery(this.requests[2].url), {
        "needsTemplate": "false",
        'ts': 'TS2'
    });

    // Receive the response
    this.requests[2].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            data: {thenewvalue: 'and something'},
            ts: 'TS3'
        })
    );

    $('#the-link').pushdowntab('destroy');
});



test("ajax data fetch, server says up-to-date", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter',
        polling: 1   // poll every second
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);
    
    this.mockMustache.expects('to_html').once();

    $('#the-link').simulate('click');

    // Check what parameters were passed to the request.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "needsTemplate": "true",
        'ts': ''
    });

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {},
            ts: 'TS1'
        })
    );

    // bump the time, to let animation have finished
    this.clock.tick(500);

    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    // Now we wait another tick, this ought to trigger the next
    // ajax refresh from the server.
    this.clock.tick(1000);
    
    // Check what parameters were passed to the request.
    equal(this.requests.length, 2);
    deepEqual(parseQuery(this.requests[1].url), {
        "needsTemplate": "false",
        'ts': 'TS1'
    });

    // Receive the response
    // This time the server says: I send you data=null, this
    // means: you are up to date.
    // That to_html never gets called, means that
    // no rendering took place.
    this.mockMustache.expects('to_html').never();
    this.requests[1].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            data: null,
            ts: 'TS2'
        })
    );

});


test("ajax data fetch, trigger events render", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter'
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    // Hitch ajax events for checking
    var ajaxEvents = [];
    function collectAjaxEvent() {
        var eventInfo = [arguments[0].type,
            Array.prototype.slice.call(arguments, 1)];
        ajaxEvents.push(eventInfo);
    }
    $('#the-link').bind({
        'pushdowntabrender': collectAjaxEvent
    });
    
    $('#the-link').simulate('click');

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {},
            state: 'STATE'
        })
    );

    // we have a render event triggered
    // and the state is passed to it as parm
    equal(ajaxEvents.length, 1);
    deepEqual(ajaxEvents[0], ['pushdowntabrender', ['STATE']]);

    // bump the time
    this.clock.tick(400);

    // yes, succeeded to show it
    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    $('#the-link').pushdowntab('destroy');
});


test("ajax data fetch, repeating, trigger events render", function () {

    $('#the-link').pushdowntab({
        name: 'mypushdown',
        selectTopBar: '#the-top-bar',
        findCounterLabel: '.the-counter',
        polling: 1   // poll every second
    });
    ok($('#popper-pushdown-mypushdown').length > 0);
    equal($('#popper-pushdown-mypushdown').is(':visible'), false);

    // Hitch ajax events for checking
    var ajaxEvents = [];
    function collectAjaxEvent() {
        var eventInfo = [arguments[0].type,
            Array.prototype.slice.call(arguments, 1)];
        ajaxEvents.push(eventInfo);
    }
    $('#the-link').bind({
        'pushdowntabrender': collectAjaxEvent
    });
    
    $('#the-link').simulate('click');

    // Receive the response
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            microtemplate: 'THIS IS A PUSHDOWN',
            data: {}
        })
    );

    // we have a render event triggered
    equal(ajaxEvents.length, 1);
    deepEqual(ajaxEvents[0], ['pushdowntabrender', [{}]]);

    // bump the time
    this.clock.tick(400);

    // yes, succeeded to show it
    equal($('#popper-pushdown-mypushdown').is(':visible'), true);

    // Now we wait another tick, this ought to trigger the next
    // ajax refresh from the server.
    this.mockMustache.expects('to_html').once();
    this.clock.tick(1000);
 
    // Check that we have a request.
    equal(this.requests.length, 2);

    // Receive the response
    this.requests[1].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            data: {thenewvalue: 'something'},
            ts: 'TS2'
        })
    );

    // we have a render event triggered
    equal(ajaxEvents.length, 2);
    deepEqual(ajaxEvents[1], ['pushdowntabrender', [{}]]);

    $('#the-link').pushdowntab('destroy');
});





module('popper-pushdownpanel', {
    // Pushdownpanel is a slave of pushdowntab.
    setup: function () {
        var self = this;
        $('#main').append(
            '<div id="the-node">The Pushdown Text</div>'
        );
        this.clock = sinon.useFakeTimers();
    },

    teardown: function () {
        this.clock.restore();
        $('#main').empty();
    }

});


test("Create / destroy", function () {

    $('#the-node').pushdownpanel({
    });

    $('#the-node').pushdownpanel('destroy');

    ok(true);
});


test("show", function () {

    $('#the-node').pushdownpanel({
    });

    equal($('#the-node').is(':visible'), false);
    
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    $('#the-node').pushdownpanel('destroy');
});


test("hide", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    // hide it
    $('#the-node').pushdownpanel('hide');

    // bump the time
    this.clock.tick(200);

    equal($('#the-node').is(':visible'), false);

    $('#the-node').pushdownpanel('destroy');
});


test("show while showing", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // show it again
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    $('#the-node').pushdownpanel('destroy');
});


test("show and show again", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    // show it again (nothing happens)
    $('#the-node').pushdownpanel('show');

    equal($('#the-node').is(':visible'), true);

    $('#the-node').pushdownpanel('destroy');
});


test("hide while showing", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // hide it (will be ignored... as it is
    // during a state change.)
    $('#the-node').pushdownpanel('hide');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    $('#the-node').pushdownpanel('destroy');
});


test("show while hiding", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    // hide it
    $('#the-node').pushdownpanel('hide');

    // show it (ignored, as we are in state change)
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), false);

    $('#the-node').pushdownpanel('destroy');
});


test("hide while hiding", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    // hide it
    $('#the-node').pushdownpanel('hide');

    // hide it again
    $('#the-node').pushdownpanel('hide');

    // bump the time
    this.clock.tick(200);

    equal($('#the-node').is(':visible'), false);

    $('#the-node').pushdownpanel('destroy');
});


test("hide and hide again", function () {

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    // hide it
    $('#the-node').pushdownpanel('hide');

    // bump the time
    this.clock.tick(200);

    equal($('#the-node').is(':visible'), false);

    // hide it again
    $('#the-node').pushdownpanel('hide');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), false);

    $('#the-node').pushdownpanel('destroy');
});


test("trigger events beforeShow, show, beforeHide, hide", function () {

    var events = [];
    function markEvent(evt) {
        events.push(evt.type);
    }

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
        beforeShow: markEvent,
        show: markEvent,
        beforeHide: markEvent,
        hide: markEvent
    });
    equal($('#the-node').is(':visible'), false);
    deepEqual(events, []);

    // show it
    $('#the-node').pushdownpanel('show');
    deepEqual(events, ['pushdownpanelbeforeshow']);

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);
    deepEqual(events, 
        ['pushdownpanelbeforeshow', 'pushdownpanelshow']);

    // hide it
    $('#the-node').pushdownpanel('hide');
    deepEqual(events,
        ['pushdownpanelbeforeshow', 'pushdownpanelshow',
        'pushdownpanelbeforehide']);

    // bump the time
    this.clock.tick(200);

    equal($('#the-node').is(':visible'), false);
    deepEqual(events,
        ['pushdownpanelbeforeshow', 'pushdownpanelshow',
        'pushdownpanelbeforehide', 'pushdownpanelhide']);

    $('#the-node').pushdownpanel('destroy');
});


test("showing a pushdown hides all the others", function () {

    // need some more
    $('#main').append(
        '<div id="second-node">And now for something completely different</div>'
    );

    // create, and see that is is not visible
    $('#the-node').pushdownpanel({
    });
    $('#second-node').pushdownpanel({
    });
    equal($('#the-node').is(':visible'), false);
    equal($('#second-node').is(':visible'), false);
    
    // show it
    $('#the-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    equal($('#the-node').is(':visible'), true);

    // Show the second one
    $('#second-node').pushdownpanel('show');

    // bump the time
    this.clock.tick(400);

    // second is shown
    equal($('#second-node').is(':visible'), true);
    // first is hidden
    equal($('#the-node').is(':visible'), false);

    $('#the-node').pushdownpanel('destroy');
    $('#second-node').pushdownpanel('destroy');
});


module('popper-notifier', {

    setup: function () {
        var self = this;
        
        this.xhr = sinon.useFakeXMLHttpRequest();
        var requests = this.requests = [];
        this.xhr.onCreate = function (xhr) {
            requests.push(xhr);
        };

        this.clock = sinon.useFakeTimers();
    },

    teardown: function () {
        this.xhr.restore();
        this.clock.restore();
        $('#main').empty();
    }
 
});


test("Create / destroy", function () {
    
    $(document).notifier({
            url: 'notifier.json',
            polling: 15
        });

    $(document).notifier('destroy');
    ok(true);
});


test("Timing the polls, first one", function () {
    var self = this;
    
    // set up the notifier
    $(document).notifier({
            url: 'notifier.json',
            polling: 1
        });

    var events = [];
    function onNotifierUpdate(evt, updates) {
        events.push(updates);
    }
    $(document).bind('notifierUpdate', onNotifierUpdate); 
    deepEqual(events, []);

    // wait for timer
    this.clock.tick(1500);

    // Check what parameters were passed to the request.
    equal(self.requests.length, 1);
    deepEqual(parseQuery(self.requests[0].url), {});

    self.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            "name1": {"cnt": 2, "ts": "2012-02-14T12:08:54.460119"},
            "name2": {"cnt": 3, "ts": "2012-02-14T12:08:54.460119"}
        })
    );

    // Check the events triggered.
    deepEqual(events, [{
        "name1": {"cnt": 2, "ts": "2012-02-14T12:08:54.460119"},
        "name2": {"cnt": 3, "ts": "2012-02-14T12:08:54.460119"}
    }]);

    $(document).unbind('notifierUpdate', onNotifierUpdate); 
    $(document).notifier('destroy');
});


test("Timing the polls, is repeating", function () {
    var self = this;
    
    // set up the notifier
    $(document).notifier({
            url: 'notifier.json',
            polling: 1
        });

    var events = [];
    function onNotifierUpdate(evt, updates) {
        events.push(updates);
    }
    $(document).bind('notifierUpdate', onNotifierUpdate); 
    deepEqual(events, []);

    // wait for timer
    this.clock.tick(1500);

    // Check what parameters were passed to the request.
    equal(self.requests.length, 1);
    deepEqual(parseQuery(self.requests[0].url), {});

    // Receive the response
    self.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            "name1": {"cnt": 2, "ts": "2012-02-14T12:08:54.460119"},
            "name2": {"cnt": 3, "ts": "2012-02-14T12:08:54.460119"}
        })
    );

    // Check the events triggered.
    equal(events.length, 1);

    // wait for next timer
    this.clock.tick(1000);

    // next request: what ts the server returned, is passed back
    equal(self.requests.length, 2);
    deepEqual(parseQuery(self.requests[1].url), {
        "name1": "2012-02-14T12%3A08%3A54.460119",
        "name2": "2012-02-14T12%3A08%3A54.460119"
    });

    // Receive the response
    self.requests[1].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            "name1": {"cnt": 2, "ts": "2012-02-14T12:08:54.460119"},
            "name2": {"cnt": 3, "ts": "2012-02-14T12:08:54.460119"}
        })
    );

    // Check the events triggered.
    equal(events.length, 2);

    $(document).unbind('notifierUpdate', onNotifierUpdate); 
    $(document).notifier('destroy');

});


test("Timing the polls, remember timestamps", function () {
    var self = this;
    
    // set up the notifier
    $(document).notifier({
            url: 'notifier.json',
            polling: 1
        });

    // wait for timer
    this.clock.tick(1500);

    // the first request: no "from" timestamps, yet
    deepEqual(parseQuery(self.requests[0].url), {});

    // Receive the response
    self.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({
            "name1": {"cnt": 2, "ts": "2012-02-14T12:08:54.460119"},
            "name2": {"cnt": 3, "ts": "2012-02-14T12:08:54.460119"}
        })
    );

    // wait for next timer
    this.clock.tick(1000);

    // next request: what ts the server returned, is passed back
    equal(self.requests.length, 2);
    deepEqual(parseQuery(self.requests[1].url), {
        "name1": "2012-02-14T12%3A08%3A54.460119",
        "name2": "2012-02-14T12%3A08%3A54.460119"
    });

    // Receive the response
    self.requests[1].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify({     // Different key set, different dates
            "name1": {"cnt": 2, "ts": "2012-02-01T12:08:54.460119"},
            "name3": {"cnt": 3, "ts": "2012-02-01T12:08:54.460119"}
        })
    );

    // wait for next timer
    this.clock.tick(1000);

    // See the timestamps updated properly.
    equal(self.requests.length, 3);
    deepEqual(parseQuery(self.requests[2].url), {
        "name1": "2012-02-01T12%3A08%3A54.460119",
        "name2": "2012-02-14T12%3A08%3A54.460119",
        "name3": "2012-02-01T12%3A08%3A54.460119"
    });

    $(document).notifier('destroy');

});


