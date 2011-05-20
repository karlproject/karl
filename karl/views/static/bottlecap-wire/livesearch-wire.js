(function($) {

function createUrlFn(urlPrefix, kind) {
    return function(query) {
        return kind
            ? urlPrefix + '?kind=' + escape($.trim(kind))
                        + '&val='  + escape($.trim(query))
            : urlPrefix + '?val='  + escape($.trim(query));
    }
}

var appUrl = $("#karl-app-url").eq(0).attr('content');
var livesearchUrl = appUrl + "/jquery_livesearch";
var advancedSearchUrl = appUrl + "/searchresults.html";

var typeLookupDisplay = {
    profile: "People",
    page: "Wikis",
    post: "Blogs",
    file: "Files",
    community: "Communities",
    calendarevent: "Events"
};

// mapping for what kind we ask the server
var kindTable = {
    Wikis: 'Pages',
    Blogs: 'Posts'
};

// mapping from kind to type
var kindToType = {
    People: 'karl_models_interfaces_IProfile',
    Wikis: 'karl_content_interfaces_IWikiPage',
    Blogs: 'karl_content_interfaces_IBlogEntry',
    Files: 'karl_content_interfaces_ICommunityFile',
    Events: 'karl_content_interfaces_ICalendarEvent',
    Communities: 'karl_models_interfaces_ICommunity'
};

function getSearchValue() {
    return $('.bc-livesearch-autocomplete').val();
}

function advancedSearchResultsUrl(query, kind) {
    if (!kind) {
        // grab current filter and use that
        kind = $.trim($('.bc-livesearch-btn-select').text());
    }
    kind = escape(kind);
    var typeQueryString = (kind === "All%20Content")
                              ? ''
                              : "&types=" + (kindToType[kind]);
    var queryString = '?body=' + escape(query) + typeQueryString;
    return advancedSearchUrl + queryString;
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

$(function() {

    $('.bc-livesearch').livesearch({
        urlFn: createUrlFn(livesearchUrl),
        search: function(event, ui) {
            var searchText = $.trim(getSearchValue());
            // in ie, the globbed character can be in the wrong place
            // we'll always just grab it from the field and put it on the end

            // suppress error displaying when searching
            // we don't have to worry about toggling it back
            // because we are loading a new page
            shouldDisplayError = false;
            window.location = (
                advancedSearchResultsUrl(searchText));
        },
        menu: function(event, ui) {
            var text = $.trim(ui.text);
            var urlFn = text === "All Content"
                ? createUrlFn(livesearchUrl)
                : createUrlFn(livesearchUrl, kindTable[text] || text);
            $('.bc-livesearch').livesearch('option', 'urlFn', urlFn);
        },
        validationFn: $.bottlecap.livesearch.prototype.numCharsValidate,
        queryTransformFn: $.bottlecap.livesearch.prototype.globQueryTransform,
        errorFn: $.bottlecap.livesearch.prototype.displayError,
        ajaxErrorFn: ajaxError,
        selectedFn: function(event, item) {
            if (item.url) {
                window.location = item.url;
                return false;
            }
            return true;
        },
        renderCompletions: renderCompletions,
        noresults: noResults
    });
    if ($.browser.msie && parseInt($.browser.version) == 7) {
        $('.bc-livesearch-btn-select').css('width', '120px');
    }
});

function renderDate(isoDateString) {
    return $.timeago(isoDateString);
}

function renderCompletions(ul, items) {
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
                    .text(typeLookupDisplay[item.type] || item.type || "Unknown")
            );
            li.append(
                $('<span class="bc-livesearch-more"></span>')
                    .attr('href', '/search/more')
                    .text('more')
                    .click((function(type) {
                        return function() {
                            var searchText = $.trim(getSearchValue());
                            var searchType = typeLookupDisplay[type] || "All Content";
                            window.location = (
                                advancedSearchResultsUrl(searchText, searchType));
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

function noResults(event, item) {
    var el = item.el;
    var displayer = el.errorDisplayer();
    var query  = item.query.replace('*', '');
    var msg = $('<span />').text('No results found. ');
    var selectButtonText = el.selectButtonText;
    var curFilter = $.trim(selectButtonText.text());
    if (curFilter !== 'All Content') {
        msg
            .append('Try searching in ')
            .append($('<a />')
                    .attr('href', '#')
                    .attr('class', 'bc-livesearch-all-content')
                    .text('All Content')
                    .click(function () {
                        displayer.hide();
                        selectButtonText.text('All Content');
                        el.menuSelected(0, {item: selectButtonText});
                        return false;
                    }))
            .append('.');
    }
    displayer.replaceWith(msg);
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
    "community":     renderCommunity
};

function _normalized(val) {
    // the server can return None or null
    // treat these values as empty
    return !val || val === "None" || val === "null"
           ? ''
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
    var authorText = _normalized(author)
                     ? ' - by ' + author + ' '
                     : ' - ';
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
                            .text(' - at ' + item.location))
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

})(jQuery);
