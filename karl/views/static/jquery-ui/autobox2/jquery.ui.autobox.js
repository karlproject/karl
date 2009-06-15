/**
 * jQuery Autobox Plugin
 * Copyright (c) 2008 Big Red Switch
 *
 * http://www.bigredswitch.com/blog/2008/12/autobox2/
 *
 * Dual licensed under the BSD and GPL licenses:
 *  http://en.wikipedia.org/wiki/Bsd_license
 *  http://en.wikipedia.org/wiki/GNU_General_Public_License
 *
 * 0.7.1 : Add prepop to options to pre-populate autobox
 *         Add addBox function to populate autobox via JS
 *         (css) Add margin-bottom to .bit-box
 * 0.7.0 : Initial version
 *         Rolled up autocomplete and autotext plugins
 *
 * ****************************************************************************
 *
 * jQuery Autocomplete
 * Written by Yehuda Katz (wycats@gmail.com) and Rein Henrichs (reinh@reinh.com)
 * Copyright 2007 Yehuda Katz, Rein Henrichs
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Facebook style text list from Guillermo Rauch's mootools script:
 *  http://devthought.com/textboxlist-fancy-facebook-like-dynamic-inputs/
 *
 * Caret position method: Diego Perini: http://javascript.nwbox.com/cursor_position/cursor.js
 *
 * 2009 Changes by Balazs Ree <ree@greenfinity.hu>
 * - change the code to be more OO and offer a reusable widget
 *
 */
