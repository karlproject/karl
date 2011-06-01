

/* this is also contained in karl.js, so if karl.js is included
 * we do not need this file. It is included for testing.
 */


$.widget('karl.karldialog', $.extend({}, $.ui.dialog.prototype, {

    options: $.extend({}, $.ui.dialog.prototype.options, {
        autoOpen: false,
        modal: true,
        bgiframe: true,    // XXX bgiFrame is currently needed for modal
        hide: 'fold'
    }),

    /* Need to replicate this, because we do not want
     * to scroll down to the first tabbable element when
     * the dialog opens. */
    open: function() {
        if (this._isOpen) { return; }

        var options = this.options,
            uiDialog = this.uiDialog;

        this.overlay = options.modal ? new $.ui.dialog.overlay(this) : null;
        (uiDialog.next().length && uiDialog.appendTo('body'));
        this._size();
        this._position(options.position);
        uiDialog.show(options.show);
        this.moveToTop(true);

        // prevent tabbing out of modal dialogs
        (options.modal && uiDialog.bind('keypress.ui-dialog', function(event) {
            if (event.keyCode != $.ui.keyCode.TAB) {
                return;
            }

            var tabbables = $(':tabbable', this),
                first = tabbables.filter(':first')[0],
                last  = tabbables.filter(':last')[0];

            if (event.target == last && !event.shiftKey) {
                setTimeout(function() {
                    first.focus();
                }, 1);
            } else if (event.target == first && event.shiftKey) {
                setTimeout(function() {
                    last.focus();
                }, 1);
            }
        }));

        //// set focus to the first tabbable element in the content area or the first button
        //// if there are no tabbable elements, set focus on the dialog itself
        //$([])
        //    .add(uiDialog.find('.ui-dialog-content :tabbable:first'))
        //    .add(uiDialog.find('.ui-dialog-buttonpane :tabbable:first'))
        //    .add(uiDialog)
        //    .filter(':first')
        //    .focus();
        // XXX Always focus on the dialog itself
        uiDialog.focus();

        this._trigger('open');
        this._isOpen = true;
    },

    // allow to use position on the dialog directly.
    // like: el.karldialog('position', {...});
    // Why is this good? Because, it seems the 'position' option
    // has a different semantics from the newest option plugin.
    // This allows positioning with the same parameters as the
    // option plugin, but without a need to look up the dialog object.
    position: function(param) {
        return this.uiDialog.position(param);
    }


}));


