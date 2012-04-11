(function($) {

// A console.log replacement that works on all browsers
// usage: log('This happened.');
// or:    log('Variables:', var1, var2, var3);
var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


// XXX Don't use this widget directly, use popper.livesearch
// that is defined below.

$.widget("popper.livesearchcore", {

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
        cookieName: 'popper.livesearch.searchType'
        // positioning of the results. If omitted, current element used.
        //position: null
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

        // Default position option (not in default options
        // but here, because it contains this.element)
        this.options.position = this.options.position || {
            my: 'right top',
            at: 'right bottom',
            of: this.element,
            collision: 'none'
        };

        // set up auto complete behavior
        el.autocomplete({
            delay: 300,
            minLength: 0,
            source: $.proxy(this.queryData, this),
            search: $.proxy(this.validateAndHandleError, this),
            position: this.options.position,
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
        ///if (typeof o.renderCompletions === 'function') {
        if (o.renderCompletions) {
            this.autoCompleteWidget._renderMenu = o.renderCompletions;
        }

        // search handlers
        // this one is if somebody hits the enter key on the keyboard
        el.bind('keydown.autocomplete', $.proxy(this.keyPressed, this));

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
        return (pos === 0 || query.charAt(pos-1) === " ") ? -1
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
        for (i = 0; i < nChars; i++) {
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
                //
                // ... hmmm, a bit shaky, but let's use the positioning
                // element's width. If this causes a headache: then let's
                // get rid of it, and just set the width from css?
                var width = $(self.options.position.of).outerWidth() - 2;

                var errorBox = $(
                    '<div><span class="bc-livesearch-autocomplete-msgicon ' +
                        'ui-icon ui-icon-info"></span>' +
                        '</div>')
                .append(msg)
                .addClass(
                    'bc-livesearch-autocomplete-notification ui-state-error' +
                    ' ui-icon-notice')
                .width(width)
                .appendTo('body')
                .position(self.options.position);
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
                for (i = 0; i < nChars; i++) {
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
        log('popper.livesearch', status);
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
            //if (typeof value === 'function') {
            if (value) {
                this.autoCompleteWidget._renderMenu = value;
            } else {
                this.autoCompleteWidget._renderMenu = this._defaultRenderCompletions;    
            }
            //} else if (value === 'default') {
            //    this.autoCompleteWidget._renderMenu = this._defaultRenderCompletions;
            //}
        }
        $.Widget.prototype._setOption.apply(this, arguments);
    },

    get_option_name: function(item) {
        var name = item.attr('name');
        if (typeof name == 'undefined') {
            name = item.text();
        }
        return name;
    }
});



//
// -- -- -- -- --
// here comes the extension of the core widget
// into a full blown KARL livesearch:
//


function lookup_type(name) {
    var types = {
        profile: {name: "people", title: "People"},
        page: {name: "wiki", title: "Wikis"},
        post: {name: "blog", title: "Blogs"},
        file: {name: "files", title: "Files"},
        community: {name: "communities", title: "Communities"},
        calendarevent: {name: "events", title: "Events"}
    };
    return types[name] || {name: null, title: null};
    /*
    var type = types[name];
    if (type === undefined) {
        type = {name: null, title: null};
    }
    return type;
    */
}


// while waiting for data to return, if a search is triggered, like if
// the user presses return or clicks on the search button, the ajax
// query gets cancelled and triggers an error. We use this flag to
// suppress displaying the error in that situation
var shouldDisplayError = true;

function ajaxError(xhr, status, exc) {
    var errDisplayer = this.errorDisplayer();
    if (errDisplayer && shouldDisplayError) {
        errDisplayer.show('We encountered an error. Please try your search again ... and contact a KARL admin if the problem persists.');
    }
}

function renderDate(isoDateString) {
    return $.timeago(isoDateString);
}

function _normalized(val) {
    // the server can return None or null
    // treat these values as empty
    return !val || val === "None" || val === "null" ? ''
           : val;
}

function renderPersonEntry(item) {
    var entry = $('<a class="bc-livesearch-profile" />');
    var titleDiv = $('<div />').append($('<span />').text(item.title));
    if (_normalized(item.department)) {
        titleDiv.append($('<span class="discreet" />').text(
            " - " + item.department));
    }
    var contactDiv = $('<div />');
    if (_normalized($.trim(item.extension))) {
        contactDiv.append($('<span class="extension" />')
                              .text('x' + item.extension));
    }
    if (_normalized(item.email)) {
        contactDiv.append(
            $('<a class="email" />')
                .attr('href', 'mailto:' + item.email)
                .text(item.email)
                .click(function() {
                    window.location = $(this).attr('href');
                    return false;
                }));
    }
    entry
        .append($('<img />')
                     .attr('src', item.thumbnail))
        .append(titleDiv)
        .append(contactDiv);
    return entry;
}

function renderGenericEntry(item) {
    return $("<a></a>").text(item.title);
}

function _meta_text(author, date) {
    // helper to generate the meta byline
    var authorText = _normalized(author) ?
        ' - by ' + author + ' ' : ' - ';
    return authorText + renderDate(date);
}

function renderPageEntry(item) {
    var entry = $('<a class="bc-livesearch-page" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    _meta_text(item.modified_by, item.modified)))
                .append($('<div class="discreet" />').text(
                    _normalized(item.community))));
    return entry;
}

function renderBlogEntry(item) {
    var entry = $('<a class="bc-livesearch-blog" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    _meta_text(item.modified_by, item.modified)))
        .append($('<div class="discreet" />').text(_normalized(
            item.community))));
    return entry;
}

function renderForumEntry(item) {
    var entry = $('<a class="bc-livesearch-forum" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    _meta_text(item.creator, item.created))));
    return entry;
}

function renderForumTopicEntry(item) {
    var entry = $('<a class="bc-livesearch-forumtopic" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    _meta_text(item.creator, item.created))))
        .append($('<div class="discreet" />').append(item.forum));
    return entry;
}

function renderCommentEntry(item) {
    var entry = $('<a class="bc-livesearch-comment" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    _meta_text(item.creator, item.created))))
        .append($('<div class="discreet" />').text(
            _normalized(item.blog) ||
            _normalized(item.forum) ||
            _normalized(item.community)));
    return entry;
}

function renderFileEntry(item) {
    var entry = $('<a class="bc-livesearch-file" />');
    entry
        .append($('<img class="icon" />')
                .attr('src', item.icon))
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    _meta_text(item.modified_by, item.modified))))
        .append(
            $('<div class="discreet" />').text(_normalized(item.community)));
    return entry;
}

function _renderCalendarDate(isoDateString) {
    var d = $.timeago.parse(isoDateString);
    var minutes = "" + d.getMinutes();
    if (minutes.length === 1) {
        minutes = "0" + minutes;
    }
    return (d.getMonth()+1) + '/' + d.getDate() + '/' + d.getFullYear() + ' ' +
           d.getHours() + ':' + minutes;
}

function renderCalendarEventEntry(item) {
    var entry = $('<a class="bc-livesearch-calendarevent" />');
    var titleDiv = $('<div />').text(item.title);
    if (_normalized(item.location)) {
        titleDiv.append($('<span class="discreet" />')
                            .text(' - at ' + item.location));
    }
    entry
        .append(titleDiv)
        .append($('<div class="discreet" />').text(
            _renderCalendarDate(item.start) + ' -> ' +
            _renderCalendarDate(item.end)))
        .append($('<div class="discreet" />').text(
            _normalized(item.community)));
    return entry;
}

function renderCommunity(item) {
    var entry = $('<a class="bc-livesearch-community" />');
    entry
        .append($('<div />').text(item.title)
                    .append($('<span class="discreet" />')
                                .text(" - " + item.num_members + " member" +
                                      (item.num_members === 1 ? '' : 's'))));
    return entry;
}

function renderOffice(item) {
    var entry = $('<a class="bc-livesearch-office" />');
    function joinElements(elts) {
        var nonnulls = $.grep(elts, function(x) { return x !== null; });
        return nonnulls.join(', ');
    }
    entry
        .append($('<div />')
                .text(item.title + ' Office')
                .append($('<span class="discreet telephone" />')
                        .text(item.telephone))
                .append($('<div class="discreet" />').text(item.address))
                .append($('<div class="discreet" />').text(joinElements([item.city, item.state])))
                .append($('<div class="discreet" />').text(item.zipcode)));
    return entry;
}

function renderItem(ul, item) {
    // Render different items in different ways
    // dispatch based on the category of the item
    var category = item.category,
        renderFn = renderDispatchTable[category] || renderGenericEntry,
        entry    = renderFn(item);
    return $("<li></li>")
        .data("item.autocomplete", item)
        .append(entry)
        .appendTo(ul);
}

var renderDispatchTable = {
    "profile":       renderPersonEntry,
    "page":          renderPageEntry,
    "reference":     renderPageEntry,
    "blogentry":     renderBlogEntry,
    "forum":         renderForumEntry,
    "forumtopic":    renderForumTopicEntry,
    "comment":       renderCommentEntry,
    "file":          renderFileEntry,
    "calendarevent": renderCalendarEventEntry,
    "community":     renderCommunity,
    "office":        renderOffice
};


// --
// Create a component that wraps and hides all
// the extension code above,
// and only exposes the options that we really
// want to set in any of our use cases.
// It is really just a wrapper to allow a nicer,
// cleaner usage of the livesearchcore component
// and the complex KARL wrapping around it.
// --

// XXX this is the widget that you have to use:

$.widget('popper.livesearch', {

    options: {
        appUrl: null,
        livesearchMethod: null,
        advancedSearchMethod: null,
        kind: '',
        scopePath: '', 
        scopeLabel: 'all KARL'
        //position: null,    // positioning of the results. 
                             // If omitted, current element used.
        //resetFilters: function(evt) {...}  // application must
                             // reset the filter visuals
    },

    _create: function () {
        var self = this;

        $('.search-site-box').livesearchcore({
            urlFn: $.proxy(self.getLivesearchUrl, self),
            search: function(event, ui) {
                var searchText = $.trim(self.element.val());
                // in ie, the globbed character can be in the wrong place
                // we'll always just grab it from the field and put it on the end

                // suppress error displaying when searching
                // we don't have to worry about toggling it back
                // because we are loading a new page
                shouldDisplayError = false;
                window.location = self.getAdvancedSearchUrl(searchText);
            },
            validationFn: $.popper.livesearchcore.prototype.numCharsValidate,
            queryTransformFn: $.popper.livesearchcore.prototype.globQueryTransform,
            errorFn: $.popper.livesearchcore.prototype.displayError,
            ajaxErrorFn: ajaxError,
            selectedFn: function(event, item) {
                if (item.url) {
                    window.location = item.url;
                    return false;
                }
                return true;
            },
            renderCompletions: $.proxy(self._renderCompletions, self),
            noresults: $.proxy(self._noResults, self),
            position: self.options.position
        });

    },

    searchButtonClicked: function(evt) {
        this.element.livesearchcore('searchButtonClicked');
    },

    _setOption: function(key, value) {
        if (key == 'kind' || key == 'scopePath' || 
                 key == 'scopeLabel') {
            // XXX TODO Must reset all caches here!!!
        }
        $.Widget.prototype._setOption.apply(this, arguments);
    },


    // --
    // private parts
    //
    // (it would be desirable to move all the class-less functions,
    // from above, to here, as class methods. Still,
    // we only move here what we must, in order to
    // make them accept our wiring parameters.)
    // --

    getLivesearchUrl: function(query) {
        var url = this.options.appUrl + this.options.scopePath + 
                '/' + this.options.livesearchMethod;
        var p = $.param({
            val: $.trim(query),
            kind: this.options.kind
        });
        if (p) {
            url += '?' + p;
        }
        return url;
    },

    getAdvancedSearchUrl: function(query, /*optional*/ kind) {
        var url = this.options.appUrl + this.options.scopePath + 
                '/' + this.options.advancedSearchMethod;
        if (kind === undefined) {
            // If the kind is not defined (we come through
            // clicking search button), then we will use
            // the current selection.
            kind = this.options.kind;
        }
        var p = $.param({
            body: $.trim(query),
            kind: kind,
            scopePath: this.options.scopePath,
            // A verbose label is needed to display 
            // in the advanced search results
            scopeLabel: this.options.scopeLabel
        });
        if (p) {
            url += '?' + p;
        }
        return url;
    },

    _noResults: function(event, item) {
        var self = this;
        var el = item.el;
        var displayer = el.errorDisplayer();
        var query  = item.query.replace('*', '');
        var msg = $('<span />').text('No results found. ');
        if (this.options.kind) {   // the default value is the empty string.
            msg
                .append('Try searching in ')
                .append($('<a />')
                        .attr('href', '#')
                        .attr('class', 'bc-livesearch-all-content')
                        .text('All Content')
                        .click(function () {
                            displayer.hide();
                            // Reset the "kind" filter.
                            self.options.kind = '';
                            // trigger an event, so the page can update the selector
                            // to actually match the current filter visually
                            self._trigger('resetFilters');
                            return false;
                        }))
                .append('.');
        }
        displayer.replaceWith(msg);
    },


    _renderCompletions: function(ul, items) {
        var self = this,
            currentType = "";
        $.each(items, function(index, item) {
            // Change autocomplete behavior which overrides the
            // searchterm
            item.data_value = item.value;
            item.value = self.term;
            if (item.type !== currentType) {
                var li = $('<li class="bc-livesearch-autocomplete-category"></li>');
                li.append(
                    $('<span class="bc-livesearch-category-text"></span>')
                        .text(lookup_type(item.type).title || item.type || "Unknown")
                );
                li.append(
                    $('<span class="bc-livesearch-more"></span>')
                        .attr('href', '/search/more')
                        .text('more')
                        .click((function(type) {
                            return function() {
                                var searchText = $.trim(self.element.val());
                                var searchType = lookup_type(type).name || '';
                                window.location = self.getAdvancedSearchUrl(searchText, searchType);
                                return false;
                            };
                        })(item.type))
                );
                ul.append(li);
                currentType = item.type;
            }
            renderItem(ul, item);
        });
        // Set a class on the first item, to remove a border on
        // the first row
        ul.find('li:first').addClass('bc-livesearch-autocomplete-first');

        // groupings that have only one element need a little bit more spacing
        // or the category label/more link on the left look cramped
        var nElements = 0;
        var prevElement = null;
        ul.find('li').each(function() {
            if ($(this).hasClass('bc-livesearch-autocomplete-category')) {
                if (nElements === 1) {
                    prevElement.css('margin-bottom', '1em');
                }
                prevElement = null;
                nElements = 0;
            } else {
                nElements += 1;
                prevElement = $(this);
            }
        });
    }


});


})(jQuery);
