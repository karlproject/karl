(function (window, undefined) {

var Globalize;

if ( typeof require !== "undefined" &&
	typeof exports !== "undefined" &&
	typeof module !== "undefined" ) {
	// Assume CommonJS
	Globalize = require( "globalize" );
} else {
	// Global variable
	Globalize = window.Globalize;
}

Globalize.perform_actions = function(el) {
    // Setup dates inside el, or if el is not specified,
    // then inside the whole document.
    el = $(el);

    // when this is called on page load the element is of
    // type 'ready', which is of no use.
    if (el.attr('type') == 'ready' || el.size() == 0) { el = $(document); }

    $('.globalize-short-date', el).each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'd',
            Globalize.culture(head_data.date_format)
        );
        $(this).text(d);
    });

    $('.globalize-long-date', el).each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'D',
            Globalize.culture(head_data.date_format)
        );
        $(this).text(d);
    });

    $('.globalize-full-date', el).each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'f',
            Globalize.culture(head_data.date_format)
        );
        $(this).text(d);
    });


    // Handle timago also (yet, not localized, but once it happens,
    // it should happen from here)
    //
    // preserve previous timeago_js macro

    $('.timeago-date', el).timeago();

};

}( this ));

$(document).bind('ready', Globalize.perform_actions);

