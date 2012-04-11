(function($) {

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

$.widget('popper.example', {

    options: {
        label: 'Hello World!'
    },

    _create: function() {
        var self = this;
        // save the old text
        this.oldText = this.element.text();
        this.element.text(this.options.label);
    },

    destroy: function() {
        this.element.text(this.oldText);
        $.Widget.prototype.destroy.call(this);
    }

});


})(jQuery);
