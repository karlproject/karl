
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */

/*globals window navigator document console setTimeout jQuery google */

(function ($) {

    "use strict";

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    // Load for the google bars
    // XXX It would _actually_ be better to have this from non-deferred.
    google.load("visualization", "1", {packages: ["corechart"]});

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


        function switchToRadarTab(tab, tabName) {
            if (tabName) {
                var currentTabName = tab.data('radarselectedtab');
                var section = 
                        $('#radar-panel .radarsection[data-radarsection="' +
                        tabName + '"]');
                if (! currentTabName) {
                    // No tab yet. Initialize it by hiding all
                    // the sections except one.
                    $('#radar-panel .radarsection').hide();
                    section.show();
                } else {
                    // Normal way: animate from one section to the other.
                    var currentSection =
                            $('#radar-panel .radarsection[data-radarsection="' +
                            currentTabName + '"]');
                    log('cu', currentTabName, currentSection);
                    // Are we switching?
                    if (currentSection.data('radarsection') != tabName) {
                        // animate the section
                        currentSection.hide('fade', function () {
                            section.show('fade');
                        });
                    }
                }
                // Remember the tab
                tab.data('radarselectedtab', tabName);
                log('Switch to radar tab', tabName);
                // Set tab active
                $('#radar-panel .radartabs li.active')
                    .removeClass('active');
                $('#radar-panel .radartabs li[data-radartab="' +
                                 tabName + '"]')
                    .addClass('active');
            }
        }

        function drawChart() {
            /*
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Year');
            data.addColumn('number', 'Sales');
            data.addColumn('number', 'Expenses');
            data.addRows([
                ['2004', 1000, 400],   
                ['2005', 1170, 460],
                ['2006', 660, 1120],   
                ['2007', 1030, 540]
            ]);
            var options = {         
                title: 'Company Performance',        
                hAxis: {
                    title: 'Year',
                    titleTextStyle: {color: 'red'}
                }
            };
            var chart = new google.visualization.ColumnChart(
                    document.getElementById('chart1')); 
            chart.draw(data, options);
            */
        }

        $('#radar')
            .bind('pushdowntabrender', function () {
                // add the tab logic to radar chatter
                var tab = $(this);
                var defaultTabName = 'home'; // XXX
                var selectedTabName = tab.data('radarselectedtab') ||
                        defaultTabName;
                tab.data('radarselectedtab', null);
                switchToRadarTab(tab, selectedTabName);
                drawChart();

                $('#radar-panel .radartabs li a').click(function () {
                    var li = $(this).parent();
                    var tabName = li.data('radartab');
                    switchToRadarTab(tab, tabName);
                });

            });


    });

})(jQuery);
