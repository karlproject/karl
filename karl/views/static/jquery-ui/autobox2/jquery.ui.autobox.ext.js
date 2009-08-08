/*
 * jQuery UI Autocomplete
 * version: 1.0 (1/2/2008)
 * @requires: jQuery v1.2 or later, dimensions plugin
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Copyright 2007 Yehuda Katz, Rein Henrichs
 */

(function($) {
  $.ui = $.ui || {};
  $.ui.autobox = $.ui.autobox || {};
  $.ui.autobox.ext = $.ui.autobox.ext || {};

  // create request manager
  var log;
  if (window.console) {
      log = console.log;
  } else {
      log = function() {};
  }
  var MiniRM = function(opt) {
    this.chainedGetJSON = opt.jsonhandler || $.getJSON;
    this.maxActive = opt.maxActive || 1;
    this.maxQueue = opt.maxQueue || 1;
    this.active = 0;
    this.queue = [];
  };
  $.extend(MiniRM.prototype, {
      getJSON: function(url, query, handler) {
        var self = this;
        var wrappedHandler = function(json) {
            self.active -= 1;
            self.log ('MiniRM IN', url, query);
            handler(json);
            var nextJob = self.queue.shift();
            if (nextJob !== undefined) {
                self.active += 1;
                self.log ('MiniRM POP/OUT', nextJob[0], nextJob[1]);
                self.chainedGetJSON.apply(null, nextJob);
            }
        };
        if (this.active < this.maxActive) {
            this.active += 1;
            this.log ('MiniRM OUT', url, query);
            this.chainedGetJSON(url, query, wrappedHandler);
        } else {
            if (this.queue.length == this.maxQueue) {
                var discardJob = this.queue.shift();
                this.log('MiniRM POP/DISCARD', discardJob[0], discardJob[1]);
            }
            this.queue.push([url, query, wrappedHandler]);
            this.log ('MiniRM PUSH', url, query);
        }
      },
      log: function(msg, url, query) {
        //log (msg, 'ACT=' + this.active, 'QUE=' + this.queue.length, url + "?" + query);
      }
  });
  var miniRM = new MiniRM({});

  $.ui.autobox.ext.ajax = function(opt) {
    var ajax = opt.ajax;
    return { getList: function(input, hash) {
      var val = input.val();
      var minQueryLength = this.options.minQueryLength;
      var minQueryNotice = this.options.minQueryNotice; 

      function tooShort(word, minQueryLength) {
        return minQueryLength && (! word || word.length < minQueryLength);
      }

      // filter words by short/long
      var words = val.replace(/\s+/, " ").split(" "), short = [], long = [];
      for (i = 0, j = words.length; i < j; i++) {
        var word = words[i];
        if (word == "") continue;
        tooShort(word, minQueryLength) ? short.push(word) : long.push(word);        
      }
      val = long.join(" ");

      // only send request if we have a long word
      if (long.length > 0) {
        miniRM.getJSON(ajax, "val=" + val, function(json) {
          if (hash) { 
            if (short.length > 0 && minQueryNotice) { 
              json.unshift(minQueryNotice); 
            }
            json = $(json).filter(function(){ return !hash[this.text]; });
            input.trigger("updateList", [json]);
          }
        });
        
      // only short words - show notice
      } else if (short.length > 0 && minQueryNotice) {
        input.trigger("updateList", [[minQueryNotice]]);
      }

    }};
  };

  $.ui.autobox.ext.templateText = function(opt) {
    var template = $.makeTemplate(opt.templateText, "<%", "%>");
    return { template: function(obj) { return template(obj); } };
  };

})(jQuery);
