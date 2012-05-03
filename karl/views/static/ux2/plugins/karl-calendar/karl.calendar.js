
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
        },

        _create: function () {
            var self = this;   

            this.el_b_today = this.element.find('.b-today');

            this.el_b_prev = this.element.find('.b-prev');
            this.el_b_next = this.element.find('.b-next');

            this.el_dd_year = this.element.find('.karl-calendar-dropdown-year');
            this.el_dd_month = this.element.find('.karl-calendar-dropdown-month');
            this.el_dd_day = this.element.find('.karl-calendar-dropdown-day');

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
                this.el_dd_year.append('<option value="' + i + '">' + i + '</option>');
            }


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
            this.el_dd_year.attr('disabled', true);
            this.el_dd_month.attr('disabled', true);
            this.el_dd_day.attr('disabled', true);
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

            this.el_dd_year.val('' + selection.year);
            this.el_dd_month.val('' + selection.month);
            this.el_dd_day.val('' + selection.day);

            
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


})(jQuery);
