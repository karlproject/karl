

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
                {"count": 2, "snippet": "nondeleteable", "tag": "one"},
                {"count": 2, "snippet": "nondeleteable", "tag": "two"},
                {"count": 2, "snippet": "nondeleteable", "tag": "three"},
                {"count": 2, "snippet": "nondeleteable", "tag": "four"}
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
    var n = $('#the-node');

    n.tagbox({
    });

    n.tagbox('destroy');

    ok(true);

});


//
// XXX Plenty of tests missing here. TODO: Add them!
//


test("Autocomplete, basics", function() {
    var n = $('#the-node');

    // Specifying an autocompleteURL will enable autocomplete.
    n.tagbox({
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

    n.tagbox('destroy');

});


test("Autocomplete, tab", function() {
    var n = $('#the-node');

    // Specifying an autocompleteURL will enable autocomplete.
    n.tagbox({
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
        .simulate('keydown', {keyCode: $.ui.keyCode.DOWN})
        .simulate('keypress', {keyCode: $.ui.keyCode.DOWN})
        .simulate('keyup', {keyCode: $.ui.keyCode.DOWN});
    // ok... we _probably_ don't need to bump the clock here,
    // but we do it in order to potentially catch more failures.
    this.clock.tick(1000);
    equal(this.requests.length, 1);

    equal(menuItems.length, 2, 'there are two menu items');
    ok(menuItems.eq(0).find('a').is('.ui-state-focus'), 'first item in focus');
    equal(input.val(), 'ab', 'input not completed');

    // Press TAB.
    input
        .simulate('keydown', {keyCode: $.ui.keyCode.DOWN})
        .simulate('keypress', {keyCode: $.ui.keyCode.DOWN})
        .simulate('keyup', {keyCode: $.ui.keyCode.DOWN});
    this.clock.tick(1000);
    equal(this.requests.length, 1);

    equal(menuItems.length, 2, 'there are two menu items');
    ok(menuItems.eq(1).find('a').is('.ui-state-focus'), 'second item in focus');
    equal(input.val(), 'ab', 'input not completed');
 
    // Press TAB.
    // This will cycle back
    input
        .simulate('keydown', {keyCode: $.ui.keyCode.DOWN})
        .simulate('keypress', {keyCode: $.ui.keyCode.DOWN})
        .simulate('keyup', {keyCode: $.ui.keyCode.DOWN});
    this.clock.tick(1000);
    equal(this.requests.length, 1);

    equal(menuItems.length, 2, 'there are two menu items');
    equal(menuItems.find('.ui-state-focus').length, 0, 'no item in focus');
    equal(input.val(), 'ab', 'input back to original');
   
    n.tagbox('destroy');
});


function assert_tags(el, tags) {
    var res = [];
    $(el).find('a.tag').each(function () {
        res.push($(this).text());
    });
    deepEqual(res, tags);
}

function assert_tag_values(el, tag_values) {
    var res = [];
    $(el).find('li[data-tagbox-bubble]').each(function () {
        res.push($(this).data('tagbox-bubble'));
    });
    deepEqual(res, tag_values);
}

function assert_counters(el, counters) {
    var res = [];
    $(el).find('a.tagCounter').each(function () {
        res.push(Number($(this).text()));
    });
    deepEqual(res, counters);
}

function assert_personals(el, personals) {
    var res = [];
    $(el).find('a.tag').each(function () {
        res.push($(this).hasClass('personal'));
    });
    deepEqual(res, personals);
}

function assert_input_values(el, input_values) {
    var res = [];
    $(el).find('input[type="hidden"]').each(function () {
        res.push($(this).attr('value'));
    });
    deepEqual(res, input_values);
}

function assert_input_name(el, input_name) {
    var res = [];
    var input_names = [];
    $(el).find('input[type="hidden"]').each(function () {
        res.push($(this).attr('name'));
        input_names.push(input_name);
    });
    deepEqual(res, input_names);
}



test("Initial rendering of boxes", function() {
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 3, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "nondeleteable", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 3, 4]);
    assert_personals(n, [false, true, false]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['park']);

    n.tagbox('destroy');

});


test("Adding a tag", function() {
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 3, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "nondeleteable", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 3, 4]);
    assert_personals(n, [false, true, false]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['park']);

    // adding as string
    n.tagbox('addTag', 'umbrella');
    
    assert_tags(n, ["flyers", "park", "office", "umbrella"]);
    assert_tag_values(n, ["flyers", "park", "office", "umbrella"]);
    assert_counters(n, [2, 3, 4, 1]);
    assert_personals(n, [false, true, false, true]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['park', 'umbrella']);
     
    deepEqual(parseQuery(n.find('li[data-tagbox-bubble="umbrella"] .tagCounter').attr('href')),
	 {"tag": "umbrella", "docid": "-1352878729"},
         'The href of the tag counter contains the docid.'
    );

    // adding as dict
    n.tagbox('addTag', {value: 'v_chair', label: 'l_chair'});
    
    assert_tags(n, ["flyers", "park", "office", "umbrella", "l_chair"]);
    assert_tag_values(n, ["flyers", "park", "office", "umbrella", "v_chair"]);
    assert_counters(n, [2, 3, 4, 1, 1]);
    assert_personals(n, [false, true, false, true, true]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['park', 'umbrella', 'v_chair']);

    deepEqual(parseQuery(n.find('li[data-tagbox-bubble="v_chair"] .tagCounter').attr('href')),
	 {"tag": "v_chair", "docid": "-1352878729"},
         'The href of the tag counter contains the docid.'
    );

    n.tagbox('destroy');

});


