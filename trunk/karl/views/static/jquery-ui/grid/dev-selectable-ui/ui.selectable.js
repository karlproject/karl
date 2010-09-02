/*
 * jQuery UI Selectable @VERSION
 *
 * Copyright (c) 2008 Paul Bakaus
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 * 
 * http://docs.jquery.com/UI/Selectables
 *
 * Depends:
 *	ui.core.js
 */
(function($) {

	$.widget('ui.selectable', {

		_init: function() {

			var self = this;

			//Set the currentFocus to the first item
			this.currentFocus = $($(this.options.filter, this.element)[0]);

			//Disable text selection
			this.element.disableSelection();

			this.element
				.bind('mousedown', function(event) {

					var item;
					$(event.target).parents().andSelf().each(function() {
						if ($(self.options.filter, self.element).index(this) != -1) item = this;
					});

					if (!item)
						return;

					self._select(event, item);
					self.element[0].focus();
					event.preventDefault();
				})
				.bind('focus.selectable', function() {
					self.currentFocus.addClass(self.options.focusClass);
				})
				.bind('blur.selectable', function() {
					self.currentFocus.removeClass(self.options.focusClass);
				})
				.bind('keydown.selectable', function(event) {

					if (event.keyCode == $.keyCode.DOWN || event.keyCode == $.keyCode.RIGHT) {
						self.selectNext(event);
						event.preventDefault();
					}

					if (event.keyCode == $.keyCode.UP || event.keyCode == $.keyCode.LEFT) {
						self.selectPrevious(event);
						event.preventDefault();
					}

					if ((event.ctrlKey || event.metaKey) && event.keyCode == $.keyCode.SPACE) {
						self._toggleSelection(self.currentFocus);
					}

				});

		},

		_selection: [],

		_clearSelection: function() {

			for (var i = this._selection.length - 1; i >= 0; i--){
				this._selection[i]
					.removeClass(this.options.selectClass)
					.data('ui-selected', false);
			};

			this._selection = [];

		},

		_toggleSelection: function(item) {
			if (item.data('ui-selected')) {
				this._removeFromSelection(item);
			} else {
				this._addToSelection(item);
			}
		},

		_addToSelection: function(item) {

			if (item.data('ui-selected'))
				return;

			this._selection.push(item);
			this.latestSelection = item;
			item
				.addClass(this.options.selectClass)
				.data('ui-selected', true);

		},

		_removeFromSelection: function(item) {

			for (var i=0; i < this._selection.length; i++) {
				if (this._selection[i][0] == item[0]) {
					this._selection[i]
						.removeClass(this.options.selectClass)
						.data('ui-selected', false);
					this._selection.splice(i,1);
					break;
				}
			};

		},

		_updateSelectionMouse: function(event) {

			if (event.shiftKey && this.options.multiple) {

				//Clear the previous selection to make room for a shift selection
				this._clearSelection();

				var dir = $(this.options.filter, this.element).index(this.latestWithoutModifier[0]) > $(this.options.filter, this.element).index(this.currentFocus[0]) ? 'prev' : 'next';
				var i = this.latestWithoutModifier.data('ui-selected') ? this.latestWithoutModifier[dir]() : this.latestWithoutModifier;
				while(i.length && i[0] != this.currentFocus[0]) {
					this._addToSelection(i);
					i = i[dir]();
				}

				//Readd the item with the current focus
				this._addToSelection(this.currentFocus);

			} else {

				if (event.ctrlKey || event.metaKey) {
					this._toggleSelection(this.currentFocus);
				} else {
					this._clearSelection();
					this._addToSelection(this.currentFocus);
					this.latestWithoutModifier = this.currentFocus;
				}

			}

		},

		_updateSelection: function(event, dir) {

			if (event.shiftKey && this.options.multiple) {

				if (this.currentFocus.data('ui-selected')) {
					this._removeFromSelection(this.previousFocus);
				} else {

					var dir2 = $(this.options.filter, this.element).index(this.latestSelection[0]) > $(this.options.filter, this.element).index(this.currentFocus[0]) ? 'next' : 'prev';
					if (!this.previousFocus.data('ui-selected')) {
						var i = dir == dir2 ? this.previousFocus[dir2]() : this.previousFocus;
						while(i.length && !i.data('ui-selected')) {
							this._addToSelection(i);
							i = i[dir2]();
						}
					}

					this._addToSelection(this.currentFocus);

				}

			} else {

				//If the CTRL or Apple/Win key is pressed, only set focus
				if (event.ctrlKey || event.metaKey)
					return;

				this._clearSelection();
				this._addToSelection(this.currentFocus);
				this.latestWithoutModifier = this.currentFocus;

			}

		},

		_select: function(event, item) {

			//Set the current selection to the previous/next item
			this.previousFocus = this.currentFocus;
			this.currentFocus = $(item);

			this.previousFocus.removeClass(this.options.focusClass);
			this.currentFocus.addClass(this.options.focusClass);

			//Set and update the selection
			this._updateSelectionMouse(event);

			//Trigger select event
			this._trigger('select', event, this._uiHash(event));

		},

		_selectAdjacent: function(event, dir) {

			//Bail if there's no previous/next item
			if (!this.currentFocus[dir]().length)
				return;

			//Set the current selection to the previous/next item
			this.previousFocus = this.currentFocus;
			this.currentFocus = this.currentFocus[dir]();

			this.previousFocus.removeClass(this.options.focusClass);
			this.currentFocus.addClass(this.options.focusClass);

			//Set and update the selection
			this._updateSelection(event, dir);

			//Trigger select event
			this._trigger('select', event, this._uiHash(event));

		},

		selectPrevious: function(event) {
			this._selectAdjacent(event, 'prev');
		},

		selectNext: function(event) {
			this._selectAdjacent(event, 'next');
		},

		_uiHash: function(event) {
			return {
				previousFocus: this.previousFocus,
				currentFocus: this.currentFocus,
				selection: $($.map(this._selection, function(i) { return i[0]; }))
			};
		}

	});

	$.extend($.ui.selectable, {
		defaults: {
			multiple: true,
			filter: '> *',
			selectClass: 'ui-selected',
			focusClass: 'ui-focused'
		}
	});

})(jQuery);
