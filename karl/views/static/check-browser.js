/* jshint globalstrict: true */
/* global document: true */

(function () {
    'use strict';

    /**
     * detect IE
     * returns version of IE or false, if browser is not Internet Explorer
     */
    function detectIE() {
        var ua = window.navigator.userAgent;

        var msie = ua.indexOf('MSIE ');
        if (msie > 0) {
            // IE 10 or older => return version number
            return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
        }

        var trident = ua.indexOf('Trident/');
        if (trident > 0) {
            // IE 11 => return version number
            var rv = ua.indexOf('rv:');
            return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
        }

        var edge = ua.indexOf('Edge/');
        if (edge > 0) {
            // IE 12 => return version number
            return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
        }

        // other browser
        return false;
    }

    // Show the status on the top of the page
    function showHtml(html) {
        window.onload = function () {
            var div = document.createElement("div");
            div.style.width = '100%';
            div.style.background = '#eddb33';
            div.style.color = 'black';
            div.style.padding = '0.75em';
            div.style.fontSize = '14px';
            div.style.zIndex = '99999';
            // position must be relative, otherwise on IE8 on the login
            // page the message will not be shown because another
            // absolutely positioned node covers it.
            div.style.position = 'relative';
            div.innerHTML = html;
            document.body.insertBefore(div, document.body.firstChild);
        };
    }

    function showStatus(/* arguments */) {
        // wrap to table for cross browser centering
        var html = Array.prototype.slice.call(arguments, 0).join(' ');
        showHtml([
                     '<table style="width: 100%; height: 30px;">',
                     '<tr>',
                     '<td style="text-align: center; vertical-align: middle;">',
                     html,
                     '</td>',
                     '</tr>',
                     '</table>',
                 ].join(' '));
    }

    var meta = document.getElementById('karl-browser-upgrade-url');
    var browser_upgrade_url = meta ? meta.getAttribute('content') || '' : '';
    var serviceSwitch = document.location.hash == '#bad-browser';
    if (browser_upgrade_url || serviceSwitch) {
        var matched = detectIE();
        var isBadBrowser = matched && matched < 9;
        // Show status if we have a bad browser,
        // or if the #bad-browser service switch hash is added to the url.
        // (Note: you may need to reload to see the effect.)
        if (serviceSwitch && browser_upgrade_url === '') {
            // If this is a testing, let's warn the tester that
            // not everything is all right.
            showStatus(
                'The browser compatibility check is not enabled',
                '(see browser_upgrade_url configuration option).'
            );
        } else if (isBadBrowser || serviceSwitch) {
            showStatus(
                'You are using an unsupported version of Internet Explorer.',
                'Please ',
                '<a href="' + browser_upgrade_url + '">',
                'click here to learn more</a>.'
            );
        }
    }

})();
