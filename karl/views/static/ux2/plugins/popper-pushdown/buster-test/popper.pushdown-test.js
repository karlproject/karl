/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console setTimeout jQuery $ */
/*globals buster assert refute */
/*globals JSON sinon */


/*
var log = function () {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};
*/



// as sinon does not provide an api for this,
// we are obliged to throw this in ourselves.
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

// we need something here, else we can't mock it
if (window.Mustache === undefined) {
    window.Mustache = {
        to_html: function () {}
    };
}


// Browser tests

buster.testCase("A module", {
    "states the obvious": function () {
        assert(true);
    }
});

buster.testCase('popper-pushdowntab', {
    
    setUp: function () {
        var self = this;
        $('body').html(
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
            if (! requests) {
                return; // ???
            }
            requests.push(xhr);
        };
        // Make sure to deplete microtemplate cache in the head data
        window.head_data = {
        };
    },

    tearDown: function () {
        this.clock.restore();
        this.xhr.restore();
        this.mockMustache.restore();
        $('body').empty();
    },

    'standard': {

        setUp: function () {
            $('#the-link').pushdowntab({
                name: 'mypushdown',
                selectTopBar: '#the-top-bar',
                findCounterLabel: '.the-counter'
            });
            assert($('#popper-pushdown-mypushdown').length > 0);
            assert.equals($('#popper-pushdown-mypushdown').is(':visible'), 
                false);
        },

        tearDown: function () {
            $('#the-link').pushdowntab('destroy');
        },

        'Create / destroy': function () {
            assert(true);
        },

        'open it': function () {

            this.mockMustache.expects('to_html').once();

            $('#the-link').simulate('click');

            // Check what parameters were passed to the request.
            assert.equals(this.requests.length, 1);
            assert.equals(parseQuery(this.requests[0].url),
                {"needsTemplate": "true", 'ts': ''});

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

            this.mockMustache.verify();

            assert($('#popper-pushdown-mypushdown')
                .is(':visible'));
        },


        'close it': function () {

            // click to open it
            $('#the-link').simulate('click');

            // Check what parameters were passed to the request.
            assert.equals(this.requests.length, 1);
            assert.equals(parseQuery(this.requests[0].url),
                {"needsTemplate": "true", 'ts': ''});

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

            assert($('#popper-pushdown-mypushdown').is(':visible'));
            
            // click again to close it
            $('#the-link').simulate('click');

            // bump the time
            this.clock.tick(200);

            refute($('#popper-pushdown-mypushdown').is(':visible'));

        }


    }

});

