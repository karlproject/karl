
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */

/*globals window navigator document console setTimeout $ */

(function ($) {

    "use strict";

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    $(function () {
        var head_data = window.head_data || {};
        // need urls
        var appUrl = window.head_data.app_url;

        $('#tagbox').tagbox({
            prevals: window.head_data.panel_data.tagbox,
            validateRegexp: "^[a-zA-Z0-9\-\._]+$",
            searchTagURL: window.head_data.context_url + 'jquery_tag_search',
            addTagURL: window.head_data.context_url + 'jquery_tag_add',
            delTagURL: window.head_data.context_url + 'jquery_tag_del',
            autocompleteURL: appUrl + '/tag_search.json'
        });


        // add the tab logic to radar chatter
        $('#radar')
            .bind('pushdowntabrender', function () {
                console.log('yeah', this);
                $('#radar-panel .radartabs li a').click(function () {
                    var li = $(this).parent();
                    var tabName = li.data('radartab');
                    if (tabName) {
                        var activeSection = $('#radar-panel .radarsection')
                            .filter(function () {
                                return $(this).is(':visible');
                            });
                        var openingSection = 
                            $('#radar-panel .radarsection[data-radarsection="' +
                                             tabName + '"]');

                        if (activeSection.data('radarsection') != tabName) {
                            activeSection.hide('fade');
                            openingSection.show('fade');
                            log('Switch to radar tab', tabName);
                        }
                    }
                });

            });
        


    });

})(jQuery);
