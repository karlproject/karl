
/* jshint globalstrict: true */
/* global document: true */

(function() {
  'use strict';

  // Browser detection, copied from:
  // https://github.com/jquery/jquery-migrate/blob/master/src/core.js
  function uaMatch(ua) {
    ua = ua.toLowerCase();
    var match = /(chrome)[ \/]([\w.]+)/.exec(ua) ||
      /(webkit)[ \/]([\w.]+)/.exec(ua) ||
      /(opera)(?:.*version|)[ \/]([\w.]+)/.exec(ua) ||
      /(msie) ([\w.]+)/.exec(ua) ||
      ua.indexOf('compatible') < 0 &&
      /(mozilla)(?:.*? rv:([\w.]+)|)/.exec(ua) ||
      [];
    return {
      browser: match[1] || '',
      version: match[2] || '0'
    };
  }

  // Show the status on the top of the page
  function showHtml(html) {
    window.onload = function() {
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
    var matched = uaMatch(navigator.userAgent);
    var isBadBrowser = matched.browser == 'msie' && parseInt(matched.version, 10) < 9;
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
