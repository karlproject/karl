
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console */
/*globals jQuery:false  */


(function ($) {

    $.fn.quickpanel = function (selector) {
        return this.each(function () {
            $(this).delegate(selector, 'click touchstart', function (e) {
                var $par = $(this).parent('[data-quickpanel="pushdown"]'),
                    dw = $(document).width(),
                    w = $par.width(),
                    l = $par.offset().left,
                    dropw = $par.find('.pushDown').width(),
                    r = dw - l - w;
                $('[data-quickpanel]')
                    .not($par)
                    .removeClass('open');
                if (r < dropw) {
                    $par.addClass('rtl');
                }
                $par.toggleClass('open');
                if (e.currentTarget.id === 'search-toggle') {
                    $par.find('.search-site-box').focus();
                }
                return false;
            });
        });
    };

    $(function () {
        $('body').quickpanel('.pushdown-toggle');
    });

}(jQuery));
