(function($) {

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

var TitleCellFormatter = function(row, cell, value, columnDef, dataContext) { 
    var url = './' + dataContext.name;
    var result = '<a href="' + url + '">' + value + '</a>';
    return result;
}; 

var AuthorCellFormatter = function(row, cell, value, columnDef, dataContext) { 
    var url = dataContext.profile_url;
    var result = '<a href="' + url + '">' + value + '</a>';
    return result;
}; 


var DateCellFormatter = function(row, cell, value, columnDef, dataContext) { 
    var year = value.substring(0, 4);
    var month = value.substring(5, 7);
    var day = value.substring(8, 10);
    if (month.charAt(0) == '0') {
        month = month.substring(1);
    }
    if (day.charAt(0) == '0') {
        day = day.substring(1);
    }
    return month + '/' + day + '/' + year;
}; 


$.widget('karl.karlwikitoc', {

    options: {
        //items: []...,
        //rowHeight: 25,
        //headerHeight: 25,
        //ux2: false,
    },

    _create: function() {
        var self = this;

        var button = this.options.ux2 ?
            '<button class="btn karl-wikitoc-button-inspector">Options</button>' :
            '<a href="#" class="karl-wikitoc-button-inspector">Options</a>';

        var footer_classes = this.options.ux2 ?
            'karl-wikitoc-footer paginationBar' :
            'karl-wikitoc-footer ui-widget-header';

        this.element.append(
          '<div class="karl-wikitoc-gridwrapper ui-helper-clearfix">' +
            '<div class="karl-wikitoc-widthconstrainer">' +
                '<div class="karl-wikitoc-grid"></div>' +
            '</div>' +
            '<div class="karl-wikitoc-inspector">' +
              '<div class="karl-wikitoc-inspector-wrapper"><div class="karl-wikitoc-inspector-wrapper2">' +
                
                  '<fieldset class="karl-wikitoc-livesearch">' +
                      '<legend>Find in text</legend>' +
                        '<div>' +
                          '<p>Letters anywhere in title, tags, or author</p>' +
                          '<div>' +
                            '<span class="karl-wikitoc-icon-search ui-icon ui-icon-search"></span>' +
                            '<input class="karl-wikitoc-input-livesearch" type="text"></input>' +
                          '</div>' +
                          '<div class="ui-helper-clearfix"></div>' +
                    '</div>' +
                  '</fieldset>' +

                  '<fieldset class="karl-wikitoc-grouping">' +
                      '<legend>Grouping</legend>' +
                        '<div>' +
                          '<p>Column, if any, to group by</p>' +
                          '<div>' +
                            '<input type="checkbox" class="karl-wikitoc-cb-grouping"></input>' +
                            '<label>Group by tags</label>' +
                          '</div>' +
                    '</div>' +
                  '</fieldset>' +

                  '<fieldset class="karl-wikitoc-columnselectors">' +
                      '<legend>Columns</legend>' +
                      '<div>' +
                          '<p>Which columns to show in the grid, in addition to title</p>' +
                          '<div>' +
                            '<input class="karl-wikitoc-cb-title" type="checkbox" checked="checked"></input>' +
                            '<label>Title</label>' +
                          '</div>' +
                          '<div>' +
                            '<input class="karl-wikitoc-cb-author_name" type="checkbox" checked="checked"></input>' +
                            '<label>Author</label>' +
                          '</div>' +
                          '<div>' +
                            '<input class="karl-wikitoc-cb-tags" type="checkbox"></input>' +
                            '<label>Tags</label>' +
                          '</div>' +
                          '<div>' +
                            '<input class="karl-wikitoc-cb-created" type="checkbox" checked="checked"></input>' +
                            '<label>Created</label>' +
                          '</div>' +
                          '<div>' +
                            '<input class="karl-wikitoc-cb-modified" type="checkbox"></input>' +
                            '<label>Modified</label>' +
                          '</div>' +
                    '</div>' +
                  '</fieldset>' +

              '</div></div>' +
            '</div>' +
          '</div>' +
          '<div class="' + footer_classes + '">' +
            '<span class="karl-wikitoc-items"><span class="karl-wikitoc-items-num">0</span> items</span>' +
            button +
          '</div>'
        );

        // this is the wrapper for grid + inspector
        this.el_gridwrapper = this.element.find('.karl-wikitoc-gridwrapper');
        // this extra wrapper is needed because setCanvas takes 
        // the _parent_ width... not the _grid_ width... so we need a parent... sigh
        this.el_widthconstrainer = this.element.find('.karl-wikitoc-widthconstrainer');
        this.el_grid = this.el_gridwrapper.find('.karl-wikitoc-grid');
        this.el_inspector = this.el_gridwrapper.find('.karl-wikitoc-inspector');
        this.el_columnselectors = this.el_inspector.find('.karl-wikitoc-columnselectors');
        this.el_footer = this.element.find('.karl-wikitoc-footer');
        this.el_button_inspector = this.el_footer.find('.karl-wikitoc-button-inspector');
        this.el_input_livesearch = this.el_inspector.find('.karl-wikitoc-input-livesearch');
        this.el_cb_grouping = this.el_inspector.find('.karl-wikitoc-cb-grouping');
        this.el_label_items_num = this.el_footer.find('.karl-wikitoc-items-num');

        // sniff the inspector width from the css.
        this.inspector_width = $('.karl-wikitoc-inspector-wrapper').width();

        this.el_column_selectors = {
            title: this.el_inspector.find('.karl-wikitoc-cb-title'),
            author_name: this.el_inspector.find('.karl-wikitoc-cb-author_name'),
            tags: this.el_inspector.find('.karl-wikitoc-cb-tags'),
            created: this.el_inspector.find('.karl-wikitoc-cb-created'), 
            modified: this.el_inspector.find('.karl-wikitoc-cb-modified') 
        };
        $.each(this.el_column_selectors, function(id, el) {
            el.click(function() {
                self.grid_columns = self.grid.getColumns();
                self.filterGridColumns();
                self.grid.setColumns(self.grid_columns);
            });
        });

        // inspector toggle
        if (! this.options.ux2) {
            this.el_button_inspector
                .button({
                    icons: { primary: 'ui-icon-triangle-1-w' }
                });
        }
        this.el_button_inspector
            .click(function(evt) {
                // we need the current sizes and order, so refresh it.
                self.grid_columns = self.grid.getColumns();
                self.toggleInspector(evt);
                return false;
            });

        // livesearch
        this.searchString = '';
        this.el_input_livesearch.keyup(function(evt) {
            Slick.GlobalEditorLock.cancelCurrentEdit();
            // clear on Esc
            if (evt.which == 27) {
                this.value = '';
            }
            self.searchString = this.value;
            self.dataView.refresh();
        }); 

        // grouping
        this.el_cb_grouping.click(function(evt) {
            var selected = $(this).is(':checked');
            if (selected) {
                self.enableGrouping();
            } else {
                self.disableGrouping();
            }
        });

        // hover
        this.el_grid.find('.slick-row')
            .live("mouseenter mouseleave", function(evt) {
                var el = $(this);
                // do not hover group rows
                if (el.is('.slick-group')) {
                    return;
                }
                // handle hover class
                if (evt.type == "mouseenter") {
                    el.addClass('karl-wikitoc-grid-row-hover');
                } else {
                    el.removeClass('karl-wikitoc-grid-row-hover');
                }
            });

        // columns
        this.inactive_columns = {};
        this.grid_columns = [
            {id:"title", name:"Title", field:"title", formatter: TitleCellFormatter, width:320, minWidth:20, sortable:true},
            {id:"author_name", name:"Author", field:"author_name", formatter: AuthorCellFormatter, width:80, minWidth:20, sortable:true},
            {id:"tags", name:"Tags", field:"tags", width: 140, minWidth:20, sortable:false},
            {id:"created", name:"Created", field:"created", formatter: DateCellFormatter, width:60, minWidth:20, sortable:true},
            {id:"modified", name:"Modified", field:"modified", formatter: DateCellFormatter, width:60, minWidth:20, sortable:true}
        ];

        this.filterGridColumns();
        var columns = this.grid_columns;

        var options = {
            enableCellNavigation: true,
            editable: false,
            forceFitColumns: true,
            rowHeight: this.options.rowHeight,
            headerHeight: this.options.headerHeight
        };

        var groupItemMetadataProvider = new Slick.Data.GroupItemMetadataProvider();
        var dataView = this.dataView = new Slick.Data.DataView({
            groupItemMetadataProvider: groupItemMetadataProvider
        });

 

        var grid = this.grid = new Slick.Grid(this.el_grid, dataView, columns, options);

        // register the group item metadata provider to add expand/collapse group handlers
        grid.registerPlugin(groupItemMetadataProvider);

        function comparer(a,b) {
            var va = a[self.sortCol].toLowerCase();
            var vb = b[self.sortCol].toLowerCase();
            return (va == vb ? 0 : (va > vb ? 1 : -1));
        }

        // sorting
        this.sortCol = "title";
        this.sortDir = 1;

        grid.onSort.subscribe(function(e, args) {
            self.sortDir = args.sortAsc ? 1 : -1;
            self.sortCol = args.sortCol.field;

            // using native sort with comparer
            // preferred method but can be very slow in IE with huge datasets
            dataView.sort(comparer, args.sortAsc);
        });

        // wire up model events to drive the grid
        dataView.onRowCountChanged.subscribe(function(e,args) {
            grid.updateRowCount();
            grid.render();
        });

        dataView.onRowsChanged.subscribe(function(e,args) {
            grid.invalidateRows(args.rows);
            grid.render();
        });
        
        // initialize the model after all the events have been hooked up
        dataView.beginUpdate();
        dataView.setItems(this.options.items);
        dataView.setFilter(function contentFilter(item) {
            return self._contentFilter(item);
        });

        // sort initially
        grid.setSortColumn(this.sortCol, this.sortDir);
        dataView.sort(comparer, this.sortDir == 1);
        dataView.endUpdate();

        // display the footer info
        this.el_label_items_num.text(this.options.items.length);       

        // ux2: remove UI markup
        if (this.options.ux2) {
            // Modification for UX2: remove ui-widget classes,
            // as this is currently the simplest way to make
            // the page styles effective inside the widget.
            // These classes are added by SlickGrid which
            // is 3rd party source for us.
            this.element
                .find('.ui-widget').removeClass('ui-widget');
            this.element
                .find('.ui-widget-header').removeClass('ui-widget-header');
            this.element
                .find('.ui-widget-content').removeClass('ui-widget-content');
        }

        // ux2: pin the header padding.
        //
        // The grid uses the header padding for calculation.
        // And it considers it never changes during the lifetime of
        // the widget. However, if the padding changes (ie, due
        // to a resize) then the grid column layout borks.
        // As a workaround we will adjust the widths with the padding.
        // We _only_ need to remember them now for the later correction ;)
        //
        //
        // Use just the first one.
        var firstHeader = this.element.find('.slick-header-column').eq(0);
        this.headerColumnPadding = parseInt(firstHeader.css('padding-left'), 10) +
                parseInt(firstHeader.css('padding-right'), 10);

    },

    //destroy: function() {
    //    $.Widget.prototype.destroy.call( this );
    //}

    _addFakeRecords: function() {
        var self = this;
        // The fake records enable a record appear in as many
        // tag groups, as needed. We enable this by adding the extra
        // records to the grid.
        if (! this._fake_records_added) {
            this._fake_records_added = true;
            // we add some fake records so each row appears multiple
            // times, under each tag group it belongs to.
            this.dataView.beginUpdate();
            var items = this.dataView.getItems();
            $.each(items, function(index, item) {
                var tags = item.tags;
                item.original = true;
                if (tags.length === 0) {
                    item.effective_tag = '';
                } else {
                    item.effective_tag = tags[0];
                    $.each(tags, function(tagindex, tag) {
                        if (tagindex === 0) {
                            return;
                        }
                        var new_item = $.extend({}, item, {
                            effective_tag: tag,
                            original: false
                            });
                        self.dataView.addItem(new_item);
                    });
                }
            });
            this.dataView.endUpdate();
        }
    },

    enableGrouping: function() {
        var self = this;
        this.groupingEnabled = true;

        // Add the fake records needed for the grouping
        this._addFakeRecords();

        this.dataView.groupBy(
            'effective_tag',
            function (g) {
                if (g.value !== '') {
                    return '<span class="karl-wikitoc-groupheader">Tag: ' + g.value + '</span>' ;
                } else {
                    return '<span class="karl-wikitoc-groupheader">Untagged:</span>';
                }
            },
            function (a, b) {
                // Search case insensitive.
                var va = a.value.toLowerCase();
                var vb = b.value.toLowerCase();
                // equality
                if (va == vb) {
                    return 0;
                }
                // We want no-tags at the end,
                // which have the value of ''.
                if (va === '') {
                    return +1;
                }
                if (vb === '') {
                    return -1;
                }
                // Otherwise just order alphabetically.
                return va < vb ? -1 : +1;
            }
        );

    },

    disableGrouping: function() {
        this.groupingEnabled = false;
        this.dataView.groupBy(null);
    },

    _contentFilter: function(item) {
        // The fake records need to be filtered out in case there is
        // no grouping.
        if (! this.groupingEnabled && this._fake_records_added && ! item.original) {
            return false;
        }
        // Next, filter based on the search string
        // provided by the user.
        var ss = this.searchString.toLowerCase();
        if (ss === '') {
            return true;
        }
        if (item.title.toLowerCase().indexOf(ss) != -1) {
            return true;
        }
        if (item.author_name.toLowerCase().indexOf(ss) != -1) {
            return true;
        }
        var found_in_tags = false;
        $.each(item.tags, function(index, tag) {
            if (tag.toLowerCase().indexOf(ss) != -1) {
                found_in_tags = true;
                return false;  // stop iteration
            }
        });
        return found_in_tags;
    },

    filterGridColumns: function() {
        var self = this;
        var inactive_columns = this.inactive_columns;
        // handle columns which become added
        $.each(inactive_columns, function(id, value) {
            var new_column = value.data;
            var selected = self.el_column_selectors[id].is(':checked');
            if (selected) {
                // add the column after its marker,
                // or if that is not present, then to the end.
                var new_columns = [];
                var added = false;
                if (! value.prev_column) {
                    // add to the beginning
                    new_columns.push(new_column);
                    added = true;
                }
                $.each(self.grid_columns, function(index, column) {
                    new_columns.push(column);
                    if (value.prev_column && column.id == value.prev_column.id) {
                        // add to the middle, after the marker
                        new_columns.push(new_column);
                        added = true;
                    }
                });
                if (! added) {
                    // add to the end
                    new_columns.push(new_column);
                }
                // delete it from inactive
                delete inactive_columns[id];
                // write back to list
                self.grid_columns = new_columns;
            }
        });
        // handle columns that are removed
        var active_columns = [];
        var prev_column = null;
        $.each(this.grid_columns, function(index, column) {
            var id = column.id;
            var selected = self.el_column_selectors[id].is(':checked');
            if (selected) {
                active_columns.push(column);
            } else {
                inactive_columns[column.id] = {
                    data: column,
                    prev_column: prev_column
                };
            }
            prev_column = column;
        });
        this.grid_columns = active_columns;
    },

    toggleInspector: function(evt) {
        var self = this;
        // avoid toggling while toggling is in progress
        if (this.inspector_button_locked) {
            return;
        }
        this.inspector_button_locked = true;
        var width = this.inspector_width;
        //
        var current_open = this._inspector_open;
        var new_open = this._inspector_open = ! current_open;
        var full_w = this.el_widthconstrainer.width();
        if (new_open) {
            // opening
            if (! this.options.ux2) {
                this.el_button_inspector
                    .button('option', 'icons', {primary: 'ui-icon-triangle-1-e'});
            }
            this.el_inspector
                .animate({
                    'width': '' + width + 'px'
                } , {
                    complete: function() {
                        var ratio = (full_w - width) / full_w;
                        $.each(self.grid_columns, function(index, column) {
                            column.width = Math.round(column.width * ratio);
                        });
                        self.el_widthconstrainer.width(full_w - width);
                        self.grid.resizeCanvas();
                        self.grid.setColumns(self.grid_columns);
                        self.inspector_button_locked = false;
                    }
                });
        } else {
            // closing
            if (! this.options.ux2) {
                this.el_button_inspector
                    .button('option', 'icons', {primary: 'ui-icon-triangle-1-w'});
            }
            this.el_inspector
                .animate({
                    'width': '0px'
                } , {
                    complete: function() {
                        self.inspector_button_locked = false;
                    }
                });
            this.el_widthconstrainer.css('width', '100%');
            this.grid.resizeCanvas();
            var ratio = (full_w + width) / full_w;
            $.each(this.grid_columns, function(index, column) {
                column.width = Math.round(column.width * ratio);
            });
            this.grid.setColumns(this.grid_columns);
        }
    },


    resizeColumns: function(evt) {
        var self = this;
        // avoid resize while toggling is in progress
        if (this.inspector_button_locked) {
            return;
        }
        this.inspector_button_locked = true;
        //
        var full_w = this.el_gridwrapper.width();
        if (this._inspector_open) {
            full_w = full_w - this.inspector_width;
            this.el_widthconstrainer.width(full_w);
        }
        //
        var width = 0;
        $.each(this.grid_columns, function(index, column) {
            width += column.width;
        });
        var ratio = full_w / width;
       // $.each(this.grid_columns, function(index, column) {
       //     column.width = Math.round(column.width * ratio);
       // });

        this.grid.autosizeColumns();
        this.grid.resizeCanvas();
        this.grid.setColumns(this.grid_columns);

        // compensate widths after setColumns
        //
        var headers = this.element.find('.slick-header-column');
        var firstHeader = headers.eq(0);
        var newHeaderColumnPadding = parseInt(firstHeader.css('padding-left'), 10) +
                parseInt(firstHeader.css('padding-right'), 10);
        var headerWidthCorrection = this.headerColumnPadding - newHeaderColumnPadding;
        this.element.find('.slick-header-column').each(function () {
            var el = $(this);
            el.width(el.width() + headerWidthCorrection); 
        });

        this.inspector_button_locked = false;
    }
    
});


})(jQuery);
