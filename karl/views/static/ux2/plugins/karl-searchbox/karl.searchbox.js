
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
    
    $.widget('karl.searchbox', {

        options: {
            //selectTopBar: null, // pushdown inserted under this element
            delay: 0,              // time to wait before processing a key
            minLength: 0  // minimum number of characters to trigger a search
        },

        _create: function () {
            var self = this;
            this.element
                .pushdownrenderer({
                    name: 'searchbox',
                    selectTopBar: this.options.selectTopBar,
                    data: {}
                })
                .pushdownrenderer('render')
                .on({
                    focus:  $.proxy(this._handleFocus, this),
                    keyup:  $.proxy(this._handleKeyUp, this)
                });

            this.timer = null;

        },

        _destroy: function () {
            this.resetTimer();
            this.element.pushdownrenderer('destroy');
            this.element.off('focus');
        },

        
        _handleFocus: function (evt) {
            this.element.pushdownrenderer('show');
        },

        _resetTimer: function () {
            if (this.timer) {
                clearTimeout(this.timer);
                this.timer = null;
            }
        },

        _handleKeyUp: function (evt) {
            var val = this.element.val();
            var length = val.length;
            this._resetTimer();
            if (length === 0) {
                this.element.pushdownrenderer('option', 'data', {});
            } else if (length < this.options.minLength) {
                this.element.pushdownrenderer('option', 'data', {
                    error: 'Please add more characters to: "' + val + '"'
                });
            } else {
                this.element.pushdownrenderer('option', 'data', {
                    progress: true
                });
                this.timer = setTimeout(
                    $.proxy(this._timeoutKey, this), this.options.delay);
            }
            this.element.pushdownrenderer('render');
        },

        _timeoutKey: function () {
            var val = this.element.val();
            log('search for:', val);
            this.element.pushdownrenderer('option', 'data', {
                goat: 'Kerfuffle'
            });
            this.element.pushdownrenderer('render');
        }

    });


})(jQuery);
