/* Copyright (c) 2006 Brandon Aaron (http://brandonaaron.net)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 *
 * $LastChangedDate: 2007-07-21 18:44:59 -0500 (Sat, 21 Jul 2007) $
 * $Rev: 2446 $
 *
 * Version 2.1.1
 */

(function($){

/**
 * The bgiframe is chainable and applies the iframe hack to get 
 * around zIndex issues in IE6. It will only apply itself in IE6 
 * and adds a class to the iframe called 'bgiframe'. The iframe
 * is appeneded as the first child of the matched element(s) 
 * with a tabIndex and zIndex of -1.
 * 
 * By default the plugin will take borders, sized with pixel units,
 * into account. If a different unit is used for the border's width,
 * then you will need to use the top and left settings as explained below.
 *
 * NOTICE: This plugin has been reported to cause perfromance problems
 * when used on elements that change properties (like width, height and
 * opacity) a lot in IE6. Most of these problems have been caused by 
 * the expressions used to calculate the elements width, height and 
 * borders. Some have reported it is due to the opacity filter. All 
 * these settings can be changed if needed as explained below.
 *
 * @example $('div').bgiframe();
 * @before <div><p>Paragraph</p></div>
 * @result <div><iframe class="bgiframe".../><p>Paragraph</p></div>
 *
 * @param Map settings Optional settings to configure the iframe.
 * @option String|Number top The iframe must be offset to the top
 * 		by the width of the top border. This should be a negative 
 *      number representing the border-top-width. If a number is 
 * 		is used here, pixels will be assumed. Otherwise, be sure
 *		to specify a unit. An expression could also be used. 
 * 		By default the value is "auto" which will use an expression 
 * 		to get the border-top-width if it is in pixels.
 * @option String|Number left The iframe must be offset to the left
 * 		by the width of the left border. This should be a negative 
 *      number representing the border-left-width. If a number is 
 * 		is used here, pixels will be assumed. Otherwise, be sure
 *		to specify a unit. An expression could also be used. 
 * 		By default the value is "auto" which will use an expression 
 * 		to get the border-left-width if it is in pixels.
 * @option String|Number width This is the width of the iframe. If
 *		a number is used here, pixels will be assume. Otherwise, be sure
 * 		to specify a unit. An experssion could also be used.
 *		By default the value is "auto" which will use an experssion
 * 		to get the offsetWidth.
 * @option String|Number height This is the height of the iframe. If
 *		a number is used here, pixels will be assume. Otherwise, be sure
 * 		to specify a unit. An experssion could also be used.
 *		By default the value is "auto" which will use an experssion
 * 		to get the offsetHeight.
 * @option Boolean opacity This is a boolean representing whether or not
 * 		to use opacity. If set to true, the opacity of 0 is applied. If
 *		set to false, the opacity filter is not applied. Default: true.
 * @option String src This setting is provided so that one could change 
 *		the src of the iframe to whatever they need.
 *		Default: "javascript:false;"
 *
 * @name bgiframe
 * @type jQuery
 * @cat Plugins/bgiframe
 * @author Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net)
 */
$.fn.bgIframe = $.fn.bgiframe = function(s) {
	// This is only for IE6
	if ( $.browser.msie && /6.0/.test(navigator.userAgent) ) {
		s = $.extend({
			top     : 'auto', // auto == .currentStyle.borderTopWidth
			left    : 'auto', // auto == .currentStyle.borderLeftWidth
			width   : 'auto', // auto == offsetWidth
			height  : 'auto', // auto == offsetHeight
			opacity : true,
			src     : 'javascript:false;'
		}, s || {});
		var prop = function(n){return n&&n.constructor==Number?n+'px':n;},
		    html = '<iframe class="bgiframe"frameborder="0"tabindex="-1"src="'+s.src+'"'+
		               'style="display:block;position:absolute;z-index:-1;'+
			               (s.opacity !== false?'filter:Alpha(Opacity=\'0\');':'')+
					       'top:'+(s.top=='auto'?'expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+\'px\')':prop(s.top))+';'+
					       'left:'+(s.left=='auto'?'expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+\'px\')':prop(s.left))+';'+
					       'width:'+(s.width=='auto'?'expression(this.parentNode.offsetWidth+\'px\')':prop(s.width))+';'+
					       'height:'+(s.height=='auto'?'expression(this.parentNode.offsetHeight+\'px\')':prop(s.height))+';'+
					'"/>';
		return this.each(function() {
			if ( $('> iframe.bgiframe', this).length == 0 )
				this.insertBefore( document.createElement(html), this.firstChild );
		});
	}
	return this;
};

})(jQuery);/*
 * jQuery UI 1.7
 *
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI
 */
;jQuery.ui || (function($) {

var _remove = $.fn.remove,
	isFF2 = $.browser.mozilla && (parseFloat($.browser.version) < 1.9);

//Helper functions and ui object
$.ui = {
	version: "1.7",

	// $.ui.plugin is deprecated.  Use the proxy pattern instead.
	plugin: {
		add: function(module, option, set) {
			var proto = $.ui[module].prototype;
			for(var i in set) {
				proto.plugins[i] = proto.plugins[i] || [];
				proto.plugins[i].push([option, set[i]]);
			}
		},
		call: function(instance, name, args) {
			var set = instance.plugins[name];
			if(!set || !instance.element[0].parentNode) { return; }

			for (var i = 0; i < set.length; i++) {
				if (instance.options[set[i][0]]) {
					set[i][1].apply(instance.element, args);
				}
			}
		}
	},

	contains: function(a, b) {
		return document.compareDocumentPosition
			? a.compareDocumentPosition(b) & 16
			: a !== b && a.contains(b);
	},

	hasScroll: function(el, a) {

		//If overflow is hidden, the element might have extra content, but the user wants to hide it
		if ($(el).css('overflow') == 'hidden') { return false; }

		var scroll = (a && a == 'left') ? 'scrollLeft' : 'scrollTop',
			has = false;

		if (el[scroll] > 0) { return true; }

		// TODO: determine which cases actually cause this to happen
		// if the element doesn't have the scroll set, see if it's possible to
		// set the scroll
		el[scroll] = 1;
		has = (el[scroll] > 0);
		el[scroll] = 0;
		return has;
	},

	isOverAxis: function(x, reference, size) {
		//Determines when x coordinate is over "b" element axis
		return (x > reference) && (x < (reference + size));
	},

	isOver: function(y, x, top, left, height, width) {
		//Determines when x, y coordinates is over "b" element
		return $.ui.isOverAxis(y, top, height) && $.ui.isOverAxis(x, left, width);
	},

	keyCode: {
		BACKSPACE: 8,
		CAPS_LOCK: 20,
		COMMA: 188,
		CONTROL: 17,
		DELETE: 46,
		DOWN: 40,
		END: 35,
		ENTER: 13,
		ESCAPE: 27,
		HOME: 36,
		INSERT: 45,
		LEFT: 37,
		NUMPAD_ADD: 107,
		NUMPAD_DECIMAL: 110,
		NUMPAD_DIVIDE: 111,
		NUMPAD_ENTER: 108,
		NUMPAD_MULTIPLY: 106,
		NUMPAD_SUBTRACT: 109,
		PAGE_DOWN: 34,
		PAGE_UP: 33,
		PERIOD: 190,
		RIGHT: 39,
		SHIFT: 16,
		SPACE: 32,
		TAB: 9,
		UP: 38
	}
};

// WAI-ARIA normalization
if (isFF2) {
	var attr = $.attr,
		removeAttr = $.fn.removeAttr,
		ariaNS = "http://www.w3.org/2005/07/aaa",
		ariaState = /^aria-/,
		ariaRole = /^wairole:/;

	$.attr = function(elem, name, value) {
		var set = value !== undefined;

		return (name == 'role'
			? (set
				? attr.call(this, elem, name, "wairole:" + value)
				: (attr.apply(this, arguments) || "").replace(ariaRole, ""))
			: (ariaState.test(name)
				? (set
					? elem.setAttributeNS(ariaNS,
						name.replace(ariaState, "aaa:"), value)
					: attr.call(this, elem, name.replace(ariaState, "aaa:")))
				: attr.apply(this, arguments)));
	};

	$.fn.removeAttr = function(name) {
		return (ariaState.test(name)
			? this.each(function() {
				this.removeAttributeNS(ariaNS, name.replace(ariaState, ""));
			}) : removeAttr.call(this, name));
	};
}

//jQuery plugins
$.fn.extend({
	remove: function() {
		// Safari has a native remove event which actually removes DOM elements,
		// so we have to use triggerHandler instead of trigger (#3037).
		$("*", this).add(this).each(function() {
			$(this).triggerHandler("remove");
		});
		return _remove.apply(this, arguments );
	},

	enableSelection: function() {
		return this
			.attr('unselectable', 'off')
			.css('MozUserSelect', '')
			.unbind('selectstart.ui');
	},

	disableSelection: function() {
		return this
			.attr('unselectable', 'on')
			.css('MozUserSelect', 'none')
			.bind('selectstart.ui', function() { return false; });
	},

	scrollParent: function() {
		var scrollParent;
		if(($.browser.msie && (/(static|relative)/).test(this.css('position'))) || (/absolute/).test(this.css('position'))) {
			scrollParent = this.parents().filter(function() {
				return (/(relative|absolute|fixed)/).test($.curCSS(this,'position',1)) && (/(auto|scroll)/).test($.curCSS(this,'overflow',1)+$.curCSS(this,'overflow-y',1)+$.curCSS(this,'overflow-x',1));
			}).eq(0);
		} else {
			scrollParent = this.parents().filter(function() {
				return (/(auto|scroll)/).test($.curCSS(this,'overflow',1)+$.curCSS(this,'overflow-y',1)+$.curCSS(this,'overflow-x',1));
			}).eq(0);
		}

		return (/fixed/).test(this.css('position')) || !scrollParent.length ? $(document) : scrollParent;
	}
});


//Additional selectors
$.extend($.expr[':'], {
	data: function(elem, i, match) {
		return !!$.data(elem, match[3]);
	},

	focusable: function(element) {
		var nodeName = element.nodeName.toLowerCase(),
			tabIndex = $.attr(element, 'tabindex');
		return (/input|select|textarea|button|object/.test(nodeName)
			? !element.disabled
			: 'a' == nodeName || 'area' == nodeName
				? element.href || !isNaN(tabIndex)
				: !isNaN(tabIndex))
			// the element and all of its ancestors must be visible
			// the browser may report that the area is hidden
			&& !$(element)['area' == nodeName ? 'parents' : 'closest'](':hidden').length;
	},

	tabbable: function(element) {
		var tabIndex = $.attr(element, 'tabindex');
		return (isNaN(tabIndex) || tabIndex >= 0) && $(element).is(':focusable');
	}
});


// $.widget is a factory to create jQuery plugins
// taking some boilerplate code out of the plugin code
function getter(namespace, plugin, method, args) {
	function getMethods(type) {
		var methods = $[namespace][plugin][type] || [];
		return (typeof methods == 'string' ? methods.split(/,?\s+/) : methods);
	}

	var methods = getMethods('getter');
	if (args.length == 1 && typeof args[0] == 'string') {
		methods = methods.concat(getMethods('getterSetter'));
	}
	return ($.inArray(method, methods) != -1);
}

$.widget = function(name, prototype) {
	var namespace = name.split(".")[0];
	name = name.split(".")[1];

	// create plugin method
	$.fn[name] = function(options) {
		var isMethodCall = (typeof options == 'string'),
			args = Array.prototype.slice.call(arguments, 1);

		// prevent calls to internal methods
		if (isMethodCall && options.substring(0, 1) == '_') {
			return this;
		}

		// handle getter methods
		if (isMethodCall && getter(namespace, name, options, args)) {
			var instance = $.data(this[0], name);
			return (instance ? instance[options].apply(instance, args)
				: undefined);
		}

		// handle initialization and non-getter methods
		return this.each(function() {
			var instance = $.data(this, name);

			// constructor
			(!instance && !isMethodCall &&
				$.data(this, name, new $[namespace][name](this, options))._init());

			// method call
			(instance && isMethodCall && $.isFunction(instance[options]) &&
				instance[options].apply(instance, args));
		});
	};

	// create widget constructor
	$[namespace] = $[namespace] || {};
	$[namespace][name] = function(element, options) {
		var self = this;

		this.namespace = namespace;
		this.widgetName = name;
		this.widgetEventPrefix = $[namespace][name].eventPrefix || name;
		this.widgetBaseClass = namespace + '-' + name;

		this.options = $.extend({},
			$.widget.defaults,
			$[namespace][name].defaults,
			$.metadata && $.metadata.get(element)[name],
			options);

		this.element = $(element)
			.bind('setData.' + name, function(event, key, value) {
				if (event.target == element) {
					return self._setData(key, value);
				}
			})
			.bind('getData.' + name, function(event, key) {
				if (event.target == element) {
					return self._getData(key);
				}
			})
			.bind('remove', function() {
				return self.destroy();
			});
	};

	// add widget prototype
	$[namespace][name].prototype = $.extend({}, $.widget.prototype, prototype);

	// TODO: merge getter and getterSetter properties from widget prototype
	// and plugin prototype
	$[namespace][name].getterSetter = 'option';
};

$.widget.prototype = {
	_init: function() {},
	destroy: function() {
		this.element.removeData(this.widgetName)
			.removeClass(this.widgetBaseClass + '-disabled' + ' ' + this.namespace + '-state-disabled')
			.removeAttr('aria-disabled');
	},

	option: function(key, value) {
		var options = key,
			self = this;

		if (typeof key == "string") {
			if (value === undefined) {
				return this._getData(key);
			}
			options = {};
			options[key] = value;
		}

		$.each(options, function(key, value) {
			self._setData(key, value);
		});
	},
	_getData: function(key) {
		return this.options[key];
	},
	_setData: function(key, value) {
		this.options[key] = value;

		if (key == 'disabled') {
			this.element
				[value ? 'addClass' : 'removeClass'](
					this.widgetBaseClass + '-disabled' + ' ' +
					this.namespace + '-state-disabled')
				.attr("aria-disabled", value);
		}
	},

	enable: function() {
		this._setData('disabled', false);
	},
	disable: function() {
		this._setData('disabled', true);
	},

	_trigger: function(type, event, data) {
		var callback = this.options[type],
			eventName = (type == this.widgetEventPrefix
				? type : this.widgetEventPrefix + type);

		event = $.Event(event);
		event.type = eventName;

		// copy original event properties over to the new event
		// this would happen if we could call $.event.fix instead of $.Event
		// but we don't have a way to force an event to be fixed multiple times
		if (event.originalEvent) {
			for (var i = $.event.props.length, prop; i;) {
				prop = $.event.props[--i];
				event[prop] = event.originalEvent[prop];
			}
		}

		this.element.trigger(event, data);

		return !($.isFunction(callback) && callback.call(this.element[0], event, data) === false
			|| event.isDefaultPrevented());
	}
};

$.widget.defaults = {
	disabled: false
};


/** Mouse Interaction Plugin **/

$.ui.mouse = {
	_mouseInit: function() {
		var self = this;

		this.element
			.bind('mousedown.'+this.widgetName, function(event) {
				return self._mouseDown(event);
			})
			.bind('click.'+this.widgetName, function(event) {
				if(self._preventClickEvent) {
					self._preventClickEvent = false;
					event.stopImmediatePropagation();
					return false;
				}
			});

		// Prevent text selection in IE
		if ($.browser.msie) {
			this._mouseUnselectable = this.element.attr('unselectable');
			this.element.attr('unselectable', 'on');
		}

		this.started = false;
	},

	// TODO: make sure destroying one instance of mouse doesn't mess with
	// other instances of mouse
	_mouseDestroy: function() {
		this.element.unbind('.'+this.widgetName);

		// Restore text selection in IE
		($.browser.msie
			&& this.element.attr('unselectable', this._mouseUnselectable));
	},

	_mouseDown: function(event) {
		// don't let more than one widget handle mouseStart
		// TODO: figure out why we have to use originalEvent
		event.originalEvent = event.originalEvent || {};
		if (event.originalEvent.mouseHandled) { return; }

		// we may have missed mouseup (out of window)
		(this._mouseStarted && this._mouseUp(event));

		this._mouseDownEvent = event;

		var self = this,
			btnIsLeft = (event.which == 1),
			elIsCancel = (typeof this.options.cancel == "string" ? $(event.target).parents().add(event.target).filter(this.options.cancel).length : false);
		if (!btnIsLeft || elIsCancel || !this._mouseCapture(event)) {
			return true;
		}

		this.mouseDelayMet = !this.options.delay;
		if (!this.mouseDelayMet) {
			this._mouseDelayTimer = setTimeout(function() {
				self.mouseDelayMet = true;
			}, this.options.delay);
		}

		if (this._mouseDistanceMet(event) && this._mouseDelayMet(event)) {
			this._mouseStarted = (this._mouseStart(event) !== false);
			if (!this._mouseStarted) {
				event.preventDefault();
				return true;
			}
		}

		// these delegates are required to keep context
		this._mouseMoveDelegate = function(event) {
			return self._mouseMove(event);
		};
		this._mouseUpDelegate = function(event) {
			return self._mouseUp(event);
		};
		$(document)
			.bind('mousemove.'+this.widgetName, this._mouseMoveDelegate)
			.bind('mouseup.'+this.widgetName, this._mouseUpDelegate);

		// preventDefault() is used to prevent the selection of text here -
		// however, in Safari, this causes select boxes not to be selectable
		// anymore, so this fix is needed
		($.browser.safari || event.preventDefault());

		event.originalEvent.mouseHandled = true;
		return true;
	},

	_mouseMove: function(event) {
		// IE mouseup check - mouseup happened when mouse was out of window
		if ($.browser.msie && !event.button) {
			return this._mouseUp(event);
		}

		if (this._mouseStarted) {
			this._mouseDrag(event);
			return event.preventDefault();
		}

		if (this._mouseDistanceMet(event) && this._mouseDelayMet(event)) {
			this._mouseStarted =
				(this._mouseStart(this._mouseDownEvent, event) !== false);
			(this._mouseStarted ? this._mouseDrag(event) : this._mouseUp(event));
		}

		return !this._mouseStarted;
	},

	_mouseUp: function(event) {
		$(document)
			.unbind('mousemove.'+this.widgetName, this._mouseMoveDelegate)
			.unbind('mouseup.'+this.widgetName, this._mouseUpDelegate);

		if (this._mouseStarted) {
			this._mouseStarted = false;
			this._preventClickEvent = (event.target == this._mouseDownEvent.target);
			this._mouseStop(event);
		}

		return false;
	},

	_mouseDistanceMet: function(event) {
		return (Math.max(
				Math.abs(this._mouseDownEvent.pageX - event.pageX),
				Math.abs(this._mouseDownEvent.pageY - event.pageY)
			) >= this.options.distance
		);
	},

	_mouseDelayMet: function(event) {
		return this.mouseDelayMet;
	},

	// These are placeholder methods, to be overriden by extending plugin
	_mouseStart: function(event) {},
	_mouseDrag: function(event) {},
	_mouseStop: function(event) {},
	_mouseCapture: function(event) { return true; }
};

$.ui.mouse.defaults = {
	cancel: null,
	distance: 1,
	delay: 0
};

})(jQuery);
(function($){

$.widget('ui.grid', {

	_generateToolbar: function() {
		this.toolbar = $('<tr class="ui-grid-toolbar"><td>Toolbar</td></tr>').appendTo(this.grid);
		this.toolbar = $('td', this.toolbar);
	},

	_generateColumns: function() {
		
		this.columnsContainer = $('<tr class="ui-grid-columns"><td><div class="ui-grid-columns-constrainer"><table cellpadding="0" cellspacing="0"><tbody><tr class="ui-grid-header ui-grid-inner"></tr></tbody></table></div></td></tr>')
			.appendTo(this.grid).find('table tbody tr');

		$('.ui-grid-columns-constrainer', this.grid).css({
			width: this.options.width,
			overflow: 'hidden'
		});
		
		this.columnsContainer.gridSortable({ instance: this });
		
	},

	_generateFooter: function() {
		this.footer = $('<tr class="ui-grid-footer"><td>'+
		'<div class="ui-grid-footer-text ui-grid-limits"></div>'+
		'</td></tr>').appendTo(this.grid).find('td');
	},
	
	_generatePagination: function(response) {
		this.pagination = $('<div class="ui-grid-footer-text" style="float: right;"></div>').appendTo(this.footer);
		var pages = Math.round(response.totalRecords/this.options.limit);
		this._updatePagination(response);
	},
	
	_updatePagination: function(response) {
		
		var pages = Math.round(response.totalRecords/this.options.limit),
			current = Math.round(this.offset / this.options.limit) + 1,
			displayed = [];

		this.pagination.empty();
		
		for (var i=current-1; i > 0 && i > current-3; i--) {
			this.pagination.prepend('<a href="#" class="ui-grid-pagination">'+i+'</a>');
			displayed.push(i);
		};
		
		for (var i=current; i < pages+1 && i < current+3; i++) {
			this.pagination.append(i==current? '<span class="ui-grid-pagination-current">'+i+'</span>' : '<a href="#" class="ui-grid-pagination">'+i+'</a>' );
			displayed.push(i);
		};


		if(pages > 1 && $.inArray(2, displayed) == -1) //Show front dots if the '2' is not already displayed and there are more pages than 1
			this.pagination.prepend('<span class="ui-grid-pagination-dots">...</span>');
		
		if($.inArray(1, displayed) == -1) //Show the '1' if it's not already shown
			this.pagination.prepend('<a href="#" class="ui-grid-pagination">1</a>');

		if($.inArray(pages-1, displayed) == -1) //Show the dots between the current elipse and the last if the one before last is not shown
			this.pagination.append('<span class="ui-grid-pagination-dots">...</span>');
		
		if($.inArray(pages, displayed) == -1) //Show the last if it's not already shown
			this.pagination.append('<a href="#" class="ui-grid-pagination">'+pages+'</a>');
			
		this.pagination.prepend(current-1 > 0 ? '<a href="#" class="ui-grid-pagination">&lt;&lt;</a>' : '<span class="ui-grid-pagination">&lt;&lt;</span>');
		this.pagination.append(current+1 > pages ? '<span class="ui-grid-pagination">&gt;&gt;</span>' : '<a href="#" class="ui-grid-pagination">&gt;&gt;</a>');

	},

	_init: function() {

		var self = this;
		this.offset = 0;

                // Set initial sort direction (if specified)
                this.sortColumn = this.options.sortColumn;
                this.sortDirection = this.options.sortDirection;

		//Generate the grid element
		this.grid = $('<table class="ui-grid ui-component ui-component-content" cellpadding="0" cellspacing="0" width="100%" height="100%"></table>')
						.css({ width: this.options.width })
						.appendTo(this.element);

		//Generate toolbar
		if(this.options.toolbar)
			this._generateToolbar();

		//Generate columns
		this._generateColumns();

		//Generate content element and table
		this.content = $('<tr><td><div class="ui-grid-content"><table cellpadding="0" cellspacing="0"><tbody></tbody></table></div></td></tr>')
			.appendTo(this.grid).find('tbody');
			
		this.contentDiv = $('.ui-grid-content', this.grid);

                // Set height of the height of the content div
                this.contentDiv.height(this.options.height);

		//Generate footer
		if(this.options.footer)
			this._generateFooter();

		//Prepare data
		this.gridmodel = $.ui.grid.model({
			url: this.options.url
		});

		//Call update for the first time
                this._initialUpdate();

		//Event bindings
		this.grid
			.bind('click.grid', function(event) {
				return self._handleClick(event);
			})
			.bind('mousemove.grid', function(event) {
				return self._handleMove(event);
			})
			.bind('mouseleave.grid', function(event) {
				$(self.tableRowHovered).removeClass('ui-grid-row-hover');
			});
		
		this.contentDiv
			.bind('scroll.grid', function(event) {
				$('div.ui-grid-columns-constrainer', self.grid)[0].scrollLeft = this.scrollLeft;
			});

		//Selection of rows
		this._makeRowsSelectable();

	},
	
	_initialUpdate: function() {		
		this._update({ columns: true });
        },

	_handleMove: function(event) {		
	
		// If we're over a columns header
		if(this.columnHandleHovered) {
			$('td.ui-grid-column-header *', this.grid).css('cursor', '');
			this.columnHandleHovered = false;
		}
		
		if($(event.target).is('.ui-grid-column-header') || $(event.target).parent().is('.ui-grid-column-header')) {

			var target = $(event.target).is('.ui-grid-column-header') ? $(event.target) : $(event.target).parent();
                        var widget = $(target).data('gridResizable');
			if (! (widget && widget._mouseCapture(event))) return;
			
			$('td.ui-grid-column-header *', this.grid).css('cursor', 'e-resize');
			this.columnHandleHovered = true;
			return; //Stop here to save performance
			
		}
	
		
		//If we're over a table row
		if($(event.target).parents('.ui-grid-row').length) {
			
			var target = $(event.target).parents('.ui-grid-row');
			
			if(this.tableRowHovered && this.tableRowHovered != target[0])
				$(this.tableRowHovered).removeClass('ui-grid-row-hover');
			
			target.addClass('ui-grid-row-hover');
			this.tableRowHovered = target[0];
			return; //Stop here to save performance
			
		} else {
			if(this.tableRowHovered)
				$(this.tableRowHovered).removeClass('ui-grid-row-hover');
		}	
		
	},

	_handleClick: function(event) {

		//Click on column header toggles sorting
		if($(event.target.parentNode).is('.ui-grid-column-header')) {
			var data = $.data(event.target.parentNode, 'grid-column-header');
			this.sortDirection = this.sortDirection == 'desc' ? 'asc' : 'desc';
			this.sortColumn = data.id;
			this._update({ columns: false, refresh: true });
		}
		
		if($(event.target).is('a.ui-grid-pagination')) {
			var html = event.target.innerHTML, current = Math.round(this.offset / this.options.limit) + 1;
			if(html == '&gt;&gt;') current = current+1;
			if(html == '&lt;&lt;') current = current-1;
			if(!isNaN(parseInt(event.target.innerHTML,10))) current = parseInt(event.target.innerHTML,10);
			
			this.offset = (current-1) * this.options.limit;
			this._update();
		}
		
		return false;

	},

	_makeRowsSelectable: function() {
		
		this.content.parent().parent().selectable({
			filter: 'tr',
			multiple: this.options.multipleSelection,
			selectClass: 'ui-grid-row-selected',
			focusClass: 'ui-grid-row-focussed',
			select: function(e, ui) {
				
				var itemOffset = ui.currentFocus.offset();
				var itemHeight = ui.currentFocus.height();
				var listOffset = $(this).offset();
				var listHeight = $(this).height();
				
				if(itemOffset.top - listOffset.top + itemHeight > listHeight) {
					this.scrollTop = ((itemOffset.top + this.scrollTop - listOffset.top + itemHeight) - listHeight);
				} else if(itemOffset.top < listOffset.top) {
					this.scrollTop = itemOffset.top + this.scrollTop - listOffset.top;
				};
				
			}
		});
		
	},

	_update: function(o) {

		var self = this,
			options = $.extend({}, o, {
				limit: this.options.limit,
				start: (!(o && o.refresh) && this.offset) || 0,
				refresh: (o && o.refresh) || (o && o.columns)
			}),
			fetchOptions = $.extend({}, options, { fill: null });

			if(options.refresh) {
				fetchOptions.start = self.infiniteScrolling ? 0 : (this.offset || 0);
			}

		//Somehow the keys for these must stay undefined no matter what
		if(this.sortColumn) fetchOptions.sortColumn = this.sortColumn;
		if(this.sortDirection) fetchOptions.sortDirection = this.sortDirection;

		//Do the ajax call
		this.gridmodel.fetch(fetchOptions, function(response) {

			//Generate or update pagination
			if(self.options.pagination && !self.pagination) {
				self._generatePagination(response);
			} else if(self.options.pagination && self.pagination) {
				self._updatePagination(response);
			}

			//Empty the content if we either use pagination or we have to restart infinite scrolling
			if(!self.infiniteScrolling || options.refresh)
				self.content.empty();

			//Empty the columns
			if(options.refresh) {
				self.columnsContainer.empty();
				self._addColumns(response.columns);
			}


			//If infiniteScrolling is used and there's no full refresh, fill rows
			if(self.infiniteScrolling && !options.refresh) {

				var data = [];
				for (var i=0; i < response.records.length; i++) {
					data.push(self._addRow(response.records[i]));
				};

				options.fill({
					chunk: options.chunk,
					data: data
				});				

			} else { //otherwise, simply append the rows to the now emptied list

				for (var i=0; i < response.records.length; i++) {
					self._addRow(response.records[i]);
				};
	
				self._syncColumnWidth();
				
				//If we're using infinite scrolling, we have to restart it
				if(self.infiniteScrolling) {
					self.contentDiv.infiniteScrolling('restart');
				}

			}
	
			//Initiate infinite scrolling if we don't use pagination and total records exceed the displayed records
			if(!self.infiniteScrolling && !self.options.pagination && self.options.limit < response.totalRecords) {
				
				self.infiniteScrolling = true;
				self.contentDiv.infiniteScrolling({
					total: self.options.allocateRows ? response.totalRecords : false,
					chunk: self.options.chunk,
					scroll: function(e, ui) {
						self.offset = ui.start;
						self._update({ fill: ui.fill, chunk: ui.chunk });
					},
					update: function(e, ui) {
						$('div.ui-grid-limits', self.footer).html('Result ' + ui.firstItem + '-' + ui.lastItem + (ui.total ? ' of '+ui.total : ''));
					}
				});
				
			}

			if(!self.infiniteScrolling)
				$('div.ui-grid-limits', self.footer).html('Result ' + options.start + '-' + (options.start + options.limit) + ' of ' + response.totalRecords);

		});

	},

	_syncColumnWidth: function() {

		var testTR = $('tr:first td', this.content);
		var totalWidth = 0;
		
		for (var i=0; i < this.columns.length; i++) {
			$(testTR[i]).width($('td:eq('+i+')', this.columnsContainer)[0].style.width);
			totalWidth += parseInt($('td:eq('+i+')', this.columnsContainer)[0].style.width, 10);
			//$('td:eq('+i+') div', this.columnsContainer).width(testTR[i].offsetWidth - 10); //TODO: Subtract real paddings of inner divs
		};
		
		this.content.parent().width(totalWidth);

	},

	_addColumns: function(item) {

		this.columns = item;
		var totalWidth = 25;
		
		for (var i=0; i < item.length; i++) {
			var column = $('<td class="ui-grid-column-header ui-state-default"><div>'+item[i].label+'</div></td>')
				.width(item[i].width)
				.data('grid-column-header', item[i])
				.appendTo(this.columnsContainer)
				.gridResizable();
			totalWidth += item[i].width;
		};
		
		//This column is the last and only used to serve as placeholder for a non-existant scrollbar
		$('<td class="ui-grid-column-header ui-state-default"><div></div></td>').width(25).appendTo(this.columnsContainer);
		
		//Update the total width of the wrapper of the column headers
		this.columnsContainer.parent().parent().width(totalWidth);

	},

	_addRow: function(item, dontAdd) {

		var row = $('<tr class="ui-grid-row"></tr>');
		if(!dontAdd) row.appendTo(this.content);

		for (var i=0; i < this.columns.length; i++) {
			$('<td class="ui-grid-column ui-state-active"><div>'+item[this.columns[i].id]+'</div></td>')
				.appendTo(row);
		};
		
		return row;

	}

});


$.widget('ui.gridResizable', $.extend({}, $.ui.mouse, {
	
	_init: function() {
		this.table = this.element.parent().parent().parent();
		this.gridTable = this.element.parents('.ui-grid').find('div.ui-grid-content > table');
		this._mouseInit();
	},
	
	_mouseCapture: function(event) {

		this.offset = this.element.offset();
		if((this.offset.left + this.element.width()) - event.pageX < 5) {
			return true;
		};
		
		return false;
		
	},
	
	_mouseStart: function(event) {
		
		$.extend(this, {
			startPosition: event.pageX,
			startWidth: this.element.width(),
			tableStartWidth: this.table.width(),
			gridTableStartWidth: this.gridTable.width(),
			index: this.element.parent().find('td').index(this.element[0])
		});
		
	},
	
	_mouseDrag: function(event) {

		this.element.css('width', this.startWidth + (event.pageX - this.startPosition));
		this.table.css('width', this.tableStartWidth + (event.pageX - this.startPosition));
		
		$('tr:eq(0) td:eq('+this.index+')', this.gridTable).css('width', this.startWidth + (event.pageX - this.startPosition));
		this.gridTable.css('width', this.gridTableStartWidth + (event.pageX - this.startPosition));
		
	},
	
	_mouseStop: function(event) {
		//TODO: Send column width update to the backend, and/or fire callback
	}
	
}));

$.extend($.ui.gridResizable, {
	defaults: {
		handle: false,
		cancel: ":input",
		delay: 0,
		distance: 1
	}
});


$.widget('ui.gridSortable', $.extend({}, $.ui.mouse, {
	
	_init: function() {
		this._mouseInit();
	},
	
	_mouseCapture: function(event) {

                var el = $(event.target);
                this.item = el.hasClass('ui-grid-column-header') ? el : el.parents('.ui-grid-column-header');
		this.offset = this.item.offset();
		
		return true;
		
	},
	
	_mouseStart: function(event) {
		
		var self = this;
		
		this.offsets = [];
		this.items = this.element.find('td').each(function(i) {
			if(self.item[0] != this) self.offsets.push([this, $(this).offset().left]);
		});
		
		$.extend(this, {
			startPosition: event.pageX,
			index: this.items.index(this.item[0])
		});
		
	},
	
	_mouseDrag: function(event) {

		var self = this;
			//this.element.css('width', this.startWidth + (event.pageX - this.startPosition));
		$(self.offsets).each(function(i) {
			
			if(
				$.ui.isOverAxis(event.pageX, this[1], this[0].offsetWidth)
			) {
				var dir = $.ui.isOverAxis(event.pageX, this[1], this[0].offsetWidth/2) ? 'left' : 'right';
				if(!self.lastHovered || self.lastHovered[0] != this[0] || self.lastHovered[1] != dir) {
					
					if(self.lastHovered) $(self.lastHovered[0]).removeClass('ui-grid-column-sort-right ui-grid-column-sort-left');
					
					self.lastHovered = [this[0], dir];
					$(self.lastHovered[0]).addClass('ui-grid-column-sort-'+dir);
				}
			}
			
		});
		
	},
	
	_mouseStop: function(event) {
		
		var self = this;
		if(this.lastHovered) {
			$(this.lastHovered[0]).removeClass('ui-grid-column-sort-right ui-grid-column-sort-left');
			$(this.lastHovered[0])[this.lastHovered[1] == 'right' ? 'after' : 'before'](this.item);
			
			//TODO: Reorder actual data columns
			$('tr', this.options.instance.contentDiv).each(function(i) {
				$('> td:eq('+self.items.index(self.lastHovered[0])+')', this)[self.lastHovered[1] == 'right' ? 'after' : 'before']($('> td:eq('+self.index+')', this));
			});

		}
	}
	
}));

$.extend($.ui.gridSortable, {
	defaults: {
		handle: false,
		cancel: ":input",
		delay: 0,
		distance: 1
	}
});


$.extend($.ui.grid, {
	defaults: {
		width: 500,
		height: 300,

		limit: false,
		pagination: true,
		allocateRows: true, //Only used for infinite scrolling
		chunk: 20, //Only used for infinite scrolling

		footer: true,
		toolbar: false,

		multipleSelection: true
	}
});

})(jQuery);
(function($) {

	$.extend($.ui.grid, {
		model: function(options) {
			options = $.extend({}, $.ui.grid.model.defaults, options);
			return {
				fetch: function(request, callback) {
					$.ajax($.extend(true, {
						url: options.url,
						data: request,
						success: function(response) {
							callback(options.parse(response));
						}
					}, options.ajax));
				}
			}
		}
	});

	$.ui.grid.model.defaults = {
		ajax: {
			dataType: "json",
			cache: false
		},
		parse: function(response) {
			var records = [];
			$.each(response.records, function() {
				var record = this;
				var result = {};
				$.each(response.columns, function(index) {
					result[this.id] = record[index];
				})
				records.push(result);
			});
			return {
				totalRecords: response.totalRecords,
				columns: response.columns,
				records: records
			};
		}
	}

})(jQuery);
/**
 * Copyright Yehuda Katz
 * with assistance by Jay Freeman
 * 
 * You may distribute this code under the same license as jQuery (BSD or GPL
 **/

