
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

$.widget('karl.karlcontentfeeds', {

    options: {
        selectTimeAgo: 'abbr.timeago',
        ajax_url: '',
        filter: ''
    },

    _create: function() {
        var self = this;

        // set initial state
        this._templates = {};
        this._summary_info = {};
        this._gen_feed_url();
        // Valid states are: 'on', 'off', 'polling', 'error'
        this._ajax_state = 'on';
        // Base state can be 'on' or 'off',
        // we use to return to after 'polling'.
        this._ajax_base_state = this._ajax_state;

    },

    destroy: function() {
        $.Widget.prototype.destroy.call( this );
        // be paranoid about IE memory leaks
        this._active_request && this._active_request.abort();
        this._active_request = null;
    },

    // reset the state of the widget
    start_over: function() {
        // delete the content
        this.element.empty();
        // reset the summary state
        this._summary_info = {};
        this._gen_feed_url();
        
        // dump active requests at this point
        this._active_request && this._active_request.abort();
        // re-set the throbber
        this.setAjaxState(this._ajax_base_state, {notify: true});

        // trigger a change
        this.element.trigger('changed.karlcontentfeeds', [this._summary_info]);
    },

    get_items: function (d) {
        // Custom version of getJSON, with error handling, making sure
        // only one request is active at a time.
        var self = this;
        d = d || {};
        // if d.force is true, the query will be done also in 'off'

        // Parse state and decide whether to issue request.  If we are
        // 'polling', or 'error', bail out.
        var states = ['polling', 'error'];
        if (! d.force) {
            states.push('off');
        }
        if (jQuery.inArray(self._ajax_state, states) > -1) {
            log('bailout: ' + self._ajax_state);
            return;
        };

        self.setAjaxState('polling', {notify: true});
        this._active_request = jQuery.ajax({
                type: "GET",
                url: this._summary_info.feed_url,
                success: function(data) {
                    // XXX It seems, that IE bumps us
                    // here on abort(), with data=null.
                    if (data != null) {
                        self._ajaxSuccess(data);
                    }
                },
                error: function(xhr, textStatus, errorThrow) {
                    self._ajaxError(xhr, textStatus, errorThrow);
                },
                dataType: 'json'
        });

        return this._active_request;
    },

    _getTemplate: function (key) {
        // Pre-compile and cache templates
        var self = this;

        var template = self._templates[key];
        if (template == null) {
            template = tmpl(key);
            self._templates[key] = template;
        }

        return template;
    },

    _ajaxSuccess: function (data) {
        // Bind some vars
        var self = this;

        var last_gen = data[0];
        var last_index = data[1];
        var earliest_gen = data[2];
        var earliest_index = data[3];
        var rows = data[4];
        var row_template = this._getTemplate('item_row');

        $.each(rows.reverse(), function (key, row) {
            var flavor_template = self._getTemplate(row.flavor);
            row.flavor = flavor_template({item: row});
            $(row_template({item: row}))
                .prependTo(self.element)
                .find(self.options.selectTimeAgo).timeago();
        });

        var i = this._summary_info;

        // Animate new items
        // but only, if this is not the first time.
        if (i.earliest_gen !== undefined) {
            this._animate(rows.length);
        }

        // update summary info
        if (i.earliest_gen !== undefined) {
            earliest_gen = Math.min(i.earliest_gen, earliest_gen);
            earliest_index = Math.min(i.earliest_index, earliest_index);
        };
        var now = this._now(); 
        this._summary_info = {
            last_gen: last_gen,
            last_index: last_index,
            earliest_gen: earliest_gen,
            earliest_index: earliest_index,
            last_update: now
        };
        this._gen_feed_url();

        // set the ajax state to the base state
        // but only if it's not already "off", in this
        // case just leave it "off"
        if (this._ajax_state != this._ajax_base_state) {
            this.setAjaxState(this._ajax_base_state, {notify: true});
        }

        // trigger a change
        this.element.trigger('changed.karlcontentfeeds', [this._summary_info]);
    },

    _animate: function(nr) {
        
        // sum the full height, to see how large we need to go.
        // (XXX hmmm... should there be a better way?)
        var full_height = 0;
        this.element.children().each(function(i) {
            if (i == nr) {
                // stop iteration after first nr items
                return false;
            }
            full_height += $(this).outerHeight(true);
        });

        // wrapper is needed for overflow
        // make sure element has no clear itself,
        // because it breaks the animation.
        var clear = this.element.css('clear'); 
        var wrapper = $('<div></div>')
            .css({overflow: 'hidden', 'clear': clear})
        this.element
            .wrap(wrapper)
            .css({marginTop: -full_height, 'clear': 'none'});

        // animate the new items
        // from the negative top margin, to zero
        this.element.animate({marginTop: 0}, {
            queue: false,
            duration: 4 * full_height, // speed proportional with nr of items.
            complete: function() {
                // when finished: remove the wrapper
                wrapper.replaceWith(self.element);
            }
        });
    },

    _gen_feed_url: function() {
        // calculate the URL to be used on next JSON request
        // and store it in summary_info
        var query = {};
        var info = this._summary_info;
        // has there been a recent query?
        if (info.last_gen !== undefined) {
            query.newer_than =  info.last_gen + ':' + info.last_index;
        }
        // is there a filter?
        if (this.options.filter) {
            query.filter = this.options.filter;
        }
        var query_string = $.param(query);
        info.feed_url = 
            this.options.ajax_url + (query_string && '?') + query_string;
    },

    summary_info: function() {
        // return the summary info
        return this._summary_info;
    },

    _now: function() {
        return new Date().toString();
    },
    
    _ajaxError: function (xhr, textStatus, errorThrown) {
        log('error: ' + textStatus);

        var errormsg = textStatus + ": " + xhr.statusText;
        this.setAjaxState('error', {errormsg: errormsg, notify: true});
    },

    setFilter: function (filter) {
        // store the value
        this.options.filter = filter;
        // start over
        this.start_over();
        // get the initial items
        // forced, means even in 'off' state.
        this.get_items({force: true});
    },

    setAjaxState: function (newstate, d) {
        // Set state and possibly update UI
        log('Changing state from "' + this._ajax_state + 
                    '" to "' + newstate + '"');
        this._ajax_state = newstate;
        // base state is either on or off
        if (newstate == 'on' || newstate == 'off') {
            this._ajax_base_state = newstate;
        }

        if (d && d.notify) {
            // Trigger only if we are calling.
            // (to avoid circular events)
            this.element.trigger('ajaxstatechanged.karlcontentfeeds', [newstate, d.errormsg]);
        }

    }

});

