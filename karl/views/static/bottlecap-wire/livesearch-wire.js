(function($) {

function createUrlFn(urlPrefix, kind) {
    return function(query) {
        return kind
            ? urlPrefix + '?kind=' + escape(kind)
                        + '&val='  + escape(query)
            : urlPrefix + '?val='  + escape(query);
    }
}

$(function() {

    var app_url = $("#karl-app-url").eq(0).attr('content');
    var livesearch_url = app_url + "/jquery_livesearch";

    $('.bc-livesearch').livesearch({
        urlFn: createUrlFn(livesearch_url),
        search: function(event, ui) {
            $('<p>Search for ' + ui.query + '</p>')
                .prependTo($('.bc-content-frame'));
        },
        menu: function(event, ui) {
            var text = ui.text;
            var urlFn = text === "All Content"
                ? createUrlFn(livesearch_url)
                : createUrlFn(livesearch_url, text);
            $('.bc-livesearch').livesearch('option', 'urlFn', urlFn);
        },
        validationFn: $.bottlecap.livesearch.prototype.numCharsValidate,
        queryTransformFn: $.bottlecap.livesearch.prototype.globQueryTransform,
        errorFn: $.bottlecap.livesearch.prototype.displayError,
        renderCompletions: renderCompletions
    });
});

function renderDate(dateString) {
    var d = new Date(dateString);
    return (d.getMonth()+1) + '/' + d.getDate() + '/' + d.getFullYear() + ' ' +
           d.getHours() + ':' + d.getMinutes();
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
                    .text(item.type)
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
    "blogentry":     renderPostEntry,
    "forum":         renderForumEntry,
    "forumtopic":    renderForumTopicEntry,
    "comment":       renderCommentEntry,
    "file":          renderFileEntry,
    "calendarevent": renderCalendarEventEntry
};

function renderPersonEntry(item) {
    var entry = $('<a class="bc-livesearch-profile" />');
    entry.append($('<img />')
                 .attr('src', item.thumbnail));
    var wrapDiv = $('<div />');
    var userInfoDiv = $('<div class="user" />')
        .append($('<div />').text(item.title))
        .append($('<div />').text(item.department));
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
                    ' - by ' + item.modified_by + ' on ' +
                    renderDate(item.modified))))
        .append($('<div />').text(item.community || ''));
    return entry;
}

function renderPostEntry(item) {
    var entry = $('<a class="bc-livesearch-post" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.modified_by + ' on ' +
                    renderDate(item.modified))))
        .append($('<div />').text(item.community));
    return entry;
}

function renderForumEntry(item) {
    var entry = $('<a class="bc-livesearch-forum" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.creator + ' on ' +
                    renderDate(item.created))));
    return entry;
}

function renderForumTopicEntry(item) {
    var entry = $('<a class="bc-livesearch-forumtopic" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.creator + ' on ' +
                    renderDate(item.created))))
        .append($('<div />').append(item.forum));
    return entry;
}

function renderCommentEntry(item) {
    var entry = $('<a class="bc-livesearch-comment" />');
    entry
        .append($('<div />')
                .append($('<span />').text(item.title))
                .append($('<span class="discreet" />').text(
                    ' - by ' + item.creator + ' on ' +
                    renderDate(item.created))))
        .append($('<div />').text(
            item.blog || item.forum || ''
        ));
    return entry;
}

function renderFileEntry(item) {
    var entry = $('<a class="bc-livesearch-file" />');
    entry
        .append($('<div />').text(item.title))
        .append($('<div class="discreet" />').text(
            'by ' + item.modified_by + ' on ' +
            renderDate(item.modified)));
    return entry;
}

function renderCalendarEventEntry(item) {
    var entry = $('<a class="bc-livesearch-calendarevent" />');
    entry
        .append($('<div />').text(item.title))
        .append($('<div class="discreet" />').text(
            renderDate(item.start) + ' - ' +
            renderDate(item.end) +
            (item.location ? ' at ' + item.location : '')))
        .append($('<div />').text(item.community || ''));
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