(function($){

  function LOG(obj){
    if(console && console.log){
      console.log(obj);
    }
    else{
      var cons=$('#log');
      if(!cons){cons=$('<div id="log"></div>');}
      if(cons){cons.append(obj).append('<br/>\n');}
    }
  }

  $.fn.resizableTextbox=function(el, options) {
    var opts=$.extend({ min: 5, max: 500, step: 7 }, options);
    var width=el.attr('offsetWidth');
    el.bind('keydown', function(e) {
        $(this).data('rt-value', this.value.length);
    })
    .bind('keyup', function(e) {
        var self=$(this);
        var newsize=opts.step * self.val().length;
        if (newsize <= opts.min) {
          newsize=width;
        }
        if (!(self.val().length == self.data('rt-value') ||
              newsize <= opts.min || newsize >= opts.max)) {
          self.width(newsize);
        }
     });
  };

  $.ui=$.ui || {}; $.ui.autobox=$.ui.autobox || {}; var count=0;

  var KEY={
    ESC: 27,
    RETURN: 13,
    TAB: 9,
    BS: 8,
    DEL: 46,
    LEFT: 37,
    RIGHT: 39,
    UP: 38,
    DOWN: 40
  };

  // Only used if directly $.fn.autobox is used
  function addBox(input, text, name){
    throw 'Wrong addBox!';
  }

$.widget('ui.autobox3', {
  //$.fn.autobox=function(opt)

    _init: function() {

        var t = this;
        var opt = this.options;

        if($.ui.autobox.ext){
          for(var ext in $.ui.autobox.ext){
            if(opt[ext]){
              this.options = opt = $.extend(opt, $.ui.autobox.ext[ext](opt));
              delete opt[ext];
            }
        } }

        // setup the widget
        t._setupWidget();

        // populate methods from options
        if (opt.getList) this._getList = opt.getList;
        if (opt.getBoxFromSelection) this._getBoxFromSelection = opt.getBoxFromSelection;
        if (opt.getBoxOnEnter) this._getBoxOnEnter = opt.getBoxOnEnter;

        this.active = null;
        this.hovered = null;
        this.off();
    },

    _bindInput: function(input) {
        var opt = this.options;
        var t = this;
        var self = this;

        // Some closed functions
        function preventTabInAutocompleteMode(e){
          var k=e.which || e.keyCode;
          if(self.activelist.is_active && k == KEY.TAB){
            e.preventDefault();
          }
        }
        function startTypingTimeout(e, input, timeout){
          $.data(input, "typingTimeout", window.setTimeout(function(){
            $(e.target || e.srcElement).trigger("autobox");
          }, timeout));
        }
        function clearTypingTimeout(input){
            var typingTimeout=$.data(input, "typingTimeout");
            if(typingTimeout) window.clearInterval(typingTimeout);
        }
        // set up the input using the above closed functions
        input
            .keydown(function(e){
              preventTabInAutocompleteMode(e);
            })
            .keyup(function(e){
              var k=e.which || e.keyCode;
              if(! self.activelist.is_active &&
                  (k == KEY.UP || k == KEY.DOWN)){
                clearTypingTimeout(this);
                startTypingTimeout(e, this, 0);
              }
              else{
                preventTabInAutocompleteMode(e);
              }
            })
            .keypress(function(e){
              var k=e.keyCode || e.which; // keyCode == 0 in Gecko/FF on keypress
              clearTypingTimeout(this);
              if($.data(document.body, "suppressKey")){
                $.data(document.body, "suppressKey", false);
                //note that IE does not generate keypress for arrow/tab keys
                if(k == KEY.TAB || k == KEY.UP || k == KEY.DOWN) return false;
              }
              if(self.activelist.is_active && k < 32 && k != KEY.BS && k != KEY.DEL) return false;
              else if(k == KEY.RETURN){
                var record = t._getBoxOnEnter();
                if (record) { t._addBox(record); }
                e.preventDefault();
              }
              else if(k == KEY.BS || k == KEY.DEL || k > 32){ // more than ESC and RETURN and the like
                startTypingTimeout(e, this, opt.timeout);
              }
            })
            .bind("autobox", function(){
              var self=$(this);
              self.one("updateList", function(e, list){//clear/update/redraw list
                t._updateList(list);
              });
              t._getList(self, t._getCurrentValsHash(self));
            })

            // Bind key event in active mode to input
            .bind("keydown.autobox", function(e){
                // Prevent if the list is not active
                if (! self.activelist.is_active) { return true; }
                var k = e.which || e.keyCode;
                if (k == KEY.ESC) {
                    self.cancel();
                } else if (k == KEY.RETURN) { 
                    // pressing return in the input will do the activation,
                    // which in turn triggers the adding of the current value.
                    self.activate();
                    e.preventDefault();
                    }
                else if(k == KEY.UP || k == KEY.TAB || k == KEY.DOWN){
                    var keystep = (k == KEY.UP) ? -1 : 1;
                    var index = -1;
                    var hlength = self.activelist.hoverable.length;
                    if (self.hovered) {
                        index = self.activelist.hoverable.index(self.hovered);
                    }
                    index += keystep;
                    if (index >= hlength) {
                        index = 0;
                    } else if (index < 0) {
                        index = hlength - 1;
                    }
                    self._setActive(self.activelist.hoverable.eq(index));
                } else { return true; }
                $.data(document.body, "suppressKey", true);
              });


        return input;
    },
    
    _updateList: function(list){
        var self = this;
        var opt = this.options;
        // input may not be set at this point...
        var val = this.input && this.input.val() || '';
        list = $(list)
            .filter(function() {
                return opt.match.call(this, val);
            })
            .map(function() {
                var node=$(opt.template.call(self, this))[0];
                $.data(node, "originalObject", this);
                return node;
            });
        this.off();
        if (!list.length) return false;
        
        var container = list.wrapAll(opt.wrapper).parents(":last").children();
        // IE seems to wrap the wrapper in a random div wrapper so
        // drill down to the node in opt.wrapper.
        var wrapper_tagName = $(opt.wrapper)[0].tagName;
        for(; container[0].tagName !== wrapper_tagName; container=container.children(':first')) {}

        var offset = this.input.offset();
        this.container = container
            .css({
                top: offset.top + this.input.outerHeight(),
                left: offset.left
            })
            .appendTo("body");

        // set the container to the minimum of the input field's width,
        // but leave it if it already extends the input.
        // Also maximize to max_width.
        var container_width = Math.max(container.width(), this.input.width());
        container_width = Math.min(container_width, this.options.maxSearchContainerWidth);
        this.container
            .css({
                width: container_width
            });

        this.activelist = {
            is_active: true,
            original: this.input.val(),
            list: list,
            // Hoverables are by default the li's, but this
            // can be changed from options.
            // XXX Current code only works if the hoverables
            // are not embedded in more levels of li's.
            hoverable: container.find(this.options.selectHoverable)
        };

       this.activelist.hoverable
            .hover(
                function() {
                    self._setActive(this);
                },
                function() {
                    self._unsetActive();
                }
            );

        container
            .bind("click.autobox", function(e) {
                self.activate();
                $.data(document.body, "suppressKey", false);
            });

    },

    //return the currently selected values as a hash
    _getCurrentValsHash: function(input){
        var vals = input.parent().parent().find('li');
        var hash = {};
        for (var i=0; i < vals.length; ++i) {
            var s = vals[i].innerHTML.match(/^[^<]+/);
            if (s) {
                hash[s]=true;
            }
        }
        return hash;
    },

    _createHolder: function (element) {
        var input = this._bindInput($('<input type="text"></input>'));
        var holder=$('<ul class="autobox-hldr"></ul>')
            .append($('<li class="autobox-input"></li>')
            .append(input));
        $.fn.resizableTextbox(input, $.extend(this.options.resizable, { min: input.attr('offsetWidth'), max: holder.width() }));
        return holder;
    },

    _setupWidget: function() {
        var self = this;

        // create and wire up widget from above functions 
        var opt = this.options;
        var e = this.element;
        this.holder = this._createHolder(e).insertAfter(e);
        this.input = this.holder.find('input');
        e.removeAttr('name');
        e.hide();

        // set starting values
        if(opt.prevals) {
            for(var i in opt.prevals) {
                this._addBox(opt.prevals[i], true);
            }
        }

        // to be sure there is no FF-autocomplete
        this.input.attr('autocomplete', 'off');

        // If a click bubbles all the way up to the window, close the autobox
        // (Note, bind to document and not to windows.
        // If windows is used, event does not bubble up on IE.
        $(document).bind("click.autobox", function(){
            self.cancel();
        });

    },
    
    // This used to be in options. We keep that possibility.
    _getList: function(input, hash){
        var list = this.options.list;
        if(hash){ list=$(list).filter(function(){  return !hash[this.text]; }); }
        input.trigger("updateList", [list]);
    },

    _addBox: function(record, /*optional*/ initializing){
        var self = this;
        var input = this.input;
        var name = this.options.name;
        var ii = $('<input type="hidden"></input>');ii.attr('name', name);ii.val(record.tag);
        var li=$('<li class="bit-box"></li>').attr('id', 'bit-' + count++).text(record.tag);
        li.append($('<a href="#" class="closebutton"></a>')
              .bind('click', function(e) {
                  self._delBox(li);
                  e.preventDefault();
              }))
          .append(ii);
        input.parent().before(li);
        input.val('');
    },

    // Keep original stub on the API.
    addBox: function (text, /*optional*/ initializing){
        return this._addBox({tag: text}, initializing);
    },

    // Produce the tag record if enter is pressed, ie text typed in.
    // The method has a way to prevent adding the box if
    // nothing is returned.
    _getBoxOnEnter: function(){
        var val = this.input.val();
        if (val) {
            return {tag: val};
        }
        // Prevent add from happening.
        return;
    },

    _getBoxFromSelection: function() {
        return {tag: $.data(this.active[0], "originalObject").text};
    },

    _delBox: function(li) {
        li.remove();
    },

    activate: function() {
        // Try hitting return to activate autobox and then hitting it again on blank input
        // to close it.  w/o checking the active object first this input.trigger() will barf.
        if(this.active && this.active[0] && $.data(this.active[0], "originalObject")){
            // Adding a value from the search results selection
            this._addBox(this._getBoxFromSelection());
        } else {
            // Adding the typed in value
            // We generate the record first...
            // (null result means we need not add it)
            var record = this._getBoxOnEnter();
            if (record) { this._addBox(record); }
        }
        if (this.active) {
            this.input.trigger("activate.autobox", [$.data(this.active[0], "originalObject")]);
        }
        //this.active && this.input.trigger("activate.autobox", [$.data(this.active[0], "originalObject")]);
        //$("body").trigger("off.autobox");
        this.off();
    },

    off: function() {
        if (this.container) {
          this.container.remove();
          this.container = null;
        }
        this.activelist = {is_active: false};
          //this.input.unbind("keydown.autobox");
          //$("body").add(window).unbind("click.autobox").unbind("cancel.autobox").unbind("activate.autobox");
    },
         
    _setActive: function(el) {
        if (! this.activelist.is_active) {
            return;
        }
        this._unsetActive();
        var el = $(el)
        this.hovered = el;
        // Find the active parent, which is the li containing the hovered element
        this.active = el.is('li') ? el : el.parents('li').eq(0);
        // add the classes
        this.hovered.addClass('hover');
        this.active.addClass('active');
        // do the selection
        this.input.trigger("itemSelected.autobox", [$.data(this.active[0], "originalObject")]);
        this._handleActive()
    },

    _handleActive: function() {
        this.input.val(this.options.insertText($.data(this.active[0], "originalObject")));
    },

    _unsetActive: function() {
        this.activelist.list.removeClass('active');
        this.activelist.hoverable.removeClass('hover');
        this.active = null;
        this.hovered = null;
    },

    cancel: function() {
        this.input.trigger("cancel.autobox");
        // revert value to the one before we activated the autobox
        this.input.val(this.activelist.original);
        this.off();
    }

});   // END widget ui.autobox3

$.extend($.ui.autobox3, {
    defaults: {
        timeout: 500,
        template: function(str) {
            return "<li>" + this.options.insertText(str) + "</li>";
        },
        insertText: function(str) {
            return str;
        },
        match: function(typed) {
            return this.match(new RegExp(typed));
        },
        wrapper: '<ul class="autobox-list"></ul>',
        resizable: {},
        selectHoverable: '> li',
        // if specified, a query starts at minimum this many characters
        minQueryLength: 0,
        // maximum width of the search container
        maxSearchContainerWidth: 400
    }
});


})(jQuery);