/*

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8">
    <title>Templating</title>
    <script src="../../jquery/dist/jquery.min.js"></script>
    <script src="jquery.templating.js"></script>
    <script>
      jQuery(function ($) {
          $("a.updateTemplate").click(function() {
            $(this.rel).loadTemplate(this.href);
            return false;
          });
          $("._template").templatize();
      });
    </script>
  </head>
  <body>
    <div class="_template" id="myTemplate">
      <![CDATA[
        <{{tag}} href={{href}}>{{first}} {{last}}</{{tag}}>
        <p>Bar</p>
        <div>First Name: {{first}}</div>
        <div>Last Name: {{last}}</div>
      ]]>
    </div>
    <a href="foo" rel="#myTemplate" class="updateTemplate">Click</a>
  </body>
</html>
  
*/

(function ($) {
  $.makeTemplate = function (template, begin, end) {
    var rebegin = begin.replace(/([\]{}[\\])/g, '\\$1');
    var reend = end.replace(/([\]{}[\\])/g, '\\$1');

    var code = "try { with (_context) {" +
      "var _result = '';" +
        template
          .replace(/[\t\r\n]/g, ' ')
          .replace(/^(.*)$/, end + '$1' + begin)
          .replace(new RegExp(reend + "(.*?)" + rebegin, "g"), function (text) {
            return text
              .replace(new RegExp("^" + reend + "(.*)" + rebegin + "$"), "$1")
              .replace(/\\/g, "\\\\")
              .replace(/'/g, "\\'")
              .replace(/^(.*)$/, end + "_result += '$1';" + begin);
          })
          .replace(new RegExp(rebegin + "=(.*?)" + reend, "g"), "_result += ($1);")
          .replace(new RegExp(rebegin + "(.*?)" + reend, "g"), ' $1 ')
          .replace(new RegExp("^" + reend + "(.*)" + rebegin + "$"), '$1') +
      "return _result;" +
    "} } catch(e) { return '' } ";

    return new Function("_context", code);
  };
})(jQuery);/*
 * jQuery UI Autocomplete
 * version: 1.0 (1/2/2008)
 * @requires: jQuery v1.2 or later, dimensions plugin
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Copyright 2007 Yehuda Katz, Rein Henrichs
 */

(function($) {
  $.ui = $.ui || {};
  $.ui.autobox = $.ui.autobox || {};
  $.ui.autobox.ext = $.ui.autobox.ext || {};

  // create request manager
  var log;
  if (window.console) {
      log = console.log;
  } else {
      log = function() {};
  }
  var MiniRM = function(opt) {
    this.chainedGetJSON = opt.jsonhandler || $.getJSON;
    this.maxActive = opt.maxActive || 1;
    this.maxQueue = opt.maxQueue || 1;
    this.active = 0;
    this.queue = [];
  };
  $.extend(MiniRM.prototype, {
      getJSON: function(url, query, handler) {
        var self = this;
        var wrappedHandler = function(json) {
            self.active -= 1;
            self.log ('MiniRM IN', url, query);
            handler(json);
            var nextJob = self.queue.shift();
            if (nextJob !== undefined) {
                self.active += 1;
                self.log ('MiniRM POP/OUT', nextJob[0], nextJob[1]);
                self.chainedGetJSON.apply(null, nextJob);
            }
        };
        if (this.active < this.maxActive) {
            this.active += 1;
            this.log ('MiniRM OUT', url, query);
            this.chainedGetJSON(url, query, wrappedHandler);
        } else {
            if (this.queue.length == this.maxQueue) {
                var discardJob = this.queue.shift();
                this.log('MiniRM POP/DISCARD', discardJob[0], discardJob[1]);
            }
            this.queue.push([url, query, wrappedHandler]);
            this.log ('MiniRM PUSH', url, query);
        }
      },
      log: function(msg, url, query) {
        //log (msg, 'ACT=' + this.active, 'QUE=' + this.queue.length, url + "?" + query);
      }
  });
  var miniRM = new MiniRM({});

  $.ui.autobox.ext.ajax = function(opt) {
    var ajax = opt.ajax;
    return { getList: function(input, hash) {
      var val = input.val();
      var minQueryLength = this.options.minQueryLength;
      if (minQueryLength && (! val || val.length < minQueryLength)) return false;
      if (val.match(/^\s*$/)) return false;
      miniRM.getJSON(ajax, "val=" + val, function(json) {
          if(hash){ json=$(json).filter(function(){  return !hash[this.text]; }); }
          input.trigger("updateList", [json]);
      });
    } };
  };

  $.ui.autobox.ext.templateText = function(opt) {
    var template = $.makeTemplate(opt.templateText, "<%", "%>");
    return { template: function(obj) { return template(obj); } };
  };

})(jQuery);
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
/*
 * jQuery UI Effects 1.7
 *
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI/Effects/
 */
;jQuery.effects || (function($) {

$.effects = {
	version: "1.7",

	// Saves a set of properties in a data storage
	save: function(element, set) {
		for(var i=0; i < set.length; i++) {
			if(set[i] !== null) element.data("ec.storage."+set[i], element[0].style[set[i]]);
		}
	},

	// Restores a set of previously saved properties from a data storage
	restore: function(element, set) {
		for(var i=0; i < set.length; i++) {
			if(set[i] !== null) element.css(set[i], element.data("ec.storage."+set[i]));
		}
	},

	setMode: function(el, mode) {
		if (mode == 'toggle') mode = el.is(':hidden') ? 'show' : 'hide'; // Set for toggle
		return mode;
	},

	getBaseline: function(origin, original) { // Translates a [top,left] array into a baseline value
		// this should be a little more flexible in the future to handle a string & hash
		var y, x;
		switch (origin[0]) {
			case 'top': y = 0; break;
			case 'middle': y = 0.5; break;
			case 'bottom': y = 1; break;
			default: y = origin[0] / original.height;
		};
		switch (origin[1]) {
			case 'left': x = 0; break;
			case 'center': x = 0.5; break;
			case 'right': x = 1; break;
			default: x = origin[1] / original.width;
		};
		return {x: x, y: y};
	},

	// Wraps the element around a wrapper that copies position properties
	createWrapper: function(element) {

		//if the element is already wrapped, return it
		if (element.parent().is('.ui-effects-wrapper'))
			return element.parent();

		//Cache width,height and float properties of the element, and create a wrapper around it
		var props = { width: element.outerWidth(true), height: element.outerHeight(true), 'float': element.css('float') };
		element.wrap('<div class="ui-effects-wrapper" style="font-size:100%;background:transparent;border:none;margin:0;padding:0"></div>');
		var wrapper = element.parent();

		//Transfer the positioning of the element to the wrapper
		if (element.css('position') == 'static') {
			wrapper.css({ position: 'relative' });
			element.css({ position: 'relative'} );
		} else {
			var top = element.css('top'); if(isNaN(parseInt(top,10))) top = 'auto';
			var left = element.css('left'); if(isNaN(parseInt(left,10))) left = 'auto';
			wrapper.css({ position: element.css('position'), top: top, left: left, zIndex: element.css('z-index') }).show();
			element.css({position: 'relative', top: 0, left: 0 });
		}

		wrapper.css(props);
		return wrapper;
	},

	removeWrapper: function(element) {
		if (element.parent().is('.ui-effects-wrapper'))
			return element.parent().replaceWith(element);
		return element;
	},

	setTransition: function(element, list, factor, value) {
		value = value || {};
		$.each(list, function(i, x){
			unit = element.cssUnit(x);
			if (unit[0] > 0) value[x] = unit[0] * factor + unit[1];
		});
		return value;
	},

	//Base function to animate from one class to another in a seamless transition
	animateClass: function(value, duration, easing, callback) {

		var cb = (typeof easing == "function" ? easing : (callback ? callback : null));
		var ea = (typeof easing == "string" ? easing : null);

		return this.each(function() {

			var offset = {}; var that = $(this); var oldStyleAttr = that.attr("style") || '';
			if(typeof oldStyleAttr == 'object') oldStyleAttr = oldStyleAttr["cssText"]; /* Stupidly in IE, style is a object.. */
			if(value.toggle) { that.hasClass(value.toggle) ? value.remove = value.toggle : value.add = value.toggle; }

			//Let's get a style offset
			var oldStyle = $.extend({}, (document.defaultView ? document.defaultView.getComputedStyle(this,null) : this.currentStyle));
			if(value.add) that.addClass(value.add); if(value.remove) that.removeClass(value.remove);
			var newStyle = $.extend({}, (document.defaultView ? document.defaultView.getComputedStyle(this,null) : this.currentStyle));
			if(value.add) that.removeClass(value.add); if(value.remove) that.addClass(value.remove);

			// The main function to form the object for animation
			for(var n in newStyle) {
				if( typeof newStyle[n] != "function" && newStyle[n] /* No functions and null properties */
				&& n.indexOf("Moz") == -1 && n.indexOf("length") == -1 /* No mozilla spezific render properties. */
				&& newStyle[n] != oldStyle[n] /* Only values that have changed are used for the animation */
				&& (n.match(/color/i) || (!n.match(/color/i) && !isNaN(parseInt(newStyle[n],10)))) /* Only things that can be parsed to integers or colors */
				&& (oldStyle.position != "static" || (oldStyle.position == "static" && !n.match(/left|top|bottom|right/))) /* No need for positions when dealing with static positions */
				) offset[n] = newStyle[n];
			}

			that.animate(offset, duration, ea, function() { // Animate the newly constructed offset object
				// Change style attribute back to original. For stupid IE, we need to clear the damn object.
				if(typeof $(this).attr("style") == 'object') { $(this).attr("style")["cssText"] = ""; $(this).attr("style")["cssText"] = oldStyleAttr; } else $(this).attr("style", oldStyleAttr);
				if(value.add) $(this).addClass(value.add); if(value.remove) $(this).removeClass(value.remove);
				if(cb) cb.apply(this, arguments);
			});

		});
	}
};


function _normalizeArguments(a, m) {

	var o = a[1] && a[1].constructor == Object ? a[1] : {}; if(m) o.mode = m;
	var speed = a[1] && a[1].constructor != Object ? a[1] : (o.duration ? o.duration : a[2]); //either comes from options.duration or the secon/third argument
		speed = $.fx.off ? 0 : typeof speed === "number" ? speed : $.fx.speeds[speed] || $.fx.speeds._default;
	var callback = o.callback || ( $.isFunction(a[1]) && a[1] ) || ( $.isFunction(a[2]) && a[2] ) || ( $.isFunction(a[3]) && a[3] );

	return [a[0], o, speed, callback];
	
}

//Extend the methods of jQuery
$.fn.extend({

	//Save old methods
	_show: $.fn.show,
	_hide: $.fn.hide,
	__toggle: $.fn.toggle,
	_addClass: $.fn.addClass,
	_removeClass: $.fn.removeClass,
	_toggleClass: $.fn.toggleClass,

	// New effect methods
	effect: function(fx, options, speed, callback) {
		return $.effects[fx] ? $.effects[fx].call(this, {method: fx, options: options || {}, duration: speed, callback: callback }) : null;
	},

	show: function() {
		if(!arguments[0] || (arguments[0].constructor == Number || (/(slow|normal|fast)/).test(arguments[0])))
			return this._show.apply(this, arguments);
		else {
			return this.effect.apply(this, _normalizeArguments(arguments, 'show'));
		}
	},

	hide: function() {
		if(!arguments[0] || (arguments[0].constructor == Number || (/(slow|normal|fast)/).test(arguments[0])))
			return this._hide.apply(this, arguments);
		else {
			return this.effect.apply(this, _normalizeArguments(arguments, 'hide'));
		}
	},

	toggle: function(){
		if(!arguments[0] || (arguments[0].constructor == Number || (/(slow|normal|fast)/).test(arguments[0])) || (arguments[0].constructor == Function))
			return this.__toggle.apply(this, arguments);
		else {
			return this.effect.apply(this, _normalizeArguments(arguments, 'toggle'));
		}
	},

	addClass: function(classNames, speed, easing, callback) {
		return speed ? $.effects.animateClass.apply(this, [{ add: classNames },speed,easing,callback]) : this._addClass(classNames);
	},
	removeClass: function(classNames,speed,easing,callback) {
		return speed ? $.effects.animateClass.apply(this, [{ remove: classNames },speed,easing,callback]) : this._removeClass(classNames);
	},
	toggleClass: function(classNames,speed,easing,callback) {
		return ( (typeof speed !== "boolean") && speed ) ? $.effects.animateClass.apply(this, [{ toggle: classNames },speed,easing,callback]) : this._toggleClass(classNames, speed);
	},
	morph: function(remove,add,speed,easing,callback) {
		return $.effects.animateClass.apply(this, [{ add: add, remove: remove },speed,easing,callback]);
	},
	switchClass: function() {
		return this.morph.apply(this, arguments);
	},

	// helper functions
	cssUnit: function(key) {
		var style = this.css(key), val = [];
		$.each( ['em','px','%','pt'], function(i, unit){
			if(style.indexOf(unit) > 0)
				val = [parseFloat(style), unit];
		});
		return val;
	}
});

/*
 * jQuery Color Animations
 * Copyright 2007 John Resig
 * Released under the MIT and GPL licenses.
 */

// We override the animation for all of these color styles
$.each(['backgroundColor', 'borderBottomColor', 'borderLeftColor', 'borderRightColor', 'borderTopColor', 'color', 'outlineColor'], function(i,attr){
		$.fx.step[attr] = function(fx) {
				if ( fx.state == 0 ) {
						fx.start = getColor( fx.elem, attr );
						fx.end = getRGB( fx.end );
				}
// XXX XXX In here we fail on IE 
try{
				fx.elem.style[attr] = "rgb(" + [
						Math.max(Math.min( parseInt((fx.pos * (fx.end[0] - fx.start[0])) + fx.start[0],10), 255), 0),
						Math.max(Math.min( parseInt((fx.pos * (fx.end[1] - fx.start[1])) + fx.start[1],10), 255), 0),
						Math.max(Math.min( parseInt((fx.pos * (fx.end[2] - fx.start[2])) + fx.start[2],10), 255), 0)
				].join(",") + ")";
} catch(e) {};
			};
});

// Color Conversion functions from highlightFade
// By Blair Mitchelmore
// http://jquery.offput.ca/highlightFade/

// Parse strings looking for color tuples [255,255,255]
function getRGB(color) {
		var result;

		// Check if we're already dealing with an array of colors
		if ( color && color.constructor == Array && color.length == 3 )
				return color;

		// Look for rgb(num,num,num)
		if (result = /rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(color))
				return [parseInt(result[1],10), parseInt(result[2],10), parseInt(result[3],10)];

		// Look for rgb(num%,num%,num%)
		if (result = /rgb\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*\)/.exec(color))
				return [parseFloat(result[1])*2.55, parseFloat(result[2])*2.55, parseFloat(result[3])*2.55];

		// Look for #a0b1c2
		if (result = /#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.exec(color))
				return [parseInt(result[1],16), parseInt(result[2],16), parseInt(result[3],16)];

		// Look for #fff
		if (result = /#([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])/.exec(color))
				return [parseInt(result[1]+result[1],16), parseInt(result[2]+result[2],16), parseInt(result[3]+result[3],16)];

		// Look for rgba(0, 0, 0, 0) == transparent in Safari 3
		if (result = /rgba\(0, 0, 0, 0\)/.exec(color))
				return colors['transparent'];

		// Otherwise, we're most likely dealing with a named color
		return colors[$.trim(color).toLowerCase()];
}

function getColor(elem, attr) {
		var color;

		do {
				color = $.curCSS(elem, attr);

				// Keep going until we find an element that has color, or we hit the body
				if ( color != '' && color != 'transparent' || $.nodeName(elem, "body") )
						break;

				attr = "backgroundColor";
		} while ( elem = elem.parentNode );

		return getRGB(color);
};

// Some named colors to work with
// From Interface by Stefan Petre
// http://interface.eyecon.ro/

var colors = {
	aqua:[0,255,255],
	azure:[240,255,255],
	beige:[245,245,220],
	black:[0,0,0],
	blue:[0,0,255],
	brown:[165,42,42],
	cyan:[0,255,255],
	darkblue:[0,0,139],
	darkcyan:[0,139,139],
	darkgrey:[169,169,169],
	darkgreen:[0,100,0],
	darkkhaki:[189,183,107],
	darkmagenta:[139,0,139],
	darkolivegreen:[85,107,47],
	darkorange:[255,140,0],
	darkorchid:[153,50,204],
	darkred:[139,0,0],
	darksalmon:[233,150,122],
	darkviolet:[148,0,211],
	fuchsia:[255,0,255],
	gold:[255,215,0],
	green:[0,128,0],
	indigo:[75,0,130],
	khaki:[240,230,140],
	lightblue:[173,216,230],
	lightcyan:[224,255,255],
	lightgreen:[144,238,144],
	lightgrey:[211,211,211],
	lightpink:[255,182,193],
	lightyellow:[255,255,224],
	lime:[0,255,0],
	magenta:[255,0,255],
	maroon:[128,0,0],
	navy:[0,0,128],
	olive:[128,128,0],
	orange:[255,165,0],
	pink:[255,192,203],
	purple:[128,0,128],
	violet:[128,0,128],
	red:[255,0,0],
	silver:[192,192,192],
	white:[255,255,255],
	yellow:[255,255,0],
	transparent: [255,255,255]
};

/*
 * jQuery Easing v1.3 - http://gsgd.co.uk/sandbox/jquery/easing/
 *
 * Uses the built in easing capabilities added In jQuery 1.1
 * to offer multiple easing options
 *
 * TERMS OF USE - jQuery Easing
 *
 * Open source under the BSD License.
 *
 * Copyright 2008 George McGinley Smith
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of
 * conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list
 * of conditions and the following disclaimer in the documentation and/or other materials
 * provided with the distribution.
 *
 * Neither the name of the author nor the names of contributors may be used to endorse
 * or promote products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
*/

// t: current time, b: begInnIng value, c: change In value, d: duration
$.easing.jswing = $.easing.swing;

$.extend($.easing,
{
	def: 'easeOutQuad',
	swing: function (x, t, b, c, d) {
		//alert($.easing.default);
		return $.easing[$.easing.def](x, t, b, c, d);
	},
	easeInQuad: function (x, t, b, c, d) {
		return c*(t/=d)*t + b;
	},
	easeOutQuad: function (x, t, b, c, d) {
		return -c *(t/=d)*(t-2) + b;
	},
	easeInOutQuad: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t + b;
		return -c/2 * ((--t)*(t-2) - 1) + b;
	},
	easeInCubic: function (x, t, b, c, d) {
		return c*(t/=d)*t*t + b;
	},
	easeOutCubic: function (x, t, b, c, d) {
		return c*((t=t/d-1)*t*t + 1) + b;
	},
	easeInOutCubic: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t + b;
		return c/2*((t-=2)*t*t + 2) + b;
	},
	easeInQuart: function (x, t, b, c, d) {
		return c*(t/=d)*t*t*t + b;
	},
	easeOutQuart: function (x, t, b, c, d) {
		return -c * ((t=t/d-1)*t*t*t - 1) + b;
	},
	easeInOutQuart: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t*t + b;
		return -c/2 * ((t-=2)*t*t*t - 2) + b;
	},
	easeInQuint: function (x, t, b, c, d) {
		return c*(t/=d)*t*t*t*t + b;
	},
	easeOutQuint: function (x, t, b, c, d) {
		return c*((t=t/d-1)*t*t*t*t + 1) + b;
	},
	easeInOutQuint: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t*t*t + b;
		return c/2*((t-=2)*t*t*t*t + 2) + b;
	},
	easeInSine: function (x, t, b, c, d) {
		return -c * Math.cos(t/d * (Math.PI/2)) + c + b;
	},
	easeOutSine: function (x, t, b, c, d) {
		return c * Math.sin(t/d * (Math.PI/2)) + b;
	},
	easeInOutSine: function (x, t, b, c, d) {
		return -c/2 * (Math.cos(Math.PI*t/d) - 1) + b;
	},
	easeInExpo: function (x, t, b, c, d) {
		return (t==0) ? b : c * Math.pow(2, 10 * (t/d - 1)) + b;
	},
	easeOutExpo: function (x, t, b, c, d) {
		return (t==d) ? b+c : c * (-Math.pow(2, -10 * t/d) + 1) + b;
	},
	easeInOutExpo: function (x, t, b, c, d) {
		if (t==0) return b;
		if (t==d) return b+c;
		if ((t/=d/2) < 1) return c/2 * Math.pow(2, 10 * (t - 1)) + b;
		return c/2 * (-Math.pow(2, -10 * --t) + 2) + b;
	},
	easeInCirc: function (x, t, b, c, d) {
		return -c * (Math.sqrt(1 - (t/=d)*t) - 1) + b;
	},
	easeOutCirc: function (x, t, b, c, d) {
		return c * Math.sqrt(1 - (t=t/d-1)*t) + b;
	},
	easeInOutCirc: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return -c/2 * (Math.sqrt(1 - t*t) - 1) + b;
		return c/2 * (Math.sqrt(1 - (t-=2)*t) + 1) + b;
	},
	easeInElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d)==1) return b+c;  if (!p) p=d*.3;
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		return -(a*Math.pow(2,10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )) + b;
	},
	easeOutElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d)==1) return b+c;  if (!p) p=d*.3;
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		return a*Math.pow(2,-10*t) * Math.sin( (t*d-s)*(2*Math.PI)/p ) + c + b;
	},
	easeInOutElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d/2)==2) return b+c;  if (!p) p=d*(.3*1.5);
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		if (t < 1) return -.5*(a*Math.pow(2,10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )) + b;
		return a*Math.pow(2,-10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )*.5 + c + b;
	},
	easeInBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		return c*(t/=d)*t*((s+1)*t - s) + b;
	},
	easeOutBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		return c*((t=t/d-1)*t*((s+1)*t + s) + 1) + b;
	},
	easeInOutBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		if ((t/=d/2) < 1) return c/2*(t*t*(((s*=(1.525))+1)*t - s)) + b;
		return c/2*((t-=2)*t*(((s*=(1.525))+1)*t + s) + 2) + b;
	},
	easeInBounce: function (x, t, b, c, d) {
		return c - $.easing.easeOutBounce (x, d-t, 0, c, d) + b;
	},
	easeOutBounce: function (x, t, b, c, d) {
		if ((t/=d) < (1/2.75)) {
			return c*(7.5625*t*t) + b;
		} else if (t < (2/2.75)) {
			return c*(7.5625*(t-=(1.5/2.75))*t + .75) + b;
		} else if (t < (2.5/2.75)) {
			return c*(7.5625*(t-=(2.25/2.75))*t + .9375) + b;
		} else {
			return c*(7.5625*(t-=(2.625/2.75))*t + .984375) + b;
		}
	},
	easeInOutBounce: function (x, t, b, c, d) {
		if (t < d/2) return $.easing.easeInBounce (x, t*2, 0, c, d) * .5 + b;
		return $.easing.easeOutBounce (x, t*2-d, 0, c, d) * .5 + c*.5 + b;
	}
});

