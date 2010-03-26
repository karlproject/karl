(function($){

/* XXX we repeat the namespace as a prefix of the name,
 * because ui creates a global jQuery plugin with the name
 * only */
$.widget('karl.karlbuttonset', {

    _init: function() {
        var self = this;
        
        // fetch parameters from original markup
        if (this.element.is('select')) {
            // Markup for single/multiple selector buttons:
            //
            // qualifier classes are:
            // "karl-buttonset-compact" or "compact"
            // "karl-buttonset-icons-only" or "icons-only"
            //
            // <select id="buttons2" name="buttons2" multiple="single"
            //         class="compact icons-only">
            //   <option value="Save" class="ui-icon-disk" selected="selected">Save</option>
            //   <option value="Delete" class="ui-icon-trash">Delete</option>
            // </select>
            //
            this.selectionType = this.element.attr('multiple') ? 'M' : 'S';
        } else {
            // Markup for pushable selector buttons:
            //
            // qualifier classes are:
            // "karl-buttonset-compact" or "compact"
            // "karl-buttonset-icons-only" or "icons-only"
            //
            // <div id="buttons1" class="compact icons-only">
            //   <button class="ui-icon-disk">Save</button>
            //   <button class="ui-icon-trash">Delete</button>
            //  </div>
            //
            this.selectionType = '';
        }
        this.compact = this.element.is('.compact') ||
                       this.element.is('.karl-buttonset-compact');
        this.iconsOnly = this.element.is('.icons-only') ||
                       this.element.is('.karl-buttonset-icons-only');

        // calculate classes needed to create the widget markup
        var clsContainer = 'fg-buttonset ui-helper-clearfix ';
        var clsButton = 'fg-button ui-state-default';
        if (this.compact) {
            clsContainer += ' fg-buttonset-single'; 
            //clsButton += ' ui-priority-primary'; // XXX ???
            // corners will be added to 1st and last button only
        } else {
            // corners added to all buttons
            clsButton += ' ui-corner-all';
        }

        if (this.options.clsContainer) {
            clsContainer += ' ' + this.options.clsContainer;
        }

        // wrap the element
        this.element.wrap('<div></div>');
        this.wrapper = this.element.parent();
        // make widget appear bound on wrapper
        this.wrapper.data(this.widgetName, this);
        // make original element disappear
        this.originalWasHidden = this.element.hasClass('ui-helper-hidden');
        this.element.addClass('ui-helper-hidden');

        // apply container class on the wrapper
        this.wrapper
            .addClass(clsContainer);

        // build buttons based on the original element
        this.buttons = []
        this.element.children().each(function(button_index) {
            var button = $(this);
            var text = button.text();
            // XXX XXX Need to test for title attr handling!
            var title = button.attr('title') || text;
            var icon_class = button.attr('class');
            var selected = button.attr('selected');
            var disabled = button.attr('disabled');
            
            var icon = '';
            if (icon_class) {
                icon = '<span class="ui-icon ' + icon_class + '"/>';
            }
            var button_class = clsButton;
            // handle disabled and selected state
            // XXX XXX skip this as it does not look good with our skin.
            // XXX XXX This breaks tests!
            if (false && disabled) {
                button_class += ' ui-state-disabled';
            } else {
                if (selected) {
                    button_class += ' ui-state-active';
                }
            }
            if (self.iconsOnly) {
                button_class += ' fg-button-icon-solo';
            } else if (icon_class) {
                button_class += ' fg-button-icon-right';
                // TODO fg-button-icon-left could be supported too
            }


            var new_button = $('<span class="' + button_class + '"><a' +
                       '     title="' + title + '" href="#">' +
                       icon +
                       text +
                       '</a></span>');
            new_button
                .appendTo(self.wrapper)
                // Clicking on buttons
                .click(function(event) {
                    // Only act if the button is currently enabled.
                    if (! new_button.hasClass('ui-state-disabled')) {
                        self._click(button_index); 
                    }
                    // Needs to prevent default in all cases. We never
                    // want to follow the # link which is the default href
                    // for the buttons.
                    event.preventDefault();
                })
                .hover(
                    function() {
                        // Only add the cue if the button is not disabled
                        if (! new_button.hasClass('ui-state-disabled')) {
                            new_button.addClass('ui-state-hover');
                        }
                    },
                    function() { new_button.removeClass('ui-state-hover'); }
                );
            self.buttons.push(new_button[0]);
        });
        this.buttons = $(this.buttons);

        // arrange corners for first and last button
        if (this.compact) {
            this.buttons.eq(0).addClass('ui-corner-left');
            this.buttons.eq(this.buttons.length - 1).addClass('ui-corner-right');
        }

    },

    destroy: function() {
        if (this.wrapper.parent().length) {
            // avoid running this twice.
            this.wrapper.removeData(this.widgetName, this);
            this.element.removeData(this.widgetName, this);
            if (! this.originalWasHidden) {
                this.element.removeClass('ui-helper-hidden');
            }
            this.element.insertAfter(this.wrapper);
            this.wrapper.remove();
        }
    },

    // Gets the button control with the given index
    getButton: function(button_index) {
        return this.buttons.eq(button_index);
    },

    _click: function(button_index) {
        var self = this;
        if (this.selectionType == 'M') {
            var button = this.buttons.eq(button_index);
            button.toggleClass('ui-state-active');
            self._change(button_index, button.hasClass('ui-state-active'));
        } else if (this.selectionType == 'S') {
            var changed = false;
            this.buttons.each(function(index) {
                if (index != button_index) {
                    var button = $(this);
                    if (button.hasClass('ui-state-active')) {
                        button.removeClass('ui-state-active');
                        self._change(index, false);
                    }
                }
            });
            var new_button = this.buttons.eq(button_index);
            if (! new_button.hasClass('ui-state-active')) {
                new_button.addClass('ui-state-active');
                self._change(button_index, true);
            }
        } else { // selectionType == 'none'
            self._change(button_index, true);
        }
    },

    _change: function(button_index, value) {
        // update the event on the original element
        if (this.selectionType != '') {
            this.element.children().eq(button_index).attr('selected', value);
        }
        // trigger the change event on both the original and wrapper node.
        // We only trigger on the original node, it will bubble out.
        this.element.trigger('change.karlbuttonset', [button_index, value]);
    }

});

$.extend($.karl.karlbuttonset, {
    getter: 'getButton',
    defaults: {
        clsContainer: null
    }
});


})(jQuery);

