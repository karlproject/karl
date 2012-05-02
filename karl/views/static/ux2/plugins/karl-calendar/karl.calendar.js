
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console */
/*globals setTimeout clearTimeout setInterval */ 
/*globals jQuery DD_roundies alert confirm */



(function ($) {

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };


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
            ddRoundies: false,                   // use DD_roundies on IE?
            ie8OnePixelCompensate: true          // compensate the 1-px differences 
                                                // on IE8? (only if ddRoundies == true)
        },

        _create: function () {
            var self = this;   

            this.element.append(
                '<span class="karl-calendar-buttonset-term">' +
                    '<input type="radio" name="karl-calendar-buttonset-term" ' +
                      'id="karl-calendar-button-day" class="karl-calendar-button-day">' +
                    '</input><label for="karl-calendar-button-day">Day</label>' +
                    '<input type="radio" name="karl-calendar-buttonset-term" ' +
                      'id="karl-calendar-button-week" class="karl-calendar-button-week">' +
                    '</input><label for="karl-calendar-button-week">Week</label>' +
                    '<input type="radio" name="karl-calendar-buttonset-term" ' +
                      'id="karl-calendar-button-month" class="karl-calendar-button-month">' +
                    '</input><label for="karl-calendar-button-month">Month</label>' +
                '</span>' +
                '<span class="karl-calendar-buttonset-viewtype">' +
                    '<input type="radio" name="karl-calendar-buttonset-viewtype" ' +
                      'id="karl-calendar-button-calendar" class="karl-calendar-button-calendar">' +
                    '</input><label for="karl-calendar-button-calendar">Calendar</label>' +
                    '<input type="radio" name="karl-calendar-buttonset-viewtype" ' +
                      'id="karl-calendar-button-list" class="karl-calendar-button-list">' +
                    '</input><label for="karl-calendar-button-list">List</label>' +
                '</span>' +

                '<button class="karl-calendar-button-today">Today</button>' +
                '<span class="karl-calendar-buttonset-navigate">' +
                    '<input type="radio" name="karl-calendar-buttonset-navigate" ' +
                      'id="karl-calendar-button-prev" class="karl-calendar-button-prev">' +
                    '</input>' +
                    '<label for="karl-calendar-button-prev" class="karl-calendar-label-prev">&nbsp;</label>' +
                    '<input type="radio" name="karl-calendar-buttonset-navigate" ' +
                      'id="karl-calendar-button-next" class="karl-calendar-button-next">' +
                    '</input>' +
                    '<label for="karl-calendar-button-next" class="karl-calendar-label-next">&nbsp;</label>' +
                '</span>' +
                '<select class="karl-calendar-dropdown-year">' +
                '</select>' +
                '<select class="karl-calendar-dropdown-month">' +
                    '<option value="1">Jan</option>' +
                    '<option value="2">Feb</option>' +
                    '<option value="3">Mar</option>' +
                    '<option value="4">Apr</option>' +
                    '<option value="5">May</option>' +
                    '<option value="6">Jun</option>' +
                    '<option value="7">Jul</option>' +
                    '<option value="8">Aug</option>' +
                    '<option value="9">Sep</option>' +
                    '<option value="10">Oct</option>' +
                    '<option value="11">Nov</option>' +
                    '<option value="12">Dec</option>' +
                '</select>' +
                '<select class="karl-calendar-dropdown-day">' +
                '</select>'
            );

            this.el_b_today = this.element.find('.karl-calendar-button-today');

            this.el_bs_navigate = this.element.find('.karl-calendar-buttonset-navigate');
            this.el_b_prev = this.element.find('.karl-calendar-button-prev');
            this.el_b_next = this.element.find('.karl-calendar-button-next');

            this.el_dd_year = this.element.find('.karl-calendar-dropdown-year');
            this.el_dd_month = this.element.find('.karl-calendar-dropdown-month');
            this.el_dd_day = this.element.find('.karl-calendar-dropdown-day');

            this.el_bs_viewtype = this.element.find('.karl-calendar-buttonset-viewtype');
            this.el_b_calendar = this.element.find('.karl-calendar-button-calendar');
            this.el_b_list = this.element.find('.karl-calendar-button-list');

            this.el_bs_term = this.element.find('.karl-calendar-buttonset-term');
            this.el_b_day = this.element.find('.karl-calendar-button-day');
            this.el_b_week = this.element.find('.karl-calendar-button-week');
            this.el_b_month = this.element.find('.karl-calendar-button-month');

            
            this.el_b_today.button({
            });
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

            this.el_bs_navigate.buttonset({
            });
            this.el_b_prev
                .button('option', 'icons', {
                    primary: 'ui-icon-triangle-1-w'
                })
                .change(function (evt) {
                    return self._navigate(evt, -1);
                });

            this.el_b_next
                .button('option', 'icons', {
                    primary: 'ui-icon-triangle-1-e'
                })
                .change(function (evt) {
                    return self._navigate(evt, +1);
                });
                

            var i;
            for (i = 2000; i < 2025; i++) {
                this.el_dd_year.append('<option value="' + i + '">' + i + '</option>');
            }

            //this.el_dd_year.find('option').addClass('karl-calendar-dropdown-item');
            /*
            this.el_dd_year.selectmenu({
                type: 'dropdown',
                select: function (evt, uiHash) {
                    var value = Number(uiHash.value);
                    if (value > 0 && self.options.selection.year != value) {
                        self.options.selection.year = value;
                        return self._change(evt);
                    }
                }
            });
            */


            //this.el_dd_month.find('option').addClass('karl-calendar-dropdown-item');
            /*
            this.el_dd_month.selectmenu({
                type: 'dropdown',
                select: function (evt, uiHash) {
                    var value = Number(uiHash.value);
                    if (value > 0 && self.options.selection.month != value) {
                        self.options.selection.month = value;
                        return self._change(evt);
                    }
                }
            });
            */



            this.el_dd_year.change(function (evt) {
                var value = Number($(this).val());
                if (value > 0 && self.options.selection.year != value) {
                    self.options.selection.year = value;
                    return self._change(evt);
                }
            });

            this.el_dd_month.change(function (evt) {
                var value = Number($(this).val());
                if (value > 0 && self.options.selection.month != value) {
                    self.options.selection.month = value;
                    return self._change(evt);
                }
            });

            this.el_dd_day.change(function (evt) {
                var value = Number($(this).val());
                if (value > 0 && self.options.selection.day != value) {
                    self.options.selection.day = value;
                    return self._change(evt);
                }
            });


            this.el_bs_viewtype.buttonset({
            });

            this.el_b_calendar.change(function (evt) {
                if (self.options.selection.viewtype != 'calendar') {
                    self.options.selection.viewtype = 'calendar';
                    return self._change(evt);
                }
            });
            this.el_b_list.change(function (evt) {
                if (self.options.selection.viewtype != 'list') {
                    self.options.selection.viewtype = 'list';
                    return self._change(evt);
                }
            });

            this.el_bs_term.buttonset({
            });

            this.el_b_day.change(function (evt) {
                if (self.options.selection.term != 'day') {
                    self.options.selection.term = 'day';
                    return self._change(evt);
                }
            });
            this.el_b_week.change(function (evt) {
                if (self.options.selection.term != 'week') {
                    self.options.selection.term = 'week';
                    return self._change(evt);
                }
            });
            this.el_b_month.change(function (evt) {
                if (self.options.selection.term != 'month') {
                    self.options.selection.term = 'month';
                    return self._change(evt);
                }
            });

            this._updateSelection();
            
            this.element.find('a.ui-selectmenu').each(function () {
                    $(this).css('margin-top', '-4px');
                });
            // Dropdowns need a -2px top offset. margin-top: -4px does not
            // work well on IE7.
            if ($.browser.msie && $.browser.version <= 7) {
                this.element.find('a.ui-selectmenu').each(function () {
                    $(this)
                        .css('top', '-2px');
                });
                this.element.find('.karl-calendar-label-prev, .karl-calendar-label-next').each(function () {
                    $(this)
                        .css('top', '-2px')
                        .height($(this).height() + 1);
                });
            }
            

            // Use DD_roundies to give the rounded corners on IE.
            if (this.options.ddRoundies) {
                if (! DD_roundies) {
                    throw new Error('DD_roundies must be present, or ddRoundies=false ' +
                                    'option must be specified.');
                }
                DD_roundies.addRule('.cal-toolbar .ui-corner-left', '4px 0 0 4px');
                DD_roundies.addRule('.cal-toolbar .ui-corner-right', '0 4px 4px 0');
                DD_roundies.addRule('.cal-toolbar .ui-corner-all', '4px 4px 4px 4px');
            }

            if (this.options.ddRoundies && this.options.ie8OnePixelCompensate) {
                                                        // compensate the 1-px differences on IE8
                if ($.browser.msie && $.browser.version == 8) {
                    // DD_roundies broken? adds a -1px offset
                    // so, let's take it away
                    this.element.find('.ui-corner-left, .ui-corner-right, ' + 
                                '.ui-corner-all')
                        .each(function () {
                            $(this)
                                .css('top', '1px')
                                .css('left', '1px')
                                // ... and add it back to the children
                                .children().each(function () {
                                    // act only on static position
                                    var el = $(this);
                                    if (el.css('position') == 'static') {
                                        el
                                            .css('position', 'relative')
                                            .css('top', '' + (this.offsetTop - 2) + 'px')
                                            .css('left', '' + (this.offsetLeft - 2) + 'px');
                                    }
                                });
                        });
                }
            }
        },
        
        disable: function (evt) {
            // grey everything
            // (before leaving the page)
            this.el_b_today.button('option', 'disabled', true);
            this.el_bs_navigate.buttonset('option', 'disabled', true);

            /*
            this.el_dd_year.selectmenu('option', 'disabled', true);
            this.el_dd_month.selectmenu('option', 'disabled', true);
            this.el_dd_day.selectmenu('option', 'disabled', true);
            */
            this.el_dd_year.attr('disabled', true);
            this.el_dd_month.attr('disabled', true);
            this.el_dd_day.attr('disabled', true);

            this.el_bs_viewtype.buttonset('option', 'disabled', true);
            this.el_bs_term.buttonset('option', 'disabled', true);
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

            
            //if (this.el_dd_day.data('selectmenu')) {
            //    this.el_dd_day.selectmenu('destroy');
            //}

            var selection = this.options.selection || {};
            this.el_dd_day.empty();
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
                this.el_dd_day.append('<option value="' + i + '">' + i + '</option>');
            }

            // rebind
            //this.el_dd_day.find('option').addClass('karl-calendar-dropdown-item');
            /*
            this.el_dd_day.selectmenu({
                type: 'dropdown',
                select: function (evt, uiHash) {
                    var value = Number(uiHash.value);
                    if (value > 0 && self.options.selection.day != value) {
                        self.options.selection.day = value;
                        return self._change(evt);
                    }
                }
            });
            */
            // re-set the margin for this newly created element
            /*
            this.element.find('a.ui-selectmenu').each(function () {
                    $(this).css('margin-top', '-4px');
                }
            );
            */

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
            this.el_b_today.button('option', 'disabled', isToday);

            // select the selection date in the dropdowns

            this.el_dd_year.val('' + selection.year);
            this.el_dd_month.val('' + selection.month);
            this.el_dd_day.val('' + selection.day);
            //this.el_dd_year.selectmenu('value', '' + selection.year);
            //this.el_dd_month.selectmenu('value', '' + selection.month);
            //this.el_dd_day.selectmenu('value', '' + selection.day);

            var el_selected_viewtype = {
                calendar: this.el_b_calendar,
                list: this.el_b_list
            }[selection.viewtype];

            if (el_selected_viewtype) {
                el_selected_viewtype.attr('checked', 'checked');
            }
            this.el_bs_viewtype.buttonset('refresh');
           
            var el_selected_term = {
                day: this.el_b_day,
                week: this.el_b_week,
                month: this.el_b_month
            }[selection.term];

            if (el_selected_term) {
                el_selected_term.attr('checked', 'checked');
            }
            this.el_bs_term.buttonset('refresh');
        },

        destroy: function () {
            this.el_b_today.button('destroy');
            this.el_bs_navigate.buttonset('destroy');
            //this.el_dd_year.selectmenu('destroy');
            //this.el_dd_month.selectmenu('destroy');
            //if (this.el_dd_day.data('selectmenu')) {
            //    this.el_dd_day.selectmenu('destroy');
            //}
            this.el_bs_viewtype.buttonset('destroy');
            this.el_bs_term.buttonset('destroy');
            $.Widget.prototype.destroy.call(this);
        }

    });


})(jQuery);
