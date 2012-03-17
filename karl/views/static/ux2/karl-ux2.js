
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


        function drawChart(elChart, data) {
            // Do we have a chart already?
            if (! elChart.data('hasChart')) {
                // Only do this if no chart yet.
                // Mark we have a chart.
                elChart.data('hasChart', true);
                // Apply data-chartwidth attribute if specified
                //if ((data.options || {}).width === undefined) {
                //    var chartWidth = Number(elChart.data('chartwidth'));
                //    if (chartWidth) {
                //        data.options.width = chartWidth;
                //    }
                //}
                // Draw the chart.
                var gdata = new google.visualization.DataTable();
                $.each(data.columns, function (index) {
                    gdata.addColumn(this[0], this[1]);
                });
                gdata.addRows(data.rows);
                var chart = new google.visualization.ColumnChart(
                        elChart[0]);
                chart.draw(gdata, data.options);
            }
        }

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
                    // Are we switching?
                    if (currentTabName != tabName) {
                        var currentSection =
                            $('#radar-panel .radarsection[data-radarsection="' +
                            currentTabName + '"]');
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
                $('#radar-panel .radartabs li.selected')
                    .removeClass('selected');
                $('#radar-panel .radartabs li[data-radartab="' +
                                 tabName + '"]')
                    .addClass('selected');
            }
        }

        $('#radar')
            .bind('pushdowntabrender', function (evt, state) {
                var tab = $(this);
                // store the newest state for the widgets
                tab.data('pushdowntabstate', state);

                // add the tab logic to radar chatter
                var defaultTabName = 'home'; // XXX
                var selectedTabName = tab.data('radarselectedtab') ||
                        defaultTabName;
                tab.data('radarselectedtab', null);

                switchToRadarTab(tab, selectedTabName);

                // Bind necessary extras
                //
                // Budget: draw the charts
                $('#radar-panel .radarchart').each(function () {
                    var elChart = $(this);
                    var name = elChart.data('chartname');
                    var chartData = state[name];
                    // XXX note, a width must be specified for google charts
                    // otherwise, they will have the wrong width
                    // if hidden initially
                    drawChart(elChart, chartData);
                });

                // implement switching by click
                $('#radar-panel .radartabs li a').click(function () {
                    var li = $(this).parent();
                    var tabName = li.data('radartab');
                    switchToRadarTab(tab, tabName);
                });

            });


    });

})(jQuery);
