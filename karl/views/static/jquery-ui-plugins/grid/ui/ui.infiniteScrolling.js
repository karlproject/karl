/*
 * jQuery UI Dialog @VERSION
 *
 * Copyright (c) 2008 Richard D. Worth (rdworth.org)
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

$.widget("ui.infiniteScrolling", {
	
	_init: function() {

		var self = this;
		this.tbody = $('> table > tbody', this.element);
		this.height = this.element.height();
		this.rowHeight = $('tr', this.tbody).height();
			
		//Prepare the cache that tells us what already has been loaded and what not
		this._prepareCache();
			
		//Alocate all rows in this.options.total to change the scrollbar size
		if(this.options.total)
			this._allocateRows();
		
		//Call update the first time to retrieve the first set of rows
		this._update();
	
		this.element.bind('scroll.infiniteScrolling', function(event) {
			if(self.prevScrollTop != this.scrollTop) {
				self.prevScrollTop = this.scrollTop;
				self._update(event);
			}
		});
		
	},
	
	restart: function() {
		
		this.element.unbind('.infiniteScrolling');
		this._init();
		
	},
	
	_prepareCache: function() {
		
		this.cache = new Array(this.options.total ? Math.ceil(this.options.total / this.options.chunk) : undefined);
		var alreadyCached = Math.floor($('tr', this.tbody).length / this.options.chunk);
		for (var i=0; i < alreadyCached; i++) {
			this.cache[i] = (new Date()).getTime();
		};
		
	},
	
	_allocateRows: function() {
	
		var num = this.options.total - $('tr', this.tbody).length;
		var colspan = $('tr:eq(0) > td', this.tbody).length;
		var newHTML = this.tbody[0].innerHTML;
		
		for (var i=0; i < num; i++) {
			newHTML += '<tr><td style="height:'+this.rowHeight+'px;border:0;padding:0;margin:0;" colspan="'+colspan+'"></td></tr>';
		};
			
		// Appending this whole block to innerHTML is drastically faster than individual appends in the loop above
		// TODO: Find out why directly setting the innerHTML is screwing IE
		if($.browser.msie)
			this.tbody.html(newHTML);
		else
			this.tbody[0].innerHTML = newHTML;
	
	},
	
	_update: function(event) {
		
		var self = this;
		var timeoutFunctions = [];
		var start = this.element[0].scrollTop;
		var stop = start + this.height;
		
		var firstItem = Math.floor((start+this.rowHeight) / this.rowHeight);
		var lastItem = Math.floor(stop / this.rowHeight); //Usually we should use 'ceil' here, but to accomodate the bottom scrollbar, we use floor
		
		var firstChunk = Math.round(firstItem / this.options.chunk);
		var lastChunk = Math.round(lastItem / this.options.chunk);

		for (var i=firstChunk - (this.options.total ? this.options.preload : 0); i <= lastChunk + this.options.preload; i++) {
			
			if(i < 0 || (this.options.total && i >= this.cache.length)) continue;
			timeoutFunctions.push(function(i2) {
				return function() {
					if(self.cache[i2]) return;
					self.cache[i2] = (new Date()).getTime(); //TODO: Revalidation option
					self._trigger('scroll', event, { total: self.options.total, chunk: i2, start: i2 * self.options.chunk, fill: function() { return self.fill.apply(self, arguments); } });
				};
			}(i));

		};
		
		
		if(this.timeout) window.clearTimeout(this.timeout);
		this.timeout = window.setTimeout(function() {

			$(timeoutFunctions).each(function() {
				this();
			});
			
			self._trigger('update', event, { firstChunk: firstChunk, lastChunk: lastChunk, firstItem: firstItem, lastItem: lastItem, total: self.options.total });

		}, this.options.delay);
		

	},
	
	fill: function(o) {
		
		var rows = this.tbody[0].rows;
		
		for (var i=0; i < o.data.length; i++) {

			if(o.data[i].jquery || o.data[i].nodeType || o.data[i].constructor == String) {
				var template = o.data[i];
			} else {
				var template = this.options.template;
				for(var r in o.data[i]) {
					template = template.replace(new RegExp('\\{\\$'+r+'\\}', 'g'), o.data[i][r]);
				}
			}

			
			//I'm sure there is a better way to do this..
			this.tbody[0][(this.options.total ? 'replace' : 'append')+'Child']($(template)[0], rows[(o.chunk * this.options.chunk)+i]);
			
		};
		
	}
	
});

$.extend($.ui.infiniteScrolling, {
	version: "@VERSION",
	defaults: {
		total: null, //If set to false, rows are not allocated
		chunk: 20,
		preload: 1,
		delay: 100
	}
	
});




})(jQuery);
