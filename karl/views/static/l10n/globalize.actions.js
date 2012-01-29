(function( window, undefined ) {

var Globalize;

if ( typeof require !== "undefined"
	&& typeof exports !== "undefined"
	&& typeof module !== "undefined" ) {
	// Assume CommonJS
	Globalize = require( "globalize" );
} else {
	// Global variable
	Globalize = window.Globalize;
}

Globalize.perform_actions = function() {

    $('.globalize-short-date').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'd',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-long-date').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'D',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-full-date').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'f',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-calendar-abbr').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'c',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-calendar-full').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'C',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-calendar-list').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'l',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-calendar-long').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            'L',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

    $('.globalize-date-time').each( function(i) {
        var d=Globalize.format(new Date($(this).text()),
            's',
            Globalize.culture(karl_client_data['date_format'])
        );
        $(this).text(d)
    });

};

}( this ));

$(document).bind('ready', Globalize.perform_actions);

