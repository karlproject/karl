
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window document */
/*globals setTimeout clearTimeout setInterval */ 
/*globals jQuery alert confirm escape */



(function ($) {

    var log = function () {
        var c = window.console;
        if (c && c.log) {
            c.log(Array.prototype.slice.call(arguments));
        }
    };



    /**
     * Date time picker field
     *
     * Bound to a single input field. This field is made hidden, and
     * three input fields yyy-date yyy-hour and yyy-minute are created.
     * The date field is bound as an ui-datepicker.
     *
     */
    $.widget('ui.karldatetimepicker', {

        options: {
            zIndex: undefined
        },

        _create: function () {
            var self = this;
            if (! jQuery.nodeName(this.element[0], 'input')) {
                throw new Error('ui.karldatetimepicker can only be bound to <input> nodes.');
            }
            // Create a container to hold the new inputs.
            this.container = $('<span class="ui-karldatetimepicker-container"></span>');
            // Position the container after the old input element,
            // which in turn gets hidden.
            this.element
                .hide()
                .after(this.container);
            // Create the date and time inputs inside the container.
            this.dateinput = $('<input class="ui-karldatetimepicker-dateinput"></input>')
                .appendTo(this.container);
            // fix the z-index
            if (this.options.zIndex) {
                // The component will always set $(input).zIndex() + 1
                // as the z-index of the popup. However, for static
                // elements zIndex is always 0. This means that the
                // z-index will mostly be 1, which is a problem because
                // we have higher z-indexes (3) on certain elements, like
                // all old-style IE rounded corner hacks.
                //
                // So, we provide a way to set the z-index. But
                // we have to actually set it on the input we just created.
                // We also have to make it position relative, otherwise
                // the popup will not pick up the index we want.
                // Not very elegant.
                this.dateinput
                    .css('position', 'relative')
                    .zIndex(this.options.zIndex - 1);
            }
            this.dateinput
                .datepicker({
                })
                .change(function (evt) {
                    self.setDate($(evt.target).val());
                });

            this.hourinput = $('<select class="ui-karldatetimepicker-hourinput"></input>')
                .appendTo(this.container)
                .change(function (evt) {
                    self.setHour($(evt.target).val());
                });
            var i;
            for (i = 0; i < 24; i++) {
                $('<option>')
                    .val(i)
                    .text(i)
                    .appendTo(this.hourinput);
            }
            this.container.append('<span class="ui-karldatetimepicker-colon">:</span>');
            this.minuteinput = $('<select class="ui-karldatetimepicker-hourinput"></input>')
                .appendTo(this.container)
                .change(function (evt) {
                    self.setMinute($(evt.target).val());
                });
            for (i = 0; i < 4; i++) {
                var strmin = ('0' + i * 15).slice(-2);
                $('<option>')
                    .val(strmin)
                    .text(strmin)
                    .appendTo(this.minuteinput);
            }
     
            // Set composite value from the input element's content.
            this.set(this.element.val());
        },

        // set the composite value (as string)
        set: function (value) {
            // Split the value
            // Everything before the first space goes to date, the rest to time
            var split_pos = value.search(' ');
            var timestr = value.substr(split_pos + 1);
            // Time is further split to hours and minutes by the colon
            var time_split_pos = timestr.search(':');
            this.composite_value = {
                datestr: value.substr(0, split_pos),
                hourstr: value.substr(split_pos + 1, time_split_pos).replace(/^0/, ''),
                minutestr: value.substr(split_pos + time_split_pos + 2)
            };
            // Sets all input values we manage
            this.dateinput.val(this.composite_value.datestr);
            this.hourinput.val(this.composite_value.hourstr);
            this.minuteinput.val(this.composite_value.minutestr);
            this.element.val(value);
            this.element.trigger('change.karldatetimepicker');
        },

        // Set date part (as string)
        setDate: function (value) {
            // Remember the value, so we are always in possession
            // of the full array of values we composite
            this.composite_value.datestr = value;
            this.dateinput.val(this.composite_value.datestr);
            this._updateComposite();
        },

        // Set hour part (as string)
        setHour: function (value) {
            // Remember the value, so we are always in possession
            // of the full array of values we composite
            this.composite_value.hourstr = value;
            this.hourinput.val(this.composite_value.hourstr);
            this._updateComposite();
        },

        // Set minute part (as string)
        setMinute: function (value) {
            // Remember the value, so we are always in possession
            // of the full array of values we composite
            this.composite_value.minutestr = value;
            this.minuteinput.val(this.composite_value.minutestr);
            this._updateComposite();
        },

        _updateComposite: function () {
            // Update the composite value, which will be submitted in the original
            // input.
            var value = this.composite_value.datestr + ' ' + 
                        this.composite_value.hourstr + ':' + this.composite_value.minutestr;
            this.element.val(value);
            this.element.trigger('change.karldatetimepicker');
        },

        // gets the value as a javascript Date object
        getAsDate: function () {
            // XXX how to handle invalid date exceptions?
            return new Date(Date.parse(this.element.val()));
        },

        // gets the value as a javascript Date object
        setAsDate: function (da) {
            var _pad = function (num) {
                var str = '0' + num;
                return str.substr(str.length - 2, 2);
            }
            // Format the date as string
            // (Re: da.getMonth() + 1, thank you javascript for making my day, ha ha.)
            var datestring = _pad(da.getMonth() + 1) + '/' + _pad(da.getDate()) + '/' + da.getFullYear() +
                ' ' + _pad(da.getHours()) + ':' + _pad(da.getMinutes());
            // set the value
            this.set(datestring);
        },

        // limit minimum or maximum.
        // minval and maxval have to be javascript Date objects, or null.
        limitMinMax: function (minval, maxval) {
            var value = this.getAsDate();
            var set_value = null;
            if (minval && value < minval) {
                set_value = minval;
            }
            if (maxval && value > maxval) {
                set_value = maxval;
            }
            if (set_value !== null) {
                // Element changed.
                this.setAsDate(set_value);
                this.dateinput.effect("pulsate", {times: 1}, 800);
                
                if (this.hourinput.is(":visible")) {
                    this.hourinput.effect("pulsate", {times: 1}, 800);
                    this.minuteinput.effect("pulsate", {times: 1}, 800);
                }
                
            }

        }

    });


    // Extend a datetimepicker with an all-day selector.

    $.widget('karl.karldatetimeallday', {
    
        options: {
            //startField: null,
            //endField: null
        },

        _create: function () {
            var self = this; 
            var checked;

            if (this.element.val() == 'True') {
                checked = 'checked="checked"'; 
                this.hideEditCalendarEventTimes();
            } else {
                checked = '';
                this.showEditCalendarEventTimes();
            }

            // add the "all-day" checkbox
            var checkbox = $('<span class="all_day">' +
                          '<input type="checkbox" name="allDay" ' + checked + ' />' + 
                          '<label for="cal_all_day">All-day</label>' + 
                         '</span>');
            $(this.options.startField).find('> div.inputs')
                .append(checkbox);

            // all-day checkbox handler
            checkbox.click(function () {
                self.removeEditCalendarEventValidationErrors();
                if (this.checked) {
                    self.element.val('True');
                    self.hideEditCalendarEventTimes();      
                } else {
                    self.element.val('False');
                    self.showEditCalendarEventTimes();
                }
            });
        },

        hideEditCalendarEventTimes: function () {
            var start = $(this.options.startField);
            var end = $(this.options.endField);
            start.find('select').hide();
            start.find('.ui-karldatetimepicker-colon').hide();
            end.find('select').hide();
            end.find('.ui-karldatetimepicker-colon').hide();
        },

        showEditCalendarEventTimes: function () {
            var start = $(this.options.startField);
            var end = $(this.options.endField);
            start.find('select').show();
            start.find('.ui-karldatetimepicker-colon').show();
            end.find('select').show();
            end.find('.ui-karldatetimepicker-colon').show();
        },

        removeEditCalendarEventValidationErrors: function () {
            var start = $(this.options.startField);
            var end = $(this.options.endField);
            start.removeClass('error');
            start.find('> span.error').remove();
            end.removeClass('error');
            end.find('> span.error').remove();
        }
     
    });

})(jQuery);
