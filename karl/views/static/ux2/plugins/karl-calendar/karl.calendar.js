
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console */
/*globals setTimeout clearTimeout setInterval */ 
/*globals jQuery DD_roundies alert confirm escape */



(function ($) {

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    var monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    $.widget('karl.karlcalendarbuttons', {

        options: {
            // selection = {
            //     viewtype: 'calendar' or 'list',
            //     term: 'day' or 'month' or 'year',
            //     year: 2011,
            //     month: 9,
            //     day: 23
            // }
            // change: function(evt, selection) {} // data is the same format as this.options.selection
        },

        _create: function () {
            var self = this;   

            this.el_b_today = this.element.find('.b-today');

            this.el_b_prev = this.element.find('.b-prev');
            this.el_b_next = this.element.find('.b-next');

            this.el_b_selyear = this.element.find('.d-selyear button');
            this.el_l_selyear = this.el_b_selyear.find('.c-label');
            this.el_dd_selyear = this.element.find('.d-selyear .dropdown-menu');
            this.el_b_selmonth = this.element.find('.d-selmonth button');
            this.el_l_selmonth = this.el_b_selmonth.find('.c-label');
            this.el_dd_selmonth = this.element.find('.d-selmonth .dropdown-menu');
            this.el_b_selday = this.element.find('.d-selday button');
            this.el_l_selday = this.el_b_selday.find('.c-label');
            this.el_dd_selday = this.element.find('.d-selday .dropdown-menu');

            this.el_group_viewtype = this.element.find('.c-viewtype');
            this.el_b_calendar = this.element.find('.b-calendar');
            this.el_b_list = this.element.find('.b-list');

            this.el_group_term = this.element.find('.c-term');
            this.el_b_day = this.element.find('.b-day');
            this.el_b_week = this.element.find('.b-week');
            this.el_b_month = this.element.find('.b-month');

            
            this.el_b_today.click(function (evt) {
                var d = new Date();
                var selection = self.options.selection || {};
                var year = d.getFullYear();
                var month = d.getMonth() + 1;
                var day = d.getDate();
                if (selection.year != year || selection.month != month ||
                        selection.day != day) {
                    self.options.selection.year = year;
                    self.options.selection.month = month;
                    self.options.selection.day = day;
                    return self._change(evt);
                }
            });

            this.el_b_prev
                .click(function (evt) {
                    return self._navigate(evt, -1);
                });

            this.el_b_next
                .click(function (evt) {
                    return self._navigate(evt, +1);
                });
                

            var i;
            for (i = 2000; i < 2025; i++) {
                self.el_dd_selyear.append('<li data-value="' +
                        i + '"><a href="#">' + i + '</a></li>');
            }
            $.each(monthLabels, function (index, value) {
                self.el_dd_selmonth.append('<li data-value="' +
                        (index + 1) + '"><a href="#">' + value + '</a></li>');
            });


            this.el_dd_selyear.on('click', 'a', function (evt) {
                var value = Number($(this).parents('li').eq(0).data('value'));
                if (value > 0 && self.options.selection.year != value) {
                    self.options.selection.year = value;
                    self._change(evt);
                }
            });

            this.el_dd_selmonth.on('click', 'a', function (evt) {
                var value = Number($(this).parents('li').eq(0).data('value'));
                if (value > 0 && self.options.selection.month != value) {
                    self.options.selection.month = value;
                    self._change(evt);
                }
            });

            this.el_dd_selday.on('click', 'a', function (evt) {
                var value = Number($(this).parents('li').eq(0).data('value'));
                if (value > 0 && self.options.selection.day != value) {
                    self.options.selection.day = value;
                    self._change(evt);
                }
            });


            this.el_b_calendar.click(function (evt) {
                if (self.options.selection.viewtype != 'calendar') {
                    self.options.selection.viewtype = 'calendar';
                    return self._change(evt);
                }
            });
            this.el_b_list.click(function (evt) {
                if (self.options.selection.viewtype != 'list') {
                    self.options.selection.viewtype = 'list';
                    return self._change(evt);
                }
            });

            this.el_b_day.click(function (evt) {
                if (self.options.selection.term != 'day') {
                    self.options.selection.term = 'day';
                    return self._change(evt);
                }
            });
            this.el_b_week.click(function (evt) {
                if (self.options.selection.term != 'week') {
                    self.options.selection.term = 'week';
                    return self._change(evt);
                }
            });
            this.el_b_month.click(function (evt) {
                if (self.options.selection.term != 'month') {
                    self.options.selection.term = 'month';
                    return self._change(evt);
                }
            });

            this._updateSelection();
            
        },
        
        disable: function (evt) {
            // grey everything
            // (before leaving the page)
            this.el_b_today.attr('disabled', true);
            this.el_b_prev.attr('disabled', true);
            this.el_b_next.attr('disabled', true);
            this.el_b_selyear.attr('disabled', true);
            this.el_b_selmonth.attr('disabled', true);
            this.el_b_selday.attr('disabled', true);
            this.el_b_day.attr('disabled', true);
            this.el_b_week.attr('disabled', true);
            this.el_b_month.attr('disabled', true);
            this.el_b_calendar.attr('disabled', true);
            this.el_b_list.attr('disabled', true);
        },

        _navigate: function (evt, direction) {
            var selection = this.options.selection || {};
            var term = selection.term;
            var msecsInADay = 86400000;
            var d1;
            var d2;
            if (term == 'month') {
                this.options.selection.month += direction;
                if (this.options.selection.month === 0) {
                    this.options.selection.month = 12;
                    this.options.selection.year -= 1;
                } else if (this.options.selection.month == 13) {
                    this.options.selection.month = 1;
                    this.options.selection.year += 1;
                }
            } else if (term == 'week') {
                d1 = new Date(selection.year, selection.month - 1, selection.day);
                d2 = new Date(d1.getTime() + direction * 7 * msecsInADay);
                this.options.selection.year = d2.getFullYear();
                this.options.selection.month = d2.getMonth() + 1;
                this.options.selection.day = d2.getDate();
            } else if (term == 'day') {
                d1 = new Date(selection.year, selection.month - 1, selection.day);
                d2 = new Date(d1.getTime() + direction * msecsInADay);
                this.options.selection.year = d2.getFullYear();
                this.options.selection.month = d2.getMonth() + 1;
                this.options.selection.day = d2.getDate();
            }
            return this._change(evt);
        },

        _change: function (evt) {
            this._updateSelection();
            this._trigger('change', evt, this.options.selection);
        },
        
        _setOption: function (key, value) {
            
            var selectionChanged = (key == 'selection') && 
                this._isSelectionChanged(this.options.selection, value);

            $.Widget.prototype._setOption.call(this, key, value);

            if (selectionChanged) {
                this._updateSelection();
            }

        },

        _isSelectionChanged: function (sel1, sel2) {
            if (!sel1 && !sel2) {
                return false;
            }
            if (!sel1 || !sel2) {
                return true;
            }
            return (
                (sel1.viewtype != sel2.viewtype) ||
                (sel1.term != sel2.term) ||
                (sel1.year != sel2.year) ||
                (sel1.month != sel2.month) ||
                (sel1.day != sel2.day)
            );
        },

        _updateDays: function () {
            var self = this;
            var selection = this.options.selection || {};
            this.el_dd_selday.empty();
            var month = selection.month;
            var days;
            if (month == 2) {
                // February
                var year = selection.year;
                // leap years
                if (year % 4 === 0 && (year == 2000 || year % 100 > 0)) {
                    days = 29;
                } else {
                    days = 28;
                }
            } else if (month == 4 || month == 6 || month == 9 || month == 11) {
                // April, June, September, November
                days = 30;
            } else {
                days = 31;
            }
            var i;
            for (i = 1; i <= days; i++) {
                self.el_dd_selday.append('<li data-value="' +
                        i + '"><a href="#">' + i + '</a></li>');
            }

        },

        _updateSelection: function () {
            var selection = this.options.selection || {};

            // update the number of days in this month
            this._updateDays();

            // disabling or enabling Today
            var d = new Date();
            var year = d.getFullYear();
            var month = d.getMonth() + 1;
            var day = d.getDate();
            var isToday = (selection.year == year && selection.month == month &&
                    selection.day == day);
            this.el_b_today.attr('disabled', isToday);

            // select the selection date in the dropdowns
            this.el_l_selyear.text('' + selection.year);
            this.el_l_selmonth.text(monthLabels[selection.month - 1]);
            this.el_l_selday.text('' + selection.day);
            
            this.el_group_viewtype.find('.active').removeClass('active');
            var el_viewtype = {
                calendar: this.el_b_calendar,
                list: this.el_b_list
            }[selection.viewtype];
            el_viewtype.addClass('active');

            this.el_group_term.find('.active').removeClass('active');
            var el_term = {
                day: this.el_b_day,
                week: this.el_b_week,
                month: this.el_b_month
            }[selection.term];
            el_term.addClass('active');

        }

    });



    /* Other calendar code that is copied over from ux2 from karl.js */

    /* auto create anon ids (used by calendar) */
    jQuery.fn.identify = function () {
        var i = 0;
        return this.each(function () {
            if ($(this).attr('id')) {
                return;
            }
            var id;
            do {
                i++;
                id = 'anon_' + i;
            } while ($('#' + id).length > 0);

            $(this).attr('id', id);
        }).attr("id");
    };

    /** =CALENDAR TIME SLOT HOVER
    ----------------------------------------------- */
    var hov = {};

    function mouseOverHour(evt) {
        var elt = $(evt.target);
        if (!elt.hasClass('cal_hour_event')) {
            elt = elt.parents(".cal_hour_event");
        }
        if (!elt) {
            return;
        }

        var id  = elt.identify("a");
        hov[id] = true;
      
        // only display if still hovered after some time
        setTimeout(function () {
            if (hov[id]) { 
                elt.addClass('hov'); 
                elt.next().addClass('hov_below');
            }
        }, 200);
    }

    function mouseOutHour(evt) {
        var elt = $(evt.target);
        if (!elt.hasClass('cal_hour_event')) {
            elt = elt.parents(".cal_hour_event");
        }
        if (!elt) {
            return;
        }

        var id  = elt.identify("a");
        delete hov[id];

        // only hide if we've outed for number of time
        setTimeout(function () {
            if (!hov[id]) { 
                elt.removeClass('hov'); 
                elt.next().removeClass('hov_below');
            }
        }, 200);
    }


    function mouseOverDay(evt) {
        var elt = $(this);
        var id  = elt.identify("a");
        hov[id] = true;
      
        // only display if still hovered after some time
        setTimeout(function () {
            if (hov[id]) {
                elt.addClass('hov');
            }
        }, 200);
    }

    function mouseOutDay(evt) {
        var elt = $(this);
        var id  = elt.identify("a");
        delete hov[id];

        // only hide if we've outed for number of time
        setTimeout(function () {
            if (!hov[id]) {
                elt.removeClass('hov');
            }
        }, 200);
    }

    /** =CALENDAR TIME SCROLLING
    ----------------------------------------------- */
    function scrollToTime() {
        var time = $('#cal_time');
        if (time.length === 0) {
            return;
        }

        var mins,
            scrollDuration;
        // Scroll to current time for today
        if (time.hasClass('today')) {
            // find current time - determine % of day passed
            var curTime = new Date();

            // total minutes passed today & total mins in a day
            mins = curTime.getHours() * 60 + curTime.getMinutes();
            scrollDuration = 1000;

            // go to ~ 8:00am
        } else {
            mins = 740;
            scrollDuration = 0;
            time.css("visibility", "hidden");
        }

        var day  = 1440;
        var perc = parseInt(mins / day * 100, 10);

        // get height of entire calendar and set position of time
        var calHeight = $('#cal_scroll').height();
        var top = parseInt(calHeight * perc / 100, 10);
        time.css('top', top + "px").show();

        // scroll to make time centered if possible
        var scrollPos = top - 250 > 0 ? top - 250 : 0;

        $("#cal_hours_scroll").scrollTo(scrollPos, { duration: scrollDuration });
    }


    /* My tooltip: add a wrapper so we can handle 
     * the overflow correctly */
    $.fn.myTooltip = function (options) {
        return this.each(function () {
            var el = $(this);
            var tt = el.next();
            var wrapper = $('<div></div>')
                .height(tt.height())
                .css('overflow', 'hidden');
            tt.wrapInner(wrapper);
            el.tooltip(options);
        });
    };


    /** =CALENDAR INIT JAVASCRIPT
    ----------------------------------------------- */

    $.widget('karl.karlcalendarbody', {
        /* Most of the legacy code, except the toolbar */

        _create: function () {
            var self = this,
                el = this.element;
        
            // MONTH VIEW - hover to show (+) icon to add events
            el.find("#cal_month td").hover(mouseOverDay, mouseOutDay);
            el.find("#cal_month .with_tooltip").myTooltip({ tip: '.tooltip', offset: [8, 50], predelay: 250});

            // WEEK/DAY VIEW - 
            var scrollHours = el.find("#cal_hours_scroll");
            scrollHours.mouseover(mouseOverHour);
            scrollHours.mouseout(mouseOutHour);
            el.find("#all_day td").hover(mouseOverDay, mouseOutDay);

            // Week tooltips
            var calScroll = el.find("#cal_scroll");
            if (calScroll.hasClass('cal_week')) {
                el.find("#all_day .with_tooltip").myTooltip({
                    tip: '.tooltip',
                    offset: [8, -48],
                    predelay: 250
                });
                el.find("#cal_scroll .cal_hour_event .with_tooltip").myTooltip({
                    tip: '.tooltip',
                    offset: [12, 5],
                    predelay: 250
                });
            }
        }
    });


    $.widget('karl.karlcalendarfooter', {

        _create: function () {
            var self = this;

            /* calendar print action */
            this.element.on('click', '.cal-actions .cal-print', function () {
                // I cannot seem to show the entire
                // calendar from css, so to avoid
                // scrolling / overflow, the height
                // is manipulated directly here.
                var inner =  $('.cal_scroll');
                var outer = $('.cal_hours_scroll');
                var fullheight = inner.height();
                var oldheight = outer.height();
                outer.height(fullheight);
                // Mark the body for the time of the printing and
                // the printing css can refer to this marker class. This
                // is simpler than putting it to the outside of all calendar views,
                // which would also be good but that marker does not exist.
                $('body').addClass('karl-calendar-printing');
                // Print now.
                window.focus();
                window.print();
                // Resume original state.
                outer.height(oldheight);
                $('body').removeClass('karl-calendar-printing');
                return false;
            });

            scrollToTime();
        }
    });


    $.widget('karl.karlcalendarsetupform', {

        _create: function () {
            // toggle add layers/categories calendar form
            $(".add_button").click(function (eventObject) {   
                eventObject.preventDefault();
                var group = $(eventObject.target).parents(".setup_group");

                group.find(".add_button").hide("fast");
                group.find(".cal_add").show("slow");
            });
            $('.cal_add button[name="form.cancel"]').click(function (eventObject) {
                eventObject.preventDefault();
                var validationErrors = $("div.portalMessage");
                if (validationErrors) {
                    validationErrors.remove();
                }

                var group = $(eventObject.target).parents(".setup_group");
                group.find(".add_button").show("fast");
                group.find(".cal_add").hide("slow");

                $(this).parents("form")[0].reset();
            });

            // automatically show form if submission failed with validation errors
            var fielderrors_target = $('#fielderrors_target').val();
            var formSelector;
            if (fielderrors_target.length > 0) {
                if (fielderrors_target == "__add_category__") {
                    formSelector = "#setup_add_category_form";
                } else if (fielderrors_target == "__add_layer__") {
                    formSelector = "#setup_add_layer_form";
                } else {
                    formSelector = "#edit_" + fielderrors_target + "_form";
                }
                $(formSelector).show();
            }

            // toggle edit layer/categories calendar form
            $(".edit_action").click(function (eventObject) {
                eventObject.preventDefault();
                var group = $(eventObject.target).parents(".setup_group");
            
                group.find("form").hide("slow");
                group.find(".add_button").hide("fast");

                var formId = "#" + $(this).identify() + "_form"; 
                $(formId).show("slow");
            });
            $('.cal_edit button[name="form.cancel"]').click(function (eventObject) {
                eventObject.preventDefault();
                var validationErrors = $("div.portalMessage");
                if (validationErrors) {
                    validationErrors.remove();
                }

                var group = $(eventObject.target).parents(".setup_group");
                group.find(".add_button").show("fast");
                group.find("form").hide("slow");

                $(this).parents("form")[0].reset();
            });

            // delete layer / category
            this.initCalendarLayersOrCategoriesDelete();

            if ($("select.category_paths").length > 0) { 
                this.initCalendarLayersEdit();
            }
        },

        // only show "Remove" if more than one category is present
        _updateRemoveLinks: function () {
            $(".layers").each(function () {
                var elts = $(this).find('td a.remove');
                elts.css('display', elts.length > 1 ? "inline" : "none");
            });
        },
        
        initCalendarLayersEdit: function () {
            var self = this;
            // add category to a layer
            $('a.add').click(function (eventObject) {
                eventObject.preventDefault();

                var layers = $(this).parents(".field").find(".layers");
                var row = layers.find("tr:last");
                row.clone().appendTo(layers).find("option").removeAttr("selected");

                self._updateRemoveLinks();
            });

            // remove category from a layer
            $('a.remove').live('click', function (eventObject) { 
                eventObject.preventDefault();

                $(this).parents('tr').remove();

                self._updateRemoveLinks();
            });

            // update remove links on page load
            this._updateRemoveLinks();
        },

        initCalendarLayersOrCategoriesDelete: function () {
            $('a.delete_category_action').bind('click', function (e) {
                if (confirm("Are you sure?")) {
                    var category = this.id.substring(16); // delete_category_*
                    $('#cal_delete_category_form > input[name="form.delete"]').val(category);
                    $('#cal_delete_category_form').submit();
                }
                return false;
            });

            $('a.delete_layer_action').bind('click', function (e) {
                if (confirm("Are you sure?")) {
                    var layer = this.id.substring(13); // delete_layer_*
                    $('#cal_delete_layer_form > input[name="form.delete"]').val(layer);
                    $('#cal_delete_layer_form').submit();
                }
                return false;
            });
        }

    });

})(jQuery);
