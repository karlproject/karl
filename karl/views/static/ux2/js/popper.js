/*jslint browser: true */
/*global jQuery: false, console: false, window: false, Modernizr:false, yepnope: false, radarlink: true, Mustache: false */

$(function () {
    // Slide down the global site-wide notification
    setTimeout( 
        function () {
            $('.globalNotification').slideDown('medium');
        }, 1000);
}(jQuery));

/* Gumball javascript */

(function ($) {

    if(Modernizr.prefixed('boxSizing')) {
        $('html').addClass('boxsizing');
    }

    var log = function () {
            if (window.console && console.log) {
                // log for FireBug or WebKit console
                console.log(Array.prototype.slice.call(arguments));
            }
        },
        initWidth = document.documentElement.clientWidth;


    var head_data = window.head_data || {};
    // need urls
    var appUrl = window.head_data.app_url;


    // polyfill for the borwsers not supporting the 'placeholder' attribute
    if (!Modernizr.input.placeholder) {
        $("input, textarea").each(function () {
            if ($(this).val() === "" && $(this).attr("placeholder") !== "") {
                $(this).val($(this).attr("placeholder"));
                $(this).focus(function () {
                    if ($(this).val() === $(this).attr("placeholder")) {
                        $(this).val("");
                    }
                });
                $(this).blur(function () {
                    if ($(this).val() === "") {
                        $(this).val($(this).attr("placeholder"));
                    }
                });
            }
        });

        $("form").submit(function () {
            $("input, textarea").each(function () {
                if ($(this).attr("placeholder") !== "") {
                    if ($(this).val() === $(this).attr("placeholder")) {
                        $(this).val("");
                    }
                }
            });
        });
    }
    
    // Add nice-looking spans to cover the standard <select> elements in the search
    if(!$('html').hasClass('oldie')) {
        $('nav.search').find('select').each(function () {
            var $that = $(this);
            $that.after('<span class="fieldCoverage">' + this[0].text + '</span>');
            $that.change(function () {
                $that.prev().text($('option:selected', $that).text());
            });
            
        });    
    }
       
    // bind community filter click event to location change
    $('#filter-options input').click(function() {window.location=this.value;});
 
    $('nav.search select').change(function () {
        $(this).next().text($('option[value="' +this.value + '"]', this).text());
    });
    
    $('#tags').tagbox({
        autocompleteURL: appUrl + '/tagbox_autocomplete.json' 
    });

    // Global notification dismissing
    $('.dismissNotification').click(function () {
        $(this).parent().slideUp('fast');
    });
    
    
    // Reveal the search options on :focus
    var $fst = $('form#search-form fieldset');
    $fst.find('.search-site-box')
        .focusin(function () {
            if (Modernizr.csstransitions && !$fst.hasClass('opened')) {
                $fst.addClass('opened');
            } else if (!Modernizr.csstransitions && !$fst.hasClass('opened')){
                $fst.animate({
                    marginTop: '.2em'
                }, 4000);            
            }
        });

    

    // --
    // Wire chatterpanel in header
    // --
    
    $(function() {


        var head_data = window.head_data || {};
        // need urls
        var appUrl = window.head_data.app_url;

        // bind the chatter pushdown
        $('a#chatter')
            .pushdowntab({
                name: 'chatter',
                dataUrl: appUrl + '/chatter.json',
                selectTopBar: '#top-bar',
                findCounterLabel: '.messageCounter'
            });


        // chatter options toggling
        var chatterOptionsPanel = $('.chatter-options-link')
            .live('click', function(e) {
                var el = $(this);
                var panel = el.parent().find('.chatter-options-panel');
                if (panel.css('opacity') != '1') {
                    panel.css('opacity', '1');
                } else {
                    panel.css('opacity', '0');
                }
                e.preventDefault();
            });


        // bind the radar pushdown
        // XXX still have to clean up what exactly fullWindow=true is for, in this one
        $('a#radar')
            .pushdowntab({
                name: 'radar',
                dataUrl: appUrl + '/radar.json',
                selectTopBar: '#top-bar',
                findCounterLabel: '.messageCounter'
            });


        // Start the central polling for notifications.
        $(document).notifier({
            url: appUrl + '/notifier.json',
            polling: 15
        });


    });


} (jQuery));