/*
 *
 * TERMS OF USE - EASING EQUATIONS
 *
 * Open source under the BSD License.
 *
 * Copyright 2001 Robert Penner
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of
 * conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list
 * of conditions and the following disclaimer in the documentation and/or other materials
 * provided with the distribution.
 *
 * Neither the name of the author nor the names of contributors may be used to endorse
 * or promote products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

})(jQuery);
/*
 * jQuery UI Effects Pulsate 1.7
 *
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI/Effects/Pulsate
 *
 * Depends:
 *	effects.core.js
 */
(function($) {

$.effects.pulsate = function(o) {

	return this.queue(function() {

		// Create element
		var el = $(this);

		// Set options
		var mode = $.effects.setMode(el, o.options.mode || 'show'); // Set Mode
		var times = o.options.times || 5; // Default # of times
		var duration = o.duration ? o.duration / 2 : $.fx.speeds._default / 2;

		// Adjust
		if (el.is(':hidden')) { // Show fadeIn
			el.css('opacity', 0);
			el.show(); // Show
			el.animate({opacity: 1}, duration, o.options.easing);
			times--;
		}

		// Animate
		for (var i = 0; i < times - 1; i++) { // Pulsate
			el.animate({opacity: 0}, duration, o.options.easing).animate({opacity: 1}, duration, o.options.easing);
		};
		if (mode == 'hide') { // Last Pulse
			el.animate({opacity: 0}, duration, o.options.easing, function(){
				el.hide(); // Hide
				if(o.callback) o.callback.apply(this, arguments); // Callback
			});
		} else {
			el.animate({opacity: 0}, duration, o.options.easing).animate({opacity: 1}, duration, o.options.easing, function(){
				if(o.callback) o.callback.apply(this, arguments); // Callback
			});
		};
		el.queue('fx', function() { el.dequeue(); });
		el.dequeue();
	});

};

})(jQuery);
/*
 * jQuery UI Effects Fold 1.7
 *
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI/Effects/Fold
 *
 * Depends:
 *	effects.core.js
 */
(function($) {

$.effects.fold = function(o) {

	return this.queue(function() {

		// Create element
		var el = $(this), props = ['position','top','left'];

		// Set options
		var mode = $.effects.setMode(el, o.options.mode || 'hide'); // Set Mode
		var size = o.options.size || 15; // Default fold size
		var horizFirst = !(!o.options.horizFirst); // Ensure a boolean value
		var duration = o.duration ? o.duration / 2 : $.fx.speeds._default / 2;

		// Adjust
		$.effects.save(el, props); el.show(); // Save & Show
		var wrapper = $.effects.createWrapper(el).css({overflow:'hidden'}); // Create Wrapper
		var widthFirst = ((mode == 'show') != horizFirst);
		var ref = widthFirst ? ['width', 'height'] : ['height', 'width'];
		var distance = widthFirst ? [wrapper.width(), wrapper.height()] : [wrapper.height(), wrapper.width()];
		var percent = /([0-9]+)%/.exec(size);
		if(percent) size = parseInt(percent[1],10) / 100 * distance[mode == 'hide' ? 0 : 1];
		if(mode == 'show') wrapper.css(horizFirst ? {height: 0, width: size} : {height: size, width: 0}); // Shift

		// Animation
		var animation1 = {}, animation2 = {};
		animation1[ref[0]] = mode == 'show' ? distance[0] : size;
		animation2[ref[1]] = mode == 'show' ? distance[1] : 0;

		// Animate
		wrapper.animate(animation1, duration, o.options.easing)
		.animate(animation2, duration, o.options.easing, function() {
			if(mode == 'hide') el.hide(); // Hide
			$.effects.restore(el, props); $.effects.removeWrapper(el); // Restore
			if(o.callback) o.callback.apply(el[0], arguments); // Callback
			el.dequeue();
		});

	});

};

})(jQuery);
/*
 * jQuery UI Datepicker 1.7
 *
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI/Datepicker
 *
 * Depends:
 *	ui.core.js
 */

(function($) { // hide the namespace

$.extend($.ui, { datepicker: { version: "1.7" } });

var PROP_NAME = 'datepicker';

/* Date picker manager.
   Use the singleton instance of this class, $.datepicker, to interact with the date picker.
   Settings for (groups of) date pickers are maintained in an instance object,
   allowing multiple different settings on the same page. */

function Datepicker() {
	this.debug = false; // Change this to true to start debugging
	this._curInst = null; // The current instance in use
	this._keyEvent = false; // If the last event was a key event
	this._disabledInputs = []; // List of date picker inputs that have been disabled
	this._datepickerShowing = false; // True if the popup picker is showing , false if not
	this._inDialog = false; // True if showing within a "dialog", false if not
	this._mainDivId = 'ui-datepicker-div'; // The ID of the main datepicker division
	this._inlineClass = 'ui-datepicker-inline'; // The name of the inline marker class
	this._appendClass = 'ui-datepicker-append'; // The name of the append marker class
	this._triggerClass = 'ui-datepicker-trigger'; // The name of the trigger marker class
	this._dialogClass = 'ui-datepicker-dialog'; // The name of the dialog marker class
	this._disableClass = 'ui-datepicker-disabled'; // The name of the disabled covering marker class
	this._unselectableClass = 'ui-datepicker-unselectable'; // The name of the unselectable cell marker class
	this._currentClass = 'ui-datepicker-current-day'; // The name of the current day marker class
	this._dayOverClass = 'ui-datepicker-days-cell-over'; // The name of the day hover marker class
	this.regional = []; // Available regional settings, indexed by language code
	this.regional[''] = { // Default regional settings
		closeText: 'Done', // Display text for close link
		prevText: 'Prev', // Display text for previous month link
		nextText: 'Next', // Display text for next month link
		currentText: 'Today', // Display text for current month link
		monthNames: ['January','February','March','April','May','June',
			'July','August','September','October','November','December'], // Names of months for drop-down and formatting
		monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], // For formatting
		dayNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], // For formatting
		dayNamesShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], // For formatting
		dayNamesMin: ['Su','Mo','Tu','We','Th','Fr','Sa'], // Column headings for days starting at Sunday
		dateFormat: 'mm/dd/yy', // See format options on parseDate
		firstDay: 0, // The first day of the week, Sun = 0, Mon = 1, ...
		isRTL: false // True if right-to-left language, false if left-to-right
	};
	this._defaults = { // Global defaults for all the date picker instances
		showOn: 'focus', // 'focus' for popup on focus,
			// 'button' for trigger button, or 'both' for either
		showAnim: 'show', // Name of jQuery animation for popup
		showOptions: {}, // Options for enhanced animations
		defaultDate: null, // Used when field is blank: actual date,
			// +/-number for offset from today, null for today
		appendText: '', // Display text following the input box, e.g. showing the format
		buttonText: '...', // Text for trigger button
		buttonImage: '', // URL for trigger button image
		buttonImageOnly: false, // True if the image appears alone, false if it appears on a button
		hideIfNoPrevNext: false, // True to hide next/previous month links
			// if not applicable, false to just disable them
		navigationAsDateFormat: false, // True if date formatting applied to prev/today/next links
		gotoCurrent: false, // True if today link goes back to current selection instead
		changeMonth: false, // True if month can be selected directly, false if only prev/next
		changeYear: false, // True if year can be selected directly, false if only prev/next
		showMonthAfterYear: false, // True if the year select precedes month, false for month then year
		yearRange: '-10:+10', // Range of years to display in drop-down,
			// either relative to current year (-nn:+nn) or absolute (nnnn:nnnn)
		showOtherMonths: false, // True to show dates in other months, false to leave blank
		calculateWeek: this.iso8601Week, // How to calculate the week of the year,
			// takes a Date and returns the number of the week for it
		shortYearCutoff: '+10', // Short year values < this are in the current century,
			// > this are in the previous century,
			// string value starting with '+' for current year + value
		minDate: null, // The earliest selectable date, or null for no limit
		maxDate: null, // The latest selectable date, or null for no limit
		duration: 'normal', // Duration of display/closure
		beforeShowDay: null, // Function that takes a date and returns an array with
			// [0] = true if selectable, false if not, [1] = custom CSS class name(s) or '',
			// [2] = cell title (optional), e.g. $.datepicker.noWeekends
		beforeShow: null, // Function that takes an input field and
			// returns a set of custom settings for the date picker
		onSelect: null, // Define a callback function when a date is selected
		onChangeMonthYear: null, // Define a callback function when the month or year is changed
		onClose: null, // Define a callback function when the datepicker is closed
		numberOfMonths: 1, // Number of months to show at a time
		showCurrentAtPos: 0, // The position in multipe months at which to show the current month (starting at 0)
		stepMonths: 1, // Number of months to step back/forward
		stepBigMonths: 12, // Number of months to step back/forward for the big links
		altField: '', // Selector for an alternate field to store selected dates into
		altFormat: '', // The date format to use for the alternate field
		constrainInput: true, // The input is constrained by the current date format
		showButtonPanel: false // True to show button panel, false to not show it
	};
	$.extend(this._defaults, this.regional['']);
	this.dpDiv = $('<div id="' + this._mainDivId + '" class="ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all ui-helper-hidden-accessible"></div>');
}

