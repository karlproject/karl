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
