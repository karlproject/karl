
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
        },

        _create: function () {
            var self = this;
            this.element
                .pushdownrenderer({
                    name: 'livesearch',
                    selectTopBar: this.options.selectTopBar
                })
                .on({
                    focus: function (evt) {
                        self.element
                            .pushdownrenderer('option', 'data', {})
                            .pushdownrenderer('render')
                            .pushdownrenderer('show');
                    }
                });

        },

        _destroy: function () {
            this.element.pushdownrenderer('destroy');
            this.element.off('focus');
        }

    });


})(jQuery);
