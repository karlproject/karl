
// This script is loaded deferred, and if we find that the jQuery ready
// event triggered _before_ this script got executed, then we
// have a problem.

(function ($) {

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };


    if ($.isReady) {
        log('FATAL PROBLEM WITH DEFERRED LOADING, please report!', $.browser);
        alert('FATAL PROBLEM WITH DEFERRED LOADING, please report with your browser version and current URL!');
    }

})(jQuery);

