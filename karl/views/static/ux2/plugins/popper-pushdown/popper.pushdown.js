
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console */
/*globals setTimeout clearTimeout setInterval */ 
/*globals jQuery Mustache */


(function ($) {

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    function isoDate(d) {
        // XXX note, this is not completely correct, one would need
        // to pad out numbers to 2 digits such as 3 -> 03
        // ... but it server our purposes well in the current form.
        return d.getUTCFullYear() + '-' + (d.getUTCMonth() + 1) +
            '-' + d.getUTCDate() + 'T' + d.getUTCHours() + ':' +
            d.getUTCMinutes() + ':' + d.getUTCSeconds();
    }

    
    $.widget('popper.pushdowntab', {
        // This component is responsible for managing the tab of
        // the pushdown. Clicking on the tab opens and closes the
        // pushdown, the click event will be bound here.
        //
        // The pushdown panel component is encapsulated
        // and created by pushdowntab, so it needs not to be touched
        // directly.
        //
        // Another responsibility of this widget is to handle the
        // update of the "recent items counter", in cooperation
        // with the popper.notifier component that broadcasts the
        // notifications streamed from the server, as well as remembers
        // the last update timestamp for each notification source.

        options: {
            name: null,  // a unique name that identifies this pushdown
            dataUrl: null, // url for ajax. It takes a parameter which tells
                                 // if we need the template.
                                 //
            //polling: 120,  // polling time of data in seconds (!!)
            polling: 25,  // polling time of data in seconds (!!)
            selectTopBar: null,  // selector for the top bar.
                                 // The panel will be inserted after this.
            findCounterLabel: null,   // find the label for the recent items
                                 //  (inside the widget's bound element)

            fullWindow: false
            //beforeShow: function(evt) {},    // onBeforeShow event handler
            //show: function(evt) {},    // onShow event handler
            //beforeHide: function(evt) {},    // onBeforeHide event handler
            //hide: function(evt) {}    // onHide event handler
            //
            //render: function(evt) {}    // onRender event handler
        },

        getCounter: function () {
            var cnt = this.counterlabel.text();
            cnt = Math.floor(Number(cnt) || 0);
            if (cnt < 0) {
                cnt = 0;
            }
            return cnt;
        },

        setCounter: function (cnt) {
            this.counterlabel.text('' + cnt);
            if (cnt > 0) {
                this.counterlabel.show();
            } else {
                this.counterlabel.hide();
            }
        },

        startAjax: function (callback) {
            // Start the ajax, then if done, call the callback.
            var self = this;

            // Do we need the template? Only, if it's not yet
            // available for us.
            var needsTemplate = (this._getTemplate() === undefined);

            if (this.xhr) {
                this.xhr.abort();
            }
            this.xhr = $.ajax({
                url: this.options.dataUrl,
                data: {
                    needsTemplate: needsTemplate,
                    ts: this.tsIso
                },
                type: 'GET'
            });

            this.panel.trigger('pushdowntabajaxstart');

            this.xhr
                .done(function (result) {
                    self._ajaxDone(result, callback);
                })
                .error($.proxy(this._ajaxError, this));
        },

        openPanel: function () {
            // Open the panel once ajax results are available

            // Reset the counter.
            // We also have to remember to ask the next update
            // starting from this moment.
            this.setCounter(0);
            var now = new Date();
            $(document).trigger('notifierSetTs', [this.options.name, now]);
            
            // Open the pushdown
            this.panel.pushdownpanel('show');

            this.isPolling = false;
        },


        // --
        // private parts
        // --
        
        _create: function () {
            var self = this;
            // initialize the panel
            this.panel = $('<div></div>')
                .attr('id', 'popper-pushdown-' + this.options.name)
                .insertAfter($(this.options.selectTopBar))
                .pushdownpanel({
                    fullWindow: this.options.fullWindow,
                    selectTopBar: this.options.selectTopBar,
                    beforeShow: $.proxy(this._onBeforeShow, this),
                    show: $.proxy(this._onShow, this),
                    beforeHide: $.proxy(this._onBeforeHide, this),
                    hide: $.proxy(this._onHide, this)
                })
                .pushdownanimator({

                });
            // make us clickable
            this.element.click($.proxy(this._onClick, this));
            // markers
            this.counterlabel =
                this.element.find(this.options.findCounterLabel);
            // Listen for counter updates
            $(document).bind('notifierUpdate',
                $.proxy(this._onNotifierUpdate, this));
            // Empty request
            this.xhr = null;
            this.isPolling = false;
            this.timer = null;
            this.tsIso = '';    // iso timestamp of last data update
        },

        _destroy: function () {
            if (this.xhr) {
                this.xhr.abort();
            }
            this.xhr = null;
            if (this.timer) {
                clearTimeout(this.timer);
            }
            this.timer = null;
            this.panel.pushdownpanel('destroy');
            this.panel.pushdownanimator('destroy');
            this.element.unbind('click');
            $(document).unbind('notifierUpdate',
                $.proxy(this._onNotifierUpdate, this));
        },

        // handle click on tab link
        _onClick: function (evt) {
            // Only act if we are hidden, and not polling.
            // If we are polling: ignore the click gracefully
            // If we are visible: do the show, but ignore the ajax
            // If we are transitioning: do the toggle as it will be ignored
            var isHidden = this.panel.pushdownpanel('isHidden');
            if (isHidden && ! this.isPolling) {
                this.isPolling = true;

                // Start the ajax, then when it's over , open the panel
                this.startAjax($.proxy(this.openPanel, this));

            } else {
                // Just toggle it.
                this.panel.pushdownpanel('toggle');
            }
            return false;
        },

        _getTemplate: function () {
            var head_data = window.head_data || {};
            var microtemplates = head_data.microtemplates || {};
            var template = microtemplates[this.options.name];
            return template;
        },

        _setTemplate: function (template) {
            var head_data = window.head_data = window.head_data || {};
            var microtemplates = head_data.microtemplates = 
                    head_data.microtemplates || {};
            microtemplates[this.options.name] = template;
        },

        // handle ajax response
        _ajaxDone: function (result, callback) {
            var self = this;
            if (! result || result.error) {
                // Allow IE to return no payload as success,
                // (to prepare for foul outcomes such as aborts on the
                // non standard browsers),
                // as well as, our view can return {error='Display me!'} to
                // signify an express error condition inside a 200 response.
                return this._ajaxError(this.xhr, result.error || 'FATAL');
            }

            this.panel.trigger('pushdowntabajaxdone');

            var template = result.microtemplate;
            if (template !== undefined) {
                // We were sent a template. So, use it, and cache it too.
                this._setTemplate(template);
            } else {
                template = this._getTemplate();
            }

            // The server can signal "no need for update at all",
            // with sending data=null. We only act if data is not null.
            if (result.data !== null) {
                // Make sure we have the template
                if (template === undefined) {
                    throw new Error('popper.pushdown: "' + this.options.name +
                        '" template does not exist in ' +
                        'head_data.microtemplates.');
                }
                // Render the template.
                log('Rendering pushdown ' + this.options.name);
                var html = Mustache.to_html(template, result.data);
                this.panel.html(html);
                // Remember the time of the succesful update.
                this.tsIso = result.ts || '';

                this._trigger('render', null, result.state);
            }

            // Continuation. For example, if ajax is started when the user
            // clicked to show the pushdown, then after the ajax has arrived,
            // we actually want to open the panel with the new content.
            if (callback) {
                callback();
            }

        },

        // handle ajax response
        _ajaxError: function (xhr, textStatus) {
            this.panel.trigger('pushdowntabajaxerror');
            log('Pushdown ajax: We will do something with this, ' + textStatus);
        },

        // handle panel event
        _onBeforeShow: function (evt) {
            this._trigger('beforeShow', evt);
            // mark parent with class selected
            this.element.parent('li').addClass('active');
        },

        // handle panel event
        _onShow: function (evt) {
            this._trigger('show', evt);
            // Start polling for data update
            this.timer = setInterval(
                $.proxy(this._poll, this),
                this.options.polling * 1000
            );
        },

        // polling
        _poll: function () {
            // Start the ajax
            log('polling pushdown data ' + this.options.name + '...');
            this.startAjax(null);
        },

        // handle panel event
        _onBeforeHide: function (evt) {
            if (this.timer) {
                clearTimeout(this.timer);
            }
            this._trigger('beforeHide', evt);
        },

        // handle panel event
        _onHide: function (evt) {
            // mark parent with class unselected
            this.element.parent('li').removeClass('active');
            this._trigger('hide', evt);
        },

        // handle notifier event
        _onNotifierUpdate: function (evt, updates) {
            var info = updates[this.options.name];
            // Is there an update that belongs to me?
            if (info !== undefined) {
                log('pushdown ' + this.options.name +
                    ' updating with: ' + info.cnt);
                // What is the state currently?
                var panel = this.panel.data('pushdownpanel');
                if (panel.state == panel._STATES.HIDDEN ||
                        panel.state == panel._STATES.TO_HIDDEN) {
                    // Hidden state: add the counter, and update.
                    var counter = this.getCounter();
                    counter += info.cnt;
                    this.setCounter(counter);
                }
                // (Visible state. Nothing to do. In this case:
                // we will reset when we go to hidden.)
            }
        }


    });


    $.widget('popper.pushdownpanel', {
        // Pushdown animation
        // This component is responsible for showing and hiding
        // the "pushdown" panel,
        // animating it, and updating its content. 

        options: {
            fullWindow: true,
            selectTopBar: null  // selector for the top bar.
                // It is _only_ used if fullWindow is false,
                // to calculate height for the pushdown.
                // XXX, could we do without this?

            //beforeShow: function(evt) {},    // onBeforeShow event handler
            //show: function(evt) {},    // onShow event handler
            //beforeHide: function(evt) {},    // onBeforeHide event handler
            //hide: function(evt) {}    // onHide event handler
        },

        show: function (callback) {
            var self = this;
            if (this.state != this._STATES.HIDDEN) {
                // Ignore it if we are not showable.
                if (callback) {
                    callback();
                }
            } else {
                // Show it.
                this.state = this._STATES.TO_VISIBLE;
                this._trigger('beforeShow', null);
                this.element.show();
                var height;
                // XXX Will need some cleanup here
                // XXX to produce desired height in a solid way.
                if (this.options.fullWindow) {
                    height = ($(window).height() - 50) - 
                        ($(this.options.selectTopBar).height() * 2);
                } else {
                    this.element.css('height', '100%');
                    height = this.element.height();
                }
                this.element.height(0);
                this.element
                    .animate({
                        height: height
                    }, 350, function () {
                        self.state = self._STATES.VISIBLE;
                        // In the end, we have to remove the height attribute
                        // that we just set above.
                        self.element.css('height', '');
                        if (callback) {
                            callback();
                        }
                        self._trigger('show', null);
                    });
                
            }
            // allow chaining
            return this;
        },

        hide: function (callback) {
            var self = this;
            if (this.state != this._STATES.VISIBLE) {
                // Ignore it if we are not hidable.
                if (callback) {
                    callback();
                }
            } else {
                // Hide it.
                this.state = this._STATES.TO_HIDDEN;
                this._trigger('beforeHide', null);
                this.element
                    .animate({
                        height: 0
                    }, 150, function () {
                        self.state = self._STATES.HIDDEN;
                        self.element.hide();
                        if (callback) {
                            callback();
                        }
                        self._trigger('hide', null);
                    });
            }
            // allow chaining
            return this;
        },

        toggle: function (callback) {
            if (this.isVisible()) {
                this.hide(callback);
            } else if (this.isHidden()) {
                this.show(callback);
            } else {
                // Ignore it if we are transitioning.
                if (callback) {
                    callback();
                }
            }
            // allow chaining
            return this;
        },

        isHidden: function () {
            return (this.state == this._STATES.HIDDEN);
        },

        isVisible: function () {
            return (this.state == this._STATES.VISIBLE);
        },


        // --
        // private parts
        // --
        

        _STATES: {
            HIDDEN: 0,
            TO_VISIBLE: 1,
            VISIBLE: 2,
            TO_HIDDEN: 3
        },

        _create: function () {
            var self = this;
            // initialize the content to hidden
            this.state = this._STATES.HIDDEN;
            this.element.hide();
            // If any other pushdown opens, we have to close.
            // So, we listen on the document where all events will bubble up.
            $(document).bind('pushdownpanelbeforeshow',
                $.proxy(this._onBeforeShowAny, this));
        },

        _destroy: function () {
            $(document).unbind('pushdownpanelbeforeshow',
                $.proxy(this._onBeforeShowAny, this));
        },

        _onBeforeShowAny: function (evt) {
            // Is this the event that we ourselves have triggered?
            if (evt.target == this.element[0]) {
                // Right, don't close ourselves, as we are the one opening
                return;
            }
            // Some other pushdown opened, so close me.
            this.hide();
        }

    });


    $.widget('popper.notifier', {
        // A singleton component that ought to be bound to the document.
        // It fetches all notifications from the server, and broadcasts
        // the notifications streamed from the server. It also remembers
        // the last update timestamp for each notification source.

        options: {
            url: null,    // url for ajax
            polling: 120  // polling time in seconds (!!)
        },


        // --
        // private parts
        // --
        
        _create: function () {
            var self = this;
            // Start the timer
            this.timer = setInterval(
                $.proxy(this._poll, this),
                this.options.polling * 1000
            );
            // Empty request
            this.xhr = null;
            // the recent updates
            this.updates = {};

            // listen to an event to set the timestamp
            $(document).bind('notifierSetTs',
                $.proxy(this._onSetTs, this));
        },

        _destroy: function () {
            clearTimeout(this.timer);
            if (this.xhr) {
                this.xhr.abort();
            }
            this.xhr = null;
            $(document).unbind('notifierSetTs',
                $.proxy(this._onSetTs, this));
        },

        // timed handler
        _poll: function () {
            if (this.xhr) {
                this.xhr.abort();
            }
            this.xhr = $.ajax({
                url: this.options.url,
                data: this.updates,
                type: 'GET'
            });
            this.xhr
                .done($.proxy(this._ajaxDone, this))
                .error($.proxy(this._ajaxError, this));
        },

        // Allows the pushdown to set their ts if they want
        // this means a pushdown is up-to-date till this moment.
        _onSetTs: function (evt, name, d) {
            log('setTs', name, d);
            // Update the timestamp for a given date.
            this.updates[name] = isoDate(d);
        },


        // handle ajax response
        _ajaxDone: function (result) {
            var self = this;
            if (! result || result.error) {
                // Allow IE to return no payload as success,
                // (to prepare for foul outcomes such as aborts on the
                // non standard browsers),
                // as well as, our view can return {error='Display me!'} to
                // signify an express error condition inside a 200 response.
                return this._ajaxError(this.xhr, result.error || 'FATAL');
            }
            // Remember our recent updates.
            $.each(result, function (name, value) {
                self.updates[name] = value.ts;
            });
            // Notify everyone who is interested.
            $(document).trigger('notifierUpdate', [result]);
        },

        // handle ajax response
        _ajaxError: function (xhr, textStatus) {
            log('Notifier ajax: We will do something with this, ' + textStatus);
        }

    });




    $.widget('popper.pushdownanimator', {
        // Pushdown animation for ajax
        // This component is responsible for showing the ajax progress,
        // and 
        // animating it, and updating its content. 

        options: {
            selectUpdating: '.updating',
            selectProblem: '.houstonWeHaveAProblem'
        },

        _create: function () {
            this.element.bind('pushdowntabajaxstart',
                $.proxy(this._onAjaxStart, this));
            this.element.bind('pushdowntabajaxdone',
                $.proxy(this._onAjaxDone, this));
            this.element.bind('pushdowntabajaxerror',
                $.proxy(this._onAjaxError, this));
        },

        _destroy: function () {
            this.element.unbind('pushdowntabajaxstart',
                $.proxy(this._onAjaxStart, this));
            this.element.unbind('pushdowntabajaxdone',
                $.proxy(this._onAjaxDone, this));
            this.element.unbind('pushdowntabajaxerror',
                $.proxy(this._onAjaxError, this));
        },

        _onAjaxStart: function (evt) {
            this.element.find(this.options.selectUpdating)
                .stop(true, true)
                .animate({
                    opacity: '1'
                }, 100);
        },

        _onAjaxStop: function (evt) {
            this.element.find(this.options.selectUpdating)
                .stop(true, true)
                .animate({
                    opacity: '0'
                }, 100);
        },

        _onAjaxDone: function (evt) {
            this._onAjaxStop(evt);
        },

        _onAjaxError: function (evt) {
            this._onAjaxStop(evt);
            this.element.find(this.options.selectProblem)
                .fadeIn(100);
        }

    });





})(jQuery);