$.extend(Datepicker.prototype, {
	/* Class name added to elements to indicate already configured with a date picker. */
	markerClassName: 'hasDatepicker',

	/* Debug logging (if enabled). */
	log: function () {
		if (this.debug)
			console.log.apply('', arguments);
	},

	/* Override the default settings for all instances of the date picker.
	   @param  settings  object - the new settings to use as defaults (anonymous object)
	   @return the manager object */
	setDefaults: function(settings) {
		extendRemove(this._defaults, settings || {});
		return this;
	},

	/* Attach the date picker to a jQuery selection.
	   @param  target    element - the target input field or division or span
	   @param  settings  object - the new settings to use for this date picker instance (anonymous) */
	_attachDatepicker: function(target, settings) {
		// check for settings on the control itself - in namespace 'date:'
		var inlineSettings = null;
		for (var attrName in this._defaults) {
			var attrValue = target.getAttribute('date:' + attrName);
			if (attrValue) {
				inlineSettings = inlineSettings || {};
				try {
					inlineSettings[attrName] = eval(attrValue);
				} catch (err) {
					inlineSettings[attrName] = attrValue;
				}
			}
		}
		var nodeName = target.nodeName.toLowerCase();
		var inline = (nodeName == 'div' || nodeName == 'span');
		if (!target.id)
			target.id = 'dp' + (++this.uuid);
		var inst = this._newInst($(target), inline);
		inst.settings = $.extend({}, settings || {}, inlineSettings || {});
		if (nodeName == 'input') {
			this._connectDatepicker(target, inst);
		} else if (inline) {
			this._inlineDatepicker(target, inst);
		}
	},

	/* Create a new instance object. */
	_newInst: function(target, inline) {
		var id = target[0].id.replace(/([:\[\]\.])/g, '\\\\$1'); // escape jQuery meta chars
		return {id: id, input: target, // associated target
			selectedDay: 0, selectedMonth: 0, selectedYear: 0, // current selection
			drawMonth: 0, drawYear: 0, // month being drawn
			inline: inline, // is datepicker inline or not
			dpDiv: (!inline ? this.dpDiv : // presentation div
			$('<div class="' + this._inlineClass + ' ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all"></div>'))};
	},

	/* Attach the date picker to an input field. */
	_connectDatepicker: function(target, inst) {
		var input = $(target);
		if (input.hasClass(this.markerClassName))
			return;
		var appendText = this._get(inst, 'appendText');
		var isRTL = this._get(inst, 'isRTL');
		if (appendText)
			input[isRTL ? 'before' : 'after']('<span class="' + this._appendClass + '">' + appendText + '</span>');
		var showOn = this._get(inst, 'showOn');
		if (showOn == 'focus' || showOn == 'both') // pop-up date picker when in the marked field
			input.focus(this._showDatepicker);
		if (showOn == 'button' || showOn == 'both') { // pop-up date picker when button clicked
			var buttonText = this._get(inst, 'buttonText');
			var buttonImage = this._get(inst, 'buttonImage');
			var trigger = $(this._get(inst, 'buttonImageOnly') ?
				$('<img/>').addClass(this._triggerClass).
					attr({ src: buttonImage, alt: buttonText, title: buttonText }) :
				$('<button type="button"></button>').addClass(this._triggerClass).
					html(buttonImage == '' ? buttonText : $('<img/>').attr(
					{ src:buttonImage, alt:buttonText, title:buttonText })));
			input[isRTL ? 'before' : 'after'](trigger);
			trigger.click(function() {
				if ($.datepicker._datepickerShowing && $.datepicker._lastInput == target)
					$.datepicker._hideDatepicker();
				else
					$.datepicker._showDatepicker(target);
				return false;
			});
		}
		input.addClass(this.markerClassName).keydown(this._doKeyDown).keypress(this._doKeyPress).
			bind("setData.datepicker", function(event, key, value) {
				inst.settings[key] = value;
			}).bind("getData.datepicker", function(event, key) {
				return this._get(inst, key);
			});
		$.data(target, PROP_NAME, inst);
	},

	/* Attach an inline date picker to a div. */
	_inlineDatepicker: function(target, inst) {
		var divSpan = $(target);
		if (divSpan.hasClass(this.markerClassName))
			return;
		divSpan.addClass(this.markerClassName).append(inst.dpDiv).
			bind("setData.datepicker", function(event, key, value){
				inst.settings[key] = value;
			}).bind("getData.datepicker", function(event, key){
				return this._get(inst, key);
			});
		$.data(target, PROP_NAME, inst);
		this._setDate(inst, this._getDefaultDate(inst));
		this._updateDatepicker(inst);
		this._updateAlternate(inst);
	},

	/* Pop-up the date picker in a "dialog" box.
	   @param  input     element - ignored
	   @param  dateText  string - the initial date to display (in the current format)
	   @param  onSelect  function - the function(dateText) to call when a date is selected
	   @param  settings  object - update the dialog date picker instance's settings (anonymous object)
	   @param  pos       int[2] - coordinates for the dialog's position within the screen or
	                     event - with x/y coordinates or
	                     leave empty for default (screen centre)
	   @return the manager object */
	_dialogDatepicker: function(input, dateText, onSelect, settings, pos) {
		var inst = this._dialogInst; // internal instance
		if (!inst) {
			var id = 'dp' + (++this.uuid);
			this._dialogInput = $('<input type="text" id="' + id +
				'" size="1" style="position: absolute; top: -100px;"/>');
			this._dialogInput.keydown(this._doKeyDown);
			$('body').append(this._dialogInput);
			inst = this._dialogInst = this._newInst(this._dialogInput, false);
			inst.settings = {};
			$.data(this._dialogInput[0], PROP_NAME, inst);
		}
		extendRemove(inst.settings, settings || {});
		this._dialogInput.val(dateText);

		this._pos = (pos ? (pos.length ? pos : [pos.pageX, pos.pageY]) : null);
		if (!this._pos) {
			var browserWidth = window.innerWidth || document.documentElement.clientWidth ||	document.body.clientWidth;
			var browserHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
			var scrollX = document.documentElement.scrollLeft || document.body.scrollLeft;
			var scrollY = document.documentElement.scrollTop || document.body.scrollTop;
			this._pos = // should use actual width/height below
				[(browserWidth / 2) - 100 + scrollX, (browserHeight / 2) - 150 + scrollY];
		}

		// move input on screen for focus, but hidden behind dialog
		this._dialogInput.css('left', this._pos[0] + 'px').css('top', this._pos[1] + 'px');
		inst.settings.onSelect = onSelect;
		this._inDialog = true;
		this.dpDiv.addClass(this._dialogClass);
		this._showDatepicker(this._dialogInput[0]);
		if ($.blockUI)
			$.blockUI(this.dpDiv);
		$.data(this._dialogInput[0], PROP_NAME, inst);
		return this;
	},

	/* Detach a datepicker from its control.
	   @param  target    element - the target input field or division or span */
	_destroyDatepicker: function(target) {
		var $target = $(target);
		if (!$target.hasClass(this.markerClassName)) {
			return;
		}
		var nodeName = target.nodeName.toLowerCase();
		$.removeData(target, PROP_NAME);
		if (nodeName == 'input') {
			$target.siblings('.' + this._appendClass).remove().end().
				siblings('.' + this._triggerClass).remove().end().
				removeClass(this.markerClassName).
				unbind('focus', this._showDatepicker).
				unbind('keydown', this._doKeyDown).
				unbind('keypress', this._doKeyPress);
		} else if (nodeName == 'div' || nodeName == 'span')
			$target.removeClass(this.markerClassName).empty();
	},

	/* Enable the date picker to a jQuery selection.
	   @param  target    element - the target input field or division or span */
	_enableDatepicker: function(target) {
		var $target = $(target);
		if (!$target.hasClass(this.markerClassName)) {
			return;
		}
		var nodeName = target.nodeName.toLowerCase();
		if (nodeName == 'input') {
		target.disabled = false;
			$target.siblings('button.' + this._triggerClass).
			each(function() { this.disabled = false; }).end().
				siblings('img.' + this._triggerClass).
				css({opacity: '1.0', cursor: ''});
		}
		else if (nodeName == 'div' || nodeName == 'span') {
			var inline = $target.children('.' + this._inlineClass);
			inline.children().removeClass('ui-state-disabled');
		}
		this._disabledInputs = $.map(this._disabledInputs,
			function(value) { return (value == target ? null : value); }); // delete entry
	},

	/* Disable the date picker to a jQuery selection.
	   @param  target    element - the target input field or division or span */
	_disableDatepicker: function(target) {
		var $target = $(target);
		if (!$target.hasClass(this.markerClassName)) {
			return;
		}
		var nodeName = target.nodeName.toLowerCase();
		if (nodeName == 'input') {
		target.disabled = true;
			$target.siblings('button.' + this._triggerClass).
			each(function() { this.disabled = true; }).end().
				siblings('img.' + this._triggerClass).
				css({opacity: '0.5', cursor: 'default'});
		}
		else if (nodeName == 'div' || nodeName == 'span') {
			var inline = $target.children('.' + this._inlineClass);
			inline.children().addClass('ui-state-disabled');
		}
		this._disabledInputs = $.map(this._disabledInputs,
			function(value) { return (value == target ? null : value); }); // delete entry
		this._disabledInputs[this._disabledInputs.length] = target;
	},

	/* Is the first field in a jQuery collection disabled as a datepicker?
	   @param  target    element - the target input field or division or span
	   @return boolean - true if disabled, false if enabled */
	_isDisabledDatepicker: function(target) {
		if (!target) {
			return false;
		}
		for (var i = 0; i < this._disabledInputs.length; i++) {
			if (this._disabledInputs[i] == target)
				return true;
		}
		return false;
	},

	/* Retrieve the instance data for the target control.
	   @param  target  element - the target input field or division or span
	   @return  object - the associated instance data
	   @throws  error if a jQuery problem getting data */
	_getInst: function(target) {
		try {
			return $.data(target, PROP_NAME);
		}
		catch (err) {
			throw 'Missing instance data for this datepicker';
		}
	},

	/* Update the settings for a date picker attached to an input field or division.
	   @param  target  element - the target input field or division or span
	   @param  name    object - the new settings to update or
	                   string - the name of the setting to change or
	   @param  value   any - the new value for the setting (omit if above is an object) */
	_optionDatepicker: function(target, name, value) {
		var settings = name || {};
		if (typeof name == 'string') {
			settings = {};
			settings[name] = value;
		}
		var inst = this._getInst(target);
		if (inst) {
			if (this._curInst == inst) {
				this._hideDatepicker(null);
			}
			extendRemove(inst.settings, settings);
			var date = new Date();
			extendRemove(inst, {rangeStart: null, // start of range
				endDay: null, endMonth: null, endYear: null, // end of range
				selectedDay: date.getDate(), selectedMonth: date.getMonth(),
				selectedYear: date.getFullYear(), // starting point
				currentDay: date.getDate(), currentMonth: date.getMonth(),
				currentYear: date.getFullYear(), // current selection
				drawMonth: date.getMonth(), drawYear: date.getFullYear()}); // month being drawn
			this._updateDatepicker(inst);
		}
	},

	// change method deprecated
	_changeDatepicker: function(target, name, value) {
		this._optionDatepicker(target, name, value);
	},

	/* Redraw the date picker attached to an input field or division.
	   @param  target  element - the target input field or division or span */
	_refreshDatepicker: function(target) {
		var inst = this._getInst(target);
		if (inst) {
			this._updateDatepicker(inst);
		}
	},

	/* Set the dates for a jQuery selection.
	   @param  target   element - the target input field or division or span
	   @param  date     Date - the new date
	   @param  endDate  Date - the new end date for a range (optional) */
	_setDateDatepicker: function(target, date, endDate) {
		var inst = this._getInst(target);
		if (inst) {
			this._setDate(inst, date, endDate);
			this._updateDatepicker(inst);
			this._updateAlternate(inst);
		}
	},

	/* Get the date(s) for the first entry in a jQuery selection.
	   @param  target  element - the target input field or division or span
	   @return Date - the current date or
	           Date[2] - the current dates for a range */
	_getDateDatepicker: function(target) {
		var inst = this._getInst(target);
		if (inst && !inst.inline)
			this._setDateFromField(inst);
		return (inst ? this._getDate(inst) : null);
	},

	/* Handle keystrokes. */
	_doKeyDown: function(event) {
		var inst = $.datepicker._getInst(event.target);
		var handled = true;
		var isRTL = inst.dpDiv.is('.ui-datepicker-rtl');
		inst._keyEvent = true;
		if ($.datepicker._datepickerShowing)
			switch (event.keyCode) {
				case 9:  $.datepicker._hideDatepicker(null, '');
						break; // hide on tab out
				case 13: var sel = $('td.' + $.datepicker._dayOverClass +
							', td.' + $.datepicker._currentClass, inst.dpDiv);
						if (sel[0])
							$.datepicker._selectDay(event.target, inst.selectedMonth, inst.selectedYear, sel[0]);
						else
							$.datepicker._hideDatepicker(null, $.datepicker._get(inst, 'duration'));
						return false; // don't submit the form
						break; // select the value on enter
				case 27: $.datepicker._hideDatepicker(null, $.datepicker._get(inst, 'duration'));
						break; // hide on escape
				case 33: $.datepicker._adjustDate(event.target, (event.ctrlKey ?
							-$.datepicker._get(inst, 'stepBigMonths') :
							-$.datepicker._get(inst, 'stepMonths')), 'M');
						break; // previous month/year on page up/+ ctrl
				case 34: $.datepicker._adjustDate(event.target, (event.ctrlKey ?
							+$.datepicker._get(inst, 'stepBigMonths') :
							+$.datepicker._get(inst, 'stepMonths')), 'M');
						break; // next month/year on page down/+ ctrl
				case 35: if (event.ctrlKey || event.metaKey) $.datepicker._clearDate(event.target);
						handled = event.ctrlKey || event.metaKey;
						break; // clear on ctrl or command +end
				case 36: if (event.ctrlKey || event.metaKey) $.datepicker._gotoToday(event.target);
						handled = event.ctrlKey || event.metaKey;
						break; // current on ctrl or command +home
				case 37: if (event.ctrlKey || event.metaKey) $.datepicker._adjustDate(event.target, (isRTL ? +1 : -1), 'D');
						handled = event.ctrlKey || event.metaKey;
						// -1 day on ctrl or command +left
						if (event.originalEvent.altKey) $.datepicker._adjustDate(event.target, (event.ctrlKey ?
									-$.datepicker._get(inst, 'stepBigMonths') :
									-$.datepicker._get(inst, 'stepMonths')), 'M');
						// next month/year on alt +left on Mac
						break;
				case 38: if (event.ctrlKey || event.metaKey) $.datepicker._adjustDate(event.target, -7, 'D');
						handled = event.ctrlKey || event.metaKey;
						break; // -1 week on ctrl or command +up
				case 39: if (event.ctrlKey || event.metaKey) $.datepicker._adjustDate(event.target, (isRTL ? -1 : +1), 'D');
						handled = event.ctrlKey || event.metaKey;
						// +1 day on ctrl or command +right
						if (event.originalEvent.altKey) $.datepicker._adjustDate(event.target, (event.ctrlKey ?
									+$.datepicker._get(inst, 'stepBigMonths') :
									+$.datepicker._get(inst, 'stepMonths')), 'M');
						// next month/year on alt +right
						break;
				case 40: if (event.ctrlKey || event.metaKey) $.datepicker._adjustDate(event.target, +7, 'D');
						handled = event.ctrlKey || event.metaKey;
						break; // +1 week on ctrl or command +down
				default: handled = false;
			}
		else if (event.keyCode == 36 && event.ctrlKey) // display the date picker on ctrl+home
			$.datepicker._showDatepicker(this);
		else {
			handled = false;
		}
		if (handled) {
			event.preventDefault();
			event.stopPropagation();
		}
	},

	/* Filter entered characters - based on date format. */
	_doKeyPress: function(event) {
		var inst = $.datepicker._getInst(event.target);
		if ($.datepicker._get(inst, 'constrainInput')) {
			var chars = $.datepicker._possibleChars($.datepicker._get(inst, 'dateFormat'));
			var chr = String.fromCharCode(event.charCode == undefined ? event.keyCode : event.charCode);
			return event.ctrlKey || (chr < ' ' || !chars || chars.indexOf(chr) > -1);
		}
	},

	/* Pop-up the date picker for a given input field.
	   @param  input  element - the input field attached to the date picker or
	                  event - if triggered by focus */
	_showDatepicker: function(input) {
		input = input.target || input;
		if (input.nodeName.toLowerCase() != 'input') // find from button/image trigger
			input = $('input', input.parentNode)[0];
		if ($.datepicker._isDisabledDatepicker(input) || $.datepicker._lastInput == input) // already here
			return;
		var inst = $.datepicker._getInst(input);
		var beforeShow = $.datepicker._get(inst, 'beforeShow');
		extendRemove(inst.settings, (beforeShow ? beforeShow.apply(input, [input, inst]) : {}));
		$.datepicker._hideDatepicker(null, '');
		$.datepicker._lastInput = input;
		$.datepicker._setDateFromField(inst);
		if ($.datepicker._inDialog) // hide cursor
			input.value = '';
		if (!$.datepicker._pos) { // position below input
			$.datepicker._pos = $.datepicker._findPos(input);
			$.datepicker._pos[1] += input.offsetHeight; // add the height
		}
		var isFixed = false;
		$(input).parents().each(function() {
			isFixed |= $(this).css('position') == 'fixed';
			return !isFixed;
		});
		if (isFixed && $.browser.opera) { // correction for Opera when fixed and scrolled
			$.datepicker._pos[0] -= document.documentElement.scrollLeft;
			$.datepicker._pos[1] -= document.documentElement.scrollTop;
		}
		var offset = {left: $.datepicker._pos[0], top: $.datepicker._pos[1]};
		$.datepicker._pos = null;
		inst.rangeStart = null;
		// determine sizing offscreen
		inst.dpDiv.css({position: 'absolute', display: 'block', top: '-1000px'});
		$.datepicker._updateDatepicker(inst);
		// fix width for dynamic number of date pickers
		// and adjust position before showing
		offset = $.datepicker._checkOffset(inst, offset, isFixed);
		inst.dpDiv.css({position: ($.datepicker._inDialog && $.blockUI ?
			'static' : (isFixed ? 'fixed' : 'absolute')), display: 'none',
			left: offset.left + 'px', top: offset.top + 'px'});
		if (!inst.inline) {
			var showAnim = $.datepicker._get(inst, 'showAnim') || 'show';
			var duration = $.datepicker._get(inst, 'duration');
			var postProcess = function() {
				$.datepicker._datepickerShowing = true;
				if ($.browser.msie && parseInt($.browser.version,10) < 7) // fix IE < 7 select problems
					$('iframe.ui-datepicker-cover').css({width: inst.dpDiv.width() + 4,
						height: inst.dpDiv.height() + 4});
			};
			if ($.effects && $.effects[showAnim])
				inst.dpDiv.show(showAnim, $.datepicker._get(inst, 'showOptions'), duration, postProcess);
			else
				inst.dpDiv[showAnim](duration, postProcess);
			if (duration == '')
				postProcess();
			if (inst.input[0].type != 'hidden')
				inst.input[0].focus();
			$.datepicker._curInst = inst;
		}
	},

	/* Generate the date picker content. */
	_updateDatepicker: function(inst) {
		var dims = {width: inst.dpDiv.width() + 4,
			height: inst.dpDiv.height() + 4};
		var self = this;
		inst.dpDiv.empty().append(this._generateHTML(inst))
			.find('iframe.ui-datepicker-cover').
				css({width: dims.width, height: dims.height})
			.end()
			.find('button, .ui-datepicker-prev, .ui-datepicker-next, .ui-datepicker-calendar td a')
				.bind('mouseout', function(){
					$(this).removeClass('ui-state-hover');
					if(this.className.indexOf('ui-datepicker-prev') != -1) $(this).removeClass('ui-datepicker-prev-hover');
					if(this.className.indexOf('ui-datepicker-next') != -1) $(this).removeClass('ui-datepicker-next-hover');
				})
				.bind('mouseover', function(){
					if (!self._isDisabledDatepicker( inst.inline ? inst.dpDiv.parent()[0] : inst.input[0])) {
						$(this).parents('.ui-datepicker-calendar').find('a').removeClass('ui-state-hover');
						$(this).addClass('ui-state-hover');
						if(this.className.indexOf('ui-datepicker-prev') != -1) $(this).addClass('ui-datepicker-prev-hover');
						if(this.className.indexOf('ui-datepicker-next') != -1) $(this).addClass('ui-datepicker-next-hover');
					}
				})
			.end()
			.find('.' + this._dayOverClass + ' a')
				.trigger('mouseover')
			.end();
		var numMonths = this._getNumberOfMonths(inst);
		var cols = numMonths[1];
		var width = 17;
		if (cols > 1) {
			inst.dpDiv.addClass('ui-datepicker-multi-' + cols).css('width', (width * cols) + 'em');
		} else {
			inst.dpDiv.removeClass('ui-datepicker-multi-2 ui-datepicker-multi-3 ui-datepicker-multi-4').width('');
		}
		inst.dpDiv[(numMonths[0] != 1 || numMonths[1] != 1 ? 'add' : 'remove') +
			'Class']('ui-datepicker-multi');
		inst.dpDiv[(this._get(inst, 'isRTL') ? 'add' : 'remove') +
			'Class']('ui-datepicker-rtl');
		if (inst.input && inst.input[0].type != 'hidden' && inst == $.datepicker._curInst)
			$(inst.input[0]).focus();
	},

	/* Check positioning to remain on screen. */
	_checkOffset: function(inst, offset, isFixed) {
		var dpWidth = inst.dpDiv.outerWidth();
		var dpHeight = inst.dpDiv.outerHeight();
		var inputWidth = inst.input ? inst.input.outerWidth() : 0;
		var inputHeight = inst.input ? inst.input.outerHeight() : 0;
		var viewWidth = (window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth) + $(document).scrollLeft();
		var viewHeight = (window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight) + $(document).scrollTop();

		offset.left -= (this._get(inst, 'isRTL') ? (dpWidth - inputWidth) : 0);
		offset.left -= (isFixed && offset.left == inst.input.offset().left) ? $(document).scrollLeft() : 0;
		offset.top -= (isFixed && offset.top == (inst.input.offset().top + inputHeight)) ? $(document).scrollTop() : 0;

		// now check if datepicker is showing outside window viewport - move to a better place if so.
		offset.left -= (offset.left + dpWidth > viewWidth && viewWidth > dpWidth) ? Math.abs(offset.left + dpWidth - viewWidth) : 0;
		offset.top -= (offset.top + dpHeight > viewHeight && viewHeight > dpHeight) ? Math.abs(offset.top + dpHeight + inputHeight*2 - viewHeight) : 0;

		return offset;
	},

	/* Find an object's position on the screen. */
	_findPos: function(obj) {
        while (obj && (obj.type == 'hidden' || obj.nodeType != 1)) {
            obj = obj.nextSibling;
        }
        var position = $(obj).offset();
	    return [position.left, position.top];
	},

	/* Hide the date picker from view.
	   @param  input  element - the input field attached to the date picker
	   @param  duration  string - the duration over which to close the date picker */
	_hideDatepicker: function(input, duration) {
		var inst = this._curInst;
		if (!inst || (input && inst != $.data(input, PROP_NAME)))
			return;
		if (inst.stayOpen)
			this._selectDate('#' + inst.id, this._formatDate(inst,
				inst.currentDay, inst.currentMonth, inst.currentYear));
		inst.stayOpen = false;
		if (this._datepickerShowing) {
			duration = (duration != null ? duration : this._get(inst, 'duration'));
			var showAnim = this._get(inst, 'showAnim');
			var postProcess = function() {
				$.datepicker._tidyDialog(inst);
			};
			if (duration != '' && $.effects && $.effects[showAnim])
				inst.dpDiv.hide(showAnim, $.datepicker._get(inst, 'showOptions'),
					duration, postProcess);
			else
				inst.dpDiv[(duration == '' ? 'hide' : (showAnim == 'slideDown' ? 'slideUp' :
					(showAnim == 'fadeIn' ? 'fadeOut' : 'hide')))](duration, postProcess);
			if (duration == '')
				this._tidyDialog(inst);
			var onClose = this._get(inst, 'onClose');
			if (onClose)
				onClose.apply((inst.input ? inst.input[0] : null),
					[(inst.input ? inst.input.val() : ''), inst]);  // trigger custom callback
			this._datepickerShowing = false;
			this._lastInput = null;
			if (this._inDialog) {
				this._dialogInput.css({ position: 'absolute', left: '0', top: '-100px' });
				if ($.blockUI) {
					$.unblockUI();
					$('body').append(this.dpDiv);
				}
			}
			this._inDialog = false;
		}
		this._curInst = null;
	},

	/* Tidy up after a dialog display. */
	_tidyDialog: function(inst) {
		inst.dpDiv.removeClass(this._dialogClass).unbind('.ui-datepicker-calendar');
	},

	/* Close date picker if clicked elsewhere. */
	_checkExternalClick: function(event) {
		if (!$.datepicker._curInst)
			return;
		var $target = $(event.target);
		if (($target.parents('#' + $.datepicker._mainDivId).length == 0) &&
				!$target.hasClass($.datepicker.markerClassName) &&
				!$target.hasClass($.datepicker._triggerClass) &&
				$.datepicker._datepickerShowing && !($.datepicker._inDialog && $.blockUI))
			$.datepicker._hideDatepicker(null, '');
	},

	/* Adjust one of the date sub-fields. */
	_adjustDate: function(id, offset, period) {
		var target = $(id);
		var inst = this._getInst(target[0]);
		if (this._isDisabledDatepicker(target[0])) {
			return;
		}
		this._adjustInstDate(inst, offset +
			(period == 'M' ? this._get(inst, 'showCurrentAtPos') : 0), // undo positioning
			period);
		this._updateDatepicker(inst);
	},

	/* Action for current link. */
	_gotoToday: function(id) {
		var target = $(id);
		var inst = this._getInst(target[0]);
		if (this._get(inst, 'gotoCurrent') && inst.currentDay) {
			inst.selectedDay = inst.currentDay;
			inst.drawMonth = inst.selectedMonth = inst.currentMonth;
			inst.drawYear = inst.selectedYear = inst.currentYear;
		}
		else {
		var date = new Date();
		inst.selectedDay = date.getDate();
		inst.drawMonth = inst.selectedMonth = date.getMonth();
		inst.drawYear = inst.selectedYear = date.getFullYear();
		}
		this._notifyChange(inst);
		this._adjustDate(target);
	},

	/* Action for selecting a new month/year. */
	_selectMonthYear: function(id, select, period) {
		var target = $(id);
		var inst = this._getInst(target[0]);
		inst._selectingMonthYear = false;
		inst['selected' + (period == 'M' ? 'Month' : 'Year')] =
		inst['draw' + (period == 'M' ? 'Month' : 'Year')] =
			parseInt(select.options[select.selectedIndex].value,10);
		this._notifyChange(inst);
		this._adjustDate(target);
	},

	/* Restore input focus after not changing month/year. */
	_clickMonthYear: function(id) {
		var target = $(id);
		var inst = this._getInst(target[0]);
		if (inst.input && inst._selectingMonthYear && !$.browser.msie)
			inst.input[0].focus();
		inst._selectingMonthYear = !inst._selectingMonthYear;
	},

	/* Action for selecting a day. */
	_selectDay: function(id, month, year, td) {
		var target = $(id);
		if ($(td).hasClass(this._unselectableClass) || this._isDisabledDatepicker(target[0])) {
			return;
		}
		var inst = this._getInst(target[0]);
		inst.selectedDay = inst.currentDay = $('a', td).html();
		inst.selectedMonth = inst.currentMonth = month;
		inst.selectedYear = inst.currentYear = year;
		if (inst.stayOpen) {
			inst.endDay = inst.endMonth = inst.endYear = null;
		}
		this._selectDate(id, this._formatDate(inst,
			inst.currentDay, inst.currentMonth, inst.currentYear));
		if (inst.stayOpen) {
			inst.rangeStart = this._daylightSavingAdjust(
				new Date(inst.currentYear, inst.currentMonth, inst.currentDay));
			this._updateDatepicker(inst);
		}
	},

	/* Erase the input field and hide the date picker. */
	_clearDate: function(id) {
		var target = $(id);
		var inst = this._getInst(target[0]);
		inst.stayOpen = false;
		inst.endDay = inst.endMonth = inst.endYear = inst.rangeStart = null;
		this._selectDate(target, '');
	},

	/* Update the input field with the selected date. */
	_selectDate: function(id, dateStr) {
		var target = $(id);
		var inst = this._getInst(target[0]);
		dateStr = (dateStr != null ? dateStr : this._formatDate(inst));
		if (inst.input)
			inst.input.val(dateStr);
		this._updateAlternate(inst);
		var onSelect = this._get(inst, 'onSelect');
		if (onSelect)
			onSelect.apply((inst.input ? inst.input[0] : null), [dateStr, inst]);  // trigger custom callback
		else if (inst.input)
			inst.input.trigger('change'); // fire the change event
		if (inst.inline)
			this._updateDatepicker(inst);
		else if (!inst.stayOpen) {
			this._hideDatepicker(null, this._get(inst, 'duration'));
			this._lastInput = inst.input[0];
			if (typeof(inst.input[0]) != 'object')
				inst.input[0].focus(); // restore focus
			this._lastInput = null;
		}
	},

	/* Update any alternate field to synchronise with the main field. */
	_updateAlternate: function(inst) {
		var altField = this._get(inst, 'altField');
		if (altField) { // update alternate field too
			var altFormat = this._get(inst, 'altFormat') || this._get(inst, 'dateFormat');
			var date = this._getDate(inst);
			dateStr = this.formatDate(altFormat, date, this._getFormatConfig(inst));
			$(altField).each(function() { $(this).val(dateStr); });
		}
	},

	/* Set as beforeShowDay function to prevent selection of weekends.
	   @param  date  Date - the date to customise
	   @return [boolean, string] - is this date selectable?, what is its CSS class? */
	noWeekends: function(date) {
		var day = date.getDay();
		return [(day > 0 && day < 6), ''];
	},

	/* Set as calculateWeek to determine the week of the year based on the ISO 8601 definition.
	   @param  date  Date - the date to get the week for
	   @return  number - the number of the week within the year that contains this date */
	iso8601Week: function(date) {
		var checkDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
		var firstMon = new Date(checkDate.getFullYear(), 1 - 1, 4); // First week always contains 4 Jan
		var firstDay = firstMon.getDay() || 7; // Day of week: Mon = 1, ..., Sun = 7
		firstMon.setDate(firstMon.getDate() + 1 - firstDay); // Preceding Monday
		if (firstDay < 4 && checkDate < firstMon) { // Adjust first three days in year if necessary
			checkDate.setDate(checkDate.getDate() - 3); // Generate for previous year
			return $.datepicker.iso8601Week(checkDate);
		} else if (checkDate > new Date(checkDate.getFullYear(), 12 - 1, 28)) { // Check last three days in year
			firstDay = new Date(checkDate.getFullYear() + 1, 1 - 1, 4).getDay() || 7;
			if (firstDay > 4 && (checkDate.getDay() || 7) < firstDay - 3) { // Adjust if necessary
				return 1;
			}
		}
		return Math.floor(((checkDate - firstMon) / 86400000) / 7) + 1; // Weeks to given date
	},

	/* Parse a string value into a date object.
	   See formatDate below for the possible formats.

	   @param  format    string - the expected format of the date
	   @param  value     string - the date in the above format
	   @param  settings  Object - attributes include:
	                     shortYearCutoff  number - the cutoff year for determining the century (optional)
	                     dayNamesShort    string[7] - abbreviated names of the days from Sunday (optional)
	                     dayNames         string[7] - names of the days from Sunday (optional)
	                     monthNamesShort  string[12] - abbreviated names of the months (optional)
	                     monthNames       string[12] - names of the months (optional)
	   @return  Date - the extracted date value or null if value is blank */
	parseDate: function (format, value, settings) {
		if (format == null || value == null)
			throw 'Invalid arguments';
		value = (typeof value == 'object' ? value.toString() : value + '');
		if (value == '')
			return null;
		var shortYearCutoff = (settings ? settings.shortYearCutoff : null) || this._defaults.shortYearCutoff;
		var dayNamesShort = (settings ? settings.dayNamesShort : null) || this._defaults.dayNamesShort;
		var dayNames = (settings ? settings.dayNames : null) || this._defaults.dayNames;
		var monthNamesShort = (settings ? settings.monthNamesShort : null) || this._defaults.monthNamesShort;
		var monthNames = (settings ? settings.monthNames : null) || this._defaults.monthNames;
		var year = -1;
		var month = -1;
		var day = -1;
		var doy = -1;
		var literal = false;
		// Check whether a format character is doubled
		var lookAhead = function(match) {
			var matches = (iFormat + 1 < format.length && format.charAt(iFormat + 1) == match);
			if (matches)
				iFormat++;
			return matches;
		};
		// Extract a number from the string value
		var getNumber = function(match) {
			lookAhead(match);
			var origSize = (match == '@' ? 14 : (match == 'y' ? 4 : (match == 'o' ? 3 : 2)));
			var size = origSize;
			var num = 0;
			while (size > 0 && iValue < value.length &&
					value.charAt(iValue) >= '0' && value.charAt(iValue) <= '9') {
				num = num * 10 + parseInt(value.charAt(iValue++),10);
				size--;
			}
			if (size == origSize)
				throw 'Missing number at position ' + iValue;
			return num;
		};
		// Extract a name from the string value and convert to an index
		var getName = function(match, shortNames, longNames) {
			var names = (lookAhead(match) ? longNames : shortNames);
			var size = 0;
			for (var j = 0; j < names.length; j++)
				size = Math.max(size, names[j].length);
			var name = '';
			var iInit = iValue;
			while (size > 0 && iValue < value.length) {
				name += value.charAt(iValue++);
				for (var i = 0; i < names.length; i++)
					if (name == names[i])
						return i + 1;
				size--;
			}
			throw 'Unknown name at position ' + iInit;
		};
		// Confirm that a literal character matches the string value
		var checkLiteral = function() {
			if (value.charAt(iValue) != format.charAt(iFormat))
				throw 'Unexpected literal at position ' + iValue;
			iValue++;
		};
		var iValue = 0;
		for (var iFormat = 0; iFormat < format.length; iFormat++) {
			if (literal)
				if (format.charAt(iFormat) == "'" && !lookAhead("'"))
					literal = false;
				else
					checkLiteral();
			else
				switch (format.charAt(iFormat)) {
					case 'd':
						day = getNumber('d');
						break;
					case 'D':
						getName('D', dayNamesShort, dayNames);
						break;
					case 'o':
						doy = getNumber('o');
						break;
					case 'm':
						month = getNumber('m');
						break;
					case 'M':
						month = getName('M', monthNamesShort, monthNames);
						break;
					case 'y':
						year = getNumber('y');
						break;
					case '@':
						var date = new Date(getNumber('@'));
						year = date.getFullYear();
						month = date.getMonth() + 1;
						day = date.getDate();
						break;
					case "'":
						if (lookAhead("'"))
							checkLiteral();
						else
							literal = true;
						break;
					default:
						checkLiteral();
				}
		}
		if (year == -1)
			year = new Date().getFullYear();
		else if (year < 100)
			year += new Date().getFullYear() - new Date().getFullYear() % 100 +
				(year <= shortYearCutoff ? 0 : -100);
		if (doy > -1) {
			month = 1;
			day = doy;
			do {
				var dim = this._getDaysInMonth(year, month - 1);
				if (day <= dim)
					break;
				month++;
				day -= dim;
			} while (true);
		}
		var date = this._daylightSavingAdjust(new Date(year, month - 1, day));
		if (date.getFullYear() != year || date.getMonth() + 1 != month || date.getDate() != day)
			throw 'Invalid date'; // E.g. 31/02/*
		return date;
	},

	/* Standard date formats. */
	ATOM: 'yy-mm-dd', // RFC 3339 (ISO 8601)
	COOKIE: 'D, dd M yy',
	ISO_8601: 'yy-mm-dd',
	RFC_822: 'D, d M y',
	RFC_850: 'DD, dd-M-y',
	RFC_1036: 'D, d M y',
	RFC_1123: 'D, d M yy',
	RFC_2822: 'D, d M yy',
	RSS: 'D, d M y', // RFC 822
	TIMESTAMP: '@',
	W3C: 'yy-mm-dd', // ISO 8601

	/* Format a date object into a string value.
	   The format can be combinations of the following:
	   d  - day of month (no leading zero)
	   dd - day of month (two digit)
	   o  - day of year (no leading zeros)
	   oo - day of year (three digit)
	   D  - day name short
	   DD - day name long
	   m  - month of year (no leading zero)
	   mm - month of year (two digit)
	   M  - month name short
	   MM - month name long
	   y  - year (two digit)
	   yy - year (four digit)
	   @ - Unix timestamp (ms since 01/01/1970)
	   '...' - literal text
	   '' - single quote

	   @param  format    string - the desired format of the date
	   @param  date      Date - the date value to format
	   @param  settings  Object - attributes include:
	                     dayNamesShort    string[7] - abbreviated names of the days from Sunday (optional)
	                     dayNames         string[7] - names of the days from Sunday (optional)
	                     monthNamesShort  string[12] - abbreviated names of the months (optional)
	                     monthNames       string[12] - names of the months (optional)
	   @return  string - the date in the above format */
	formatDate: function (format, date, settings) {
		if (!date)
			return '';
		var dayNamesShort = (settings ? settings.dayNamesShort : null) || this._defaults.dayNamesShort;
		var dayNames = (settings ? settings.dayNames : null) || this._defaults.dayNames;
		var monthNamesShort = (settings ? settings.monthNamesShort : null) || this._defaults.monthNamesShort;
		var monthNames = (settings ? settings.monthNames : null) || this._defaults.monthNames;
		// Check whether a format character is doubled
		var lookAhead = function(match) {
			var matches = (iFormat + 1 < format.length && format.charAt(iFormat + 1) == match);
			if (matches)
				iFormat++;
			return matches;
		};
		// Format a number, with leading zero if necessary
		var formatNumber = function(match, value, len) {
			var num = '' + value;
			if (lookAhead(match))
				while (num.length < len)
					num = '0' + num;
			return num;
		};
		// Format a name, short or long as requested
		var formatName = function(match, value, shortNames, longNames) {
			return (lookAhead(match) ? longNames[value] : shortNames[value]);
		};
		var output = '';
		var literal = false;
		if (date)
			for (var iFormat = 0; iFormat < format.length; iFormat++) {
				if (literal)
					if (format.charAt(iFormat) == "'" && !lookAhead("'"))
						literal = false;
					else
						output += format.charAt(iFormat);
				else
					switch (format.charAt(iFormat)) {
						case 'd':
							output += formatNumber('d', date.getDate(), 2);
							break;
						case 'D':
							output += formatName('D', date.getDay(), dayNamesShort, dayNames);
							break;
						case 'o':
							var doy = date.getDate();
							for (var m = date.getMonth() - 1; m >= 0; m--)
								doy += this._getDaysInMonth(date.getFullYear(), m);
							output += formatNumber('o', doy, 3);
							break;
						case 'm':
							output += formatNumber('m', date.getMonth() + 1, 2);
							break;
						case 'M':
							output += formatName('M', date.getMonth(), monthNamesShort, monthNames);
							break;
						case 'y':
							output += (lookAhead('y') ? date.getFullYear() :
								(date.getYear() % 100 < 10 ? '0' : '') + date.getYear() % 100);
							break;
						case '@':
							output += date.getTime();
							break;
						case "'":
							if (lookAhead("'"))
								output += "'";
							else
								literal = true;
							break;
						default:
							output += format.charAt(iFormat);
					}
			}
		return output;
	},

	/* Extract all possible characters from the date format. */
	_possibleChars: function (format) {
		var chars = '';
		var literal = false;
		for (var iFormat = 0; iFormat < format.length; iFormat++)
			if (literal)
				if (format.charAt(iFormat) == "'" && !lookAhead("'"))
					literal = false;
				else
					chars += format.charAt(iFormat);
			else
				switch (format.charAt(iFormat)) {
					case 'd': case 'm': case 'y': case '@':
						chars += '0123456789';
						break;
					case 'D': case 'M':
						return null; // Accept anything
					case "'":
						if (lookAhead("'"))
							chars += "'";
						else
							literal = true;
						break;
					default:
						chars += format.charAt(iFormat);
				}
		return chars;
	},

	/* Get a setting value, defaulting if necessary. */
	_get: function(inst, name) {
		return inst.settings[name] !== undefined ?
			inst.settings[name] : this._defaults[name];
	},

	/* Parse existing date and initialise date picker. */
	_setDateFromField: function(inst) {
		var dateFormat = this._get(inst, 'dateFormat');
		var dates = inst.input ? inst.input.val() : null;
		inst.endDay = inst.endMonth = inst.endYear = null;
		var date = defaultDate = this._getDefaultDate(inst);
		var settings = this._getFormatConfig(inst);
		try {
			date = this.parseDate(dateFormat, dates, settings) || defaultDate;
		} catch (event) {
			this.log(event);
			date = defaultDate;
		}
		inst.selectedDay = date.getDate();
		inst.drawMonth = inst.selectedMonth = date.getMonth();
		inst.drawYear = inst.selectedYear = date.getFullYear();
		inst.currentDay = (dates ? date.getDate() : 0);
		inst.currentMonth = (dates ? date.getMonth() : 0);
		inst.currentYear = (dates ? date.getFullYear() : 0);
		this._adjustInstDate(inst);
	},

	/* Retrieve the default date shown on opening. */
	_getDefaultDate: function(inst) {
		var date = this._determineDate(this._get(inst, 'defaultDate'), new Date());
		var minDate = this._getMinMaxDate(inst, 'min', true);
		var maxDate = this._getMinMaxDate(inst, 'max');
		date = (minDate && date < minDate ? minDate : date);
		date = (maxDate && date > maxDate ? maxDate : date);
		return date;
	},

	/* A date may be specified as an exact value or a relative one. */
	_determineDate: function(date, defaultDate) {
		var offsetNumeric = function(offset) {
			var date = new Date();
			date.setDate(date.getDate() + offset);
			return date;
		};
		var offsetString = function(offset, getDaysInMonth) {
			var date = new Date();
			var year = date.getFullYear();
			var month = date.getMonth();
			var day = date.getDate();
			var pattern = /([+-]?[0-9]+)\s*(d|D|w|W|m|M|y|Y)?/g;
			var matches = pattern.exec(offset);
			while (matches) {
				switch (matches[2] || 'd') {
					case 'd' : case 'D' :
						day += parseInt(matches[1],10); break;
					case 'w' : case 'W' :
						day += parseInt(matches[1],10) * 7; break;
					case 'm' : case 'M' :
						month += parseInt(matches[1],10);
						day = Math.min(day, getDaysInMonth(year, month));
						break;
					case 'y': case 'Y' :
						year += parseInt(matches[1],10);
						day = Math.min(day, getDaysInMonth(year, month));
						break;
				}
				matches = pattern.exec(offset);
			}
			return new Date(year, month, day);
		};
		date = (date == null ? defaultDate :
			(typeof date == 'string' ? offsetString(date, this._getDaysInMonth) :
			(typeof date == 'number' ? (isNaN(date) ? defaultDate : offsetNumeric(date)) : date)));
		date = (date && date.toString() == 'Invalid Date' ? defaultDate : date);
		if (date) {
			date.setHours(0);
			date.setMinutes(0);
			date.setSeconds(0);
			date.setMilliseconds(0);
		}
		return this._daylightSavingAdjust(date);
	},

	/* Handle switch to/from daylight saving.
	   Hours may be non-zero on daylight saving cut-over:
	   > 12 when midnight changeover, but then cannot generate
	   midnight datetime, so jump to 1AM, otherwise reset.
	   @param  date  (Date) the date to check
	   @return  (Date) the corrected date */
	_daylightSavingAdjust: function(date) {
		if (!date) return null;
		date.setHours(date.getHours() > 12 ? date.getHours() + 2 : 0);
		return date;
	},

	/* Set the date(s) directly. */
	_setDate: function(inst, date, endDate) {
		var clear = !(date);
		var origMonth = inst.selectedMonth;
		var origYear = inst.selectedYear;
		date = this._determineDate(date, new Date());
		inst.selectedDay = inst.currentDay = date.getDate();
		inst.drawMonth = inst.selectedMonth = inst.currentMonth = date.getMonth();
		inst.drawYear = inst.selectedYear = inst.currentYear = date.getFullYear();
		if (origMonth != inst.selectedMonth || origYear != inst.selectedYear)
			this._notifyChange(inst);
		this._adjustInstDate(inst);
		if (inst.input) {
			inst.input.val(clear ? '' : this._formatDate(inst));
		}
	},

	/* Retrieve the date(s) directly. */
	_getDate: function(inst) {
		var startDate = (!inst.currentYear || (inst.input && inst.input.val() == '') ? null :
			this._daylightSavingAdjust(new Date(
			inst.currentYear, inst.currentMonth, inst.currentDay)));
			return startDate;
	},

	/* Generate the HTML for the current state of the date picker. */
	_generateHTML: function(inst) {
		var today = new Date();
		today = this._daylightSavingAdjust(
			new Date(today.getFullYear(), today.getMonth(), today.getDate())); // clear time
		var isRTL = this._get(inst, 'isRTL');
		var showButtonPanel = this._get(inst, 'showButtonPanel');
		var hideIfNoPrevNext = this._get(inst, 'hideIfNoPrevNext');
		var navigationAsDateFormat = this._get(inst, 'navigationAsDateFormat');
		var numMonths = this._getNumberOfMonths(inst);
		var showCurrentAtPos = this._get(inst, 'showCurrentAtPos');
		var stepMonths = this._get(inst, 'stepMonths');
		var stepBigMonths = this._get(inst, 'stepBigMonths');
		var isMultiMonth = (numMonths[0] != 1 || numMonths[1] != 1);
		var currentDate = this._daylightSavingAdjust((!inst.currentDay ? new Date(9999, 9, 9) :
			new Date(inst.currentYear, inst.currentMonth, inst.currentDay)));
		var minDate = this._getMinMaxDate(inst, 'min', true);
		var maxDate = this._getMinMaxDate(inst, 'max');
		var drawMonth = inst.drawMonth - showCurrentAtPos;
		var drawYear = inst.drawYear;
		if (drawMonth < 0) {
			drawMonth += 12;
			drawYear--;
		}
		if (maxDate) {
			var maxDraw = this._daylightSavingAdjust(new Date(maxDate.getFullYear(),
				maxDate.getMonth() - numMonths[1] + 1, maxDate.getDate()));
			maxDraw = (minDate && maxDraw < minDate ? minDate : maxDraw);
			while (this._daylightSavingAdjust(new Date(drawYear, drawMonth, 1)) > maxDraw) {
				drawMonth--;
				if (drawMonth < 0) {
					drawMonth = 11;
					drawYear--;
				}
			}
		}
		inst.drawMonth = drawMonth;
		inst.drawYear = drawYear;
		var prevText = this._get(inst, 'prevText');
		prevText = (!navigationAsDateFormat ? prevText : this.formatDate(prevText,
			this._daylightSavingAdjust(new Date(drawYear, drawMonth - stepMonths, 1)),
			this._getFormatConfig(inst)));
		var prev = (this._canAdjustMonth(inst, -1, drawYear, drawMonth) ?
			'<a class="ui-datepicker-prev ui-corner-all" onclick="DP_jQuery.datepicker._adjustDate(\'#' + inst.id + '\', -' + stepMonths + ', \'M\');"' +
			' title="' + prevText + '"><span class="ui-icon ui-icon-circle-triangle-' + ( isRTL ? 'e' : 'w') + '">' + prevText + '</span></a>' :
			(hideIfNoPrevNext ? '' : '<a class="ui-datepicker-prev ui-corner-all ui-state-disabled" title="'+ prevText +'"><span class="ui-icon ui-icon-circle-triangle-' + ( isRTL ? 'e' : 'w') + '">' + prevText + '</span></a>'));
		var nextText = this._get(inst, 'nextText');
		nextText = (!navigationAsDateFormat ? nextText : this.formatDate(nextText,
			this._daylightSavingAdjust(new Date(drawYear, drawMonth + stepMonths, 1)),
			this._getFormatConfig(inst)));
		var next = (this._canAdjustMonth(inst, +1, drawYear, drawMonth) ?
			'<a class="ui-datepicker-next ui-corner-all" onclick="DP_jQuery.datepicker._adjustDate(\'#' + inst.id + '\', +' + stepMonths + ', \'M\');"' +
			' title="' + nextText + '"><span class="ui-icon ui-icon-circle-triangle-' + ( isRTL ? 'w' : 'e') + '">' + nextText + '</span></a>' :
			(hideIfNoPrevNext ? '' : '<a class="ui-datepicker-next ui-corner-all ui-state-disabled" title="'+ nextText + '"><span class="ui-icon ui-icon-circle-triangle-' + ( isRTL ? 'w' : 'e') + '">' + nextText + '</span></a>'));
		var currentText = this._get(inst, 'currentText');
		var gotoDate = (this._get(inst, 'gotoCurrent') && inst.currentDay ? currentDate : today);
		currentText = (!navigationAsDateFormat ? currentText :
			this.formatDate(currentText, gotoDate, this._getFormatConfig(inst)));
		var controls = (!inst.inline ? '<button type="button" class="ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all" onclick="DP_jQuery.datepicker._hideDatepicker();">' + this._get(inst, 'closeText') + '</button>' : '');
		var buttonPanel = (showButtonPanel) ? '<div class="ui-datepicker-buttonpane ui-widget-content">' + (isRTL ? controls : '') +
			(this._isInRange(inst, gotoDate) ? '<button type="button" class="ui-datepicker-current ui-state-default ui-priority-secondary ui-corner-all" onclick="DP_jQuery.datepicker._gotoToday(\'#' + inst.id + '\');"' +
			'>' + currentText + '</button>' : '') + (isRTL ? '' : controls) + '</div>' : '';
		var firstDay = parseInt(this._get(inst, 'firstDay'),10);
		firstDay = (isNaN(firstDay) ? 0 : firstDay);
		var dayNames = this._get(inst, 'dayNames');
		var dayNamesShort = this._get(inst, 'dayNamesShort');
		var dayNamesMin = this._get(inst, 'dayNamesMin');
		var monthNames = this._get(inst, 'monthNames');
		var monthNamesShort = this._get(inst, 'monthNamesShort');
		var beforeShowDay = this._get(inst, 'beforeShowDay');
		var showOtherMonths = this._get(inst, 'showOtherMonths');
		var calculateWeek = this._get(inst, 'calculateWeek') || this.iso8601Week;
		var endDate = inst.endDay ? this._daylightSavingAdjust(
			new Date(inst.endYear, inst.endMonth, inst.endDay)) : currentDate;
		var defaultDate = this._getDefaultDate(inst);
		var html = '';
		for (var row = 0; row < numMonths[0]; row++) {
			var group = '';
			for (var col = 0; col < numMonths[1]; col++) {
				var selectedDate = this._daylightSavingAdjust(new Date(drawYear, drawMonth, inst.selectedDay));
				var cornerClass = ' ui-corner-all';
				var calender = '';
				if (isMultiMonth) {
					calender += '<div class="ui-datepicker-group ui-datepicker-group-';
					switch (col) {
						case 0: calender += 'first'; cornerClass = ' ui-corner-' + (isRTL ? 'right' : 'left'); break;
						case numMonths[1]-1: calender += 'last'; cornerClass = ' ui-corner-' + (isRTL ? 'left' : 'right'); break;
						default: calender += 'middle'; cornerClass = ''; break;
					}
					calender += '">';
				}
				calender += '<div class="ui-datepicker-header ui-widget-header ui-helper-clearfix' + cornerClass + '">' +
					(/all|left/.test(cornerClass) && row == 0 ? (isRTL ? next : prev) : '') +
					(/all|right/.test(cornerClass) && row == 0 ? (isRTL ? prev : next) : '') +
					this._generateMonthYearHeader(inst, drawMonth, drawYear, minDate, maxDate,
					selectedDate, row > 0 || col > 0, monthNames, monthNamesShort) + // draw month headers
					'</div><table class="ui-datepicker-calendar"><thead>' +
					'<tr>';
				var thead = '';
				for (var dow = 0; dow < 7; dow++) { // days of the week
					var day = (dow + firstDay) % 7;
					thead += '<th' + ((dow + firstDay + 6) % 7 >= 5 ? ' class="ui-datepicker-week-end"' : '') + '>' +
						'<span title="' + dayNames[day] + '">' + dayNamesMin[day] + '</span></th>';
				}
				calender += thead + '</tr></thead><tbody>';
				var daysInMonth = this._getDaysInMonth(drawYear, drawMonth);
				if (drawYear == inst.selectedYear && drawMonth == inst.selectedMonth)
					inst.selectedDay = Math.min(inst.selectedDay, daysInMonth);
				var leadDays = (this._getFirstDayOfMonth(drawYear, drawMonth) - firstDay + 7) % 7;
				var numRows = (isMultiMonth ? 6 : Math.ceil((leadDays + daysInMonth) / 7)); // calculate the number of rows to generate
				var printDate = this._daylightSavingAdjust(new Date(drawYear, drawMonth, 1 - leadDays));
				for (var dRow = 0; dRow < numRows; dRow++) { // create date picker rows
					calender += '<tr>';
					var tbody = '';
					for (var dow = 0; dow < 7; dow++) { // create date picker days
						var daySettings = (beforeShowDay ?
							beforeShowDay.apply((inst.input ? inst.input[0] : null), [printDate]) : [true, '']);
						var otherMonth = (printDate.getMonth() != drawMonth);
						var unselectable = otherMonth || !daySettings[0] ||
							(minDate && printDate < minDate) || (maxDate && printDate > maxDate);
						tbody += '<td class="' +
							((dow + firstDay + 6) % 7 >= 5 ? ' ui-datepicker-week-end' : '') + // highlight weekends
							(otherMonth ? ' ui-datepicker-other-month' : '') + // highlight days from other months
							((printDate.getTime() == selectedDate.getTime() && drawMonth == inst.selectedMonth && inst._keyEvent) || // user pressed key
							(defaultDate.getTime() == printDate.getTime() && defaultDate.getTime() == selectedDate.getTime()) ?
							// or defaultDate is current printedDate and defaultDate is selectedDate
							' ' + this._dayOverClass : '') + // highlight selected day
							(unselectable ? ' ' + this._unselectableClass + ' ui-state-disabled': '') +  // highlight unselectable days
							(otherMonth && !showOtherMonths ? '' : ' ' + daySettings[1] + // highlight custom dates
							(printDate.getTime() >= currentDate.getTime() && printDate.getTime() <= endDate.getTime() ? // in current range
							' ' + this._currentClass : '') + // highlight selected day
							(printDate.getTime() == today.getTime() ? ' ui-datepicker-today' : '')) + '"' + // highlight today (if different)
							((!otherMonth || showOtherMonths) && daySettings[2] ? ' title="' + daySettings[2] + '"' : '') + // cell title
							(unselectable ? '' : ' onclick="DP_jQuery.datepicker._selectDay(\'#' +
							inst.id + '\',' + drawMonth + ',' + drawYear + ', this);return false;"') + '>' + // actions
							(otherMonth ? (showOtherMonths ? printDate.getDate() : '&#xa0;') : // display for other months
							(unselectable ? '<span class="ui-state-default">' + printDate.getDate() + '</span>' : '<a class="ui-state-default' +
							(printDate.getTime() == today.getTime() ? ' ui-state-highlight' : '') +
							(printDate.getTime() >= currentDate.getTime() && printDate.getTime() <= endDate.getTime() ? // in current range
							' ui-state-active' : '') + // highlight selected day
							'" href="#">' + printDate.getDate() + '</a>')) + '</td>'; // display for this month
						printDate.setDate(printDate.getDate() + 1);
						printDate = this._daylightSavingAdjust(printDate);
					}
					calender += tbody + '</tr>';
				}
				drawMonth++;
				if (drawMonth > 11) {
					drawMonth = 0;
					drawYear++;
				}
				calender += '</tbody></table>' + (isMultiMonth ? '</div>' + 
							((numMonths[0] > 0 && col == numMonths[1]-1) ? '<div class="ui-datepicker-row-break"></div>' : '') : '');
				group += calender;
			}
			html += group;
		}
		html += buttonPanel + ($.browser.msie && parseInt($.browser.version,10) < 7 && !inst.inline ?
			'<iframe src="javascript:false;" class="ui-datepicker-cover" frameborder="0"></iframe>' : '');
		inst._keyEvent = false;
		return html;
	},

	/* Generate the month and year header. */
	_generateMonthYearHeader: function(inst, drawMonth, drawYear, minDate, maxDate,
			selectedDate, secondary, monthNames, monthNamesShort) {
		minDate = (inst.rangeStart && minDate && selectedDate < minDate ? selectedDate : minDate);
		var changeMonth = this._get(inst, 'changeMonth');
		var changeYear = this._get(inst, 'changeYear');
		var showMonthAfterYear = this._get(inst, 'showMonthAfterYear');
		var html = '<div class="ui-datepicker-title">';
		var monthHtml = '';
		// month selection
		if (secondary || !changeMonth)
			monthHtml += '<span class="ui-datepicker-month">' + monthNames[drawMonth] + '</span> ';
		else {
			var inMinYear = (minDate && minDate.getFullYear() == drawYear);
			var inMaxYear = (maxDate && maxDate.getFullYear() == drawYear);
			monthHtml += '<select class="ui-datepicker-month" ' +
				'onchange="DP_jQuery.datepicker._selectMonthYear(\'#' + inst.id + '\', this, \'M\');" ' +
				'onclick="DP_jQuery.datepicker._clickMonthYear(\'#' + inst.id + '\');"' +
			 	'>';
			for (var month = 0; month < 12; month++) {
				if ((!inMinYear || month >= minDate.getMonth()) &&
						(!inMaxYear || month <= maxDate.getMonth()))
					monthHtml += '<option value="' + month + '"' +
						(month == drawMonth ? ' selected="selected"' : '') +
						'>' + monthNamesShort[month] + '</option>';
			}
			monthHtml += '</select>';
		}
		if (!showMonthAfterYear)
			html += monthHtml + ((secondary || changeMonth || changeYear) && (!(changeMonth && changeYear)) ? '&#xa0;' : '');
		// year selection
		if (secondary || !changeYear)
			html += '<span class="ui-datepicker-year">' + drawYear + '</span>';
		else {
			// determine range of years to display
			var years = this._get(inst, 'yearRange').split(':');
			var year = 0;
			var endYear = 0;
			if (years.length != 2) {
				year = drawYear - 10;
				endYear = drawYear + 10;
			} else if (years[0].charAt(0) == '+' || years[0].charAt(0) == '-') {
				year = drawYear + parseInt(years[0], 10);
				endYear = drawYear + parseInt(years[1], 10);
			} else {
				year = parseInt(years[0], 10);
				endYear = parseInt(years[1], 10);
			}
			year = (minDate ? Math.max(year, minDate.getFullYear()) : year);
			endYear = (maxDate ? Math.min(endYear, maxDate.getFullYear()) : endYear);
			html += '<select class="ui-datepicker-year" ' +
				'onchange="DP_jQuery.datepicker._selectMonthYear(\'#' + inst.id + '\', this, \'Y\');" ' +
				'onclick="DP_jQuery.datepicker._clickMonthYear(\'#' + inst.id + '\');"' +
				'>';
			for (; year <= endYear; year++) {
				html += '<option value="' + year + '"' +
					(year == drawYear ? ' selected="selected"' : '') +
					'>' + year + '</option>';
			}
			html += '</select>';
		}
		if (showMonthAfterYear)
			html += (secondary || changeMonth || changeYear ? '&#xa0;' : '') + monthHtml;
		html += '</div>'; // Close datepicker_header
		return html;
	},

	/* Adjust one of the date sub-fields. */
	_adjustInstDate: function(inst, offset, period) {
		var year = inst.drawYear + (period == 'Y' ? offset : 0);
		var month = inst.drawMonth + (period == 'M' ? offset : 0);
		var day = Math.min(inst.selectedDay, this._getDaysInMonth(year, month)) +
			(period == 'D' ? offset : 0);
		var date = this._daylightSavingAdjust(new Date(year, month, day));
		// ensure it is within the bounds set
		var minDate = this._getMinMaxDate(inst, 'min', true);
		var maxDate = this._getMinMaxDate(inst, 'max');
		date = (minDate && date < minDate ? minDate : date);
		date = (maxDate && date > maxDate ? maxDate : date);
		inst.selectedDay = date.getDate();
		inst.drawMonth = inst.selectedMonth = date.getMonth();
		inst.drawYear = inst.selectedYear = date.getFullYear();
		if (period == 'M' || period == 'Y')
			this._notifyChange(inst);
	},

	/* Notify change of month/year. */
	_notifyChange: function(inst) {
		var onChange = this._get(inst, 'onChangeMonthYear');
		if (onChange)
			onChange.apply((inst.input ? inst.input[0] : null),
				[inst.selectedYear, inst.selectedMonth + 1, inst]);
	},

	/* Determine the number of months to show. */
	_getNumberOfMonths: function(inst) {
		var numMonths = this._get(inst, 'numberOfMonths');
		return (numMonths == null ? [1, 1] : (typeof numMonths == 'number' ? [1, numMonths] : numMonths));
	},

	/* Determine the current maximum date - ensure no time components are set - may be overridden for a range. */
	_getMinMaxDate: function(inst, minMax, checkRange) {
		var date = this._determineDate(this._get(inst, minMax + 'Date'), null);
		return (!checkRange || !inst.rangeStart ? date :
			(!date || inst.rangeStart > date ? inst.rangeStart : date));
	},

	/* Find the number of days in a given month. */
	_getDaysInMonth: function(year, month) {
		return 32 - new Date(year, month, 32).getDate();
	},

	/* Find the day of the week of the first of a month. */
	_getFirstDayOfMonth: function(year, month) {
		return new Date(year, month, 1).getDay();
	},

	/* Determines if we should allow a "next/prev" month display change. */
	_canAdjustMonth: function(inst, offset, curYear, curMonth) {
		var numMonths = this._getNumberOfMonths(inst);
		var date = this._daylightSavingAdjust(new Date(
			curYear, curMonth + (offset < 0 ? offset : numMonths[1]), 1));
		if (offset < 0)
			date.setDate(this._getDaysInMonth(date.getFullYear(), date.getMonth()));
		return this._isInRange(inst, date);
	},

	/* Is the given date in the accepted range? */
	_isInRange: function(inst, date) {
		// during range selection, use minimum of selected date and range start
		var newMinDate = (!inst.rangeStart ? null : this._daylightSavingAdjust(
			new Date(inst.selectedYear, inst.selectedMonth, inst.selectedDay)));
		newMinDate = (newMinDate && inst.rangeStart < newMinDate ? inst.rangeStart : newMinDate);
		var minDate = newMinDate || this._getMinMaxDate(inst, 'min');
		var maxDate = this._getMinMaxDate(inst, 'max');
		return ((!minDate || date >= minDate) && (!maxDate || date <= maxDate));
	},

	/* Provide the configuration settings for formatting/parsing. */
	_getFormatConfig: function(inst) {
		var shortYearCutoff = this._get(inst, 'shortYearCutoff');
		shortYearCutoff = (typeof shortYearCutoff != 'string' ? shortYearCutoff :
			new Date().getFullYear() % 100 + parseInt(shortYearCutoff, 10));
		return {shortYearCutoff: shortYearCutoff,
			dayNamesShort: this._get(inst, 'dayNamesShort'), dayNames: this._get(inst, 'dayNames'),
			monthNamesShort: this._get(inst, 'monthNamesShort'), monthNames: this._get(inst, 'monthNames')};
	},

	/* Format the given date for display. */
	_formatDate: function(inst, day, month, year) {
		if (!day) {
			inst.currentDay = inst.selectedDay;
			inst.currentMonth = inst.selectedMonth;
			inst.currentYear = inst.selectedYear;
		}
		var date = (day ? (typeof day == 'object' ? day :
			this._daylightSavingAdjust(new Date(year, month, day))) :
			this._daylightSavingAdjust(new Date(inst.currentYear, inst.currentMonth, inst.currentDay)));
		return this.formatDate(this._get(inst, 'dateFormat'), date, this._getFormatConfig(inst));
	}
});

