
/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */
/*globals window navigator document console */
/*globals setTimeout clearTimeout setInterval */ 
/*globals jQuery Mustache */


(function ($) {

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };
    
    $.widget('karl.searchbox', {

        options: {
            //selectTopBar: null,   // pushdown inserted under this element
            delay: 0,               // time to wait before processing a key
            minLength: 0,           // minimum number of characters
                                    // to trigger a search
            //url: null,            // url to query for search results
            scopeOptions: {},
            staffOnlyChecked: false,
            pastYearChecked: false
        },

        _create: function () {
            var self = this;

            this.parameters = this._getParameters();

            this.element
                .pushdownrenderer({
                    name: 'searchbox',
                    selectTopBar: this.options.selectTopBar,
                    data: {},
                    defaultData: this.parameters
                    //createpanel: $.proxy(this._handleCreatePanel, this)
                })
                .pushdownrenderer('render')
                .on({
                    focus:  $.proxy(this._handleFocus, this),
                    keyup:  $.proxy(this._handleKeyUp, this)
                });

            this.timer = null;
            this.req = null;

            // bind actions to the panel
            var $panel = this.element.pushdownrenderer('getPanel');
            $panel.on('click', '.sb-close',
                $.proxy(this._handleHidePanel, this));
            $panel.on('click', 'input[name="sb_staff_only"]',
                $.proxy(this._handleStaffOnly, this));
            $panel.on('click', 'input[name="sb_past_year"]',
                $.proxy(this._handlePastYear, this));
            $panel.on('change', 'select[name="sb_scope"]',
                $.proxy(this._handleScope, this));

        },

        _destroy: function () {
            this._resetTimer();
            this._abortRequest();
            var $panel = this.element.pushdownrenderer('getPanel');
            this.element.off('focus keyup');
            $panel.off('click', '.sb-close');
            $panel.off('click', 'input[name="sb_staff_only"]');
            $panel.off('click', 'input[name="sb_past_year"]');
            $panel.off('change', 'select[name="sb_scope"]');
            this.element.pushdownrenderer('destroy');
        },

        _getParameters: function () {
            // Return the search parameters needed
            // for all searches on this page
            var selectedScope;
            var scopeOptions = this.options.scopeOptions;
            $.each(scopeOptions, function (index, item) {
                if (item.selected) {
                    selectedScope = item.value;
                    return false;
                }
            });
            if (! selectedScope && scopeOptions.length > 0) {
                selectedScope = scopeOptions[0].name;
            }

            // The search parameters to be passed to the server
            var parameters = {
                scope: selectedScope,
                staffOnly: this.options.staffOnlyChecked,
                pastYear: this.options.pastYearChecked,
                // we don't pass scopeOptions to the server,
                // but the renderer needs this data for the template.
                scopeOptions: this.options.scopeOptions    

            };
            return parameters;
        },

        _resetTimer: function () {
            if (this.timer) {
                clearTimeout(this.timer);
                this.timer = null;
            }
        },

        _abortRequest: function () {
            if (this.req) {
                this.req.abort();
                this.req = null;
            }
        },

        //_handleCreatePanel: function (evt, info) {
        //    var panel = info.panel;
        //    ...
        //},

        _handleHidePanel: function (evt) {
            this.element.pushdownrenderer('hide');
        },

        _handleFocus: function (evt) {
            this.element.pushdownrenderer('show');
        },

        _handleKeyUp: function (evt) {
            var val = this.element.val();
            var length = val.length;
            this._resetTimer();
            if (length === 0) {
                this.element.pushdownrenderer('option', 'data', {});
            } else if (length < this.options.minLength) {
                this.element.pushdownrenderer('option', 'data', {
                    error: 'Please add more characters to: "' + val + '"'
                });
            } else {
                this.element.pushdownrenderer('option', 'data', {
                    progress: true
                });
                this.timer = setTimeout(
                    $.proxy(this._finishRefresh, this), this.options.delay);
            }
            this.element.pushdownrenderer('render');
        },

        _handleStaffOnly: function (evt) {
            var staffOnly = $(evt.target).is(':checked');
            if (staffOnly != this.parameters.staffOnly) {
                this.parameters.staffOnly = staffOnly;
                this.element.pushdownrenderer('option', 
                    'defaultData', this.parameters);
                // Refresh the search.
                this.refresh();
            }
        },

        _handlePastYear: function (evt) {
            var pastYear = $(evt.target).is(':checked');
            if (pastYear != this.options.pastYear) {
                this.parameters.pastYear = pastYear; 
                this.element.pushdownrenderer('option', 
                    'defaultData', this.parameters);
                // Refresh the search.
                this.refresh();
            }
        },

        _handleScope: function (evt) {
            var scope = $(evt.target).val();
            if (scope != this.parameters.scope) {
                this.parameters.scope = scope;
                this.element.pushdownrenderer('option', 
                    'defaultData', this.parameters);
                // We also need to update the scope options here,
                // which is used to re-render the panel.
                $.each(this.options.scopeOptions, function (index, item) {
                    item.selected = item.path == scope;
                });
                // Refresh the search.
                this.refresh();
            }
        },

        refresh: function () {
            // Switch on the progress indicator.
            this.element.pushdownrenderer('option', 'data', {
                progress: true
            });
            this.element.pushdownrenderer('render');
            this._finishRefresh();
        },

        _finishRefresh: function () {
            var val = this.element.val();
            var parameters = this.parameters;
            
            this._abortRequest();
            this.req = $.ajax({
                url: this.options.url,
                type: 'GET',
                data: {
                    val:       val + '*',
                    // From parameters we pass only these,
                    // and ignore the scopeOptions.
                    scope:     parameters.scope,
                    staffOnly: parameters.staffOnly,
                    pastYear:  parameters.pastYear
                },
                dataType: 'json'
            });
            this.req
                .done($.proxy(this._ajaxDone, this))
                .fail($.proxy(this._ajaxFail, this));
        },

        _convertData: function (data) {
            // Convert the data from the format provided by the server,
            // into the format we need to render down the template.
            
            var groups = {};
            $.each(data, function (index, value) {
                var category = value.category;
                var group = groups[category];
                if (group === undefined) {
                    // Initialize a new group.
                    var label = category.substr(0, 1).toUpperCase() +
                            category.substr(1).toLowerCase();
                    group = groups[category] = {
                        category: category,
                        label: label,
                        urlShowMore: '#',
                        urlFullSearch: '#',
                        items: []
                    };        
                }
                // Add this record.
                group.items.push(value);
            });

            var columns = {
                column1: {
                    groups: []
                },
                column2: {
                    groups: []
                },
                column3: {
                    groups: []
                }
            };
            $.each(['people'], function (index, value) {
                var group = groups[value];
                if (group !== undefined) {
                    columns.column1.groups.push(group);
                }
            });
            $.each(['calendarevent', 'community'],
                                                    function (index, value) {
                var group = groups[value];
                if (group !== undefined) {
                    columns.column2.groups.push(group);
                }
            });
            $.each(['page', 'post', 'file'],
                                                    function (index, value) {
                var group = groups[value];
                if (group !== undefined) {
                    columns.column3.groups.push(group);
                }
            });

            log('COLUMNS', columns);
            return columns;
        },

        _ajaxDone: function (data) {

            var columns = this._convertData(data);

            this.element.pushdownrenderer('option', 'data', {
                goat: columns
            });
            this.element.pushdownrenderer('render');
        },

        _ajaxFail: function (jqXHR, textStatus) {
            log('FAIL', textStatus);
            this.element.pushdownrenderer('option', 'data', {
                error: 'Server error: ' + textStatus + ''
            });
            this.element.pushdownrenderer('render');
        }


    });


})(jQuery);
