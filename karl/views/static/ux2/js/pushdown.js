/*globals jQuery:false  */
(function ($) {

    $(function () {
        $('body').quickpanel('.pushdown-toggle');
    });

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
                if(e.currentTarget.id === 'search-toggle') {
                    $par.find('.search-site-box').focus();
                }
                return false;
            });
        });
    };

}(jQuery));