test("Adding existing tag which is not ours", function() {
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 3, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "nondeleteable", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 3, 4]);
    assert_personals(n, [false, true, false]);

    n.tagbox('addTag', 'flyers');
    
    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [3, 3, 4]);
    assert_personals(n, [true, true, false]);

    deepEqual(parseQuery(n.find('li[data-tagbox-bubble="flyers"] .tagCounter').attr('href')),
	 {"tag": "flyers", "docid": "-1352878729"},
         'The href of the tag counter contains the docid.'
    );
    n.tagbox('destroy');

});


test("Adding existing tag which is ours", function() {
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 3, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "nondeleteable", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 3, 4]);
    assert_personals(n, [false, true, false]);

    n.tagbox('addTag', 'park');
    
    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 3, 4]);
    assert_personals(n, [false, true, false]);

    deepEqual(parseQuery(n.find('li[data-tagbox-bubble="flyers"] .tagCounter').attr('href')),
	 {"tag": "flyers", "docid": "-1352878729"},
         'The href of the tag counter contains the docid.'
    );

    n.tagbox('destroy');

});


test("Deleting a tag", function() {
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 1, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 4]);
    assert_personals(n, [false, true, true]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['park', 'office']);

    n.tagbox('delTag', 'park');
    
    assert_tags(n, ["flyers", "office"]);
    assert_counters(n, [2, 4]);
    assert_personals(n, [false, true]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['office']);

    n.tagbox('destroy');

});


test("Deleting a tag which others still have", function() {
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 1, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 4]);
    assert_personals(n, [false, true, true]);
    assert_input_name(n, 'tags');
    assert_input_values(n, ['park', 'office']);

    n.tagbox('delTag', 'office');
    
    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 3]);
    assert_personals(n, [false, true, false]);
    assert_input_name(n, 'tags');
    // essential check: input has disapeared.
    assert_input_values(n, ['park']);

    n.tagbox('destroy');

});


test("Deleting a tag which we don't have but others do (ignore)", function() {
    // (this won't really happen as the user cannot click here)
    var n = $('#the-node');

    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 1, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 4]);
    assert_personals(n, [false, true, true]);

    n.tagbox('delTag', 'flyers');
    
    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 4]);
    assert_personals(n, [false, true, true]);

    n.tagbox('destroy');

});


test("Deleting a tag which noone has (ignore)", function() {
    // (this won't really happen as the user cannot click here)
    var n = $('#the-node');
    
    n.tagbox({
        prevals: {
            "records": [
                {"count": 2, "snippet": "nondeleteable", "tag": "flyers"},
                {"count": 1, "snippet": "", "tag": "park"},
                {"count": 4, "snippet": "", "tag": "office"}
            ],
            "docid": -1352878729
        }
    });

    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 4]);
    assert_personals(n, [false, true, true]);

    n.tagbox('delTag', 'umbrella');
    
    assert_tags(n, ["flyers", "park", "office"]);
    assert_counters(n, [2, 1, 4]);
    assert_personals(n, [false, true, true]);

    n.tagbox('destroy');

});

