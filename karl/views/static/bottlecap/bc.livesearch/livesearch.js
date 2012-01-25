(function($) {

// A console.log replacement that works on all browsers
// // If the browser does not have a console, it's silent
//
// usage: log('This happened.');
// or:    log('Variables:', var1, var2, var3);
//
var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

$.widget("bottlecap.livesearch", {

    options: {
        // function to call for ajax url request
        // scope is set to this widget
        urlFn: null,
        // function to call to render items from ajax request
        renderCompletions: null,
        // to transform the query before the ajax call
        queryTransformFn: null,
        // validation to run before the query is transformed
        validationFn: null,
        // display an error to the user if validation fails
        errorFn: null,
        // called when there is an ajax error
        ajaxErrorFn: null,
        // called when an item is selected from the list
        selectedFn: null,
        // name of cookie to save context menu search under
        cookieName: 'bottlecap.livesearch.searchType'
    },

    _create: function () {
        var el = this.element,
             o = this.options;

        // store state on plugin widget itself
        this.urlFn = o.urlFn;
        this.transformQuery = (o.queryTransformFn ||
                               function(query) { return query; });
        this.validateFn = o.validationFn || function() { return true; };
        this.errorFn = o.errorFn || function() {};
        this.ajaxErrorFn = o.ajaxErrorFn ? o.ajaxErrorFn : this._ajaxErrorFn;
        this.ajaxManager = $.manageAjax.create(
            'livesearch',
            {queue: true, cacheResponse: true}
        );
        this.cookieName = o.cookieName;
        this.cookieValue = $.cookie(o.cookieName);

        // store references to elements
        this.selectList = el.prev('ul').first();
        this.selectButton = this.selectList.prev('button').first();
        this.searchButton = el.next('button').first();

        // set up select button behavior
        this.selectButton.button({
            icons: {secondary: "ui-icon-triangle-1-s"}
        });
        this.selectButtonText = this.selectButton.find('.ui-button-text');
        this.selectList.menu({
            select: $.proxy(this.menuSelected, this),
            input: this.selectList
        }).hide();
        this.selectButton.click($.proxy(this.selectButtonClicked, this));
        this.selectList.click($.proxy(this.selectButtonClicked, this));

        // set up auto complete behavior
        el.autocomplete({
            delay: 300,
            minLength: 0,
            source: $.proxy(this.queryData, this),
            search: $.proxy(this.validateAndHandleError, this),
            position: {
                my: "right top",
                at: "right bottom",
                of: this.searchButton,
                collision: "none"
            },
            select: $.proxy(this.completionSelected, this)
        });
        this.autoCompleteWidget = el.data('autocomplete');
        this.autoCompleteWidget.menu.element
            .addClass('bc-livesearch-autocomplete-results');

        // if user pastes from mouse, also trigger a search
        el.bind('paste', $.proxy(this.textPasted, this));

        // plug in rendering function when results come in
        // first save the default
        this._defaultRenderCompletions = this.autoCompleteWidget._renderMenu;
        if (typeof o.renderCompletions === 'function') {
            this.autoCompleteWidget._renderMenu = o.renderCompletions;
        }

        // search handlers
        // this one is if somebody clicks on the search icon
        this.searchButton.click($.proxy(this.searchButtonClicked, this));
        // this one is if somebody hits the enter key on the keyboard
        el.bind('keydown.autocomplete', $.proxy(this.keyPressed, this));

        // Initialize selected search type
        var searchType = 'all_content';
        if (this.cookieValue) {
            // if the cookie exists, we need to select the appropriate
            // category in the context menu
            searchType = this.cookieValue;
        }
        var liNodes = this.selectList.find('li');
        var liArray = $.makeArray(liNodes);
        for (var i = 0; i < liArray.length; i++) {
            var li = $(liArray[i]);
            if (this.get_option_name(li) === searchType) {
                var dontSaveCookie = true;
                this.menuSelected(0, {item: li}, dontSaveCookie);
                break;
            }
        }

        // Set the magnifying glass button on the right
        this.searchButton.button({
            text: false,
            icons: {primary: "ui-icon-search"}
        });

        // add in classes on appropriate elements
        el.addClass('bc-livesearch bc-livesearch-autocomplete');
        this.selectList.addClass('bc-livesearch bc-livesearch-menu');
        this.selectButton.addClass(
            'bc-livesearch bc-livesearch-btn bc-livesearch-btn-select');
        this.searchButton.addClass(
            'bc-livesearch bc-livesearch-btn bc-livesearch-btn-search');

        // dynamically set height to match
        var height = this.selectButton.outerHeight();
        var wrapper = $('<span></span>');
        wrapper
            .css('display', 'inline-block')
            .css('margin', '0')
            .css('padding', '0')
            .css('border', '0')
            .css('height', height +'px')
            .css('verticalAlign', 'top');
        el
            .wrap(wrapper)
            .css('margin', '0')
            .css('padding', '0 3px')
            .css('height', '' + (height - 2) + 'px')
            .css('lineHeight', '' + (height - 2) + 'px');

        var marginTop = this.selectButton.css('marginTop');
        // this  is essential _sometimes_ on WebKit
        el.css('marginTop', marginTop);
        // hack IE7 that handles top margin differently
        if ($.browser.msie && parseInt($.browser.version) == 7) {
            this.selectButton.css('marginTop', '1px');
        }
    },

    // called when a particular category menu item is selected from the ul
    menuSelected: function(event, ui, dontSaveCookie) {
        var item = ui.item,
            text = item.text();

        this.selectButtonText.text(text);

        // store the selection in the cookie this function is also
        // called initially to populate the right selection so we
        // don't want to resave the cookie at that point
        if (!dontSaveCookie) {
            this.cookieValue = this.get_option_name(item);
            $.cookie(this.cookieName, this.cookieValue, {path: "/"});
        }

        this.selected_item = {
            item: item,
            text: text,
            name: this.get_option_name(item)
        };
        this._trigger('menu', 0, this.selected_item);

        // when the menu changes, we should also trigger a search
        var searchText = this.element.val();
        if (searchText) {
            // this should trigger the entire search, beginning with
            // the ajax query
            this.autoCompleteWidget.search();
            // focus the element to rely on the widget's blur handler
            // to fix menus and interaction properly
            this.element.focus();
        }
    },

    selectButtonClicked: function() {
        var menu = this.selectList;
        if (menu.is(":visible")) {
            menu.hide();
            return false;
        }
        menu.menu("deactivate").show().css({top:0, left:0}).position({
            my: "left top",
            at: "left bottom",
            of: this.selectButton
        });
        $(document).one("click", function() {
            menu.hide();
        });
        return false;
    },

    completionSelected: function(event, ui) {
        var item = ui.item;
        if (this._trigger('selectedFn', event, item) !== false) {
            this.performSearch(item.label || '');
        }
    },

    _findGlobPosition: function(query, caretPosition) {
        var length = query.length,
            pos = -1;

        // go to the end of the current word
        for (pos = caretPosition; pos < length; pos++) {
            if (query.charAt(pos) === " ") {
                break;
            }
        }
        // if we are right after some whitespace, then we return -1
        // which signals that we don't want to add a glob
        return (pos == 0 || query.charAt(pos-1) === " ")
               ? -1
               : pos;
    },

    // add a * for globbing to the query where the cursor is
    globQueryTransform: function(query) {
        var caretPosition = this.element.caret().start;
        var pos = this._findGlobPosition(query, caretPosition);
        if (pos !== -1) {
            query = query.substring(0, pos) + "*" + query.substring(pos);
            // normalize spaces
            query = query.replace(/\s+/, ' ');
        }
        query = $.trim(query);
        return query;
    },

    // validate that the word the cursor is on has at least 3 characters
    numCharsValidate: function(query, nChars) {
        nChars = nChars || 3;
        if (query.length < nChars) {
            return false;
        }
        var caretPosition = this.element.caret().start;
        var pos = this._findGlobPosition(query, caretPosition);
        if (pos === -1) {
            return $.trim(query).length >= nChars;
        }
        if (pos < nChars) {
            return false;
        }
        for (var i = 0; i < nChars; i++) {
            if (query.charAt(pos-1-i) === " ") {
                return false;
            }
        }
        return true;
    },

    validateAndHandleError: function(event) {
        var query = this.element.val();
        if (this.validateFn(query)) {
            this.errorFn.call(this, null);
            return true;
        } else {
            // ensure results box is closed first on error
            this.autoCompleteWidget.close();

            this.errorFn.call(this, query);
            return false;
        }
    },

    errorDisplayer: function() {
        if (!this._errorDisplayer) {
            var self = this;
            this._errorDisplayer = (function() {
                var msg = $('<span></span>')
                    .addClass('bc-livesearch-autocomplete-message');
                // A box, hidden initially, to show error messages such as
                // "you didn't type enough characters"
                var width = (self.element.outerWidth() +
                             self.searchButton.outerWidth() - 2);
                var errorBox = $(
                    '<div><span class="bc-livesearch-autocomplete-msgicon ' +
                        'ui-icon ui-icon-info"></span>' +
                        '</div>')
                .append(msg)
                .addClass(
                    'bc-livesearch-autocomplete-notification ui-state-error'
                    + ' ui-icon-notice')
                .width(width)
                .appendTo('.bc-header')
                .position({
                    my: "right top",
                    at: "right bottom",
                    of: $('.bc-header-toolbox')
                });
                // expose functions to show/hide the error box
                return {
                    hide: function() { errorBox.hide(); },
                    show: function(text) {
                        if (text) {
                            msg.text(text);
                        }
                        errorBox.show();
                    },
                    replaceWith: function(replacement) {
                        msg.replaceWith(replacement);
                        msg = replacement;
                        errorBox.show();
                    }
                };
            })();
        }
        return this._errorDisplayer;
    },

    displayError: function(err) {
        var displayer = this.errorDisplayer();

        if (err === null) {
            // an err of null signals that we should clear the error message
            displayer.hide();
        } else {
            var caretPosition = this.element.caret().start,
                query = err,
                pos = this._findGlobPosition(query, caretPosition);
            if (pos === -1) {
                if ($.trim(query).length === 0) {
                    displayer.hide();
                } else {
                    // cursor is after whitespace,
                    // but we don't have enough characters
                    displayer.show('not enough characters entered');
                }
            } else {
                // find the offending substring that failed validation
                var nChars = 3,
                    startPos = 0;
                for (var i = 0; i < nChars; i++) {
                    if (query.charAt(pos-1-i) === " ") {
                        startPos = pos-i;
                        break;
                    }
                }
                var errorSubstring = query.substring(startPos, pos);
                displayer.show('Please add more characters to: "' +
                               errorSubstring + '"');
            }
        }
    },

    _ajaxErrorFn: function(xhr, status, exc) {
        log('bc.livesearch', status);
    },

    queryData: function(request, response) {
        var query = this.transformQuery(request.term),
            url = this.urlFn.call(this, query),
            self = this;

        $.manageAjax.add(
            'livesearch',
            {url: url,
             dataType: 'json',
             maxRequests: 1,
             queue: 'clear',
             abortOld: true,
             success: function(data) {
                 // ensure that the context menu isn't displayed when
                 // showing completion results
                 self.selectList.hide();
                 // always call response - on no data it cleans up properly
                 response(data);
                 if (!data || !data.length) {
                     self._trigger('noresults', 0,
                                   {query: query, url: url, el: self});
                 }
             },
             error: function (xhr, status, exc) {
                 // call response with no data to clean up loading state
                 response();
                 self.ajaxErrorFn.apply(self, arguments);
             }
        });
    },

    searchButtonClicked: function() {
        var val = this.transformQuery(this.element.val());
        this.performSearch(val);
        return false;
    },

    textPasted: function(e) {
        // we need to use set timeout to capture the pasted text
        // the text field doesn't contain the pasted text before the timeout
        // and the event object doesn't contain it
        setTimeout($.proxy(function() {
            this.autoCompleteWidget.search();
        }, this), 0);
    },

    keyPressed: function(e) {
        // In the case when an element is highlighted in the
        // suggestion dropdown and enter is pressed, this event gets
        // fired as well, but after the auto complete handler. If that
        // handler is called, it prevents the default action, in which
        // case we want to ignore our search handler.
        if (!e.isDefaultPrevented() &&
            (e.keyCode === $.ui.keyCode.ENTER ||
             e.keyCode === $.ui.keyCode.NUMPAD_ENTER)) {
            // close the selections first if necessary
            this.autoCompleteWidget.close();

            var val = this.transformQuery(this.element.val());
            this.performSearch(val);
            return false;
        }
        return true;
    },

    performSearch: function(query) {
        this._trigger('search', 0, {query: query, item: this.selected_item});
    },

    _setOption: function(key, value) {
        if (key === 'urlFn') {
            this.urlFn = value;
        } else if (key === 'renderCompletions') {
            if (typeof value === 'function') {
                this.autoCompleteWidget._renderMenu = value;
            } else if (value === 'default') {
                this.autoCompleteWidget._renderMenu = this._defaultRenderCompletions;
            }
        }
    },

    get_option_name: function(item) {
        var name = item.attr('name');
        if (typeof name == 'undefined') {
            name = item.text();
        }
        return name;
    }
});

})(jQuery);
