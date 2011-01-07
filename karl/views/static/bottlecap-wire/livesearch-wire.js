(function($){


function createUrlFn(urlPrefix) {
    return function(query) {
        return urlPrefix + '?q=' + escape(query);
    }
}


$(document).ready(function() {

    var app_url = $("#karl-app-url").eq(0).attr('content');
    ///var livesearch_url = app_url + '/livesearch.json');
    ///var livesearch_url = app_url + '/livesearch_people.json');
    // XXX static testing
    var livesearch_url = app_url + '/static/bottlecap/sl/livesearch/data.json';
    var livesearch_people_url = app_url + '/static/bottlecap/sl/livesearch/data-people.json';

    $('.ui-ls-autocomplete').livesearch({
        urlFn: createUrlFn(livesearch_url),
        search: function(event, ui) {
            $('<p>Search for ' + ui.query + '</p>')
                .prependTo($('.bc-content-frame'));
        },
        menu: function(event, ui) {
            var text = ui.text;
            var urlFn = createUrlFn(
                text === 'People' ? livesearch_people_url : livesearch_url);
            $('.ui-ls-autocomplete').livesearch('option', 'urlFn', urlFn);
        },
        validationFn: $.bottlecap.livesearch.prototype.numCharsValidate,
        queryTransformFn: $.bottlecap.livesearch.prototype.globQueryTransform,
        errorFn: $.bottlecap.livesearch.prototype.displayError,
        renderCompletions: renderCompletions
    });

    // The magnifying glass button on the right
    $(".ui-ls-gobtn").button({
        text: false,
        icons: {primary: "ui-icon-search"}
    });

    // XXX should this be in the livesearch widget itself?
    // Dynamically set some positioning
    $('.ui-ls-autocomplete')
        .height($('.ui-ls-menu').outerHeight())
        .focus()
        .position({
            of: $('.ui-ls-menu'),
            at: "right top",
            my: "left top"
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
            var li = $('<li class="ui-autocomplete-category"></li>');
            li.append(
                $('<span class="ui-ls-category-text"></span>')
                    .text(item.category)
            );
            li.append(
                $('<span class="ui-ls-more"></span>')
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
    ul.find('li:first').addClass('ui-ls-autocomplete-first');
}

function renderItem(ul, item) {
    var li = $('<li>');
    var entry, div;
     // Render different items in different ways
    switch (item.type) {
        case 'profile': {
            entry = $('<a class="ui-ls-profile"></a>');
            entry.append($('<img>').attr('src', item.icon));
            div = entry.append($('<div>'));
            div.append(
                $('<span class="ui-ls-profilelabel"></span>')
                    .text(item.label)
            );
            div.append($('<span>')
                       .text(item.extension));
            entry.append($('<div>').text(item.department));
            break;
        };
         default: {
            entry = $( "<a></a>" ).text( item.label );
        };
    };
    return $( "<li></li>" )
        .data( "item.autocomplete", item )
        .append( entry )
        .appendTo( ul );
}



})(jQuery);

