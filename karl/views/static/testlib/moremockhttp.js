
(function(){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

window.MoreMockHttpServer = function(handler) {
    if (handler) {
        this.handle = handler;
    }
    // if timed responses are set,
    // this remembers the active requests.
    this.set_timed_responses(false);
    this._active_requests = [];
    this.length = 0;
    // this can be used as a condition from handle
    // it can be a number, or even a dict of options
    this.set_server_state(0);
};
MoreMockHttpServer.prototype = {

    start: function() {
        var self = this;

        function Request() {
            this.onsend = function() {
                self._handle(this);
            };
            // methods needed for bypassing
            this.logmethod = function(name) {
                var orig = this[name];
                this[name] = function() {
                    // save this call to the action log
                    this.action_log.push([name, arguments]);
                    // call the original method
                    orig.apply(this, arguments);
                };
            };
            this.logreplay = function(on_request) {
                for (var i = 0; i < this.action_log.length; i++) {
                    var action = this.action_log[i];
                    on_request[action[0]].apply(on_request, action[1]);
                }
            };
            // remember actions for a possible bypass
            this.action_log = [];
            // Make some methods logged, so they can
            // be replayed on another (typically real)
            // request.
            this.logmethod('open');
            this.logmethod('setRequestHeader');
            this.logmethod('send');
            // do the init
            MockHttpRequest.apply(this, arguments);
        }
        Request.prototype = MockHttpRequest.prototype;
        
        // allow chaining, useful for bypass
        this.OriginalHttpRequest = window.XMLHttpRequest;
        window.XMLHttpRequest = Request;
    },

    stop: function() {
        window.XMLHttpRequest = this.OriginalHttpRequest;
    },

    set_timed_responses: function(timed_responses) {
        // if this is set true, responses can be timed
        // by calling
        //
        //      this.execute(n)
        //
        // otherwise, it happens immediately.
        //
        // This can be used to test async issues
        // and various race conditions.
        //
        this.timed_responses = timed_responses;
    },

    set_server_state: function(nr) {
        this._server_state = nr;
    },

    set_ajax_heartbeat: function(nr) {
        log('BBB: set_ajax_heartbeat is deprecated', 'please use set_server_state instead.',
            'Will be removed after 2011-05-01.') 
        this.set_server_state(nr);
    },

    execute: function(nr) {
        var callback = this._active_requests[nr].execute;
        // it should not execute twice
        this._active_requests[nr].execute = catch_request;
        var catch_request = function() {
            throw new Error('Mock request already executed');
        };
        // do it
        callback.call(this._active_requests[nr]);
    },

    // bypass and execute (timed requests)
    bypass: function(nr) {
        var callback = this._active_requests[nr].bypass;
        // it should not bypass twice
        this._active_requests[nr].bypass = catch_request;
        var catch_request = function() {
            throw new Error('Mock request already bypassed');
        };
        // do it
        callback.call(this._active_requests[nr]);
    },

    // active requests can be timed
    // for testing race conditions
    _handle: function(request) {
        var self = this;
        // Dress up the request. When we call execute,
        // we want the current values and not the then-values.
        request._server_state = this._server_state;
        request._handle = this.handle;
        request.execute = function() {
            if (this.readyState == this.UNSENT) {
                // Aborted? Good. :)
                return;
            }
            // call the part that generates the mock response
            this._handle.call(self, this, this._server_state);
        };
        request.bypass = function() {
            if (this.readyState == this.UNSENT) {
                // Aborted? Good. :)
                return;
            }
            // call the part that bypasses to a real request
            self._bypass.call(self, this);
        };
        // Decide if we want the response timed
        if (this.timed_responses) {
            // save the request so tests can reach it.
            this._active_requests.push(request);
            this.length = this._active_requests.length;
        } else {
            // Do the response immediately.
            request.execute();
        }
    },

    // Bypass to a real request
    _bypass: function(request) {
        // make a new request
        var r = new this.OriginalHttpRequest();
        // copy the onreadystatechange
        r.onreadystatechange = request.onreadystatechange;
        // aborting the request will abort the bypassed request
        request.abort = function() {
            r.abort();
        };
        // replay actions from the original request
        request.logreplay(r);
        // set back response into the new request,
        // needed for sync requests.
        request.responseText = r.responseText;
        request.responseXML = r.responseXML;
    },

    handle: function(request, server_state) {
        // Instances should override this.
    }
};

})();