/* jQuery extend now ignores nulls! */
function extendRemove(target, props) {
	$.extend(target, props);
	for (var name in props)
		if (props[name] == null || props[name] == undefined)
			target[name] = props[name];
	return target;
};

/* Determine whether an object is an array. */
function isArray(a) {
	return (a && (($.browser.safari && typeof a == 'object' && a.length) ||
		(a.constructor && a.constructor.toString().match(/\Array\(\)/))));
};

/* Invoke the datepicker functionality.
   @param  options  string - a command, optionally followed by additional parameters or
                    Object - settings for attaching new datepicker functionality
   @return  jQuery object */
$.fn.datepicker = function(options){

	/* Initialise the date picker. */
	if (!$.datepicker.initialized) {
		$(document).mousedown($.datepicker._checkExternalClick).
			find('body').append($.datepicker.dpDiv);
		$.datepicker.initialized = true;
	}

	var otherArgs = Array.prototype.slice.call(arguments, 1);
	if (typeof options == 'string' && (options == 'isDisabled' || options == 'getDate'))
		return $.datepicker['_' + options + 'Datepicker'].
			apply($.datepicker, [this[0]].concat(otherArgs));
	return this.each(function() {
		typeof options == 'string' ?
			$.datepicker['_' + options + 'Datepicker'].
				apply($.datepicker, [this].concat(otherArgs)) :
			$.datepicker._attachDatepicker(this, options);
	});
};

