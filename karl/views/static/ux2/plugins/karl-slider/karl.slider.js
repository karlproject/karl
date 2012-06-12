
(function($){

/**
 * Extended slider
 */
var ui_slider = $.ui.slider;
$.widget('ui.karlslider', $.extend({}, ui_slider.prototype, {
    widgetName: 'karlslider',

    options: $.extend({}, ui_slider.prototype.options, {

        enableClickJump: false, // clicking will jump instead of positioning the slider
        jumpStep: undefined,    // unit of jump step. Should be a multiple of 'step'.
        enableKeyJump: false    // up-down keys will also use the jump unit instead of the step unit.
    }),

    _create: function() {
        var o = this.options;
        if (! o.jumpStep) {
            // jumpStep equals the step by default.
            o.jumpStep = o.step;
            o.alignStep = o.step;
        } else {
            // Well... there is one place, where it accesses o.step
            // directly, for the keys... and there is no way to override
            // this. So, we rename
            //      jumpStep -> step
            //      step ->     alignStep
            // and we will use alignStep instead of step everywhere else.
            o.alignStep = o.step;
            // o.step will _only_ be used for keys now (from keydown handler)
            o.step = o.enableKeyJump ? o.jumpStep : o.step;
        }
        ui_slider.prototype._create.call(this);
    },

    destroy: function() {
        ui_slider.prototype.destroy.call(this);
    },

    // Copypaste _mouseCapture 
    //
    _mouseCapture: function( event ) {
        var o = this.options,
            position,
            normValue,
            distance,
            closestHandle,
            self,
            index,
            allowed,
            offset,
            mouseOverHandle;

        if ( o.disabled ) {
            return false;
        }

        this.elementSize = {
            width: this.element.outerWidth(),
            height: this.element.outerHeight()
        };
        this.elementOffset = this.element.offset();

        position = { x: event.pageX, y: event.pageY };
        normValue = this._normValueFromMouse( position );
        distance = this._valueMax() - this._valueMin() + 1;
        self = this;
        this.handles.each(function( i ) {
            var thisDistance = Math.abs( normValue - self.values(i) );
            if ( distance > thisDistance ) {
                distance = thisDistance;
                closestHandle = $( this );
                index = i;
            }
        });

        // workaround for bug #3736 (if both handles of a range are at 0,
        // the first is always used as the one with least distance,
        // and moving it is obviously prevented by preventing negative ranges)
        if( o.range === true && this.values(1) === o.min ) {
            index += 1;
            closestHandle = $( this.handles[index] );
        }

        allowed = this._start( event, index );
        if ( allowed === false ) {
            return false;
        }
        this._mouseSliding = true;

        self._handleIndex = index;

        closestHandle
            .addClass( "ui-state-active" )
            .focus();
        
        offset = closestHandle.offset();
        mouseOverHandle = !$( event.target ).parents().andSelf().is( ".ui-slider-handle" );
        this._clickOffset = mouseOverHandle ? { left: 0, top: 0 } : {
            left: event.pageX - offset.left - ( closestHandle.width() / 2 ),
            top: event.pageY - offset.top -
                ( closestHandle.height() / 2 ) -
                ( parseInt( closestHandle.css("borderTopWidth"), 10 ) || 0 ) -
                ( parseInt( closestHandle.css("borderBottomWidth"), 10 ) || 0) +
                ( parseInt( closestHandle.css("marginTop"), 10 ) || 0)
        };

        normValue = this._normValueFromMouse( position );

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
                var mod = stepping % o.alignStep;
                if (mod > 0) {
                    // round upwards. So, always step.
                    stepping = stepping - mod + o.alignStep;
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
                this._animateOff = true;
                return false;
            }
        } else {
            // compatibility default
            this._slide(event, index, normValue);
            this._animateOff = true;
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

    // Handling the jumpStep differently from (alignStep) step.
    // (it is burned directly into the keydown handle and changing
    // it would require to replicate the whole _create)
    //
    // XXX options.step -> options.alignStep
    //
    // returns the alignStep-aligned value that val is closest to, between (inclusive) min and max
    _trimAlignValue: function( val ) {
        if ( val < this._valueMin() ) {
            return this._valueMin();
        }
        if ( val > this._valueMax() ) {
            return this._valueMax();
        }
        var step = ( this.options.alignStep > 0 ) ? this.options.alignStep : 1,
            valModStep = val % step,
            alignValue = val - valModStep;

        if ( Math.abs(valModStep) * 2 >= step ) {
            alignValue += ( valModStep > 0 ) ? step : ( -step );
        }

        // Since JavaScript has problems with large floats, round
        // the final value to 5 digits after the decimal point (see #4124)
        return parseFloat( alignValue.toFixed(5) );
    },

    _setOption: function(key, value) {
        if (key == 'jump') {
            this.options.alignStep = value;
            if (! this.options.enableKeyJump) {
                // set step the same, as jumpStep.
                this.options.step = value;
            }
        } else if (key == 'jumpStep') {
            this.options.jumpStep = value;
            if (this.options.enableKeyJump) {
                // set step the same, as jumpStep.
                this.options.step = value;
            }
        } else {
            ui_slider.prototype._setOption.apply(this, arguments);
        }
    }

}));

})(jQuery);

