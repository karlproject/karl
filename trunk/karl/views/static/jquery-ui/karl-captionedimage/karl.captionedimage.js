
(function($){

/**
 * Captioned images
 */
$.widget('karl.karlcaptionedimage', {

    options: {
        clsWrapper: 'karl-captionedimage-wrapper'
    },

    _create: function() {
        var self = this;
        this.wrapper = $('<div></div>');
        this.proxy = $('<img>').appendTo(this.wrapper);
        this.wrapper.append('<br />');
        this.caption = $('<span></span>').appendTo(this.wrapper);
        // Copy image attributes to proxy
        var captiontext = this.element.attr('alt');
        var width = this.element.attr('width');
        this.proxy
            .attr('alt', captiontext)
            .attr('width', width)
            .attr('height', this.element.attr('height'))
            .attr('src', this.element.attr('src'))
            .addClass('karl-captionedimage-image');
        // Copy image attributes to wrapper
        this.wrapper[0].style.cssText = this.element[0].style.cssText;
        // Copy the css from the original element to the wrapper
        this.wrapper
            .attr('class', this.element.attr('class'))
            .removeClass('tiny-imagedrawer-captioned')
            .addClass(this.options.clsWrapper)
            // Set width of the wrapper, to allow easy centering. 
            .width(width);
        // convert image alignment to wrapper
        var align = this.element.attr('align');
        if (align == 'left') {
            this.wrapper.css('float', 'left');
        } else if (align == 'right') {
            this.wrapper.css('float', 'right');
        }
        // set caption text
        this.caption
            .text(captiontext)
            .addClass('karl-captionedimage-caption');
        // wrap the image
        // centerer plays a role on IE
        // XXX inlines don't work currently, though:
        // they become centered.
        this.centerer = $('<div></div>')
            .css('text-align', 'center')
            .append(this.wrapper);
        this.element.after(this.centerer);
        this.element
            .hide()
            .appendTo(this.centerer);
    },

    _destroy: function() {
        // unwrap the image
        this.centerer.replaceWith(this.element);
        this.element.show();
        $.Widget.prototype.destroy.call( this );
    }

});


})(jQuery);

