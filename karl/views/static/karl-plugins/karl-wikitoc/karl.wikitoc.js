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
    },

    _create: function() {
        var self = this;

        this.element.append(
          '<div class="karl-wikitoc-gridwrapper ui-helper-clearfix">' +
            '<div class="karl-wikitoc-widthconstrainer">' +
                '<div class="karl-wikitoc-grid"></div>' +
            '</div>' +
            '<div class="karl-wikitoc-inspector ui-widget-header">' +
              '<div class="karl-wikitoc-inspector-wrapper">' +

                  '<p>Search in title:</p>' +
                  '<div>' +
                    '<span class="ui-icon ui-icon-search" style="float: left; position: relative;"></span>' +
                    '<input type="text" disabled style="margin-left: -16px;></input>' +
                  '</div>' +
                  '<div class="ui-helper-clearfix"></div>' +
                  '<div>' +
                    '<input type="checkbox" disabled></input>' +
                    '<label>Group by tags</label>' +
                  '</div>' +

                  '<div class="karl-wikitoc-columnselectors">' +
                      '<p>Select columns:</p>' +
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
                        '<input class="karl-wikitoc-cb-creation_date" type="checkbox" checked="checked"></input>' +
                        '<label>Created</label>' +
                      '</div>' +
                  '</div>' +

              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="karl-wikitoc-footer ui-widget-header">' +
            '<a href="#" class="karl-wikitoc-button-inspector">Inspector</a>' +
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

        // sniff the inspector width from the css.
        this.inspector_width = $('.karl-wikitoc-inspector-wrapper').width();

        this.el_column_selectors = {
            title: this.el_inspector.find('.karl-wikitoc-cb-title'),
            author_name: this.el_inspector.find('.karl-wikitoc-cb-author_name'),
            tags: this.el_inspector.find('.karl-wikitoc-cb-tags'),
            creation_date: this.el_inspector.find('.karl-wikitoc-cb-creation_date') 
        };
        $.each(this.el_column_selectors, function(id, el) {
            el.click(function() {
                self.grid_columns = self.grid.getColumns();
                self.filterGridColumns();
                self.grid.setColumns(self.grid_columns);
            });
        });

        this.el_button_inspector
            .button({
                icons: { primary: 'ui-icon-circle-triangle-w' }
            })
            .click(function(evt) {
                // we need the current sizes and order, so refresh it.
                self.grid_columns = self.grid.getColumns();
                self.toggleInspector(evt);
                return false;
            });

        this.inactive_columns = {};
        this.grid_columns = [
            {id:"title", name:"Title", field:"title", formatter: TitleCellFormatter, width:280, minWidth:20, sortable:true},
            {id:"author_name", name:"Author", field:"author_name", width:80, minWidth:20, sortable:true},
            {id:"tags", name:"Tags", field:"tags", width: 140, minWidth:20, sortable:true},
            {id:"creation_date", name:"Created", field:"creation_date", formatter: DateCellFormatter, width:100, minWidth:20, sortable:true}
        ];

        this.filterGridColumns();
        var columns = this.grid_columns;

        var options = {
            enableCellNavigation: true,
            editable: false,
            forceFitColumns: true
        };

        var sortcol = "creation_date";
        var sortdir = -1;

        function comparer(a,b) {
            var x = a[sortcol], y = b[sortcol];
            return (x == y ? 0 : (x > y ? 1 : -1));
        }


        var groupItemMetadataProvider = new Slick.Data.GroupItemMetadataProvider();
        var dataView = new Slick.Data.DataView({
            groupItemMetadataProvider: groupItemMetadataProvider
        });
        
        var grid = this.grid = new Slick.Grid(this.el_grid, dataView, columns, options);

        // wire up model events to drive the grid
        dataView.onRowCountChanged.subscribe(function(e,args) {
            grid.updateRowCount();
            grid.render();
        });

        dataView.onRowsChanged.subscribe(function(e,args) {
            grid.invalidateRows(args.rows);
            grid.render();
        });


        //var pager = new Slick.Controls.Pager(dataView, grid, this.footer);
        //var columnpicker = new Slick.Controls.ColumnPicker(columns, grid, options);

        grid.onSort.subscribe(function(e, args) {
            sortdir = args.sortAsc ? 1 : -1;
            sortcol = args.sortCol.field;

            // using native sort with comparer
            // preferred method but can be very slow in IE with huge datasets
            dataView.sort(comparer, args.sortAsc);
        });

        // initialize the model after all the events have been hooked up
        dataView.beginUpdate();
        dataView.setItems(this.options.items);
        dataView.endUpdate();
        
    },

    //destroy: function() {
    //    $.Widget.prototype.destroy.call( this );
    //}

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
            this.el_button_inspector
                .button('option', 'icons', {primary: 'ui-icon-circle-triangle-e'});
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
            this.el_button_inspector
                .button('option', 'icons', {primary: 'ui-icon-circle-triangle-w'});
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
    }
    
});


})(jQuery);
