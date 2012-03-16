
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


        function drawChart(el) {
            log('Draw chart.', el);
            el.each(function () {
                // Do we have a chart already?
                var elChart = $(this);
                if (! elChart.data('hasChart')) {
                    // Only do this if no chart yet.
                    // Mark we have a chart.
                    elChart.data('hasChart', true);
                    // Draw the chart.
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
                            this);
                    chart.draw(data, options);
                }
            });
        }

        function switchToRadarTab(tab, tabName, /*optional*/ callbackShown) {
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
                    if (callbackShown) {
                        callbackShown(tab, tabName, section);
                    }
                } else {
                    // Normal way: animate from one section to the other.
                    // Are we switching?
                    if (currentTabName != tabName) {
                        var currentSection =
                            $('#radar-panel .radarsection[data-radarsection="' +
                            currentTabName + '"]');
                        // animate the section
                        currentSection.hide('fade', function () {
                            section.show('fade', function () {
                                if (callbackShown) {
                                    callbackShown(tab, tabName, section);
                                }
                            });
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

        $('#radar')
            .bind('pushdowntabrender', function () {
                // add the tab logic to radar chatter
                var tab = $(this);
                var defaultTabName = 'home'; // XXX
                var selectedTabName = tab.data('radarselectedtab') ||
                        defaultTabName;
                tab.data('radarselectedtab', null);

                function callbackShown(tab, tabName, section) {
                    if (tabName == 'budget') {
                        log('Budget!!!');
                        drawChart($('#radar-panel .radarchart'));
                    }
                }

                switchToRadarTab(tab, selectedTabName,
                    function (tab, tabName, section) {
                        // XXX Next problem. We can only bind the google 
                        // chart when the panel is actually shown. Due to the
                        // animation, this will happen later. So we will need
                        // an event for this, but for now,
                        // let's just quick-and-dirty...
                        var panelVisible = tab.data('pushdowntab')
                            .panel.data('pushdownpanel')
                            .isVisible();
                        if (panelVisible) {
                            log('onrender PREDRAW');
                            // panel is visible now
                            callbackShown(tab, tabName, section);
                        } else {
                            // panel is not visible, it will be when open.
                            // XXX Try to do this with proper event
                            // XXX from component.
                            tab.one('pushdowntabshow', function () {
                                log('onrender post draw');
                                callbackShown(tab, tabName, section);
                            });
                        }
                    }
                );

                $('#radar-panel .radartabs li a').click(function () {
                    var li = $(this).parent();
                    var tabName = li.data('radartab');
                    switchToRadarTab(tab, tabName, callbackShown);
                });

            });


    });

})(jQuery);
