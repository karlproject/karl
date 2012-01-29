(function($) {

function createUrlFn(urlPrefix, kind) {
    return function(query) {
        return kind
            ? urlPrefix + '?kind=' + escape(kind)
                        + '&val='  + escape(query)
            : urlPrefix + '?val='  + escape(query);
    }
}

var advancedSearchUrl = "/searchresults.html";

var typeLookupDisplay = {
    profile: "People",
    page: "Pages",
    post: "Posts",
    file: "Files",
    other: "Other"
};


function getSearchValue() {
    return $('.bc-livesearch-autocomplete').val();
}

function advancedSearchResultsUrl(query, type) {
    if (query.length >= 3) {
        query += "*";
    }
    if (!type) {
        // grab current filter and use that
        type = $('.bc-livesearch-btn-select').text();
    }
    var typeQueryString = (type === "All Content")
                              ? ''
                              : "&kind=" + escape(type);
    var queryString = '?body=' + escape(query) + typeQueryString;
    return advancedSearchUrl + queryString;
}

$(function() {

    $('.bc-livesearch').livesearch({
        urlFn: createUrlFn('data.json'),
        search: function(event, ui) {
            $('<p>Search for ' + ui.query + '</p>')
                .prependTo($('.bc-content-frame'));
        },
        menu: function(event, ui) {
            var text = ui.text;
            var urlFn = createUrlFn(
                text === 'People' ? 'data-people.json' : 'data.json');
            $('.bc-livesearch').livesearch('option', 'urlFn', urlFn);
        },
        validationFn: $.bottlecap.livesearch.prototype.numCharsValidate,
        queryTransformFn: $.bottlecap.livesearch.prototype.globQueryTransform,
        errorFn: $.bottlecap.livesearch.prototype.displayError,
        selectedFn: function(event, item) {
            if (item.url) {
                window.location = item.url;
                return false;
            }
            return true;
        },
        renderCompletions: renderCompletions
    });
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
                    .text(typeLookupDisplay[item.type] || "Other")
            );
            li.append(
                $('<span class="bc-livesearch-more"></span>')
                    .attr('href', '/search/more')
                    .text('more')
                    .click((function(type) {
                        return function() {
                            $('<p>More link clicked for '
                              + type + '</p>')
                                .prependTo($('.bc-content-frame'));
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

function renderPersonEntry(item) {
    var entry = $('<a class="bc-livesearch-profile" />');
    entry.append($('<img />')
                 .attr('src', item.thumbnail));
    var wrapDiv = $('<div />');
    var userInfoDiv = $('<div class="user" />')
        .append($('<div />').text(item.title))
        .append($('<div class="discreet" />').text(item.department));
    var contactDiv = $('<div class="contact" />')
        .append($('<div />')
                .append($('<a />')
                        .attr('href', 'mailto:' + item.email)
                        .text(item.email)
                        .click(function() {
                            window.location = 'mailto:' + item.email;
                            return false;
                        })))
        .append($('<div />').text(item.extension));
    wrapDiv.append(userInfoDiv).append(contactDiv);
    entry.append(wrapDiv).append($('<div style="clear: both" />'));
    return entry;
}

function renderGenericEntry(item) {
    return $("<a></a>").text(item.title);
}

function renderPageEntry(item) {
    var entry = $('<a class="bc-livesearch-page" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.modified_by + ' ' +
                    renderDate(item.modified))))
        .append($('<div class="discreet" />').text(item.community || ''));
    return entry;
}

function renderBlogEntry(item) {
    var entry = $('<a class="bc-livesearch-blog" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.modified_by + ' ' +
                    renderDate(item.modified))))
        .append($('<div class="discreet" />').text(item.community));
    return entry;
}

function renderForumEntry(item) {
    var entry = $('<a class="bc-livesearch-forum" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.creator + ' ' +
                    renderDate(item.created))));
    return entry;
}

function renderForumTopicEntry(item) {
    var entry = $('<a class="bc-livesearch-forumtopic" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.creator + ' ' +
                    renderDate(item.created))))
        .append($('<div class="discreet" />').append(item.forum));
    return entry;
}

function renderCommentEntry(item) {
    var entry = $('<a class="bc-livesearch-comment" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.creator + ' ' +
                    renderDate(item.created))))
        .append($('<div class="discreet" />').text(
            item.blog || item.forum || item.community || ''));
    return entry;
}

function renderFileEntry(item) {
    var entry = $('<a class="bc-livesearch-file" />');
    entry
        .append($('<div />').text(item.title))
        .append(
            $('<div />')
                .append($('<span class="discreet" />').text(
                    'by ' + item.modified_by + ' ' +
                        renderDate(item.modified))));
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
    entry
        .append($('<div />')
                    .text(item.title)
                .append($('<span class="discreet" />')
                            .text(' - at ' + item.location)))
        .append($('<div class="discreet" />').text(
            _renderCalendarDate(item.start) + ' -> ' +
            _renderCalendarDate(item.end)))
        .append($('<div class="discreet" />').text(item.community || ''));
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
