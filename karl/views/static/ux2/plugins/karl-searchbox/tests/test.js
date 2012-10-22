/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console setTimeout jQuery module test $ */
/*globals module test start stop expect equal deepEqual ok raises */
/*globals MockHttpServer JSON sinon */
/*globals escape unescape */


var log = function () {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


if (window.Mustache === undefined) {
    window.Mustache = {to_html: function () {}};
}

if (jQuery.fn.pushdownrenderer === undefined) {
    jQuery.fn.pushdownrenderer = function () {
        return this;
    };
}
 
module('karl-searchbox', {

    setup: function () {
        var self = this;
        $('#main').append(
            '<div id="the-top-bar">' +
                '<input id="the-input">' +
                '</input>' +
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
   
        function returnThis() {
            return this;
        }
        this.mockRenderer = sinon.stub($.fn, 'pushdownrenderer', returnThis);
    },

    teardown: function () {
        this.clock.restore();
        this.xhr.restore();
        this.mockMustache.verify();
        this.mockRenderer.restore();
        $('#main').empty();
    }

});


test("Create / destroy", function () {


    $('#the-input').searchbox({
        selectTopBar: '#the-top-bar'
    });

    $('#the-input').searchbox('destroy');

    ok(true);
});


test("Handles focus", function () {


    $('#the-input').searchbox({
        selectTopBar: '#the-top-bar'
    });

    equal(this.mockRenderer.callCount, 1);

    $('#the-input').focus();

    equal(this.mockRenderer.callCount, 4);

    $('#the-input').searchbox('destroy');

    ok(true);
});


