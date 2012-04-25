
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console */
/*globals setTimeout clearTimeout setInterval */ 
/*globals jQuery Slick alert confirm */



(function ($) {

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    var months = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];

    var currentYear = new Date().getFullYear();

    var cellFormatters = {

        /* The table-wrapping in each cellformatter serves the purpose
         * of vertical alignments of the cell's content.
         * So they must be added to all formatters, else no
         * vertical alignment will happen.
         * If nothing specific is needed, use the "base" formatter!
         */

        base: function (row, cell, value, columnDef, dataContext) {
            var result = '<table><tr><td>';
            result += value;
            result += '</td></tr></table>';
            return result;
        },

        icon: function (row, cell, value, columnDef, dataContext) {
            var result = '<table><tr><td>';
            var icon_url = dataContext[columnDef.field + '_icon_url'];
            result += '<img src="' + icon_url + '" alt="icon" title="' + value + '"/>';
            result += '</td></tr></table>';
            return result;
        },

        link: function (row, cell, value, columnDef, dataContext) {
            var result = '<table><tr><td>';
            var url = dataContext[columnDef.field + '_url'];
            result += '<a href="' + url + '">' + value + '</a>';
            result += '</td></tr></table>';
            return result;
        }

    };

    // field names that map a default cell formatter
    // This can be overridden by specifying formatterName: 'theformatter'
    // on the column specifier!
    var defaultFieldFormating = {
        filetype: 'icon',
        title: 'link'
    };


    $.widget('popper.poppergrid', {

        options: {
            url: null,          // the url of the server side search
            //manageQueue: true,  // if to use the ajax queue manager
            manageQueue: false,  // if to use the ajax queue manager
            minimumLoad: null,   // load at least as much records
            loadData: null,     // load these records initially.
                                // Same format as the ajax payload.
            ////hideGridColumnHeader: false, // hide the grid's own column headers
            columns: [],
            // further example:
            //
            // columns: [
            //    {field: 'logo', name: 'Logo', width: 90},
            //    {field: 'title', name: 'Title', width: 292},
            //    {field: 'end_date', name: 'Date', width: 100, 
            //         formatterName: 'date'}
            // ],
            focus: false,          // should it get initial focus (to make button navigation possible)
            //extraQuery: {},
            rowHeight: 34,           // height of the grid rows
            checkboxSelectColumn: false,       // a checkbox column in the left.
                                              // This field has to be defined and named as "sel".
            autoResizeColumns: true
            // updateTotal: function(evt, data) {}   // data is like: {total: 1234}
            // selectedRowsChanged: function(evt) {}   //
        },

        _create: function () {
            var self = this;

            // grid columns
            this.gridColumns = [];

            // A checkbox column is added, if the option is selected
            if (this.options.checkboxSelectColumn) {
                this.checkboxSelector = new Slick.CheckboxSelectColumn({});
                this.saveSelectedColumns = null;
            }

            $.each(this.options.columns, function (index, value) {
                // fill out reasonable default values
                var defaults;
                var fieldName = value.field;
                var formatterName = value.formatterName || defaultFieldFormating[fieldName];
                if (fieldName == 'sel' && self.options.checkboxSelectColumn) {
                    // Special meaning: add the selection column here.
                    defaults = self.checkboxSelector.getColumnDefinition();
                    defaults.cssClass = 'cell-' + fieldName; // (fieldName == 'sel')
                    // save the original formatter as slickgrid closures it for us,
                    // and the formatter will need it.
                    defaults.cbFormatter = defaults.formatter;
                    if (formatterName) {
                        defaults.formatter = cellFormatters[formatterName];
                        defaults.cssClass += ' cellformatter-' + formatterName;
                    }
                } else {
                    // If there is no formatter specified, use base.
                    if (! formatterName) {
                        formatterName = 'base';
                    }
                    // All other (non-selection) fields
                    defaults = {
                        id: fieldName,
                        formatter: cellFormatters[formatterName],
                        cssClass:  'cell-' + fieldName + ' cellformatter-' + formatterName,
                        sortable: true
                    };
                }
                self.gridColumns.push($.extend({}, defaults, value));
                // this results in a row like:
                // {id: 'title', name: 'title', field: 'title', formatter: cellFormatter.titledescr,
                // cssClass: 'cell-title cellformatter-titledescr',
                //     width: 292, sortable: true},
            });

            var options = {
                enableCellNavigation: true,
                editable: false,
                forceFitColumns: true,
                rowHeight: this.options.rowHeight
            };

            var el_wrapper = this.el_wrapper = $(
                '<div class="pp-grid-wrapper">' +
                     '<div class="pp-grid"></div>' +
                '</div>'
            ).appendTo(this.element);

            this.data = {length: 0};

            this.el_grid = this.element.find('.pp-grid');

            // fetch default sorting for the loader
            var sortCol = null;
            var sortDir = 1;
            if (this.options.loadData) {
                // if we have initial data,
                // set the sorting based on what the server said.
                sortCol = this.options.loadData.sortCol;
                sortDir = this.options.loadData.sortDir;
            }

            // create the grid
            this.grid = new Slick.Grid(this.el_grid, this.data, this.gridColumns, options);

            var el_grid_viewport = this.element.find('.slick-viewport');

            //// hide the slickgrid header (columns)
            //if (this.options.hideGridColumnHeader) {
            //    this.element.find('.slick-header').hide();
            //    el_grid_viewport.height(this.el_grid.height());
            //} else {

            // initialize the sorting
            if (sortCol) {
                // let the grid add its sorting indicator
                this.grid.setSortColumn(sortCol, sortDir);
                // give sorted column a different color
                this._updateSortColumn(sortCol);
            }

            // initial focus if specified
            if (this.options.focus) {
                el_grid_viewport.focus();
            }

            // create the loader
            this.element.poppergridloader({
                url: this.options.url,
                manageQueue: this.options.manageQueue,
                sortCol: sortCol,
                sortDir: sortDir,
                extraQuery: this.options.extraQuery,
                minimumLoad: this.options.minimumLoad,
                dataLoading: function (evt) {
                    self.createLoadingIndicator();
                    self.loadingIndicator.show();
                },
                dataLoaded: function (evt, data) {
                    if (data.from !== undefined) {
                        //log('Arrived:', data.from, data.to);
                        var i;
                        for (i = data.from; i < data.to; i++) {
                            self.grid.invalidateRow(i);
                        }
                        self.grid.updateRowCount();
                        self.grid.render();
                        // display totals
                        self._displayTotal(data.total);
                        // restore selections
                        self._restoreSelection();
                    }
                    if (self.loadingIndicator) {
                        self.loadingIndicator.fadeOut();
                    }
                }
            });
            this.loader = this.element.data('poppergridloader');
            this.loader.setData(this.data);

            /* sorting by column */
            this.grid.onSort.subscribe(function (evt, args) {
                var sortDir = args.sortAsc ? 1 : -1;
                var sortCol = args.sortCol.field;
                // notify the loader that the sorting changed
                self.sortingChange(sortCol, sortDir);
            });

            // scrolling
            this.scrollPosition = -1;  // force movement forward
            this.grid.onViewportChanged.subscribe(function (evt, args) {
                var vp = self.grid.getViewport();
                var top = vp.top;
                var bottom = vp.bottom;
                var direction = top >= self.scrollPosition ? +1 : -1;
                self.loader.ensureData(top, bottom, direction);
                self.scrollPosition = top;
            });

            // selection
            if (this.options.checkboxSelectColumn) {
                this.grid.setSelectionModel(new Slick.RowSelectionModel({selectActiveRow: false}));
                this.grid.registerPlugin(this.checkboxSelector);
            }
            this.grid.onSelectedRowsChanged.subscribe(function (evt) { 
                self._trigger('selectedRowsChanged', evt, null);
            });

            // de-class jquery-ui (cells will still get .ui-widget-content though.)
            this.element.find('.ui-widget').removeClass('ui-widget');
            this.element.find('.ui-widget-header').removeClass('ui-widget-header');
            this.element.find('.ui-widget-content').removeClass('ui-widget-content');

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


            // handle initial load
            var data = this.options.loadData;
            if (data) {
                this.loader.loadData(data);
                this.grid.updateRowCount();
                this.grid.render();
                // display totals
                this._displayTotal(data.total);
            } else {
                // load the first page
                this.grid.onViewportChanged.notify();
            }

            // autoresize columns
            if (this.options.autoResizeColumns) {
                var timer;
                $(window).resize(function (evt) {
                    if (timer !== null) {
                        clearTimeout(timer);
                    }
                    timer = setTimeout(function () {
                        self.resizeColumns();
                        timer = null;
                    }, 400);
                });

            }
        },

        destroy: function () {
            this.loader.destroy();
            $.Widget.prototype.destroy.call(this);
            // be paranoid
            this.data = null;
        },

        createLoadingIndicator: function () {
            if (! this.loadingIndicator) {
                this.loadingIndicator = $(
                    '<span class="loading-indicator">' +
                        '<label>Buffering...</label>' +
                    '</span>')
                    .appendTo(document.body);
                this.loadingIndicator.position({
                    my: "center center",
                    at: "center center",
                    of: this.element
                });
            }
        },

        _displayTotal: function (total) {
            // format the total with commas, eg. 12,356,980
            total = '' + total;
            var newTotal = '';
            while (total.length > 0) {
                var segmentPos = total.length - 3;
                if (segmentPos < 0) {
                    segmentPos = 0;
                }
                var segment = total.substring(segmentPos);
                total = total.substring(0, segmentPos);
                if (newTotal.length > 0) {
                    newTotal = segment + ',' + newTotal;
                } else {
                    newTotal = segment;
                }
            }
            // Trigger an event to update external panels
            this._trigger('updateTotal', null, {total: newTotal});
        },

        _updateSortColumn: function (sortCol) {
            // give the sorting column the visual focus cue (different color)
            var el_grid_columns = this.el_grid.find('.slick-header-columns');
            var el_columns = el_grid_columns.children();
            el_columns.each(function (index) {
                var el = $(this);
                var fieldId = el.data('fieldId');
                if (fieldId == sortCol) {
                    el.addClass('ui-state-focus');
                } else {
                    el.removeClass('ui-state-focus');
                }
            });
        },

        sortingChange: function (sortCol, sortDir) {
            // re-sort
            //
            // give sorted column a different color
            this._updateSortColumn(sortCol);
            // notify the grid
            this.loader.option({
                sortCol: sortCol,
                sortDir: sortDir
            });
            this.clearData();
        },

        clearData: function () {
            this._clearData();
            // let the viewport load records currently visible
            this.grid.onViewportChanged.notify();
        },

        _setOption: function (key, value) {
            $.Widget.prototype._setOption.call(this, key, value);
            if (key == 'extraQuery') {
                this._reFilter();
            }
        },

        setExtraQueryKey: function (qkey, qvalue) {
            if (this.options.extraQuery === undefined) {
                this.options.extraQuery = {};
            }
            this.options.extraQuery[qkey] = qvalue;
            this._reFilter();
        },

        _reFilter: function () {
            this.loader.option({
                extraQuery: this.options.extraQuery
            });
            this._clearData();
            this.grid.onViewportChanged.notify();
        },

        getSelectedRows: function () {
            return this.grid.getSelectedRows();
        },

        getSelectedRowIds: function () {
            var selections =  this.getSelectedRows();
            var rows = this.getData();
            var results = [];
            if (selections.length > 100) {
                // Do not support selection of >100 items.
                return false;
            }
            $.each(selections, function (index, value) {
                var row = rows[value];
                // XXX XXX XXX
                if (row !== undefined) {
                    results.push(row.id);
                } else {
                    log('MISSED and IGNORED selection of uncached row #' + value);
                }
            });
            return results;
        },

        getData: function () {
            return this.grid.getData();
        },

        _clearData: function () {
            // destroy the current selection as well
            // but also save the ids.
            if (this.options.checkboxSelectColumn && this.saveSelectedColumns === null) {
                var data = this.getData();
                var rowIndexes = this.grid.getSelectedRows();
                // save which rows were selected.
                var selected = this.saveSelectedColumns = {};
                $.each(rowIndexes, function (index, rowIndex) {
                    var row = data[rowIndex];
                    selected[row.id] = true;
                });
                ////this.grid.setSelectedRows([]);
            }
            // clear the data
            this.loader.clearData();
        },

        _restoreSelection: function () {
            var self = this;
            // do we have a selection saved?
            if (this.options.checkboxSelectColumn && this.saveSelectedColumns !== null) {
                var selected = [];
                var data = this.getData();
                $.each(data, function (index, row) {
                    if (row !== undefined && self.saveSelectedColumns[row.id]) {
                        selected.push(index);
                    }
                });
                this.grid.setSelectedRows(selected);
                this.saveSelectedColumns = null;
            }
        },

        resizeColumns: function (evt) {
            var self = this;
            //
            var full_w = this.el_wrapper.width();
            //
            var width = 0;
            $.each(this.gridColumns, function (index, column) {
                width += column.width;
            });
            var ratio = full_w / width;
           // $.each(this.gridColumns, function(index, column) {
           //     column.width = Math.round(column.width * ratio);
           // });

            this.grid.autosizeColumns();
            this.grid.resizeCanvas();
            this.grid.setColumns(this.gridColumns);

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

        }
        

    });

    var _createdQ = false;
    var _qName = 'poppergridloaderQueue';

    function _createQ() {
        if (! _createdQ) {
            $.manageAjax.create(_qName, {
                queue: true,
                maxRequests: 1
            });
            _createdQ = true;
        }
    }


    /* slickgrid's data manager, made into a generic component */
    $.widget('popper.poppergridloader', {

        options: {
            url: null,          // the url of the server side search
            manageQueue: true,  // if to use the ajax queue manager
            sortCol: null,
            sortDir: 1,
            reallyAbort: false   // really abort all the outgoing requests. Leaving it on false
                                 // seems to be the best way. Note that independently of this
                                 // setting, the data clears (resort, or refilter) always do abort.
            // dataLoading: function(evt, data) {}   // data is like: {from: from, to: to}
            // dataLoaded: function(evt, data) {}    // data is what the server returned
            // extraQuery: {}
        },

        _create: function () {
            if (this.options.manageQueue) {
                // Is the code present?
                if (! $.manageAjax) {
                    throw new Error('The jquery.ajaxmanager.js must be loaded, if the grid is ' +
                        'created with the default option manageQueue=true.');
                }
                // Sadly, there is no way to check if a given named queue
                // exists.... so we need to do this globally
                _createQ();
            }
            this._active_request = null;
        },

        setData: function (data) {
            // We cannot pass data as options, because it clones it.
            // We must make sure we use the _identical_ data object
            // together with the grid.
            this.data = data;
        },

        getData: function (data) {
            return this.data;
        },

        destroy: function () {
            $.Widget.prototype.destroy.call(this);
            // XXX do not destroy the queue, as other grids may use it
            // XXX do something here!
            //
            // Just abort the request, make sure it always happens
            this._abortRequest(true);
            // (be paranoid about IE memory leaks)
            this.data = null;
        },

        clearData: function () {
            var data = this.data;
            $.each(data, function (key, value) {
                delete data[key];
            });
            // We force to abort all requests, even if reallyAbort=false
            this._abortRequest(true);
        },

        _abortRequest: function (force) {
            // (Note that in case the queue manager is used,
            // 'undefined' is a valid, non-null result for the
            // _active_request id. So, we _always_ check against 'null'!)
            // The 'force' parameter is set true when a clear data is complete
            // (on change of sorting or filtering), otherwise the 'reallyAbort'
            // parameter specifies if a physical abort is being performed.
            if (this._active_request !== null) {
                // abort the previous request
                if (this.options.manageQueue) {
                    $.manageAjax.clear(_qName, force || this.options.reallyAbort);
                } else {
                    if (force || this.options.reallyAbort) {
                        this._active_request.abort();
                    }
                }
            }
            this._active_request = null;
        },

        ensureData: function (from, to, direction) {
            //log('Records in viewport:', from, to, direction);
            var self = this;
            // abort the previous request
            this._abortRequest();

            if (from < 0) {
                throw new Error('"from" must not be negative');
            }
            if (from >= to) {
                throw new Error('"to" must be greater than "from"');
            }

            var start;
            var end;
            if (direction == +1) {
                start = from;
                end = to - 1;
            } else {
                start = to - 1;
                end = from;
            }

            // do we have all records in the viewport?
            var i = start;
            var firstMissing = null;
            var lastMissing = null;
            while (true) {
                if (! this.data[i]) {
                    if (firstMissing === null) {
                        firstMissing = i;
                    }
                    lastMissing = i;
                }
                if (i == end) {
                    break;
                }
                i += direction;
            }

            if (firstMissing === null) {
                // All records present.
                // We can return, nothing to fetch.
                //log('Has already', start, end);
                //
                // must trigger loaded, even if no actual data
                this._trigger('dataLoaded', null, null);
                return;
            }

            start = firstMissing;
            end = lastMissing;

            //log('Missing:', firstMissing, lastMissing);

            // Load at least minimumLoad records
            if (this.options.minimumLoad && (to - from) < this.options.minimumLoad) {
                end = start + direction * this.options.minimumLoad;
            }

            // Sort start and end now, and we can start loading.
            if (start > end) {
                from = end;
                to = start;
            } else {
                from = start;
                to = end;
            }
            if (from < 0) {
                from = 0;
            }
            // 'to' is the last item now = make it an index.
            to += 1;

            // hmmm... we actually don't know the total, do we?

            //log('Will load:', from, to, direction);

            this._trigger('dataLoading', null, {from: from, to: to});

            var ajaxOptions = {
                type: "GET",
                url: this.options.url,
                data: $.extend({
                    from: from,
                    to: to,
                    sortCol: this.options.sortCol,
                    sortDir: this.options.sortDir
                }, (this.options.extraQuery || {})),
                success: function (data) {
                    // XXX It seems, that IE bumps us
                    // here on abort(), with data=null.
                    if (data !== null) {
                        self._ajaxSuccess(data);
                    }
                    self._active_request = null;
                    self._trigger('dataLoaded', null, data);
                },
                error: function (xhr, textStatus, errorThrow) {
                    self._active_request = null;
                    self._ajaxError(xhr, textStatus, errorThrow);
                },
                dataType: 'json'
            };

            if (this.options.manageQueue) {
                this._active_request = $.manageAjax.add(_qName, ajaxOptions);
            } else {
                this._active_request = $.ajax(ajaxOptions);
            }

        },

        loadData: function (data) {
            var from = data.from,
                to = data.to,
                i;
            for (i = from; i < to; i++) {
                this.data[i] = data.records[i - from];
            }
            this.data.length = data.total;
        },

        _ajaxSuccess: function (data) {
            this.loadData(data);
        },

        _ajaxError: function (xhr, textStatus, errorThrown) {
            if (textStatus != 'abort') {
                log('error: ' + textStatus);
            }
        }


    });



    // wired from gridbox.pt panel
    // where it fills this.el markers from the template,
    // and wires events to actions.
    $.widget('popper.poppergridbox', {

        options: {
            //deleteUrl=...
            //moveToUrl=...
        },

        _create: function () {
            var self = this;

            // XXX Kept from ux1, needs replace.
            // create menu for move
            this.menuMove = $('<ul></ul>')
                .insertAfter(this.element)
                .hide()
                .width(250)
                .addClass('karl-gridbox-menu')  // a marker for css
                .css('max-height', '325px')
                .css('position', 'absolute')
                .css('overflow-x', 'hidden')
                .css('overflow-y', 'auto')
                .menu({
                    select: function (evt, selection) {
                        log('LOTETU here');
                        self.menuMove.hide();
                        var selected = selection.item;
                        if (selected) {
                            var targetFolderInfo = selected.data('folder');
                            self._onMoveSelected(evt, targetFolderInfo);
                        }
                    }
                });
                ////.popup();
            // XXX escape from the menu needs to be done manually,
            // this will arrive in jquery-ui 1.9 when this will not
            // be needed any longer (or it will simply break)
            this.menuMove.bind("keydown", function (evt) {
                if (self.menuMove.menu('option', 'disabled')) {
                    return;
                }
                if (evt.keyCode == $.ui.keyCode.ESCAPE) {
                    self.menuMove.hide();
                    evt.preventDefault();
                    evt.stopImmediatePropagation();
                }
            });
            $('body').bind("mousedown", function (evt) {
                if (self.menuMove.menu('option', 'disabled') ||
                    // escape if the menu is disabled
                    self.menuMove.is(':hidden') ||
                    // or if the menu is hidden
                    $(evt.target).is('.karl-gridbox-menu') ||
                    $(evt.target).is('.karl-gridbox-menu *')) {
                    // or if we are not outside the menu
                    return;
                }
                self.menuMove.hide();
                evt.preventDefault();
                evt.stopImmediatePropagation();
            });
            // XXX end of ux1 stuff


            // The widget does not finish the setup,
            // it has to be done from the create event.
        },

        deleteFiles: function (evt) {
            var self = this;
            var filenames = this.el.grid.poppergrid('getSelectedRowIds');
            if (filenames === false) {
                alert('You have selected more than 100 rows. Please select less rows.');
                return;
            }
            var ok = confirm('Are you sure you want to delete the ' +
                             'selected files and/or folders?');
            if (ok) {
                // Do the deletion.
                $.ajax({
                    url: this.options.deleteUrl,
                    type: 'POST',
                    dataType: 'json',
                    timeout: 20000,
                    data: {
                        file: filenames
                    },
                    success: function (data, textStatus, jqXHR) {
                        if (data && data.result == 'OK') {
                            self.deleteSuccess(data);
                        } else {
                            self.deleteError(data);
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        self.deleteError({result: 'ERROR', error: 'Unknown server error: ' + textStatus});
                    }
                });
            }
            
        },

        deleteSuccess: function (data) {
            var message = '' + data.deleted + ' file(s) succesfully deleted';
            alert(message);
            this.el.grid.poppergrid('clearData');
        },

        deleteError: function (data) {
            var message = 'Deletion failed: ' + data.error;
            alert(message);
        },

        moveFiles: function (evt) {
            var self = this;
            var filenames = this.el.grid.poppergrid('getSelectedRowIds');
            if (filenames === false) {
                alert('You have selected more than 100 rows. Please select less rows.');
                return;
            }

            // XXX Kept from ux1, needs replace.
            this.menuMove.show();
            this.menuMove.position({
                my: 'left bottom',
                at: 'left top',
                of: evt.target,
                collision: 'fit'
            });
            this.menuMove.focus();

        },
    

        // code copied for ux1, needs replace
        setTargetFolders: function (state) {
            if (state.targetFolders === undefined) {
                return;
            }
            var folders = state.targetFolders;
            var current_folder = state.currentFolder;
            // We assume that folders are sorted,
            // otherwise the containment stucture would not work nicely
            var self = this;
            this.menuMove.find('li').remove();
            function countSlashes(s) {
                var n = 0;
                var i;
                for (i = 1; i < s.length; i++) {
                    if (s.charAt(i) === "/") {
                        n++;
                    }
                }
                return n;
            }
            
            // XXX
            // ie chokes on a large number of folders, so we are limiting it for now
            var limit = ($.browser.msie ? Math.min(folders.length, 400) : folders.length);
            var i;
            for (i = 0; i < limit; i++) {
                var folder = folders[i];
                var folder_path = folder.path;
                var folder_title = folder.title;
                if (! folder_path || folder_path.charAt(0) != '/') {
                    throw new Error('Fatal error: folder path must start with a "/"');
                }
                var level;
                if (folder_path == '/') {
                    // special case, handle differently.
                    level = 0;
                } else {
                    if (folder_path && folder_path.charAt(folder_path.length - 1) == '/') {
                        throw new Error('Fatal error: folder path must not end with a "/"');
                    }
                    // The folder path is like /f1/f2/f3
                    // we want to produce leafFolder = f3, level = 2 from this.
                    //level = folder_path.match(/\//g).length - 1;
                    level = countSlashes(folder_path);
                }
                // create the item
                var item = $('<li></li>')
                    .css('textAlign', 'left')
                    .data('folder', folder)
                    .appendTo(self.menuMove);

                // create the label. If this is not the current folder, it will be an <a>.
                // If this is the target folder, it will be a <span>. Also in this case
                // it needs the appear in the results, but it should not be selectable.           
                var label;
                if (folder_path != current_folder) {
                    label = $('<a></a>');
                } else {
                    label = $('<span></span>');
                }
                label
                    .appendTo(item)
                    .text(folder_title)
                    .css('marginLeft', '' + (level * self.options.folderMenuIndent) + 'px');
            }
            window.midTime = (new Date()).valueOf();
            this.menuMove.menu('refresh');
        },

        _onMoveSelected: function (evt, targetFolderInfo) {
            log(targetFolderInfo);
            var self = this;
            var filenames = this.el.grid.poppergrid('getSelectedRowIds');
            if (filenames === false) {
                alert('You have selected more than 100 rows. Please select less rows.');
                return;
            }
            var ok = confirm('Are you sure you want to move these ' +
                             'selected files/folders to "' + targetFolderInfo.title + '"?');
            if (ok) {
                // Do the moving.
                $.ajax({
                    url: this.options.moveToUrl,
                    type: 'POST',
                    dataType: 'json',
                    timeout: 20000,
                    data: {
                        file: filenames,
                        target_folder: targetFolderInfo.path
                    },
                    success: function (data, textStatus, jqXHR) {
                        if (data && data.result == 'OK') {
                            self.moveToSuccess(data);
                        } else {
                            self.moveToError(data);
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        self.moveToError({result: 'ERROR', error: 'Unknown server error: ' + textStatus});
                    }
                });
            }
            
        },

        moveToSuccess: function (data) {
            var message = '' + data.moved + ' file(s) succesfully moved.';
            alert(message);
            this.el.grid.poppergrid('clearData');
        },

        moveToError: function (data) {
            var message = 'Moving files failed: ' + data.error;
            alert(message);
        }


    });


})(jQuery);