$.widget('karl.karlcontentfeeds_info', {

    options: {
        selectLastUpdate: '.last-update',
        selectLastGen: '.last-gen',
        selectLastIndex: '.last-index',
        selectFeedUrl: '.feed-url'
    },

    _create: function() {
        // locate markers where we will update
        this.lastUpdate = this.element.find(this.options.selectLastUpdate);
        this.lastGen = this.element.find(this.options.selectLastGen);
        this.lastIndex = this.element.find(this.options.selectLastIndex);
        this.feedUrl = this.element.find(this.options.selectFeedUrl);
    },

    //destroy: function() {
    //    $.Widget.prototype.destroy.call( this );
    //},

    update: function(value) {
        this.lastGen.text(value.last_gen);
        this.lastIndex.text(value.last_index);
        this.lastUpdate.text(value.last_update);
        this.feedUrl
            .text(value.feed_url)
            .attr('href', value.feed_url);
    }

});


$.widget('karl.karlcontentfeeds_polling', {

    options: {
        selectInfoButton: '#polling-info',
        selectDetailsInfo: '.polling-details.info',
        selectError: '.polling-details.errormessage',
        selectErrorDetails: '#kf-errordetail',
        selectCloseButton: '.close',
        selectIndicator: '#poll-indicator'
    },

    _create: function() {
        var self = this;

        // locate markers where we will update
        this.infoButton = this.element.find(this.options.selectInfoButton);
        this.detailsInfo = this.element.find(this.options.selectDetailsInfo);
        this.error = this.element.find(this.options.selectError);
        this.errorDetail = this.element.find(this.options.selectErrorDetail);
        this.closeButton = this.element.find(this.options.selectCloseButton);
        this.indicator = this.element.find(this.options.selectIndicator);

        //
        // bind events
        //
        
        this.infoButton.click(function() {
            self.detailsInfo.fadeIn("fast");
        });
        this.closeButton.click(function() {
            // The same class functions for both close buttons.
            // This makes only either one of the following two lines
            // active at the same time.
            self.detailsInfo.fadeOut("fast");
            self.error.fadeOut("fast");
            });
        // On-off indicator
        var ind = this.indicator;
        ind.click(function() {
            if (ind.hasClass('on') || ind.hasClass('polling')) {
                ind.removeClass('on polling');
                ind.addClass('off');
                // trigger a change
                self.element.trigger('ajaxstatechanged.karlcontentfeeds', ['off']);
            } else if (self.indicator.hasClass('off')) {
                ind.removeClass('off');
                ind.addClass('on');
                // trigger a change
                self.element.trigger('ajaxstatechanged.karlcontentfeeds', ['on']);
            } else if (ind.hasClass('error')) {
                self.error.fadeIn("fast");
            }
        });
    },

    destroy: function() {
        $.Widget.prototype.destroy.call( this );

        // unbind events
        this.infoButton.unbind('click');
        this.closeButton.unbind('click');
        this.indicator.unbind('click');
    },

    setAjaxState: function (newstate, d) {
        // update UI
        this.indicator.removeClass('on off polling error');
        this.indicator.addClass(newstate);
        // if it's an error, also update the error message
        if (newstate == 'error') {
            this.errorDetail.text(d.errormsg);
        }

        if (d && d.notify) {
            // Trigger only if we are calling.
            // (to avoid circular events)
            this.element.trigger('ajaxstatechanged.karlcontentfeeds', [newstate, d.errormsg]);
        }

    }


});


})(jQuery);

