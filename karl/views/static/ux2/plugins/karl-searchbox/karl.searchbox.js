
!function ($) {

    "use strict"; // jshint ;_;

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };
    

    /* PUBLIC CLASS DEFINITION
    * ======================== */

    var SearchBox = function (element, options) {
        element = $(element);
        this.init('slickgrid', element, options);
    };


    SearchBox.prototype = {

        constructor: SearchBox,

        init: function (type, element, options) {
            var self = this;
            this.element = $(element);
            this.options = options;

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
            //$panel.on('change', 'input[name="sb_staff_only"]',
            //    $.proxy(this._handleStaffOnly, this));
            //$panel.on('change', 'input[name="sb_past_year"]',
            //    $.proxy(this._handlePastYear, this));
            $panel.on('change', 'select[name="sb_scope"]',
                $.proxy(this._handleScope, this));

        },

        destroy: function () {
            this._resetTimer();
            this._abortRequest();
            var $panel = this.element.pushdownrenderer('getPanel');
            this.element.off('focus keyup');
            $panel.off('click', '.sb-close');
            //$panel.off('change', 'input[name="sb_staff_only"]');
            //$panel.off('change', 'input[name="sb_past_year"]');
            $panel.off('change', 'select[name="sb_scope"]');
            this.element.pushdownrenderer('destroy');
        },

        _getParameters: function () {
            // Return the search parameters needed
            // for all searches on this page
            var selectedScope;
            var selectedScopeLabel;
            var scopeOptions = this.options.scopeOptions || [];
            $.each(scopeOptions, function (index, item) {
                if (item.selected) {
                    selectedScope = item.value;
                    selectedScopeLabel = item.label;
                    return false;
                }
            });
            if (! selectedScope && scopeOptions.length > 0) {
                selectedScope = scopeOptions[0].value;
                selectedScopeLabel = scopeOptions[0].label;
            }

            // The search parameters that we use to render the mustache template.
            // These will be each time combined with the data that the server sends to us.
            var parameters = {
                scope: selectedScope,
                scopeLabel: selectedScopeLabel,
                //staffOnly: this.options.staffOnlyChecked,
                //pastYear: this.options.pastYearChecked,
                //
                // we never need to pass the followings to the server,
                // since they are provided by the server initially.
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
            var self = this;
            var val = $.trim(this.element.val());
            var length = val.length;
            this._resetTimer();
            if (length === 0) {
                this.element.pushdownrenderer('option', 'data', {});
                // detach in async to increase responsiveness of typing
                setTimeout(function () {
                    self.element.pushdownrenderer('render');
                }, 0);
            } else if (length < this.options.minLength) {
                this.element.pushdownrenderer('option', 'data', {
                    error: 'Please add more characters to: "' + val + '"'
                });
                // detach in async to increase responsiveness of typing
                setTimeout(function () {
                    self.element.pushdownrenderer('render');
                }, 0);
            } else {
                this.refresh();
            }
        },
        
        _refreshIfValidSearch: function () {
            // Refresh only if there are enough characters to search.
            var val = $.trim(this.element.val());
            var length = val.length;
            if (length >= this.options.minLength) {
                this.refresh();
            }
        },

        //_handleStaffOnly: function (evt) {
        //    var staffOnly = $(evt.target).is(':checked');
        //    if (staffOnly != this.parameters.staffOnly) {
        //        this.parameters.staffOnly = staffOnly;
        //        this.element.pushdownrenderer('option', 
        //            'defaultData', this.parameters);
        //        // Refresh the search, unless the input is too short.
        //        this._refreshIfValidSearch();
        //    }
        //},

        //_handlePastYear: function (evt) {
        //    var pastYear = $(evt.target).is(':checked');
        //    if (pastYear != this.parameters.pastYear) {
        //        this.parameters.pastYear = pastYear; 
        //        this.element.pushdownrenderer('option', 
        //            'defaultData', this.parameters);
        //        // Refresh the search, unless the input is too short.
        //        this._refreshIfValidSearch();
        //    }
        //},

        _handleScope: function (evt) {
            var self = this;
            var scope = $(evt.target).val();
            if (scope != this.parameters.scope) {
                this.parameters.scope = scope;
                this.element.pushdownrenderer('option', 
                    'defaultData', this.parameters);
                // We also need to update the scope options here,
                // which is used to re-render the panel.
                this.parameters.scopeOptions = this.options.scopeOptions || [];
                $.each(this.options.scopeOptions, function (index, item) {
                    item.selected = (item.path == scope);
                    if (item.selected) {
                        self.parameters.scopeLabel = item.label;
                    }
                });
                // Refresh the search, unless the input is too short.
                this._refreshIfValidSearch();
            }
        },

        refresh: function () {
            // Switch on the progress indicator, but keep the previous
            // content for a smoother transition to the update.
            var oldData = this.element.pushdownrenderer('option', 'data');
            var oldResults = oldData.results;
            if (oldResults) {
                oldResults.progress = true;
            }
            var oldError = oldData.error;
            this.element.pushdownrenderer('option', 'data', {
                progress: true,
                // Keep the previous content (or error).
                // This will make the transition to the next update nicer,
                // because we skip a short blip of emptiness in between.
                results: oldResults,
                error: oldError
            });
            // Doing finish in async, to increase responsiveness.
            this.timer = setTimeout(
                $.proxy(this._finishRefresh, this), this.options.delay);
        },

        _finishRefresh: function () {
            var val = $.trim(this.element.val()).toLowerCase();
            var parameters = this.parameters;
            
            this._abortRequest();
            this.req = $.ajax({
                url: this.options.url,
                type: 'GET',
                data: {
                    val:       val + '*',
                    // From parameters we pass only these,
                    // and ignore the scopeOptions.
                    scope:     parameters.scope
                    //staffOnly: parameters.staffOnly,
                    //pastYear:  parameters.pastYear
                },
                dataType: 'json'
            });
            this.req
                .done($.proxy(this._ajaxDone, this))
                .fail($.proxy(this._ajaxFail, this));
            
            // Finally, render.
            this.element.pushdownrenderer('render');
        },

        groupLabels: {
            profile: 'People',
            page: 'Wikis',
            post: 'Blogs',
            file: 'Files',
            community: 'Communities',
            calendarevent: 'Events'
        },

        columnOrder: [
            ['profile'],
            ['calendarevent', 'community'],
            ['page', 'post', 'file']
        ],

        _renderCalendarDate: function (isoDateString) {
            var d = $.timeago.parse(isoDateString);
            var minutes = "" + d.getMinutes();
            if (minutes.length === 1) {
                minutes = "0" + minutes;
            }
            return (d.getMonth() + 1) + '/' +
                   d.getDate() + '/' + d.getFullYear() + ' ' +
                   d.getHours() + ':' + minutes;
        },

        _convertData: function (data) {
            var self = this;
            // Convert the data from the format provided by the server,
            // into the format we need to render down the template.
            var groups = {};
            var scope = this.parameters.scope || '';
            var scopeLabel = this.parameters.scopeLabel || '';
            $.each(data, function (index, value) {
                var category = value.category;
                var type = value.type;
                // Store the item into its group
                var group = groups[type];
                if (group === undefined) {
                    // Make group label capitalized and plural.
                    var label = self.groupLabels[type];
                    // Calculate the Full Search link for this group.
                    var urlFullSearch = self.options.urlResults + '?' + $.param({
                        body: $.trim(self.element.val()).toLowerCase(),
                        type: type,
                        scopePath: scope,
                        scopeLabel: scopeLabel
                    });
                    // Initialize a new group.
                    group = groups[type] = {
                        category: category,
                        label: label,
                        urlShowMore: '#',
                        urlFullSearch: urlFullSearch,
                        items: []
                    };        
                }
                // Additional data needed for rendering the logic-less template.
                if (value.num_numbers !== undefined) {
                    // for category = 'community'
                    value.num_numbers_plural = (value.num_members === 1 ? 
                                                    '' : 's');
                }
                if (value.modified !== undefined) {
                    // Readable date.
                    value.modified_ago = $.timeago(value.modified);
                }
                if (value.category == 'calendarevent') {
                    // Event's date format. Taken from ux1 without revision.
                    value.start_fmt = self._renderCalendarDate(value.start);
                    value.end_fmt = self._renderCalendarDate(value.end);
                }
                // Add this record.
                var item = {};
                item[category] = value;
                group.items.push(item);
            });

            // Arrange columns into the format required
            // by the mustache template
            var columns = [];
            $.each(self.columnOrder, function (columnIndex, columnValue) {
                var column = [];
                $.each(columnValue, function (index, value) {
                    var groupValue = groups[value];
                    if (groupValue !== undefined) {
                        column.push(groupValue);
                    }
                });
                columns.push({groups: column});
            });
            return columns;
        },

        _ajaxDone: function (data) {
            var columns = this._convertData(data);
            this.element.pushdownrenderer('option', 'data', {
                results: {columns: columns}
            });
            this.element.pushdownrenderer('render');
        },

        _ajaxFail: function (jqXHR, textStatus) {
            if (textStatus != 'aborted') {
                log('FAIL', textStatus);
                this.element.pushdownrenderer('option', 'data', {
                    error: 'Server error: ' + textStatus + ''
                });
                this.element.pushdownrenderer('render');
            }
        }

    };


    /* PLUGIN DEFINITION */

    $.fn.searchbox = function (option) {
        return this.each(function () {
            var $this = $(this),
                data = $this.data('searchbox'),
                options = typeof option == 'object' && option;
            if (!data) {
                $this.data('searchbox', (data = new SearchBox(this, options)));
            }
            if (typeof option == 'string') {
                data[option]();
            }
        });
    };

    $.fn.searchbox.Constructor = SearchBox;

    $.fn.searchbox.defaults = {
        //selectTopBar: null,   // pushdown inserted under this element
        delay: 0,               // time to wait before processing a key
        minLength: 0,           // minimum number of characters
                                // to trigger a search
        //url: null,            // url to query for search results
        //urlResults: null,     // url for static results (searchresults.html)
        scopeOptions: {},
        staffOnlyChecked: false,
        pastYearChecked: false
    };


}(window.jQuery);