$.datepicker = new Datepicker(); // singleton instance
$.datepicker.initialized = false;
$.datepicker.uuid = new Date().getTime();
$.datepicker.version = "1.7";

// Workaround for #4055
// Add another global to avoid noConflict issues with inline event handlers
window.DP_jQuery = $;

})(jQuery);
/*
 * jQuery UI Dialog 1.7
 *
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://docs.jquery.com/UI/Dialog
 *
 * Depends:
 *	ui.core.js
 *	ui.draggable.js
 *	ui.resizable.js
 */
(function($) {

var setDataSwitch = {
		dragStart: "start.draggable",
		drag: "drag.draggable",
		dragStop: "stop.draggable",
		maxHeight: "maxHeight.resizable",
		minHeight: "minHeight.resizable",
		maxWidth: "maxWidth.resizable",
		minWidth: "minWidth.resizable",
		resizeStart: "start.resizable",
		resize: "drag.resizable",
		resizeStop: "stop.resizable"
	},
	
	uiDialogClasses =
		'ui-dialog ' +
		'ui-widget ' +
		'ui-widget-content ' +
		'ui-corner-all ';

$.widget("ui.dialog", {

	_init: function() {
		this.originalTitle = this.element.attr('title');

		var self = this,
			options = this.options,

			title = options.title || this.originalTitle || '&nbsp;',
			titleId = $.ui.dialog.getTitleId(this.element),

			uiDialog = (this.uiDialog = $('<div/>'))
				.appendTo(document.body)
				.hide()
				.addClass(uiDialogClasses + options.dialogClass)
				.css({
					position: 'absolute',
					overflow: 'hidden',
					zIndex: options.zIndex
				})
				// setting tabIndex makes the div focusable
				// setting outline to 0 prevents a border on focus in Mozilla
				.attr('tabIndex', -1).css('outline', 0).keydown(function(event) {
					(options.closeOnEscape && event.keyCode
						&& event.keyCode == $.ui.keyCode.ESCAPE && self.close(event));
				})
				.attr({
					role: 'dialog',
					'aria-labelledby': titleId
				})
				.mousedown(function(event) {
					self.moveToTop(false, event);
				}),

			uiDialogContent = this.element
				.show()
				.removeAttr('title')
				.addClass(
					'ui-dialog-content ' +
					'ui-widget-content')
				.appendTo(uiDialog),

			uiDialogTitlebar = (this.uiDialogTitlebar = $('<div></div>'))
				.addClass(
					'ui-dialog-titlebar ' +
					'ui-widget-header ' +
					'ui-corner-all ' +
					'ui-helper-clearfix'
				)
				.prependTo(uiDialog),

			uiDialogTitlebarClose = $('<a href="#"/>')
				.addClass(
					'ui-dialog-titlebar-close ' +
					'ui-corner-all'
				)
				.attr('role', 'button')
				.hover(
					function() {
						uiDialogTitlebarClose.addClass('ui-state-hover');
					},
					function() {
						uiDialogTitlebarClose.removeClass('ui-state-hover');
					}
				)
				.focus(function() {
					uiDialogTitlebarClose.addClass('ui-state-focus');
				})
				.blur(function() {
					uiDialogTitlebarClose.removeClass('ui-state-focus');
				})
				.mousedown(function(ev) {
					ev.stopPropagation();
				})
				.click(function(event) {
					self.close(event);
					return false;
				})
				.appendTo(uiDialogTitlebar),

			uiDialogTitlebarCloseText = (this.uiDialogTitlebarCloseText = $('<span/>'))
				.addClass(
					'ui-icon ' +
					'ui-icon-closethick'
				)
				.text(options.closeText)
				.appendTo(uiDialogTitlebarClose),

			uiDialogTitle = $('<span/>')
				.addClass('ui-dialog-title')
				.attr('id', titleId)
				.html(title)
				.prependTo(uiDialogTitlebar);

		uiDialogTitlebar.find("*").add(uiDialogTitlebar).disableSelection();

		(options.draggable && $.fn.draggable && this._makeDraggable());
		(options.resizable && $.fn.resizable && this._makeResizable());

		this._createButtons(options.buttons);
		this._isOpen = false;

		(options.bgiframe && $.fn.bgiframe && uiDialog.bgiframe());
		(options.autoOpen && this.open());
		
	},

	destroy: function() {
		(this.overlay && this.overlay.destroy());
		this.uiDialog.hide();
		this.element
			.unbind('.dialog')
			.removeData('dialog')
			.removeClass('ui-dialog-content ui-widget-content')
			.hide().appendTo('body');
		this.uiDialog.remove();

		(this.originalTitle && this.element.attr('title', this.originalTitle));
	},

	close: function(event) {
		var self = this;
		
		if (false === self._trigger('beforeclose', event)) {
			return;
		}

		(self.overlay && self.overlay.destroy());
		self.uiDialog.unbind('keypress.ui-dialog');

		(self.options.hide
			? self.uiDialog.hide(self.options.hide, function() {
				self._trigger('close', event);
			})
			: self.uiDialog.hide() && self._trigger('close', event));

		$.ui.dialog.overlay.resize();

		self._isOpen = false;
	},

	isOpen: function() {
		return this._isOpen;
	},

	// the force parameter allows us to move modal dialogs to their correct
	// position on open
	moveToTop: function(force, event) {

		if ((this.options.modal && !force)
			|| (!this.options.stack && !this.options.modal)) {
			return this._trigger('focus', event);
		}
		
		if (this.options.zIndex > $.ui.dialog.maxZ) {
			$.ui.dialog.maxZ = this.options.zIndex;
		}
		(this.overlay && this.overlay.$el.css('z-index', $.ui.dialog.overlay.maxZ = ++$.ui.dialog.maxZ));

		//Save and then restore scroll since Opera 9.5+ resets when parent z-Index is changed.
		//  http://ui.jquery.com/bugs/ticket/3193
		var saveScroll = { scrollTop: this.element.attr('scrollTop'), scrollLeft: this.element.attr('scrollLeft') };
		this.uiDialog.css('z-index', ++$.ui.dialog.maxZ);
		this.element.attr(saveScroll);
		this._trigger('focus', event);
	},

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

		// set focus to the first tabbable element in the content area or the first button
		// if there are no tabbable elements, set focus on the dialog itself
		$([])
			.add(uiDialog.find('.ui-dialog-content :tabbable:first'))
			.add(uiDialog.find('.ui-dialog-buttonpane :tabbable:first'))
			.add(uiDialog)
			.filter(':first')
			.focus();

		this._trigger('open');
		this._isOpen = true;
	},

	_createButtons: function(buttons) {
		var self = this,
			hasButtons = false,
			uiDialogButtonPane = $('<div></div>')
				.addClass(
					'ui-dialog-buttonpane ' +
					'ui-widget-content ' +
					'ui-helper-clearfix'
				);

		// if we already have a button pane, remove it
		this.uiDialog.find('.ui-dialog-buttonpane').remove();

		(typeof buttons == 'object' && buttons !== null &&
			$.each(buttons, function() { return !(hasButtons = true); }));
		if (hasButtons) {
			$.each(buttons, function(name, fn) {
				$('<button type="button"></button>')
					.addClass(
						'ui-state-default ' +
						'ui-corner-all'
					)
					.text(name)
					.click(function() { fn.apply(self.element[0], arguments); })
					.hover(
						function() {
							$(this).addClass('ui-state-hover');
						},
						function() {
							$(this).removeClass('ui-state-hover');
						}
					)
					.focus(function() {
						$(this).addClass('ui-state-focus');
					})
					.blur(function() {
						$(this).removeClass('ui-state-focus');
					})
					.appendTo(uiDialogButtonPane);
			});
			uiDialogButtonPane.appendTo(this.uiDialog);
		}
	},

	_makeDraggable: function() {
		var self = this,
			options = this.options,
			heightBeforeDrag;

		this.uiDialog.draggable({
			cancel: '.ui-dialog-content',
			handle: '.ui-dialog-titlebar',
			containment: 'document',
			start: function() {
				heightBeforeDrag = options.height;
				$(this).height($(this).height()).addClass("ui-dialog-dragging");
				(options.dragStart && options.dragStart.apply(self.element[0], arguments));
			},
			drag: function() {
				(options.drag && options.drag.apply(self.element[0], arguments));
			},
			stop: function() {
				$(this).removeClass("ui-dialog-dragging").height(heightBeforeDrag);
				(options.dragStop && options.dragStop.apply(self.element[0], arguments));
				$.ui.dialog.overlay.resize();
			}
		});
	},

	_makeResizable: function(handles) {
		handles = (handles === undefined ? this.options.resizable : handles);
		var self = this,
			options = this.options,
			resizeHandles = typeof handles == 'string'
				? handles
				: 'n,e,s,w,se,sw,ne,nw';

		this.uiDialog.resizable({
			cancel: '.ui-dialog-content',
			alsoResize: this.element,
			maxWidth: options.maxWidth,
			maxHeight: options.maxHeight,
			minWidth: options.minWidth,
			minHeight: options.minHeight,
			start: function() {
				$(this).addClass("ui-dialog-resizing");
				(options.resizeStart && options.resizeStart.apply(self.element[0], arguments));
			},
			resize: function() {
				(options.resize && options.resize.apply(self.element[0], arguments));
			},
			handles: resizeHandles,
			stop: function() {
				$(this).removeClass("ui-dialog-resizing");
				options.height = $(this).height();
				options.width = $(this).width();
				(options.resizeStop && options.resizeStop.apply(self.element[0], arguments));
				$.ui.dialog.overlay.resize();
			}
		})
		.find('.ui-resizable-se').addClass('ui-icon ui-icon-grip-diagonal-se');
	},

	_position: function(pos) {
		var wnd = $(window), doc = $(document),
			pTop = doc.scrollTop(), pLeft = doc.scrollLeft(),
			minTop = pTop;

		if ($.inArray(pos, ['center','top','right','bottom','left']) >= 0) {
			pos = [
				pos == 'right' || pos == 'left' ? pos : 'center',
				pos == 'top' || pos == 'bottom' ? pos : 'middle'
			];
		}
		if (pos.constructor != Array) {
			pos = ['center', 'middle'];
		}
		if (pos[0].constructor == Number) {
			pLeft += pos[0];
		} else {
			switch (pos[0]) {
				case 'left':
					pLeft += 0;
					break;
				case 'right':
					pLeft += wnd.width() - this.uiDialog.outerWidth();
					break;
				default:
				case 'center':
					pLeft += (wnd.width() - this.uiDialog.outerWidth()) / 2;
			}
		}
		if (pos[1].constructor == Number) {
			pTop += pos[1];
		} else {
			switch (pos[1]) {
				case 'top':
					pTop += 0;
					break;
				case 'bottom':
					pTop += wnd.height() - this.uiDialog.outerHeight();
					break;
				default:
				case 'middle':
					pTop += (wnd.height() - this.uiDialog.outerHeight()) / 2;
			}
		}

		// prevent the dialog from being too high (make sure the titlebar
		// is accessible)
		pTop = Math.max(pTop, minTop);
		this.uiDialog.css({top: pTop, left: pLeft});
	},

	_setData: function(key, value){
		(setDataSwitch[key] && this.uiDialog.data(setDataSwitch[key], value));
		switch (key) {
			case "buttons":
				this._createButtons(value);
				break;
			case "closeText":
				this.uiDialogTitlebarCloseText.text(value);
				break;
			case "dialogClass":
				this.uiDialog
					.removeClass(this.options.dialogClass)
					.addClass(uiDialogClasses + value);
				break;
			case "draggable":
				(value
					? this._makeDraggable()
					: this.uiDialog.draggable('destroy'));
				break;
			case "height":
				this.uiDialog.height(value);
				break;
			case "position":
				this._position(value);
				break;
			case "resizable":
				var uiDialog = this.uiDialog,
					isResizable = this.uiDialog.is(':data(resizable)');

				// currently resizable, becoming non-resizable
				(isResizable && !value && uiDialog.resizable('destroy'));

				// currently resizable, changing handles
				(isResizable && typeof value == 'string' &&
					uiDialog.resizable('option', 'handles', value));

				// currently non-resizable, becoming resizable
				(isResizable || this._makeResizable(value));
				break;
			case "title":
				$(".ui-dialog-title", this.uiDialogTitlebar).html(value || '&nbsp;');
				break;
			case "width":
				this.uiDialog.width(value);
				break;
		}

		$.widget.prototype._setData.apply(this, arguments);
	},

	_size: function() {
		/* If the user has resized the dialog, the .ui-dialog and .ui-dialog-content
		 * divs will both have width and height set, so we need to reset them
		 */
		var options = this.options;

		// reset content sizing
		this.element.css({
			height: 0,
			minHeight: 0,
			width: 'auto'
		});

		// reset wrapper sizing
		// determine the height of all the non-content elements
		var nonContentHeight = this.uiDialog.css({
				height: 'auto',
				width: options.width
			})
			.height();

		this.element
			.css({
				minHeight: Math.max(options.minHeight - nonContentHeight, 0),
				height: options.height == 'auto'
					? 'auto'
					: Math.max(options.height - nonContentHeight, 0)
			});
	}
});

$.extend($.ui.dialog, {
	version: "1.7",
	defaults: {
		autoOpen: true,
		bgiframe: false,
		buttons: {},
		closeOnEscape: true,
		closeText: 'close',
		dialogClass: '',
		draggable: true,
		hide: null,
		height: 'auto',
		maxHeight: false,
		maxWidth: false,
		minHeight: 150,
		minWidth: 150,
		modal: false,
		position: 'center',
		resizable: true,
		show: null,
		stack: true,
		title: '',
		width: 300,
		zIndex: 1000
	},

	getter: 'isOpen',

	uuid: 0,
	maxZ: 0,

	getTitleId: function($el) {
		return 'ui-dialog-title-' + ($el.attr('id') || ++this.uuid);
	},

	overlay: function(dialog) {
		this.$el = $.ui.dialog.overlay.create(dialog);
	}
});

$.extend($.ui.dialog.overlay, {
	instances: [],
	maxZ: 0,
	events: $.map('focus,mousedown,mouseup,keydown,keypress,click'.split(','),
		function(event) { return event + '.dialog-overlay'; }).join(' '),
	create: function(dialog) {
		if (this.instances.length === 0) {
			// prevent use of anchors and inputs
			// we use a setTimeout in case the overlay is created from an
			// event that we're going to be cancelling (see #2804)
			setTimeout(function() {
				$(document).bind($.ui.dialog.overlay.events, function(event) {
					var dialogZ = $(event.target).parents('.ui-dialog').css('zIndex') || 0;
					return (dialogZ > $.ui.dialog.overlay.maxZ);
				});
			}, 1);

			// allow closing by pressing the escape key
			$(document).bind('keydown.dialog-overlay', function(event) {
				(dialog.options.closeOnEscape && event.keyCode
						&& event.keyCode == $.ui.keyCode.ESCAPE && dialog.close(event));
			});

			// handle window resize
			$(window).bind('resize.dialog-overlay', $.ui.dialog.overlay.resize);
		}

		var $el = $('<div></div>').appendTo(document.body)
			.addClass('ui-widget-overlay').css({
				width: this.width(),
				height: this.height()
			});

		(dialog.options.bgiframe && $.fn.bgiframe && $el.bgiframe());

		this.instances.push($el);
		return $el;
	},

	destroy: function($el) {
		this.instances.splice($.inArray(this.instances, $el), 1);

		if (this.instances.length === 0) {
			$([document, window]).unbind('.dialog-overlay');
		}

		$el.remove();
	},

	height: function() {
		// handle IE 6
		if ($.browser.msie && $.browser.version < 7) {
			var scrollHeight = Math.max(
				document.documentElement.scrollHeight,
				document.body.scrollHeight
			);
			var offsetHeight = Math.max(
				document.documentElement.offsetHeight,
				document.body.offsetHeight
			);

			if (scrollHeight < offsetHeight) {
				return $(window).height() + 'px';
			} else {
				return scrollHeight + 'px';
			}
		// handle "good" browsers
		} else {
			return $(document).height() + 'px';
		}
	},

	width: function() {
		// handle IE 6
		if ($.browser.msie && $.browser.version < 7) {
			var scrollWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body.scrollWidth
			);
			var offsetWidth = Math.max(
				document.documentElement.offsetWidth,
				document.body.offsetWidth
			);

			if (scrollWidth < offsetWidth) {
				return $(window).width() + 'px';
			} else {
				return scrollWidth + 'px';
			}
		// handle "good" browsers
		} else {
			return $(document).width() + 'px';
		}
	},

	resize: function() {
		/* If the dialog is draggable and the user drags it past the
		 * right edge of the window, the document becomes wider so we
		 * need to stretch the overlay. If the user then drags the
		 * dialog back to the left, the document will become narrower,
		 * so we need to shrink the overlay to the appropriate size.
		 * This is handled by shrinking the overlay before setting it
		 * to the full document size.
		 */
		var $overlays = $([]);
		$.each($.ui.dialog.overlay.instances, function() {
			$overlays = $overlays.add(this);
		});

		$overlays.css({
			width: 0,
			height: 0
		}).css({
			width: $.ui.dialog.overlay.width(),
			height: $.ui.dialog.overlay.height()
		});
	}
});

