/*
 * Globalize Cultures
 *
 * http://github.com/jquery/globalize
 *
 * Custom culture files for Karl
 */

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

Globalize.addCultureInfo( "en-US", "default", {
	name: "en-US",
	englishName: "English (United States)",
	calendars: {
		standard: {
			firstDay: 1,
			patterns: {
				d: "MM/dd/yyyy",
				D: "MMMM dd yyyy",
				t: "HH:mm",
				T: "HH:mm:ss",
				f: "dddd, MMMM dd yyyy HH:mm",
				F: "dddd, MMMM dd yyyy HH:mm:ss",
                l: "ddd, MMM d",
                L: "dddd, MMMM d",
                c: "ddd M/d",
                C: "dddd M/d",
				M: "MMMM dd",
				Y: "MMMM yyyy"
			}
		}
	}
});

Globalize.addCultureInfo( "en-GB", "default", {
	name: "en-GB",
	englishName: "English (United Kingdom)",
	nativeName: "English (United Kingdom)",
	numberFormat: {
		currency: {
			pattern: ["-$n","$n"],
			symbol: "£"
		}
	},
	calendars: {
		standard: {
			firstDay: 1,
			patterns: {
				d: "dd/MM/yyyy",
				D: "dd MMMM yyyy",
				t: "HH:mm",
				T: "HH:mm:ss",
				f: "dddd, dd MMMM yyyy HH:mm",
				F: "dddd, dd MMMM yyyy HH:mm:ss",
                l: "ddd, d MMM",
                L: "dddd, d MMMM",
                c: "ddd d/M",
                C: "dddd d/M",
				M: "dd MMMM",
				Y: "MMMM yyyy"
			}
		}
	}
});

}( this ));

