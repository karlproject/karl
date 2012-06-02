
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 135, indent: 4 */
/*jslint sub: true */

/*globals window navigator document setTimeout jQuery google Globalize Mustache*/

(function ($) {

    "use strict";

    var log = function () {
        var c = window.console;
        if (c && c.log) {
            // log for FireBug or WebKit console
            c.log(Array.prototype.slice.call(arguments));
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
                // General: dates
                Globalize.perform_actions('#radar-panel');

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
                //
                // Approvals: bind the tabs from column2
                $('#radar-panel .approvalsection').hide();
                var currentTabName = tab.data('radar.approval.activeTab');
                var currentSection = $('#radar-panel .approvalsection[data-approvalsection="' +
                    currentTabName + '"]');
                currentSection.show();
                // set the active link, initially
                $('#radar-panel a.approvaltab').removeClass('selected');
                var currentTab = $('#radar-panel .approvaltab[data-approvaltab="' +
                    currentTabName + '"]');
                currentTab.addClass('selected');
                // handle change by click
                $('#radar-panel a.approvaltab').click(function () {
                    var link = $(this);
                    var currentTabName = tab.data('radar.approval.activeTab');
                    var tabName = link.data('approvaltab');
                    var section = $('#radar-panel .approvalsection[data-approvalsection="' +
                            tabName + '"]');
                    // Only act, if we have a section, and the tab is changing.
                    if (section.length > 0 && tabName != currentTabName) {
                        if (currentTabName) {
                            // animate the section
                            var currentSection = $('#radar-panel .approvalsection[data-approvalsection="' +
                                    currentTabName + '"]');
                            currentSection.stop().hide('fade', function () {
                                section.stop().show('fade');
                            });
                        } else {
                            // quick show
                            section.stop().show();
                        }
                        // change the link
                        $('#radar-panel a.approvaltab.selected').removeClass('selected');
                        link.addClass('selected');
                        // remember
                        link.data('approvaltabActive', tabName);
                        tab.data('radar.approval.activeTab', tabName);
                    }
                });

                // implement switching by click
                $('#radar-panel .radartabs li a').click(function () {
                    var li = $(this).parent();
                    var tabName = li.data('radartab');
                    switchToRadarTab(tab, tabName);
                });

        });

        $(document).on('mouseenter', '.panel-item-header .timeago', function () {
            $(this).hide();
            $(this).next().show();
        });
        $(document).on('mouseleave', '.panel-item-header .post-options', function () {
            $(this).hide();
            $(this).prev().show();
        });

        $(document).on('submit', '#chatter-post-form', function (event) {
            event.preventDefault();
            var self = this;
            $.ajax({
                url: $(this).attr('action'),
                type: 'post',
                data: $(this).serialize(),
                dataType: 'json',
                error: function (xhr, status, error) {
                    $('.houstonWeHaveAProblem').show();
                },
                success: function (data, status, xhr) {
                    $(self).find('.new-post-text').val('');
                    var html = Mustache.to_html(data.template, data.data);
                    var items = $(self).closest('.panel').find('.panel-header');
                    items.after(html);
                    $('.timeago').timeago();
                }
            });
        })

        function chatterViewMore(items) {
            items.each(function (idx, item) {
                var outer = $(this).children('.messagewrapper');
                var inner = $(outer).children('.messagetext');
                if (inner.height() > outer.height()) {
                    var more = $(this).parent().find(".panel-item-header > .post-options > .view-more");
                    more.show();
                 }
            });
        }

        $(document).on('click', '.panel-header .post-options .add-new-post', function () {
            var target = $(this).closest(".panel-header").find(".new-post");
            target.toggle();
        });
        $(document).on('click', '.panel-item-header .post-options .view-more', function () {
            var message = $(this).closest(".panel-item").find(".panel-item-content > .messagewrapper");
            message.addClass('messagewrapper-view-all');
            $(this).hide();
            $(this).next(".view-less").show();
        });

        $(document).on('click', '.panel-item-header .post-options .view-less', function () {
            var message = $(this).closest(".panel-item").find(".panel-item-content > .messagewrapper");
            message.removeClass('messagewrapper-view-all');
            $(this).hide();
            $(this).prev(".view-more").show();
        });

        $(document).on('pushdowntabonshow', '#popper-pushdown-chatter', function (evt, state) {
            var items = $("#chatter-panel .panel-item-content");
            chatterViewMore(items);
            $("#chatter-panel .panel-item-header .timeago").timeago();
        });

        $(document).on('pushdowntabrender', '#popper-pushdown-chatter', function (evt, state) {
            var items = $("#chatter-panel .panel-item-content");
            chatterViewMore(items);
            $("#chatter-panel .panel-item-header .timeago").timeago();
            $('#chatter-recipient').autocomplete({
                source: $('#chatter-recipient').attr('data-source'),
                minLength: 2
            });
        });

        // ugly hack to remove empty notes in vcards because markup is still there
        $('.peopledir-hcard .vcard p.note').filter(function () {
            return $.trim($(this).html()) === '';
        }).remove();

        $(".timeago").timeago();

        var update_chatter_messages = function (data, user, useritem) {
            $('.user-item').removeClass('selected');
            useritem.addClass('selected');
            var target = $('.chatter-messages');
            $(target).find('.message-item').remove();
            var html = Mustache.to_html(data.template, {'messages': data.data});
            $(target).append(html);
            $('.timeago').timeago();
            $('input[name="recipient"]').val(user);
            setQuipActions();
            setQuipTargets();
        }

        $('#chatter-message-user').autocomplete({
            source: $('#chatter-message-user').attr('data-source'),
            minLength: 2,
            select: function (evt, state) {
                var user = state.item.value;
                $.ajax({
                    url: $(this).attr('data-action') + user,
                    type: 'get',
                    dataType: 'json',
                    error: function (xhr, status, error) {
                        log(error);
                    },
                    success: function (data, status, xhr) {
                        var useritem = $('.user-item').first();
                        update_chatter_messages(data, user, useritem);
                    }
                });
            }
        });

        $('#chatter-tag').autocomplete({
            source: $('#chatter-tag').attr('data-source'),
            minLength: 1
        });

        $('.chatter-messages-users').on('click', '.user-item', function (evt, state) {
            var self = this;
            var user = $(self).attr('data-user');
            $.ajax({
                url: $(self).attr('data-action'),
                type: 'get',
                dataType: 'json',
                error: function (xhr, status, error) {
                    log(error);
                },
                success: function (data, status, xhr) {
                    update_chatter_messages(data, user, $(self));
                }
            });
        });
    });

})(jQuery);