$.extend($.ui.dialog.overlay.prototype, {
	destroy: function() {
		$.ui.dialog.overlay.destroy(this.$el);
	}
});

})(jQuery);
 // $Id$
 //

new (function() {                  // BEGIN CLOSURE Karl

var Karl = window.Karl = {};
var t = this;

// Some defaults and constants
Karl.NAME = "Karl";
Karl.VERSION = "3.00";

var createLiveForms = function createLiveForms() {
    $('.mceEditor').each(function () {
        var el = this;
        for(var node=this; node.parentNode; node = node.parentNode) {
            if(node.tagName.toLowerCase() == 'form') {
                node.onsubmit = function (e) {
                    tinyMCE.triggerSave();
                    ////var editor = tinyMCE.get(el.id)
                    ////el.value = editor.getContent();
                };
                break;
            }
        }
    });
};


/**
 * Load TinyMCE
 */
var loadTinyMCE = function loadTinyMCE() {
    // Instead of relying on exception handling, simply check
    // if tiny is available. This allows catching the real exceptions
    // during init.
    var _has_tinyMCE = true;
    try {
        tinyMCE;
    } catch (e) {
        _has_tinyMCE = false;
    }
    if (_has_tinyMCE && tinyMCE.init) {
        // Say "no thanks" to the scriptloader of tiny.
        // Reason: it works excellent, but for both development and production
        // modes, we end up better if we include our resources ourselves.
        // We do this by marking the resources as loaded already.
        // Thist must be in sync with what actually gets loaded in the page.
        var pref = tinymce.baseURL + '/';
        var mark = function mark(path) {
            // Mark resource as loaded for both .js and _src.js
            // Path should not contain the .js ending.
            tinymce.ScriptLoader.markDone(pref + path + '.js');
            tinymce.ScriptLoader.markDone(pref + path + '_src.js');
        };
        mark('langs/en');
        mark('themes/advanced/editor_template');
        mark('plugins/paste/editor_plugin');
        mark('plugins/wicked/editor_plugin');
        mark('plugins/wicked/langs/en');
        mark('plugins/embedmedia/editor_plugin');
        // See if the wiki plugin needs to be enabled.
        var widget_data = window.karl_client_data && karl_client_data.text || {};
        var plugins = 'paste,embedmedia';
        if (widget_data.enable_wiki_plugin) {
            plugins += ',wicked';
        }
        // Do the init.
        tinyMCE.init({
            theme: 'advanced',
            skin: 'karl',
            mode: 'specific_textareas',
            editor_selector : 'mceEditor',
            height: '400',
            width: '550',
            convert_urls : false,
            gecko_spellcheck : true,
            submit_patch: false,
            entity_encoding: "numeric",
            add_form_submit_trigger: false,
            add_unload_trigger: false,
            strict_loading_mode: true,
            paste_create_paragraphs : false,
            paste_create_linebreaks : false,
            paste_use_dialog : false,
            paste_auto_cleanup_on_paste : true,
            paste_convert_middot_lists : true,
            paste_unindented_list_class : "unindentedList",
            paste_convert_headers_to_strong : true,
            theme_advanced_toolbar_location: 'top',
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, image, embedmedia, addwickedlink, delwickedlink',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: plugins,
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            relative_urls : false,
            forced_root_block : 'p'
        });  
    } else {
        // XXX raise an error here?
    }
};

// Load TinyMCE
loadTinyMCE();


/**
 * Navigation menus
 *
 * Required for IE only
 * fakes :hover handling
 * see http://www.htmldog.com/articles/suckerfish/dropdowns/ for explanation
 *
 * The following is a port of the Karl2 navmenus.
 */
var enableOldStyleDropdowns = function () {
    if (jQuery.browser.msie) {
        $('#left li.submenu').each(function() {
            $(this).mouseover(function() {
                $(this).addClass('iehover');
            });
            $(this).mouseout(function() {
                $(this).removeClass('iehover');
            });
        });
    }
};


// Custom jquery extensions

$.widget('ui.karlstatusbox', {
    
    _init: function() {
        // initialize the queue
        this.queue = [];
    },

    /*
     * Public methods
     **/

    /* Clear all messages, or all messages with a given queueCategory */
    clear: function(/*optional*/ queueCategory) {
        if (queueCategory === undefined) {
            // shortcut: clear all items
            this.element.empty();
            this.queue = [];
        } else {
            // Clear items of the given category
            var newQueue = [];
            $(this.queue).each(function() {
                // The element may have been deleted (by closebutton),
                // but we don't check for this, since remove() works
                // safe with elements already removed.
                if (this.queueCategory == queueCategory) {
                    this.item.remove();
                } else {
                    // keep item in queue
                    newQueue.push(this);
                }
            });
            this.queue = newQueue;
        }
    },

    /* Append a message */
    append: function(message, /*optional*/ queueCategory) {
        // default queue category is null.
        if (queueCategory === undefined) {
            queueCategory = null;
        }
        // Append the item
        var item = $('<div class="' + this.options.clsItem + '"></div>');
        item.append($('<div class="message"></div>').append(message));
        if (this.options.hasCloseButton) {
            item.append($('<a href="#" class="statusbox-closebutton">X</a>')
                        .click(function(e) {
                            item.remove();    
                            e.preventDefault();
                        })
            );
        }
        // clearing floats
        if (jQuery.browser.msie) {
            item.addClass('clear-ie-container');
        } else {
            item.append('<div class="clear"></div>');
        }
        this.element.append(item);
        // Remember it on the queue
        this.queue.push({
            item: item,
            queueCategory: queueCategory
        });
    },

    /* Append a message after clearing previous messages.
     * If queueCategory is specified, only the messages added with the
     * same category are cleared. */
    clearAndAppend: function(message, /*optional*/ queueCategory) {
        this.clear(queueCategory);
        this.append(message, queueCategory);
    }


    /*
     * Private methods
     **/


});

$.extend($.ui.karlstatusbox, {
    defaults: {
        clsItem: 'statusbox-item',
        hasCloseButton: true
    }
});


$.widget('ui.karllivesearch', $.extend({}, $.ui.autobox3.prototype, {

    activate: function() {
        if (this.active && this.active[0] && $.data(this.active[0], "originalObject")) {
            var href = $.data(this.active[0], "originalObject").href;
            window.location = href;
        } else {
            // submit the form
            document.forms['ff'].submit();
        }
    },

    _setupWidget: function() {
        var self = this;
        this.input = this._bindInput(this.element);

        // to be sure there is no FF-autocomplete
        this.input.attr('autocomplete', 'off');

        // If a click bubbles all the way up to the window, close the autobox
        // (Note, bind to document and not to windows.
        // If windows is used, event does not bubble up on IE.
        $(document).bind("click.autobox", function(){
            self.cancel();
        });

    },
    
    _getBoxOnEnter: function(){
        // When enter is pressed, always submit the form.
        // This is needed when autobox is inactive.
        document.forms['ff'].submit();
        // Prevent add from happening.
    },
 
    _handleActive: function() {
        // Don't copy the value to the input,
        // like superclass does.
    }
                    
}));

$.extend($.ui.karllivesearch, {
    defaults: $.extend({}, $.ui.autobox3.defaults, {
        selectHoverable: '.result .item, .showall .item',
        // start search from 3rd input character only
        minQueryLength: 3
    })
});


Karl.makeSnippets = function(snippetmap) {
    // compile templates
    var compiled_map = {};
    for (var snippet in snippetmap) {
        compiled_map[snippet] = $.makeTemplate(snippetmap[snippet], "<%", "%>");
    }
    return function(record) {
        var snippet = record.snippet || '';
        var template = compiled_map[snippet];
        return template(record);
    };
};

var wid = 0;

Karl.getJSON = function getJSON(url, data, callback, error) {
    return jQuery.ajax({
            type: "POST",
            url: url,
            data: data,
            success: callback,
            error: error,
            dataType: 'json'
    });
};

$.widget('ui.karltagbox', $.extend({}, $.ui.autobox3.prototype, {

    _addBox: function (record, /*optional*/ initializing) {
        var self = this;
        // Update bubble if we already have it
        var cachekey = record.id || record.tag;
        var cached = this.bubbles[cachekey];
        if (cached) {
            // Is this my tag already?
            var cachedrecord = cached.record;
            if (cachedrecord.snippet != 'nondeleteable') {
                // Don't worry then. We have this tag,
                // just ignore the event.
                return;
            }
            // Change the snippet, increase the counter,
            // and update the widget.
            cachedrecord.snippet = '';
            cachedrecord.count++;
            this._updateBox(cached);
        } else {
            // Add the bubble.
            // tagusers_url depends on if we have the data available
            var tagusers_url;
            if (this.options.docid) {
                tagusers_url = this.options.tagusers_url +
                        '?tag=' + record.tag +
                        '&docid=' + this.options.docid;
            } else {
                // if there is no docid (for example a page being added)
                // just don't make the link clickable.
                tagusers_url = 'javascript://return false;';
            }
            // add extra info to the records
            record = $.extend({
                    // default values for when we add the tag from code
                    count: 1,
                    tagusers_url: tagusers_url
                },
                record,
                {
                    _name: this.options.name || 'box',
                    _wid: 'bit-' + wid,
                    showtag_url: this.options.showtag_url + (record.id || record.tag)
                });
            wid++;
            // render the bubble
            var rendered = this._renderBox(record);

            // Validate the tag on client side.
            // If this fails the add will not happen.
            if (! initializing) {
                var error = this._validateTag(record.tag);
                if (error) {
                    // Report the error.
                    this._appendStatusWithBubble(
                        'Adding tag failed: ' + error,
                        rendered);
                    rendered.remove();
                    // Finish here.
                    return;
                }
            }

            // cache the record internally
            this.bubbles[cachekey] = cached = {record:record, li:rendered[0]};
        }
        // Ajax save is skipped in the boxes that are added initially.
        if (! initializing && this.options.ajaxAdd) {
            Karl.getJSON(this.options.ajaxAdd, "val=" + record.tag,
                function(json) {self._ajaxAddSuccess(cached, json);},
                function(json) {self._ajaxAddFailure(cached, json);}
                );
        }
    },

    _validateTag: function(tag) {
        if (this.options.validateRegexp) {
            if (tag.match(this.options.validateRegexp) == null) {
                return 'Value contains characters that are not allowed in a tag.';
            }
        }
        // No error.
        return;
    },

    _ajaxAddSuccess: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (error) {
            this._ajaxAddFailure(cached, json);
        }
    },
    
    _ajaxAddFailure: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (! error) {
            error = 'Server error when adding tag';
        }
        // Report the error
        this._appendStatusWithBubble(error, cached.li);
        // Remove bubble
        this._delBox(cached.li, true);
    },

    _renderBox: function (record) {
        var self = this;
        // render the snippet
        var rendered = this.options.snippets(record);
        rendered = this.holder.find('.autobox-input').before(rendered).prev();
        this.input.val('');
        // Bind the close button
        $('.closebutton', rendered).bind('click', function(e) {
                  self._delBox(rendered);
                  e.preventDefault();
              });
        return rendered;
    },

    _delBox: function(li, /*optional*/ initializing) {
        var self = this;
        // Update bubble if counter > 1
        var tagkey = li.find('input')[0].value;
        var cached = this.bubbles[tagkey];

        if (cached && cached.record.count > 1) {
            // This is also a global tag.
            var cachedrecord = cached.record;
            // Change the snippet, increase the counter,
            // and update the widget.
            cachedrecord.snippet = 'nondeleteable';
            cachedrecord.count--;
            this._updateBox(cached);
        } else {
            // Else proceed with deletion 
            $.ui.autobox3.prototype._delBox.call(this, li);
            // And delete it from the cache too
            delete this.bubbles[tagkey];
        }
        // Do the ajax in any case
        if (! initializing && this.options.ajaxDel) {
            Karl.getJSON(this.options.ajaxDel, "val=" + tagkey,
                function(json) {self._ajaxDelSuccess(cached, json);},
                function(json) {self._ajaxDelFailure(cached, json);}
                );
        }
    },

    _ajaxDelSuccess: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (error) {
            this._ajaxDelFailure(cached, json);
        }
    },
 
    _ajaxDelFailure: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (! error) {
            error = 'Server error when deleting tag';
        }
        // Report the error
        this._appendStatusWithBubble(error, cached.li);
        // add back the bubble
        this._addBox(cached.record, true);
    },


    _updateBox: function(cached) {
        // render the bubble
        var rendered = this._renderBox(cached.record);
        // and replace the original li with it
        $(cached.li).after(rendered).remove();
        cached.li = rendered;
    },
    
    _createHolder: function (element) {
        var holder = $.ui.autobox3.prototype._createHolder.call(this, element);
        // Add a div around it and place the original widget and a status box
        // into this wrapper div
        var newholder = holder.wrap('<div class="statusbox-wrapper"></div>').parent()
            .append(
                $('<div class="statusbox"></div>')
                    .karlstatusbox()
                )
        this.statusbox = $("*:last", newholder);
        return newholder;
    },

    _clearStatus: function() {
        this.statusbox.karlstatusbox('clear');
    },

    _appendStatus: function(message) {
        this.statusbox.karlstatusbox('append', message);
    },

    _appendStatusWithBubble: function(message, bubble) {
        // clone the bubble and remove the input from it
        // to avoid collision in case it gets submitted in form
        bubble = $(bubble).clone()
        bubble.find('input').remove()
        var fullmessage = $('<span class="message-span"></span><span class="bubble-span"></span>');
        fullmessage.eq(0).text(message);
        fullmessage.eq(1).append(bubble);
        this._appendStatus(fullmessage);
        // bind the bubble's closebutton
        var item = this.statusbox.find('>:last-child');
        $('.closebutton', bubble)
            .bind('click', function(e) {
                item.remove(); 
                e.preventDefault();
            });
    },
 
    _setupWidget: function() {
        // initialize tag cache
        this.bubbles = {};
        $.ui.autobox3.prototype._setupWidget.call(this);
        var self = this;
        // add a button after the input
        // also wrap it to avoid breaking
        this.input.wrap('<span></span>');
        $('<button class="standalone addtag-button" type="button">Add</button>')
            .bind('click', function(e) {
                // We generate the record first...
                // (null result means we need not add it)
                var record = self._getBoxOnEnter();
                if (record) { self._addBox(record); }
                e.preventDefault();
            })
            .insertAfter(this.input);


        // populate additional methods from options
        if (this.options.validateTag) this._validateTag = this.options.validateTag;
    },

    _updateList: function(list){
        // store the value
        this.cached_result = list;
        $.ui.autobox3.prototype._updateList.call(this, list);
        if (this.options.selectFirst) {
            // is there at least one selectable in the list?
            if ($("> *", this.container).length > 0) {
                // Select the first element
                this.selected = 0;
                this._select();
            }
        }
    },

    _getCurrentValsHash: function(input) {
        // (XXX ignore "input" really... the parameter seems
        // to serve little or no role here.)
        var hash = {};
        // The hash that we construct will serve to exclude
        // these elements from the new searches.
        for (var tagkey in this.bubbles) {
            var cachedrecord = this.bubbles[tagkey].record;
            if (cachedrecord.snippet != 'nondeleteable') {
                // This value will be exluded from search results.
                // We _always_ use the tag text here.
                hash[cachedrecord.tag] = true;
            }
        }
        return hash;
    }


}));

var _snip_pre =     '<span>' + 
                    '<a class="showtag-link" href="<%= showtag_url %>"><%= tag %></a>' +
                    '<span class="count">&nbsp;(' +
                    '<a class="tagusers-link"  href="<%= tagusers_url %>"><%= count %></a>)</span>';
var _snip_post =    '<input type="hidden" name="<%= _name %>" value="<%= tag %>" />' +
                    '</span>' +
                    '</li>';

$.extend($.ui.karltagbox, {
    defaults: $.extend({}, $.ui.autobox3.defaults, {
        //
        // Livesearch results with better highlighting
        //
        match: function(typed) {
            this.typed = typed;
            this.pre_match = this.text;
            this.match = this.post_match = '';
            if (!this.ajax && !typed || typed.length == 0) { return true; }
            var match_at = this.text.search(new RegExp("\\b" + typed, "i"));
            if (match_at != -1) {
                this.pre_match = this.text.slice(0,match_at);
                this.match = this.text.slice(match_at,match_at + typed.length);
                this.post_match = this.text.slice(match_at + typed.length);
                return true;
            }
            return false;
        },
        insertText: function(obj) {
            return obj.tag;
        },
        templateText: "<li><%= pre_match %><span class='matching' ><%= match %></span><%= post_match %></li>",
        //
        // Snippets for more flexible client side rendering
        //
        snippets: Karl.makeSnippets({
            '': 
                '<li id="<%= _wid %>" class="bit-box">' +
                _snip_pre +
                '<a href="#" class="closebutton"></a>' +
                _snip_post,
            nondeleteable: 
                '<li id="<%= _wid %>" class="bit-box nondeleteable">' +
                _snip_pre + 
                _snip_post
        }),
        // The only items addable are the one from the search result.
        strictAdd: false,
        selectFirst: false,
        validateRegexp: null
    })
});


/*
 * A variant of the tagbox, used for members.
 * It only allows entering the items from the search result set.
 */
$.widget('ui.karlmemberbox', $.extend({}, $.ui.karltagbox.prototype, {
}));

$.extend($.ui.karlmemberbox, {
    defaults: $.extend({}, $.ui.karltagbox.defaults, {
        strictAdd: true,
        selectFirst: true,
        getBoxFromSelection: function() {
            // Is there an active object?
            var record = this.active && this.active[0] && $.data(this.active[0], "originalObject");
            if (! record) {
                // Prevent it from happen.
                return;
            }
            return {
                tag: record.text,
                id: record.id
            };
        },
        getBoxOnEnter: function() {return this._getBoxFromSelection()},
        snippets: Karl.makeSnippets({
            '': 
                '<li id="<%= _wid %>" class="bit-box">'
                + '<span>'
                + '<a class="showtag-link" href="<%= showtag_url %>"><%= tag %></a>'
                + '<a href="#" class="closebutton"></a>'
                + '<input type="hidden" name="<%= _name %>" value="<%= id %>" />'
                + '</span>'
                + '</li>'
        })

    })

});


