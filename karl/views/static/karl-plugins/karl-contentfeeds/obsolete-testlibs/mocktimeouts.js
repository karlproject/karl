/**
 * mocktimeouts.js
 *
 * Copyright 2010, Balazs Ree <ree@greenfinity.hu>
 * Released under LGPL License.
 *
 */


// make it conditional on the presence of mocktimeouts_pre.js.
if (window._saved_setTimeout && window._saved_clearTimeout) {
    // Hook to methods saved from mocktimeouts_pre.js
    // needed for correct operation on IE
    // it directs all calls through window.X
    function setTimeout(f, millis) {
        return window._saved_setTimeout(f, millis);
    };
    function clearTimeout(nr) {
        return window._saved_clearTimeout(nr);
    };
} else if (/msie/i.test(navigator.userAgent) && !/opera/i.test(navigator.userAgent)) {
    // no mocktimeouts_pre.js: it fails on all IE versions. Warn about this.
    throw Error('To use mocktimeouts.js on IE, you must include mocktimeouts_pre.js before.');
};


(function(){

window.MockTimeouts = function() {
    this.init.apply(this, arguments);
};
MockTimeouts.prototype = {

    // hooks for mocktimeout_pre.js
    saved_setTimeout: window.setTimeout,
    saved_clearTimeout: window.clearTimeout,

    init: function() {
        this._callbacks = [];
        this.length = 0;
        this.hooked = false;
    },

    _push: function(item) {
        this._callbacks.push(item);
        this.length = this._callbacks.length;
    },

    start: function() {
        var self = this;
        if (this.hooked) {
            // already started.
            return;
        }
        this.hooked = true;
        this._save_setTimeout = window.setTimeout;
        this._save_clearTimeout = window.clearTimeout;
        window.setTimeout = function(f, millis) {
            var callback = function() {
                if (typeof f == 'string') {
                    eval(f);
                } else {
                    f();
                }
            };
            self._push(callback);
            return self.length - 1;
        };

        window.clearTimeout = function(nr) {
            var callback = function() {};
            self._callbacks[nr] = callback;
        };
        
    },

    stop: function() {
        if (! this.hooked) {
            // Already stopped.
            return;
        }
        this.hooked = false;
        window.setTimeout = this._save_setTimeout;
        window.clearTimeout = this._save_clearTimeout;
    },

    execute: function(nr) {
        var callback = this._callbacks[nr];
        // it should not execute twice
        this._callbacks[nr] = catch_callback;
        var catch_callback = function() {
            throw new Error('Mock timer already executed');
        };
        // do it
        callback();
    }

};


})();


