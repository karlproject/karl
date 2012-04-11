

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


module('popper-tagbox', {

    setup: function() {
        var self = this;
        $('#main').append(
            '<div id="the-node"></div>'
        );
        // XXX Instead of falling back on window.head_data, the widget should
        // rely on options. TODO
        window.head_data = {'panel_data': {'tagbox': {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 2, "snippet": "nondeleteable", "tag": "park"}
            ],
            "docid": -1352878729
        }}};

        this.clock = sinon.useFakeTimers();
        
        this.xhr = sinon.useFakeXMLHttpRequest();
        var requests = this.requests = [];
        this.xhr.onCreate = function (xhr) {
            requests.push(xhr);
        };

        
    },

    teardown: function() {
        this.xhr.restore();
        this.clock.restore();
        $('#main').empty();
    }

});


test("Create / destroy", function() {

    $('#the-node').tagbox({
    });

    $('#the-node').tagbox('destroy');

    ok(true);

});


//
// XXX Plenty of tests missing here. TODO: Add them!
//


test("Autocomplete, basics", function() {

    // Specifying an autocompleteURL will enable autocomplete.
    $('#the-node').tagbox({
        autocompleteURL: 'http://foo.bar/autocomplete.json'
    });

    var input = $('#the-node input#newTag');
    
    // Start typing in the input box.
    // This is, of course, not a complete event simulation,
    // we just try to trigger the three main key events.
    input
        .val('a')   // ... also need to set this, the events
                    // in itself won't set the val()
        .simulate('keydown', {keyCode: 97}) // 'a'
        .simulate('keypress', {keyCode: 97})
        .simulate('keyup', {keyCode: 97});

    // wait some - autocomplete has smart delay logic.
    this.clock.tick(1000);

    // Nothing happened, because only the 2nd char starts the search.
    equal(this.requests.length, 0);
    
    // Start typing in the input box.
    input
        .val('ab')   // ... also need to set this, the events
                    // in itself won't set the val()
        .simulate('keydown', {keyCode: 98})  // 'b'
        .simulate('keypress', {keyCode: 98})
        .simulate('keyup', {keyCode: 98});

    // wait some - autocomplete has smart delay logic.
    this.clock.tick(1000);

    // The 2nd char ... starts the search.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "term": "ab"
    });

    // Oh good! Let's feed it a response.
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify(['abstinence', 'abcde'])
    );


    // Try again, now a 3rd character.
    input
        .val('abc')   // ... also need to set this, the events
                    // in itself won't set the val()
        .simulate('keydown', {keyCode: 99})  // 'c'
        .simulate('keypress', {keyCode: 99})
        .simulate('keyup', {keyCode: 99});
    this.clock.tick(1000);
    equal(this.requests.length, 2);
    deepEqual(parseQuery(this.requests[1].url), {
        "term": "abc"
    });
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify(['abcde'])
    );

    $('#the-node').tagbox('destroy');

});


test("Autocomplete, tab", function() {

    // Specifying an autocompleteURL will enable autocomplete.
    $('#the-node').tagbox({
        autocompleteURL: 'http://foo.bar/autocomplete.json'
    });

    var input = $('#the-node input#newTag');
    
    // Start typing in the input box.
    // This is, of course, not a complete event simulation,
    // we just try to trigger the three main key events.
    input
        .val('a')   // ... also need to set this, the events
                    // in itself won't set the val()
        .simulate('keydown', {keyCode: 97}) // 'a'
        .simulate('keypress', {keyCode: 97})
        .simulate('keyup', {keyCode: 97});

    // wait some - autocomplete has smart delay logic.
    this.clock.tick(1000);

    // Nothing happened, because only the 2nd char starts the search.
    equal(this.requests.length, 0);
    
    // Start typing in the input box.
    input
        .val('ab')   // ... also need to set this, the events
                    // in itself won't set the val()
        .simulate('keydown', {keyCode: 98})  // 'b'
        .simulate('keypress', {keyCode: 98})
        .simulate('keyup', {keyCode: 98});

    // wait some - autocomplete has smart delay logic.
    this.clock.tick(1000);

    // The 2nd char ... starts the search.
    equal(this.requests.length, 1);
    deepEqual(parseQuery(this.requests[0].url), {
        "term": "ab"
    });

    // Oh good! Let's feed it a response.
    this.requests[0].respond(200,
        {'Content-Type': 'application/json; charset=UTF-8'},
        JSON.stringify(['abstinence', 'abcde'])
    );

    var menu = $('.ui-autocomplete.ui-menu');
    equal(menu.length, 1, 'there is only one menu');
    var menuItems = menu.find('.ui-menu-item');
    equal(menuItems.length, 2, 'there are two menu items');
    equal(menuItems.find('.ui-state-focus').length, 0, 'no item in focus');

    // Press TAB.
    input
        .simulate('keydown', {keyCode: $.ui.keyCode.TAB})
        .simulate('keypress', {keyCode: $.ui.keyCode.TAB})
        .simulate('keyup', {keyCode: $.ui.keyCode.TAB});
    // ok... we _probably_ don't need to bump the clock here,
    // but we do it in order to potentially catch more failures.
    this.clock.tick(1000);
    equal(this.requests.length, 1);

    equal(menuItems.length, 2, 'there are two menu items');
    ok(menuItems.eq(0).find('a').is('.ui-state-focus'), 'first item in focus');
    equal(input.val(), 'abstinence', 'input completed');

    // Press TAB.
    input
        .simulate('keydown', {keyCode: $.ui.keyCode.TAB})
        .simulate('keypress', {keyCode: $.ui.keyCode.TAB})
        .simulate('keyup', {keyCode: $.ui.keyCode.TAB});
    this.clock.tick(1000);
    equal(this.requests.length, 1);

    equal(menuItems.length, 2, 'there are two menu items');
    ok(menuItems.eq(1).find('a').is('.ui-state-focus'), 'second item in focus');
    equal(input.val(), 'abcde', 'input completed');
 
    // Press TAB.
    // This will cycle back
    input
        .simulate('keydown', {keyCode: $.ui.keyCode.TAB})
        .simulate('keypress', {keyCode: $.ui.keyCode.TAB})
        .simulate('keyup', {keyCode: $.ui.keyCode.TAB});
    this.clock.tick(1000);
    equal(this.requests.length, 1);

    equal(menuItems.length, 2, 'there are two menu items');
    equal(menuItems.find('.ui-state-focus').length, 0, 'no item in focus');
    equal(input.val(), 'ab', 'input back to original');
   
    $('#the-node').tagbox('destroy');
});







