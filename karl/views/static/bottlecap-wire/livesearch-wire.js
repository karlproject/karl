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

function renderCompletions(ul, items) {
    var self = this,
        currentCategory = "";
    $.each(items, function(index, item) {
        // Change autocomplete behavior which overrides the
        // searchterm
        item.data_value = item.value;
        item.value = self.term;
         if (item.category !== currentCategory) {
            var li = $('<li class="bc-livesearch-autocomplete-category"></li>');
            li.append(
                $('<span class="bc-livesearch-category-text"></span>')
                    .text(item.category)
            );
            li.append(
                $('<span class="bc-livesearch-more"></span>')
                    .attr('href', '/search/more')
                    .text('more')
                    .click((function(category) {
                        return function() {
                            $('<p>More link clicked for '
                              + category + '</p>')
                                .prependTo($('.bc-content-frame'));
                            return false;
                        };
                    })(item.category))
            );
            ul.append(li);
            currentCategory = item.category;
        }
        renderItem(ul, item);
    });
    // Set a class on the first item, to remove a border on
    // the first row
    ul.find('li:first').addClass('bc-livesearch-autocomplete-first');
}

var renderDispatchTable = {
    "profile":   renderPersonEntry,
    "wikipage":  renderPageEntry,
    "blogentry": renderPostEntry,
    "file":      renderFileEntry,
    "folder":    renderFileEntry
};

function renderPersonEntry(item) {
    var entry = $('<a class="bc-livesearch-profile"></a>');
    entry.append($('<img>')
                 .attr('src', item.icon));
    var wrapDiv = $('<div>');
    var userInfoDiv = $('<div class="user">')
        .append($('<div>').text(item.label))
        .append($('<div>').text(item.department));
    var contactDiv = $('<div class="contact">')
        .append($('<div>')
                .append($('<a>')
                        .attr('href', 'mailto:' + item.email)
                        .text(item.email)
                        .click(function() {
                            window.location = 'mailto:' + item.email;
                            return false;
                        })))
        .append($('<div>').text(item.extension));
    wrapDiv.append(userInfoDiv).append(contactDiv);
    entry.append(wrapDiv).append($('<div style="clear: both">'));
    return entry;
}

function renderGenericEntry(item) {
    return $("<a></a>").text(item.label);
}

function renderPageEntry(item) {
    var entry = $('<a class="bc-livesearch-page">');
    entry
        .append($('<div>')
                .append($('<span>').text(item.label))
                .append($('<span class="discreet">').text(
                    ' - by ' + item.author + ' on ' + item.modified)))
        .append($('<div>').text(item.community));
    return entry;
}

function renderPostEntry(item) {
    var entry = $('<a class="bc-livesearch-post">');
    entry
        .append($('<div>')
                .append($('<span>').text(item.label))
                .append($('<span class="discreet">').text(
                    ' - by ' + item.author + ' on ' + item.created)))
        .append($('<div>').text(item.community));
    return entry;
}

function renderFileEntry(item) {
    var entry = $('<a class="bc-livesearch-file">');
    entry
        .append($('<div>').text(item.label))
        .append($('<div class="discreet">').text(
            'by ' + item.author + ' on ' + item.modified));
    return entry;
}

function renderItem(ul, item) {
    var li = $('<li>');
    // Render different items in different ways
    // dispatch based on the type of the item
    var type     = item.type,
        renderFn = renderDispatchTable[type] || renderGenericEntry,
        entry    = renderFn(item);
    return $("<li></li>")
        .data("item.autocomplete", item)
        .append(entry)
        .appendTo(ul);
}

})(jQuery);