$.widget('ui.karlgrid', $.extend({}, $.ui.grid.prototype, {

    _generateColumns: function() {

        this.columnsContainer = $('<tr class="ui-grid-columns"><td><div class="ui-grid-columns-constrainer"><table cellpadding="0" cellspacing="0"><tbody><tr class="ui-grid-header ui-grid-inner"></tr></tbody></table></div></td></tr>')
            .appendTo(this.grid).find('table tbody tr');

        $('.ui-grid-columns-constrainer', this.grid).css({
            width: this.options.width,
            overflow: 'hidden'
        });
        
        // columns will have borders collapsed
        $('table', this.grid).css({
            'border-collapse': 'collapse'
        });

        // XXX Do _not_ make it sortable.
        //this.columnsContainer.gridSortable({ instance: this });
        
    },

    _syncColumnWidth: function() {
        var self = this;

        // calculate desired widths
        var column_widths = [];
        var totalWidth = 0;
        $('td', this.columnsContainer).each(function() {
            var width = $(this).outerWidth();
            column_widths.push(width);
            totalWidth += width;
        });
        
        // set width on all cells
        // XXX This would probably work bad with infinite scrolling!
        $('> tr', this.content).each(function() {
            $('> td', this).each(function(i) {
                var elem = $(this);
                var width = column_widths[i];
                // Take offset into consideration
                var offset = elem.outerWidth() - elem.width();
                if (i==0) {
                    // Since we have no bordercollapse in the column part:
                    // increase first field's width with the left border
                    offset -= self.leftBorder; 
                }
                width -= offset;
                // adjust cell width
                elem
                    // overflow is essential for column width
                    .css('overflow', 'hidden')
                    .width(width);
            });

        });

        // set the width of the whole table
        this.content.parent()     // this.content is the <tbody>, parent is the <table>.
            .width(totalWidth)
            //.css('overflow', 'hidden')
            // table-layout is essential for column width
            .css('table-layout', 'fixed');

    },

    _addColumns: function(columns) {

        this.columns = columns;
        //// XXX XXX there is no placeholder column now
        //var totalWidth = 25;
        var totalWidth = 0;
        this.columns_by_id = {};
        
        // Use sort column and direction as set by _onClick handler,
        // allow to provide initial defaults by options.
        var sortColumn = this.sortColumn || this.options.sortColumn;
        var sortDirection = this.sortDirection || this.options.sortDirection;

        for (var i=0; i < columns.length; i++) {
            var column_meta = columns[i];

            var sortDirectionClass = '';
            // Do we have a sorting direction?
            if (sortColumn == column_meta.id) {
                sortDirectionClass = ' ui-icon ' + (sortDirection == 'asc' ? 'ui-icon-carat-1-s' : 'ui-icon-carat-1-n');
            }

            var column = $('<td class="ui-grid-column-header ui-state-default">' +
                           '  <div style="position: relative;">' + // inner div is needed for relativizing position
                           '    <a href="#">' +
                           '      <span class="ui-grid-column-header-text">' + column_meta.label + '</span>' +
                           '    </a>' +
                           '    <span class="ui-grid-visual-sorting-indicator' + sortDirectionClass + '"></span>' +
                           '  </div>' +
                           '</td>')
                .data('grid-column-header', column_meta)
                .appendTo(this.columnsContainer);

            var offset = column.outerWidth() - column.width();
            if (i==0) {
                // the first column gets the left offset
                // subscribed from width as well
                // this is needed to compensate for left column border
                //this.leftBorder = column[0].offsetLeft;
                if (jQuery.browser.msie) {
                    this.leftBorder = 0;
                } else {
                    // FF, Safari
                    // XXX for now we suppose a (table) border of 1
                    this.leftBorder = 1;
                }
                offset += this.leftBorder;
            }
            column.width(column_meta.width - offset);

            totalWidth += column_meta.width;
            
            // XXX Do not make the columns resizable.
            //column.gridResizable();
        };
        
        //This column is the last and only used to serve as placeholder for a non-existant scrollbar
        // XXX XXX temporary disabled, as currently we don't use features it allows,
        // and it causes a layout artifact on FF.
        //$('<td class="ui-grid-column-header ui-state-default"><div></div></td>').width(25).appendTo(this.columnsContainer);
        
        //Update the total width of the wrapper of the column headers
        var header_table = this.columnsContainer.parent().parent();
        header_table.width(totalWidth);

        // Send event that columns are setup
        this.element.trigger('karlgrid_columns_set');

    },

    _handleClick: function(event) {

        var el = $(event.target);

        // Click on column header toggles sorting
        if (el.is('.ui-grid-column-header, .ui-grid-column-header *')) {
            var header = el.hasClass('ui-grid-column-header') ? el : el.parents('.ui-grid-column-header');
            var data = header.data('grid-column-header');
            this.sortDirection = this.sortDirection == 'desc' ? 'asc' : 'desc';
            this.sortColumn = data.id;
            this._update ({columns: false, refresh: true});
        }
        
        // Handle click on pagination buttons
        if (el.is('.ui-grid-pagination a, .ui-grid-pagination a *')) {
            var current= Math.floor((this.offset + this.options.limit - 1) / this.options.limit) + 1;
            if (el.hasClass('ui-icon-circle-arrow-w') || el.find('.ui-icon-circle-arrow-w').length > 0) current --;
            if (el.hasClass('ui-icon-circle-arrow-e') || el.find('.ui-icon-circle-arrow-e').length > 0) current ++;
            if (! isNaN(parseInt(event.target.innerHTML, 10))) current = parseInt(event.target.innerHTML, 10);
            
            this.offset = (current - 1) * this.options.limit;
            this._update();
        }
        
        return false;

    },


    _makeRowsSelectable: function() {
        
        var table = this.content.parent().parent();
        table.bind('mousedown', function(event) {
            var filter = 'tr';
            var item;
            $(event.target).parents().andSelf().each(function() {
                if ($('tr', table).index(this) != -1) item = this;
            });

            if (!item)
                return;

            // follow the link in it
            var links = $('a', item);
            if (links.length > 0) {
                window.location = links[0].href;
            }

            event.preventDefault();
        });
        
    },

    _addRow: function(item, dontAdd) {

        var row = $.ui.grid.prototype._addRow.call(this, item, dontAdd);

        // Calculate the oddity of the newly added row. We do the
        // following check after the row has already been added.
        var oddity = (this.content.find('tr').length % 2 == 1)

        // Add class based on oddity and options
        if (oddity && this.options.oddRowClass) {
            row.addClass(this.options.oddRowClass);
        }

        if (! oddity && this.options.evenRowClass) {
            row.addClass(this.options.evenRowClass);
        }

        return row;

    },

    _generateFooter: function() {
        this.footer = $('<tr class="ui-grid-footer ui-widget-header"><td>'+
        '<span class="ui-grid-footer-text ui-grid-limits"></span>'+
        '</td></tr>').appendTo(this.grid).find('td');
    },

    _generatePagination: function(response) {
        this.pagination = $('<span class="ui-grid-pagination clearafter"></span>').appendTo(this.footer);
        this.footerResultsBox = $('.ui-grid-limits, .ui-grid-no-limits', this.footer);
        this._updatePagination(response);
    },

    /* XXX need to overwrite this for not showing
     * pagination if there are 0 or 1 pages */
    _updatePagination: function(response) {
        
        var pages = Math.floor((response.totalRecords + this.options.limit - 1) / this.options.limit),
            current= Math.floor((this.offset + this.options.limit - 1) / this.options.limit) + 1,
            displayed = [];

        this.pagination.empty();
        
        if (pages <= 1) {
            // Deactivate the Results: box
            // This means that if it does not have the ui-grid-limits
            // class, the updater won't update the Results: infoline on it
            this.footerResultsBox
                .removeClass('ui-grid-limits')
                .addClass('ui-grid-no-limits')
                .html('');
            return;
        }

        // Activate the Results: box
        this.footerResultsBox
            .removeClass('ui-grid-no-limits')
            .addClass('ui-grid-limits');

        for (var i=current-1; i > 0 && i > current-3; i--) {
            this.pagination.prepend('<a href="#" class="ui-state-default">'+i+'</a>');
            displayed.push(i);
        };
        
        for (var i=current; i < pages+1 && i < current+3; i++) {
            this.pagination.append(i==current? '<span class="ui-state-active">'+i+'</span>' :
                    '<a href="#" class="ui-state-default">'+i+'</a>' );
            displayed.push(i);
        };


        if(pages > 1 && $.inArray(2, displayed) == -1) //Show front dots if the '2' is not already displayed and there are more pages than 1
            // XXX XXX
            this.pagination.prepend('<span class="ui-grid-pagination-dots">...</span>');
        
        if($.inArray(1, displayed) == -1) //Show the '1' if it's not already shown
            this.pagination.prepend('<a href="#" class="ui-state-default">1</a>');

        if($.inArray(pages-1, displayed) == -1) //Show the dots between the current elipse and the last if the one before last is not shown
            // XXX XXX
            this.pagination.append('<span class="ui-grid-pagination-dots">...</span>');
        
        if($.inArray(pages, displayed) == -1) //Show the last if it's not already shown
            this.pagination.append('<a href="#" class="ui-state-default">'+pages+'</a>');
            
        this.pagination.prepend(current-1 > 0 ?
                '<a href="#" class="ui-state-default ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-w">Prev</div></a>' :
                '<span class="ui-state-default ui-state-disabled ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-w">Prev</div></span>');
        this.pagination.append(current+1 > pages ?
                '<span href="#" class="ui-state-default ui-state-disabled ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-e">Next</div></span>' :
                '<a href="#" class="ui-state-default ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-e">Next</div></a>');

        this.pagination.find('a.ui-state-default')
            .hover(
                function() {
                    $(this).addClass('ui-state-hover');
                },
                function() {
                    $(this).removeClass('ui-state-hover');
                }
            );

    },

    _extendFetchOptions: function(fetchOptions) {
        return $.extend({}, fetchOptions, {
            limit: this.options.limit,
            start: (! (fetchOptions && fetchOptions.refresh) && this.offset) || 0,
            refresh: (fetchOptions && fetchOptions.refresh) || (fetchOptions && fetchOptions.columns)
        })
    },

    /* XXX need to overwrite this to be able to customize
     * behaviour like displaying Results data.  */
    _update: function(o) {
        var self = this;

        var fetchOptions = $.extend({}, this._extendFetchOptions(fetchOptions), {
        // XXX Is this needed?
        //    fill: null
        });
        
        if (fetchOptions.refresh) {
            fetchOptions.start = this.infiniteScrolling ? 0 : (this.offset || 0);
        }
        //Somehow the keys for these must stay undefined no matter what
        if(this.sortColumn) fetchOptions.sortColumn = this.sortColumn;
        if(this.sortDirection) fetchOptions.sortDirection = this.sortDirection;

        //Do the ajax call
        this.gridmodel.fetch(fetchOptions, function(state) {
            self._doUpdate(state, o);
        });

    },

    _initialUpdate: function() {		
        var initialState = this.options.initialState;
        if (initialState) {
            // Initial state: use it to load content
            // Need to convert each record from a flat list to a keyed dict
	    initialState = $.ui.grid.model.defaults.parse(initialState);
            // load them to the table
            this._doUpdate(initialState, {columns: true});
        } else {
            // Query the content from the server
            this._update({columns: true});
        }
    },

    _doUpdate: function(state, o) {
        var self = this;

        //Generate or update pagination
        if (this.options.pagination && ! this.pagination) {
            this._generatePagination(state);
        } else if (this.options.pagination && this.pagination) {
            this._updatePagination(state);
        }

        var self = this;
        var fetchOptions = this._extendFetchOptions(o);

        //Empty the content if we either use pagination or we have to restart infinite scrolling
        if (!this.infiniteScrolling || fetchOptions.refresh)
            this.content.empty();

        //Empty the columns
        if (fetchOptions.refresh) {
            this.columnsContainer.empty();
            this._addColumns(state.columns);
        }

        //If infiniteScrolling is used and there's no full refresh, fill rows
        if(this.infiniteScrolling && ! fetchOptions.refresh) {

            var data = [];
            for (var i=0; i < state.records.length; i++) {
                data.push(this._addRow(state.records[i]));
            };

            o.fill({
                chunk: o.chunk,
                data: data
            });

        } else { //otherwise, simply append the rows to the now emptied list

            for (var i=0; i < state.records.length; i++) {
                this._addRow(state.records[i]);
            };

            this._syncColumnWidth();
                
            //If we're using infinite scrolling, we have to restart it
            if(this.infiniteScrolling) {
                this.contentDiv.infiniteScrolling('restart');
            }

        }

        //Initiate infinite scrolling if we don't use pagination and total records exceed the displayed records
        if(!this.infiniteScrolling && !this.options.pagination && fetchOptions.limit < state.totalRecords) {
                
            this.infiniteScrolling = true;
            this.contentDiv.infiniteScrolling({
                total: self.options.allocateRows ? state.totalRecords : false,
                chunk: self.options.chunk,
                scroll: function(e, ui) {
                    self.offset = ui.start;
                    self._update({ fill: ui.fill, chunk: ui.chunk });
                },
                update: function(e, ui) {
                    $('.ui-grid-limits', self.footer).html('Result ' + ui.firstItem + '-' + ui.lastItem + (ui.total ? ' of '+ui.total : ''));
                }
            });
                
        }

        if(!this.infiniteScrolling)
            $('.ui-grid-limits', this.footer).html('Result ' + fetchOptions.start + '-' + (fetchOptions.start + fetchOptions.limit) + ' of ' + state.totalRecords);

    }
 
}));


$.extend($.ui.karlgrid, {
    defaults: {
        width: 500,
        height: 300,

        limit: false,
        pagination: true,
        allocateRows: true, //Only used for infinite scrolling
        chunk: 20, //Only used for infinite scrolling

        footer: true,
        toolbar: false,

        multipleSelection: true,

        evenRowClass: 'even',
        oddRowClass: 'odd',

        sortColumn: '',
        sortDirection: '',

        initialState: null
    }
});



$.widget('ui.karldialog', $.extend({}, $.ui.dialog.prototype, {

    _init: function() {
        $.ui.dialog.prototype._init.call(this);
    },

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
        uiDialog.focus()

        this._trigger('open');
        this._isOpen = true;
    }


}));

$.extend($.ui.karldialog, {
    defaults: $.extend({}, $.ui.dialog.defaults, {
        autoOpen: false,
        modal: true,
        bgiframe: true,    // XXX bgiFrame is currently needed for modal
        hide: 'fold'
    })
});


$.widget('ui.karlmultiupload', {

    _init: function() {
        var self = this;
        this.stub = this.element.find(this.options.selectorStub);
        // Set up the stub
        var input = this.stub
            .hide()
            .find('input')
        this.name = input.attr('name');
        input.removeAttr('name');
        // Set up the add button
        this.element.find(this.options.selectorAddButton)
            .click(function(e) {
                self._add();
                e.preventDefault();
            });
    },

    // Add a new stub
    _add: function() {
        var new_stub = this.stub.clone()
            .insertBefore(this.stub);
        var input = new_stub.find('input')
        input.attr('name', this.name + this._getCounter());
        // bind the close button
        new_stub.find(this.options.selectorCloseButton)
            .click(function(e) {
                new_stub.remove();
                e.preventDefault();
            });
        new_stub.show();
    },

    _getCounter: function() {
        this.counter = this.counter || 0;
        return this.counter++;
    }

});

$.extend($.ui.karlmultiupload, {
    defaults: {
        selectorStub: '.muf-stub',
        selectorCloseButton: '.muf-closebutton',
        selectorAddButton: '.muf-addbutton'
    }
});


$.widget('ui.karlsingleupload', {

    _init: function() {
        var self = this;
        this.stub = this.element.find(this.options.selectorStub);
        // Set up the stub
        var input = this.stub
            .hide()
            .find('input')
        this.name = input.attr('name');
        input.removeAttr('name');
        // Set up the options
        this.element.find(this.options.selectorNoChange)
            .click(function(e) {
                if (self.real) {
                    self._del();
                }
            });
        this.element.find(this.options.selectorUpload)
            .click(function(e) {
                if (! self.real) {
                    self._add();
                }
            });

    },

    // Add a new stub
    _add: function() {
        var _r = this.real = this.stub.clone()
            .insertBefore(this.stub);
        var input = _r.find('input')
        input.attr('name', this.name);
        _r.show();
    },

    // Delete the stub
    _del: function() {
        this.real.remove();
        this.real = null;
    }

});

$.extend($.ui.karlsingleupload, {
    defaults: {
        selectorStub: '.sif-stub',
        selectorNoChange: '.sif-nochange',
        selectorUpload: '.sif-upload'
    }
});


/**
 * Quotable comments
 *
 * - The widget is bound to a comment.
 * - The "pasteToActiveTiny" event pastes the designated text area
 *   into the selection of the active tinymce window
 * - A click to the "Quote" link will trigger above event.
 *
 */
$.widget('ui.karlquotablecomment', {

    _init: function() {
        var self = this;
        this.text = this.element.find(this.options.selectorText);
        // Set up the paste button
        this.element.find(this.options.selectorPasteButton)
            .click(function(e) {
                self.pasteToActiveTiny();
                e.preventDefault();
            })
    },

    // Paste into the active tinymce window
    pasteToActiveTiny: function() {
        var raw_text = this.text.html()
        var editor = tinyMCE.activeEditor;
        // set focus to this editor
        editor.focus();
        // paste the content
        editor.selection.setContent(
            this.options.wrapperPre +
            raw_text +
            this.options.wrapperPost
        );
    }

});

$.extend($.ui.karlquotablecomment, {
    defaults: {
        selectorText: '.commentText',
        selectorPasteButton: '.quo-paste',
        wrapperPre: '<div class="quotedreplytext">',
        // An empty paragraph must be added after the quote.
        wrapperPost: '</div><div><p></p></div>'
    }
});


/**
 * Date time picker field
 *
 * Bound to a single input field. This field is made hidden, and
 * three input fields yyy-date yyy-hour and yyy-minute are created.
 * The date field is bound as an ui-datepicker.
 *
 */
$.widget('ui.karldatetimepicker', {

    _init: function() {
        var self = this;
        if (! jQuery.nodeName(this.element[0], 'input')) {
            throw new Error('ui.karldatetimepicker can only be bound to <input> nodes.');
        }
        // Creare a container to hold the new inputs.
        this.container = $('<span class="ui-karldatetimepicker-container"></span>');
        // Position the container after the old input element,
        // which in turn gets hidden.
        this.element
            .hide()
            .after(this.container);
        // Create the date and time inputs inside the container.
        this.dateinput = $('<input class="ui-karldatetimepicker-dateinput"></input>')
            .appendTo(this.container)
            .datepicker({
            })
            .change(function(evt) {
                self.setDate($(evt.target).val());
            });
        this.hourinput = $('<select class="ui-karldatetimepicker-hourinput"></input>')
            .appendTo(this.container)
            .change(function(evt) {
                self.setHour($(evt.target).val());
            });
        for (var i=0; i<24; i++) {
            $('<option>')
                .val(i)
                .text(i)
                .appendTo(this.hourinput);
        }
        this.container.append('<span class="ui-karldatetimepicker-colon">:</span>');
        this.minuteinput = $('<select class="ui-karldatetimepicker-hourinput"></input>')
            .appendTo(this.container)
            .change(function(evt) {
                self.setMinute($(evt.target).val());
            });
        for (var i=0; i<4; i++) {
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
    set: function(value) {
        // Split the value
        // Everything before the first space goes to date, the rest to time
        var split_pos = value.search(' ');
        var timestr = value.substr(split_pos + 1);
        // Time is further split to hours and minutes by the colon
        var time_split_pos = timestr.search(':');
        this.composite_value = {
            datestr: value.substr(0, split_pos),
            hourstr: value.substr(split_pos + 1, time_split_pos),
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
    setDate: function(value) {
        // Remember the value, so we are always in possession
        // of the full array of values we composite
        this.composite_value.datestr = value;
        this.dateinput.val(this.composite_value.datestr);
        this._updateComposite();
    },

    // Set hour part (as string)
    setHour: function(value) {
        // Remember the value, so we are always in possession
        // of the full array of values we composite
        this.composite_value.hourstr = value;
        this.hourinput.val(this.composite_value.hourstr);
        this._updateComposite();
    },

    // Set minute part (as string)
    setMinute: function(value) {
        // Remember the value, so we are always in possession
        // of the full array of values we composite
        this.composite_value.minutestr = value;
        this.minuteinput.val(this.composite_value.minutestr);
        this._updateComposite();
    },

    _updateComposite: function() {
        // Update the composite value, which will be submitted in the original
        // input.
        var value = this.composite_value.datestr + ' ' + 
                    this.composite_value.hourstr + ':' + this.composite_value.minutestr;
        this.element.val(value);
        this.element.trigger('change.karldatetimepicker');
    },

    // gets the value as a javascript Date object
    getAsDate: function() {
        // XXX how to handle invalid date exceptions?
        return new Date(Date.parse(this.element.val()));
    },

    // gets the value as a javascript Date object
    setAsDate: function(da) {
        var _pad = function(num) {
            var str = '0' + num;
            return str.substr(str.length-2, 2);
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
    limitMinMax: function(minval, maxval) {
        var value = this.getAsDate();
        var set_value = null;
        if (minval && value < minval) {
            set_value = minval;
        }
        if (maxval && value > maxval) {
            set_value = maxval;
        }
        if (set_value != null) {
            // Element changed.
            this.setAsDate(set_value);
            this.dateinput.effect("pulsate", {times: 1}, 800);
            this.hourinput.effect("pulsate", {times: 1}, 800);
            this.minuteinput.effect("pulsate", {times: 1}, 800);
        }

    }

});

$.ui.karldatetimepicker.getter = "getAsDate";
$.extend($.ui.karldatetimepicker, {
    defaults: {
    }
});


/**
 * Dropdown menu
 *
 *  <li class="karldropdown">
 *     <a class="karldropdown-heading" href="#">Add</a>
 *     <ul class="karldropdown-menu">
 *       <li>
 *         <a href="#">Folder</a>
 *       </li>
 *       <li>
 *         <a href="#">Forum</a>
 *       </li>
 *       <li>
 *         <a href="#">File</a>
 *       </li>
 *     </ul>
 *   </li>
 *
 * It may appear on a menubar:
 *
 *   <ul class="menubar">
 *     <li>...</li>
 *     <li class="karldropdown">
 *     <li>...</li>
 *   </ul>
 *
 */

$.widget('ui.karldropdown', {

    _init: function() {
        var self = this;
        this._locate();

        // to be on the safe side...
        this.menu.hide();

        // add the dropdown indicator
        $('<div>')
            .attr('class', 'karldropdown-indicator ui-icon ui-icon-triangle-1-s')
            .insertBefore(this.menu);

        // bind the menu
        this.element
            .mouseenter(function() {self.show();})
            .mouseleave(function() {self.hide();});
        this.items
            .mouseover(function() {self.hoverItem(this);})

        // needed to control the item hovers
        this.current_item = null;
    },

    _locate: function() {
        this.heading = this.element.find('> .karldropdown-heading');
        this.menu = this.element.find('> .karldropdown-menu');
        this.items = this.menu.find('> li');
    },

    // --
    // Control
    // --
    
    // show the dropdown
    show: function() {
        // position and size it
        var top = this.element.height();
        this.menu
            .css('position', 'absolute')
            .css('left', 0)
            .css('top', top);
        // calculate the padding to fit first child's padding
        var first_child = this.element.find(':first');
        this.padding_left = Math.round(first_child.position().left +
                                parseFloat(first_child.css('padding-left')) || 0);
        this.resetAllItems();
        // show it
        this.menu
            .stop(true, true)
            .slideDown(150);
        // Make the item widths expand the menu
        // We would not need this if there were no IE
        var max_width = 0;
        this.items
            .each(function() {
                // XXX I don't like it!
                var width;
                if (jQuery.browser.msie) {
                    width = this.offsetWidth;
                } else {
                    width = $(this).width();
                }
                max_width = Math.max(max_width, width);
            })
            .each(function() {
                $(this)
                    .width(max_width)
            });
    },

    // hide the dropdown
    hide: function() {
        // Reset all items
        this.resetAllItems();
        this.current_item = null;
        this.menu
            .stop(true, true)
            .fadeOut(50);
    },

    // reset all items to initial state
    resetAllItems: function() {
        var self = this;
        this.items.each(function() {self.resetItem(this);});
    },

    // reset an item to initial state
    resetItem: function(item) {
        // Reset animation and css
        $(item)
            .stop(true, true)
            .css('backgroundColor', '#666666')
            .css('color', '#000000')
            .css('paddingLeft', this.padding_left)
            .css('paddingRight', '11px');
    },

    // hover an item
    hoverItem: function(item) {
        var self = this;
        // Lazy leaving of element eliminates juggling effects.
        // Prevent anything from happening if we return to same element.
        if (this.items.index(this.current_item) == this.items.index(item)) {
            return;
        }
        // If there was a previous item, leave it now.
        if (this.current_item) {
            this.leaveItem(this.current_item);
        }
        var item = $(item);
        item
            .stop(true, true)
            .animate({
                backgroundColor: '#cecece',
                color: '#ffffff'
            }, 100)
            .animate({
                paddingLeft: self.padding_left + 6,
                paddingRight: '5px'
            }, 150);
        this.current_item = item;
    },

    // leave an item
    leaveItem: function(item) {
        var self = this;
        var item = $(item);
        item
            .stop(true, true)
            .animate({
                paddingLeft: self.padding_left,
                paddingRight: '11px'
                }, 50)
            .css('backgroundColor', '#666666')
            .css('color', '#000000');
        this.current_item = null;
    }

});

$.extend($.ui.karldropdown, {
    defaults: {
    }
});



// Initialize jquery
$(document).ready(function() {
    
    // Initialize tinymce live forms
    createLiveForms();

    var app_url = $("#karl-app-url")[0].content;
    var here_url = $("#karl-here-url")[0].content;

    $("#livesearch-input").karllivesearch({
        ajax: app_url + "/jquery_livesearch",
        match: function(typed) { return true; },
        insertText: function(obj) { return obj.title },
        wrapper: '<ul class="livesearch-list"></ul>',
        templateText: '<li class="<%= rowclass %>"><%= pre %><div class="item"><a href="<%= href %>"><%= title %></a></div><%= post %></li>'
    });

    var tagbox_data = window.karl_client_data && karl_client_data.tagbox || {};

    var _check_tagbox_data = function() {
        if (! tagbox_data.records) {
            throw 'karl_client_data.tagbox not specified or has no records.';
        }
    };
    var tagsearch_input = $("#tagsearch-input");

    // check karl_client_data.tagbox only if we have a tagbox in the page
    if (tagsearch_input.length > 0) _check_tagbox_data();
    tagsearch_input.karltagbox({
        validateRegexp: "^[a-zA-Z0-9\-\._]+$",
        ajax: app_url + "/jquery_tag_search",
        ajaxAdd: here_url + "jquery_tag_add",
        ajaxDel: here_url + "jquery_tag_del",
        prevals: tagbox_data.records,
        docid: tagbox_data.docid,
        showtag_url: app_url + '/showtag/',
        tagusers_url: app_url + '/tagusers.html'
    });

    var membersearch_input = $("#membersearch-input");
    // XXX this widget has no init data atm
    //if (box_input.length > 0) _check_tagbox_data();
    membersearch_input.karlmemberbox({
        ajax: here_url + "jquery_member_search",
        showtag_url: app_url + '/profiles/',
        name: 'users'
    });


    // quotable comments
    
    $('.blogComment').karlquotablecomment({
    });
    
    
    // Enable old style dropdowns
    enableOldStyleDropdowns();

}); // END document ready handler

// For debugging and development.
// (only works on FF)
Karl.themeroller = function() {
    if (window.jquitr) {
        jquitr.addThemeRoller();
    } else {
        jquitr = {};
        jquitr.s = document.createElement('script');
        jquitr.s.src = 'http://jqueryui.com/themeroller/developertool/developertool.js.php';
        document.getElementsByTagName('head')[0].appendChild(jquitr.s); 
    }
};

})();                   // END CLOSURE Karl

