
(function($){

/**
 * Extended slider
 */
var ui_slider = $.ui.slider;
$.widget('karl.karlslider', $.extend({}, ui_slider.prototype, {

    _init: function() {
        var o = this.options;
        if (! o.jumpStep) {
            // jumpStep equals the step by default.
            o.jumpStep = o.step;
        }
        ui_slider.prototype._init.call(this);
    },

    destroy: function() {
        ui_slider.prototype.destroy.call(this);
    },

    // Copypaste _mouseCapture 
    _mouseCapture: function(event) {

        var o = this.options;

        if (o.disabled)
            return false;

        this.elementSize = {
            width: this.element.outerWidth(),
            height: this.element.outerHeight()
        };
        this.elementOffset = this.element.offset();

        var position = { x: event.pageX, y: event.pageY };
        var normValue = this._normValueFromMouse(position);

        var distance = this._valueMax() + 1, closestHandle;
        var self = this, index;
        this.handles.each(function(i) {
            var thisDistance = Math.abs(normValue - self.values(i));
            if (distance > thisDistance) {
                distance = thisDistance;
                closestHandle = $(this);
                index = i;
            }
        });

        // workaround for bug #3736 (if both handles of a range are at 0,
        // the first is always used as the one with least distance,
        // and moving it is obviously prevented by preventing negative ranges)
        if(o.range == true && this.values(1) == o.min) {
            closestHandle = $(this.handles[++index]);
        }

        this._start(event, index);

        self._handleIndex = index;

        closestHandle
            .addClass("ui-state-active")
            .focus();
        
        var offset = closestHandle.offset();
        var mouseOverHandle = !$(event.target).parents().andSelf().is('.ui-slider-handle');
        this._clickOffset = mouseOverHandle ? { left: 0, top: 0 } : {
            left: event.pageX - offset.left - (closestHandle.width() / 2),
            top: event.pageY - offset.top
                - (closestHandle.height() / 2)
                - (parseInt(closestHandle.css('borderTopWidth'),10) || 0)
                - (parseInt(closestHandle.css('borderBottomWidth'),10) || 0)
                + (parseInt(closestHandle.css('marginTop'),10) || 0)
        };

        normValue = this._normValueFromMouse(position);
        
        if (this.options.enableClickJump) {
            var current = this.values(index);
            var delta = normValue - current; 
            if (delta == 0) {
                // clicked on handle. Do not slide, but permit the mouse capture.
                //console.log('nulldelta', normValue);
                return true;
            } else {
                var stepping = o.jumpStep;
                // mod the stepping with the step
                var mod = stepping % o.step;
                if (mod > 0) {
                    // round upwards. So, always step.
                    stepping = stepping - mod + o.step;
                }
                var value;
                if (delta < 0) {
                    value = current - stepping;
                } else {
                    value = current + stepping;
                }

                //console.log('stepping', normValue,  stepping);
                // value will be limited into the range from _slide.
                this._slide(event, index, value);
                // Prevent the capture.
                this._mouseStop(event);
                return false;
            }
        } else {
            // compatibility default
            this._slide(event, index, normValue);
            return true;
        }

    },
    
    _slide: function(event, index, newVal) {
        // limit the value with the minimum and maximum
        // this will make limits effective for both click and key movements
        // as the clicks don't do limitation, this is crucial for enableKeyJump
	newVal = Math.max(newVal, this._valueMin());
	newVal = Math.min(newVal, this._valueMax());
        // (XXX should also mod it here ???, otherwise key movements could fall
        // out the step grid if jumpStep is not a multiple of step)
        ui_slider.prototype._slide.call(this, event, index, newVal);
    },

    _step: function() {
        var o = this.options;
        return o.enableKeyJump ? o.jumpStep : o.step;
    }

}));

$.extend($.karl.karlslider, {
    getter: ui_slider.getter,
    version: ui_slider.version + "-1.1",
    eventPrefix: ui_slider.eventPrefix,
    defaults: $.extend({}, ui_slider.defaults, {
        enableClickJump: false, // clicking will jump instead of positioning the slider
        jumpStep: undefined,    // unit of jump step. Should be a multiple of 'step'.
        enableKeyJump: false    // up-down keys will also use the jump unit instead of the step unit.
    })
});


})(jQuery);

