 // $Id$
 //

new (function() {                  // BEGIN CLOSURE Karl

var Karl = window.Karl = {};
var t = this;

// Some defaults and constants
Karl.NAME = "Karl";
Karl.VERSION = "3.00";

var createLiveForms = function createLiveForms() {
    $('.mceEditor').each(function () {
        var el = this;
        for(var node=this; node.parentNode; node = node.parentNode) {
            if(node.tagName.toLowerCase() == 'form') {
                node.onsubmit = function (e) {
                    tinyMCE.triggerSave();
                    ////var editor = tinyMCE.get(el.id)
                    ////el.value = editor.getContent();
                };
                break;
            }
        }
    });
};


/**
 * Load TinyMCE
 */
var loadTinyMCE = function loadTinyMCE() {
    // Instead of relying on exception handling, simply check
    // if tiny is available. This allows catching the real exceptions
    // during init.
    var _has_tinyMCE = true;
    try {
        tinyMCE;
    } catch (e) {
        _has_tinyMCE = false;
    }
    if (_has_tinyMCE && tinyMCE.init) {
        // Say "no thanks" to the scriptloader of tiny.
        // Reason: it works excellent, but for both development and production
        // modes, we end up better if we include our resources ourselves.
        // We do this by marking the resources as loaded already.
        // Thist must be in sync with what actually gets loaded in the page.
        var pref = tinymce.baseURL + '/';
        var mark = function mark(path) {
            // Mark resource as loaded for both .js and _src.js
            // Path should not contain the .js ending.
            tinymce.ScriptLoader.markDone(pref + path + '.js');
            tinymce.ScriptLoader.markDone(pref + path + '_src.js');
        };
        mark('langs/en');
        mark('themes/advanced/editor_template');
        mark('plugins/paste/editor_plugin');
        mark('plugins/wicked/editor_plugin');
        mark('plugins/wicked/langs/en');
        mark('plugins/spellchecker/editor_plugin');
        mark('plugins/embedmedia/editor_plugin');

        // See if the wiki plugin needs to be enabled.
        var widget_data = window.karl_client_data && karl_client_data.text || {};
        var plugins = 'paste,embedmedia';
        if (widget_data.enable_wiki_plugin) {
            plugins += ',wicked';
        }
        plugins += ',spellchecker'

        // Do the init.
        tinyMCE.init({
            theme: 'advanced',
            skin: 'karl',
            mode: 'specific_textareas',
            editor_selector : 'mceEditor',
            height: '400',
            width: '550',
            convert_urls : false,
            gecko_spellcheck : true,
            submit_patch: false,
            entity_encoding: "numeric",
            add_form_submit_trigger: false,
            add_unload_trigger: false,
            strict_loading_mode: true,
            paste_create_paragraphs : false,
            paste_create_linebreaks : false,
            paste_use_dialog : false,
            paste_auto_cleanup_on_paste : true,
            paste_convert_middot_lists : true,
            paste_unindented_list_class : "unindentedList",
            paste_convert_headers_to_strong : true,
            theme_advanced_toolbar_location: 'top',
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, image, embedmedia, addwickedlink, delwickedlink, spellchecker',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: plugins,
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            relative_urls : false,
            forced_root_block : 'p',
            spellchecker_rpc_url: "/tinymce_spellcheck",
            spellchecker_languages : "+English=en"
            
        });  
    } else {
        // XXX raise an error here?
    }
};

// Load TinyMCE
loadTinyMCE();


/**
 * Navigation menus
 *
 * Required for IE only
 * fakes :hover handling
 * see http://www.htmldog.com/articles/suckerfish/dropdowns/ for explanation
 *
 * The following is a port of the Karl2 navmenus.
 */
var enableOldStyleDropdowns = function () {
    if (jQuery.browser.msie) {
        $('#left li.submenu').each(function() {
            $(this).mouseover(function() {
                $(this).addClass('iehover');
            });
            $(this).mouseout(function() {
                $(this).removeClass('iehover');
            });
        });
    }
};


// Custom jquery extensions

$.widget('ui.karlstatusbox', {
    
    _init: function() {
        // initialize the queue
        this.queue = [];
    },

    /*
     * Public methods
     **/

    /* Clear all messages, or all messages with a given queueCategory */
    clear: function(/*optional*/ queueCategory) {
        if (queueCategory === undefined) {
            // shortcut: clear all items
            this.element.empty();
            this.queue = [];
        } else {
            // Clear items of the given category
            var newQueue = [];
            $(this.queue).each(function() {
                // The element may have been deleted (by closebutton),
                // but we don't check for this, since remove() works
                // safe with elements already removed.
                if (this.queueCategory == queueCategory) {
                    this.item.remove();
                } else {
                    // keep item in queue
                    newQueue.push(this);
                }
            });
            this.queue = newQueue;
        }
    },

    /* Append a message */
    append: function(message, /*optional*/ queueCategory) {
        // default queue category is null.
        if (queueCategory === undefined) {
            queueCategory = null;
        }
        // Append the item
        var item = $('<div class="' + this.options.clsItem + '"></div>');
        item.append($('<div class="message"></div>').append(message));
        if (this.options.hasCloseButton) {
            item.append($('<a href="#" class="statusbox-closebutton">X</a>')
                        .click(function(e) {
                            item.remove();    
                            e.preventDefault();
                        })
            );
        }
        // clearing floats
        if (jQuery.browser.msie) {
            item.addClass('clear-ie-container');
        } else {
            item.append('<div class="clear"></div>');
        }
        this.element.append(item);
        // Remember it on the queue
        this.queue.push({
            item: item,
            queueCategory: queueCategory
        });
    },

    /* Append a message after clearing previous messages.
     * If queueCategory is specified, only the messages added with the
     * same category are cleared. */
    clearAndAppend: function(message, /*optional*/ queueCategory) {
        this.clear(queueCategory);
        this.append(message, queueCategory);
    }


    /*
     * Private methods
     **/


});

$.extend($.ui.karlstatusbox, {
    defaults: {
        clsItem: 'statusbox-item',
        hasCloseButton: true
    }
});


$.widget('ui.karllivesearch', $.extend({}, $.ui.autobox3.prototype, {

    activate: function() {
        if (this.active && this.active[0] && $.data(this.active[0], "originalObject")) {
            var href = $.data(this.active[0], "originalObject").href;
            window.location = href;
        } else {
            // submit the form
            document.forms['ff'].submit();
        }
    },

    _setupWidget: function() {
        var self = this;
        this.input = this._bindInput(this.element);

        // to be sure there is no FF-autocomplete
        this.input.attr('autocomplete', 'off');

        // If a click bubbles all the way up to the window, close the autobox
        // (Note, bind to document and not to windows.
        // If windows is used, event does not bubble up on IE.
        $(document).bind("click.autobox", function(){
            self.cancel();
        });

    },
    
    _getBoxOnEnter: function(){
        // When enter is pressed, always submit the form.
        // This is needed when autobox is inactive.
        document.forms['ff'].submit();
        // Prevent add from happening.
    },
 
    _handleActive: function() {
        // Don't copy the value to the input,
        // like superclass does.
    }
                    
}));

$.extend($.ui.karllivesearch, {
    defaults: $.extend({}, $.ui.autobox3.defaults, {
        selectHoverable: '.result .item, .showall .item',
        // start search from 3rd input character only
        minQueryLength: 3
    })
});


Karl.makeSnippets = function(snippetmap) {
    // compile templates
    var compiled_map = {};
    for (var snippet in snippetmap) {
        compiled_map[snippet] = $.makeTemplate(snippetmap[snippet], "<%", "%>");
    }
    return function(record) {
        var snippet = record.snippet || '';
        var template = compiled_map[snippet];
        return template(record);
    };
};

var wid = 0;

Karl.getJSON = function getJSON(url, data, callback, error) {
    return jQuery.ajax({
            type: "POST",
            url: url,
            data: data,
            success: callback,
            error: error,
            dataType: 'json'
    });
};

$.widget('ui.karltagbox', $.extend({}, $.ui.autobox3.prototype, {

    _addBox: function (record, /*optional*/ initializing) {
        var self = this;
        // Update bubble if we already have it
        var cachekey = record.id || record.tag;
        var cached = this.bubbles[cachekey];
        if (cached) {
            // Is this my tag already?
            var cachedrecord = cached.record;
            if (cachedrecord.snippet != 'nondeleteable') {
                // Don't worry then. We have this tag,
                // just ignore the event.
                return;
            }
            // Change the snippet, increase the counter,
            // and update the widget.
            cachedrecord.snippet = '';
            cachedrecord.count++;
            this._updateBox(cached);
        } else {
            // Add the bubble.
            // tagusers_url depends on if we have the data available
            var tagusers_url;
            if (this.options.docid) {
                tagusers_url = this.options.tagusers_url +
                        '?tag=' + record.tag +
                        '&docid=' + this.options.docid;
            } else {
                // if there is no docid (for example a page being added)
                // just don't make the link clickable.
                tagusers_url = 'javascript://return false;';
            }
            // add extra info to the records
            record = $.extend({
                    // default values for when we add the tag from code
                    count: 1,
                    tagusers_url: tagusers_url
                },
                record,
                {
                    _name: this.options.name || 'box',
                    _wid: 'bit-' + wid,
                    showtag_url: this.options.showtag_url + (record.id || record.tag)
                });
            wid++;
            // render the bubble
            var rendered = this._renderBox(record);

            // Validate the tag on client side.
            // If this fails the add will not happen.
            if (! initializing) {
                var error = this._validateTag(record.tag);
                if (error) {
                    // Report the error.
                    this._appendStatusWithBubble(
                        'Adding tag failed: ' + error,
                        rendered);
                    rendered.remove();
                    // Finish here.
                    return;
                }
            }

            // cache the record internally
            this.bubbles[cachekey] = cached = {record:record, li:rendered[0]};
        }
        // Ajax save is skipped in the boxes that are added initially.
        if (! initializing && this.options.ajaxAdd) {
            Karl.getJSON(this.options.ajaxAdd, "val=" + record.tag,
                function(json) {self._ajaxAddSuccess(cached, json);},
                function(json) {self._ajaxAddFailure(cached, json);}
                );
        }
    },

    _validateTag: function(tag) {
        if (this.options.validateRegexp) {
            if (tag.match(this.options.validateRegexp) == null) {
                return 'Value contains characters that are not allowed in a tag.';
            }
        }
        // No error.
        return;
    },

    _ajaxAddSuccess: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (error) {
            this._ajaxAddFailure(cached, json);
        }
    },
    
    _ajaxAddFailure: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (! error) {
            error = 'Server error when adding tag';
        }
        // Report the error
        this._appendStatusWithBubble(error, cached.li);
        // Remove bubble
        this._delBox(cached.li, true);
    },

    _renderBox: function (record) {
        var self = this;
        // render the snippet
        var rendered = this.options.snippets(record);
        rendered = this.holder.find('.autobox-input').before(rendered).prev();
        this.input.val('');
        // Bind the close button
        $('.closebutton', rendered).bind('click', function(e) {
                  self._delBox(rendered);
                  e.preventDefault();
              });
        return rendered;
    },

    _delBox: function(li, /*optional*/ initializing) {
        var self = this;
        // Update bubble if counter > 1
        var tagkey = li.find('input')[0].value;
        var cached = this.bubbles[tagkey];

        if (cached && cached.record.count > 1) {
            // This is also a global tag.
            var cachedrecord = cached.record;
            // Change the snippet, increase the counter,
            // and update the widget.
            cachedrecord.snippet = 'nondeleteable';
            cachedrecord.count--;
            this._updateBox(cached);
        } else {
            // hide first to work with rounded corners in IE (using DD_roundies)
            li.css("display", "none");

            // Else proceed with deletion 
            $.ui.autobox3.prototype._delBox.call(this, li);
            
            // And delete it from the cache too
            delete this.bubbles[tagkey];
        }
        // Do the ajax in any case
        if (! initializing && this.options.ajaxDel) {
            Karl.getJSON(this.options.ajaxDel, "val=" + tagkey,
                function(json) {self._ajaxDelSuccess(cached, json);},
                function(json) {self._ajaxDelFailure(cached, json);}
                );
        }
    },

    _ajaxDelSuccess: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (error) {
            this._ajaxDelFailure(cached, json);
        }
    },
 
    _ajaxDelFailure: function (cached, json) {
        // use error sent by server, if available
        var error = json && json.error;
        if (! error) {
            error = 'Server error when deleting tag';
        }
        // Report the error
        this._appendStatusWithBubble(error, cached.li);
        // add back the bubble
        this._addBox(cached.record, true);
    },


    _updateBox: function(cached) {
        // render the bubble
        var rendered = this._renderBox(cached.record);
        // and replace the original li with it
        $(cached.li).after(rendered).remove();
        cached.li = rendered;
    },
    
    _createHolder: function (element) {
        var holder = $.ui.autobox3.prototype._createHolder.call(this, element);
        // Add a div around it and place the original widget and a status box
        // into this wrapper div
        var newholder = holder.wrap('<div class="statusbox-wrapper"></div>').parent()
            .append(
                $('<div class="statusbox"></div>')
                    .karlstatusbox()
                )
        this.statusbox = $("*:last", newholder);
        return newholder;
    },

    _clearStatus: function() {
        this.statusbox.karlstatusbox('clear');
    },

    _appendStatus: function(message) {
        this.statusbox.karlstatusbox('append', message);
    },

    _appendStatusWithBubble: function(message, bubble) {
        // clone the bubble and remove the input from it
        // to avoid collision in case it gets submitted in form
        bubble = $(bubble).clone()
        bubble.find('input').remove()
        var fullmessage = $('<span class="message-span"></span><span class="bubble-span"></span>');
        fullmessage.eq(0).text(message);
        fullmessage.eq(1).append(bubble);
        this._appendStatus(fullmessage);
        // bind the bubble's closebutton
        var item = this.statusbox.find('>:last-child');
        $('.closebutton', bubble)
            .bind('click', function(e) {
                item.remove(); 
                e.preventDefault();
            });
    },
 
    _setupWidget: function() {
        // initialize tag cache
        this.bubbles = {};
        $.ui.autobox3.prototype._setupWidget.call(this);
        var self = this;
        // add a button after the input
        // also wrap it to avoid breaking
        this.input.wrap('<span></span>');
        $('<button class="standalone addtag-button" type="button">Add</button>')
            .bind('click', function(e) {
                // We generate the record first...
                // (null result means we need not add it)
                var record = self._getBoxOnEnter();
                if (record) { self._addBox(record); }
                e.preventDefault();
            })
            .insertAfter(this.input);


        // populate additional methods from options
        if (this.options.validateTag) this._validateTag = this.options.validateTag;
    },

    _updateList: function(list){
        // store the value
        this.cached_result = list;
        $.ui.autobox3.prototype._updateList.call(this, list);
        if (this.options.selectFirst) {
            // is there at least one selectable in the list?
            if ($("> *", this.container).length > 0) {
                // Select the first element
                this.selected = 0;
                this._select();
            }
        }
    },

    _getCurrentValsHash: function(input) {
        // (XXX ignore "input" really... the parameter seems
        // to serve little or no role here.)
        var hash = {};
        // The hash that we construct will serve to exclude
        // these elements from the new searches.
        for (var tagkey in this.bubbles) {
            var cachedrecord = this.bubbles[tagkey].record;
            if (cachedrecord.snippet != 'nondeleteable') {
                // This value will be exluded from search results.
                // We _always_ use the tag text here.
                hash[cachedrecord.tag] = true;
            }
        }
        return hash;
    }


}));

var _snip_pre =     '<span>' + 
                    '<a class="showtag-link" href="<%= showtag_url %>"><%= tag %></a>' +
                    '<span class="count">&nbsp;(' +
                    '<a class="tagusers-link"  href="<%= tagusers_url %>"><%= count %></a>)</span>';
var _snip_post =    '<input type="hidden" name="<%= _name %>" value="<%= tag %>" />' +
                    '</span>' +
                    '</li>';

$.extend($.ui.karltagbox, {
    defaults: $.extend({}, $.ui.autobox3.defaults, {
        //
        // Livesearch results with better highlighting
        //
        match: function(typed) {
            this.typed = typed;
            this.pre_match = this.text;
            this.match = this.post_match = '';
            if (!this.ajax && !typed || typed.length == 0) { return true; }
            var match_at = this.text.search(new RegExp("\\b" + typed, "i"));
            if (match_at != -1) {
                this.pre_match = this.text.slice(0,match_at);
                this.match = this.text.slice(match_at,match_at + typed.length);
                this.post_match = this.text.slice(match_at + typed.length);
                return true;
            }
            return false;
        },
        insertText: function(obj) {
            return obj.tag;
        },
        templateText: "<li><%= pre_match %><span class='matching' ><%= match %></span><%= post_match %></li>",
        //
        // Snippets for more flexible client side rendering
        //
        snippets: Karl.makeSnippets({
            '': 
                '<li id="<%= _wid %>" class="bit-box">' +
                _snip_pre +
                '<a href="#" class="closebutton"></a>' +
                _snip_post,
            nondeleteable: 
                '<li id="<%= _wid %>" class="bit-box nondeleteable">' +
                _snip_pre + 
                _snip_post
        }),
        // The only items addable are the one from the search result.
        strictAdd: false,
        selectFirst: false,
        validateRegexp: null
    })
});


/*
 * A variant of the tagbox, used for members.
 * It only allows entering the items from the search result set.
 */
$.widget('ui.karlmemberbox', $.extend({}, $.ui.karltagbox.prototype, {
}));

$.extend($.ui.karlmemberbox, {
    defaults: $.extend({}, $.ui.karltagbox.defaults, {
        strictAdd: true,
        selectFirst: true,
        getBoxFromSelection: function() {
            // Is there an active object?
            var record = this.active && this.active[0] && $.data(this.active[0], "originalObject");
            if (! record) {
                // Prevent it from happen.
                return;
            }
            return {
                tag: record.text,
                id: record.id
            };
        },
        getBoxOnEnter: function() {return this._getBoxFromSelection()},
        snippets: Karl.makeSnippets({
            '': 
                '<li id="<%= _wid %>" class="bit-box">'
                + '<span>'
                + '<a class="showtag-link" href="<%= showtag_url %>"><%= tag %></a>'
                + '<a href="#" class="closebutton"></a>'
                + '<input type="hidden" name="<%= _name %>" value="<%= id %>" />'
                + '</span>'
                + '</li>'
        })

    })

});


$.widget('ui.karlgrid', $.extend({}, $.ui.grid.prototype, {

    _generateColumns: function() {

        this.columnsContainer = $('<tr class="ui-grid-columns"><td><div class="ui-grid-columns-constrainer"><table cellpadding="0" cellspacing="0"><tbody><tr class="ui-grid-header ui-grid-inner"></tr></tbody></table></div></td></tr>')
            .appendTo(this.grid).find('table tbody tr');

        $('.ui-grid-columns-constrainer', this.grid).css({
            width: this.options.width,
            overflow: 'hidden'
        });
        
        // columns will have borders collapsed
        $('table', this.grid).css({
            'border-collapse': 'collapse'
        });

        // XXX Do _not_ make it sortable.
        //this.columnsContainer.gridSortable({ instance: this });
        
    },

    _syncColumnWidth: function() {
        var self = this;

        // calculate desired widths
        var column_widths = [];
        var totalWidth = 0;
        $('td', this.columnsContainer).each(function() {
            var width = $(this).outerWidth();
            column_widths.push(width);
            totalWidth += width;
        });
        
        // set width on all cells
        // XXX This would probably work bad with infinite scrolling!
        $('> tr', this.content).each(function() {
            $('> td', this).each(function(i) {
                var elem = $(this);
                var width = column_widths[i];
                // Take offset into consideration
                var offset = elem.outerWidth() - elem.width();
                if (i==0) {
                    // Since we have no bordercollapse in the column part:
                    // increase first field's width with the left border
                    offset -= self.leftBorder; 
                }
                width -= offset;
                // adjust cell width
                elem
                    // overflow is essential for column width
                    .css('overflow', 'hidden')
                    .width(width);
            });

        });

        // set the width of the whole table
        this.content.parent()     // this.content is the <tbody>, parent is the <table>.
            .width(totalWidth)
            //.css('overflow', 'hidden')
            // table-layout is essential for column width
            .css('table-layout', 'fixed');

    },

    _addColumns: function(columns) {

        this.columns = columns;
        //// XXX XXX there is no placeholder column now
        //var totalWidth = 25;
        var totalWidth = 0;
        this.columns_by_id = {};
        
        // Use sort column and direction as set by _onClick handler,
        // allow to provide initial defaults by options.
        var sortColumn = this.sortColumn || this.options.sortColumn;
        var sortDirection = this.sortDirection || this.options.sortDirection;

        for (var i=0; i < columns.length; i++) {
            var column_meta = columns[i];

            var sortDirectionClass = '';
            // Do we have a sorting direction?
            if (sortColumn == column_meta.id) {
                sortDirectionClass = ' ui-icon ' + (sortDirection == 'asc' ? 'ui-icon-carat-1-s' : 'ui-icon-carat-1-n');
            }

            var column = $('<td class="ui-grid-column-header ui-state-default">' +
                           '  <div style="position: relative;">' + // inner div is needed for relativizing position
                           '    <a href="#">' +
                           '      <span class="ui-grid-column-header-text">' + column_meta.label + '</span>' +
                           '    </a>' +
                           '    <span class="ui-grid-visual-sorting-indicator' + sortDirectionClass + '"></span>' +
                           '  </div>' +
                           '</td>')
                .data('grid-column-header', column_meta)
                .appendTo(this.columnsContainer);

            var offset = column.outerWidth() - column.width();
            if (i==0) {
                // the first column gets the left offset
                // subscribed from width as well
                // this is needed to compensate for left column border
                //this.leftBorder = column[0].offsetLeft;
                if (jQuery.browser.msie) {
                    this.leftBorder = 0;
                } else {
                    // FF, Safari
                    // XXX for now we suppose a (table) border of 1
                    this.leftBorder = 1;
                }
                offset += this.leftBorder;
            }
            column.width(column_meta.width - offset);

            totalWidth += column_meta.width;
            
            // XXX Do not make the columns resizable.
            //column.gridResizable();
        };
        
        //This column is the last and only used to serve as placeholder for a non-existant scrollbar
        // XXX XXX temporary disabled, as currently we don't use features it allows,
        // and it causes a layout artifact on FF.
        //$('<td class="ui-grid-column-header ui-state-default"><div></div></td>').width(25).appendTo(this.columnsContainer);
        
        //Update the total width of the wrapper of the column headers
        var header_table = this.columnsContainer.parent().parent();
        header_table.width(totalWidth);

        // Send event that columns are setup
        this.element.trigger('karlgrid_columns_set');

    },

    _handleClick: function(event) {

        var el = $(event.target);

        // Click on column header toggles sorting
        if (el.is('.ui-grid-column-header, .ui-grid-column-header *')) {
            var header = el.hasClass('ui-grid-column-header') ? el : el.parents('.ui-grid-column-header');
            var data = header.data('grid-column-header');
            this.sortDirection = this.sortDirection == 'desc' ? 'asc' : 'desc';
            this.sortColumn = data.id;
            this._update ({columns: false, refresh: true});
        }
        
        // Handle click on pagination buttons
        if (el.is('.ui-grid-pagination a, .ui-grid-pagination a *')) {
            var current= Math.floor((this.offset + this.options.limit - 1) / this.options.limit) + 1;
            if (el.hasClass('ui-icon-circle-arrow-w') || el.find('.ui-icon-circle-arrow-w').length > 0) current --;
            if (el.hasClass('ui-icon-circle-arrow-e') || el.find('.ui-icon-circle-arrow-e').length > 0) current ++;
            if (! isNaN(parseInt(event.target.innerHTML, 10))) current = parseInt(event.target.innerHTML, 10);
            
            this.offset = (current - 1) * this.options.limit;
            this._update();
        }
        
        return false;

    },


    _makeRowsSelectable: function() {
        
        var table = this.content.parent().parent();
        table.bind('mousedown', function(event) {
            var filter = 'tr';
            var item;
            $(event.target).parents().andSelf().each(function() {
                if ($('tr', table).index(this) != -1) item = this;
            });

            if (!item)
                return;

            // follow the link in it
            var links = $('a', item);
            if (links.length > 0) {
                window.location = links[0].href;
            }

            event.preventDefault();
        });
        
    },

    _addRow: function(item, dontAdd) {

        var row = $.ui.grid.prototype._addRow.call(this, item, dontAdd);

        // Calculate the oddity of the newly added row. We do the
        // following check after the row has already been added.
        var oddity = (this.content.find('tr').length % 2 == 1)

        // Add class based on oddity and options
        if (oddity && this.options.oddRowClass) {
            row.addClass(this.options.oddRowClass);
        }

        if (! oddity && this.options.evenRowClass) {
            row.addClass(this.options.evenRowClass);
        }

        return row;

    },

    _generateFooter: function() {
        this.footer = $('<tr class="ui-grid-footer ui-widget-header"><td>'+
        '<span class="ui-grid-footer-text ui-grid-limits"></span>'+
        '</td></tr>').appendTo(this.grid).find('td');
    },

    _generatePagination: function(response) {
        this.pagination = $('<span class="ui-grid-pagination clearafter"></span>').appendTo(this.footer);
        this.footerResultsBox = $('.ui-grid-limits, .ui-grid-no-limits', this.footer);
        this._updatePagination(response);
    },

    /* XXX need to overwrite this for not showing
     * pagination if there are 0 or 1 pages */
    _updatePagination: function(response) {
        
        var pages = Math.floor((response.totalRecords + this.options.limit - 1) / this.options.limit),
            current= Math.floor((this.offset + this.options.limit - 1) / this.options.limit) + 1,
            displayed = [];

        this.pagination.empty();
        
        if (pages <= 1) {
            // Deactivate the Results: box
            // This means that if it does not have the ui-grid-limits
            // class, the updater won't update the Results: infoline on it
            this.footerResultsBox
                .removeClass('ui-grid-limits')
                .addClass('ui-grid-no-limits')
                .html('');
            return;
        }

        // Activate the Results: box
        this.footerResultsBox
            .removeClass('ui-grid-no-limits')
            .addClass('ui-grid-limits');

        for (var i=current-1; i > 0 && i > current-3; i--) {
            this.pagination.prepend('<a href="#" class="ui-state-default">'+i+'</a>');
            displayed.push(i);
        };
        
        for (var i=current; i < pages+1 && i < current+3; i++) {
            this.pagination.append(i==current? '<span class="ui-state-active">'+i+'</span>' :
                    '<a href="#" class="ui-state-default">'+i+'</a>' );
            displayed.push(i);
        };


        if(pages > 1 && $.inArray(2, displayed) == -1) //Show front dots if the '2' is not already displayed and there are more pages than 1
            // XXX XXX
            this.pagination.prepend('<span class="ui-grid-pagination-dots">...</span>');
        
        if($.inArray(1, displayed) == -1) //Show the '1' if it's not already shown
            this.pagination.prepend('<a href="#" class="ui-state-default">1</a>');

        if($.inArray(pages-1, displayed) == -1) //Show the dots between the current elipse and the last if the one before last is not shown
            // XXX XXX
            this.pagination.append('<span class="ui-grid-pagination-dots">...</span>');
        
        if($.inArray(pages, displayed) == -1) //Show the last if it's not already shown
            this.pagination.append('<a href="#" class="ui-state-default">'+pages+'</a>');
            
        this.pagination.prepend(current-1 > 0 ?
                '<a href="#" class="ui-state-default ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-w">Prev</div></a>' :
                '<span class="ui-state-default ui-state-disabled ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-w">Prev</div></span>');
        this.pagination.append(current+1 > pages ?
                '<span href="#" class="ui-state-default ui-state-disabled ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-e">Next</div></span>' :
                '<a href="#" class="ui-state-default ui-grid-pagination-icon"><div class="ui-icon ui-icon-circle-arrow-e">Next</div></a>');

        this.pagination.find('a.ui-state-default')
            .hover(
                function() {
                    $(this).addClass('ui-state-hover');
                },
                function() {
                    $(this).removeClass('ui-state-hover');
                }
            );

    },

    _extendFetchOptions: function(fetchOptions) {
        return $.extend({}, fetchOptions, {
            limit: this.options.limit,
            start: (! (fetchOptions && fetchOptions.refresh) && this.offset) || 0,
            refresh: (fetchOptions && fetchOptions.refresh) || (fetchOptions && fetchOptions.columns)
        })
    },

    /* XXX need to overwrite this to be able to customize
     * behaviour like displaying Results data.  */
    _update: function(o) {
        var self = this;

        var fetchOptions = $.extend({}, this._extendFetchOptions(fetchOptions), {
        // XXX Is this needed?
        //    fill: null
        });
        
        if (fetchOptions.refresh) {
            fetchOptions.start = this.infiniteScrolling ? 0 : (this.offset || 0);
        }
        //Somehow the keys for these must stay undefined no matter what
        if(this.sortColumn) fetchOptions.sortColumn = this.sortColumn;
        if(this.sortDirection) fetchOptions.sortDirection = this.sortDirection;

        //Do the ajax call
        this.gridmodel.fetch(fetchOptions, function(state) {
            self._doUpdate(state, o);
        });

    },

    _initialUpdate: function() {		
        var initialState = this.options.initialState;
        if (initialState) {
            // Initial state: use it to load content
            // Need to convert each record from a flat list to a keyed dict
	    initialState = $.ui.grid.model.defaults.parse(initialState);
            // load them to the table
            this._doUpdate(initialState, {columns: true});
        } else {
            // Query the content from the server
            this._update({columns: true});
        }
    },

    _doUpdate: function(state, o) {
        var self = this;

        //Generate or update pagination
        if (this.options.pagination && ! this.pagination) {
            this._generatePagination(state);
        } else if (this.options.pagination && this.pagination) {
            this._updatePagination(state);
        }

        var self = this;
        var fetchOptions = this._extendFetchOptions(o);

        //Empty the content if we either use pagination or we have to restart infinite scrolling
        if (!this.infiniteScrolling || fetchOptions.refresh)
            this.content.empty();

        //Empty the columns
        if (fetchOptions.refresh) {
            this.columnsContainer.empty();
            this._addColumns(state.columns);
        }

        //If infiniteScrolling is used and there's no full refresh, fill rows
        if(this.infiniteScrolling && ! fetchOptions.refresh) {

            var data = [];
            for (var i=0; i < state.records.length; i++) {
                data.push(this._addRow(state.records[i]));
            };

            o.fill({
                chunk: o.chunk,
                data: data
            });

        } else { //otherwise, simply append the rows to the now emptied list

            for (var i=0; i < state.records.length; i++) {
                this._addRow(state.records[i]);
            };

            this._syncColumnWidth();
                
            //If we're using infinite scrolling, we have to restart it
            if(this.infiniteScrolling) {
                this.contentDiv.infiniteScrolling('restart');
            }

        }

        //Initiate infinite scrolling if we don't use pagination and total records exceed the displayed records
        if(!this.infiniteScrolling && !this.options.pagination && fetchOptions.limit < state.totalRecords) {
                
            this.infiniteScrolling = true;
            this.contentDiv.infiniteScrolling({
                total: self.options.allocateRows ? state.totalRecords : false,
                chunk: self.options.chunk,
                scroll: function(e, ui) {
                    self.offset = ui.start;
                    self._update({ fill: ui.fill, chunk: ui.chunk });
                },
                update: function(e, ui) {
                    $('.ui-grid-limits', self.footer).html('Result ' + ui.firstItem + '-' + ui.lastItem + (ui.total ? ' of '+ui.total : ''));
                }
            });
                
        }

        if (! this.infiniteScrolling) {
            // start numbering from 1
            var firstItem = fetchOptions.start + 1;
            // last  should not be more than the total records
            var lastItem = Math.min(fetchOptions.start + fetchOptions.limit, state.totalRecords);
            $('.ui-grid-limits', this.footer).html('Result ' + 
                    (firstItem == lastItem ? firstItem : firstItem + '-' + lastItem) + 
                    ' of ' + state.totalRecords);
        }
    }
 
}));


$.extend($.ui.karlgrid, {
    defaults: {
        width: 500,
        height: 300,

        limit: false,
        pagination: true,
        allocateRows: true, //Only used for infinite scrolling
        chunk: 20, //Only used for infinite scrolling

        footer: true,
        toolbar: false,

        multipleSelection: true,

        evenRowClass: 'even',
        oddRowClass: 'odd',

        sortColumn: '',
        sortDirection: '',

        initialState: null
    }
});



$.widget('ui.karldialog', $.extend({}, $.ui.dialog.prototype, {

    _init: function() {
        $.ui.dialog.prototype._init.call(this);
    },

    /* Need to replicate this, because we do not want
     * to scroll down to the first tabbable element when
     * the dialog opens. */
    open: function() {
        if (this._isOpen) { return; }

        var options = this.options,
            uiDialog = this.uiDialog;

        this.overlay = options.modal ? new $.ui.dialog.overlay(this) : null;
        (uiDialog.next().length && uiDialog.appendTo('body'));
        this._size();
        this._position(options.position);
        uiDialog.show(options.show);
        this.moveToTop(true);

        // prevent tabbing out of modal dialogs
        (options.modal && uiDialog.bind('keypress.ui-dialog', function(event) {
            if (event.keyCode != $.ui.keyCode.TAB) {
                return;
            }

            var tabbables = $(':tabbable', this),
                first = tabbables.filter(':first')[0],
                last  = tabbables.filter(':last')[0];

            if (event.target == last && !event.shiftKey) {
                setTimeout(function() {
                    first.focus();
                }, 1);
            } else if (event.target == first && event.shiftKey) {
                setTimeout(function() {
                    last.focus();
                }, 1);
            }
        }));

        //// set focus to the first tabbable element in the content area or the first button
        //// if there are no tabbable elements, set focus on the dialog itself
        //$([])
        //    .add(uiDialog.find('.ui-dialog-content :tabbable:first'))
        //    .add(uiDialog.find('.ui-dialog-buttonpane :tabbable:first'))
        //    .add(uiDialog)
        //    .filter(':first')
        //    .focus();
        // XXX Always focus on the dialog itself
        uiDialog.focus()

        this._trigger('open');
        this._isOpen = true;
    }


}));

$.extend($.ui.karldialog, {
    defaults: $.extend({}, $.ui.dialog.defaults, {
        autoOpen: false,
        modal: true,
        bgiframe: true,    // XXX bgiFrame is currently needed for modal
        hide: 'fold'
    })
});


$.widget('ui.karlmultiupload', {

    _init: function() {
        var self = this;
        this.stub = this.element.find(this.options.selectorStub);
        // Set up the stub
        var input = this.stub
            .hide()
            .find('input')
        this.name = input.attr('name');
        input.removeAttr('name');
        // Set up the add button
        this.element.find(this.options.selectorAddButton)
            .click(function(e) {
                self._add();
                e.preventDefault();
            });
    },

    // Add a new stub
    _add: function() {
        var new_stub = this.stub.clone()
            .insertBefore(this.stub);
        var input = new_stub.find('input')
        input.attr('name', this.name + this._getCounter());
        // bind the close button
        new_stub.find(this.options.selectorCloseButton)
            .click(function(e) {
                new_stub.remove();
                e.preventDefault();
            });
        new_stub.show();
    },

    _getCounter: function() {
        this.counter = this.counter || 0;
        return this.counter++;
    }

});

$.extend($.ui.karlmultiupload, {
    defaults: {
        selectorStub: '.muf-stub',
        selectorCloseButton: '.muf-closebutton',
        selectorAddButton: '.muf-addbutton'
    }
});


$.widget('ui.karlsingleupload', {

    _init: function() {
        var self = this;
        this.stub = this.element.find(this.options.selectorStub);
        // Set up the stub
        var input = this.stub
            .hide()
            .find('input')
        this.name = input.attr('name');
        input.removeAttr('name');
        // Set up the options
        this.element.find(this.options.selectorNoChange)
            .click(function(e) {
                if (self.real) {
                    self._del();
                }
            });
        this.element.find(this.options.selectorUpload)
            .click(function(e) {
                if (! self.real) {
                    self._add();
                }
            });

    },

    // Add a new stub
    _add: function() {
        var _r = this.real = this.stub.clone()
            .insertBefore(this.stub);
        var input = _r.find('input')
        input.attr('name', this.name);
        _r.show();
    },

    // Delete the stub
    _del: function() {
        this.real.remove();
        this.real = null;
    }

});

$.extend($.ui.karlsingleupload, {
    defaults: {
        selectorStub: '.sif-stub',
        selectorNoChange: '.sif-nochange',
        selectorUpload: '.sif-upload'
    }
});


/**
 * Quotable comments
 *
 * - The widget is bound to a comment.
 * - The "pasteToActiveTiny" event pastes the designated text area
 *   into the selection of the active tinymce window
 * - A click to the "Quote" link will trigger above event.
 *
 */
$.widget('ui.karlquotablecomment', {

    _init: function() {
        var self = this;
        this.text = this.element.find(this.options.selectorText);
        // Set up the paste button
        this.element.find(this.options.selectorPasteButton)
            .click(function(e) {
                self.pasteToActiveTiny();
                e.preventDefault();
            })
    },

    // Paste into the active tinymce window
    pasteToActiveTiny: function() {
        var raw_text = this.text.html()
        var editor = tinyMCE.activeEditor;
        // set focus to this editor
        editor.focus();
        // paste the content
        editor.selection.setContent(
            this.options.wrapperPre +
            raw_text +
            this.options.wrapperPost
        );
    }

});

$.extend($.ui.karlquotablecomment, {
    defaults: {
        selectorText: '.commentText',
        selectorPasteButton: '.quo-paste',
        wrapperPre: '<div class="quotedreplytext">',
        // An empty paragraph must be added after the quote.
        wrapperPost: '</div><div><p></p></div>'
    }
});


/**
 * Date time picker field
 *
 * Bound to a single input field. This field is made hidden, and
 * three input fields yyy-date yyy-hour and yyy-minute are created.
 * The date field is bound as an ui-datepicker.
 *
 */
$.widget('ui.karldatetimepicker', {

    _init: function() {
        var self = this;
        if (! jQuery.nodeName(this.element[0], 'input')) {
            throw new Error('ui.karldatetimepicker can only be bound to <input> nodes.');
        }
        // Creare a container to hold the new inputs.
        this.container = $('<span class="ui-karldatetimepicker-container"></span>');
        // Position the container after the old input element,
        // which in turn gets hidden.
        this.element
            .hide()
            .after(this.container);
        // Create the date and time inputs inside the container.
        this.dateinput = $('<input class="ui-karldatetimepicker-dateinput"></input>')
            .appendTo(this.container)
            .datepicker({
            })
            .change(function(evt) {
                self.setDate($(evt.target).val());
            });
        this.hourinput = $('<select class="ui-karldatetimepicker-hourinput"></input>')
            .appendTo(this.container)
            .change(function(evt) {
                self.setHour($(evt.target).val());
            });
        for (var i=0; i<24; i++) {
            $('<option>')
                .val(i)
                .text(i)
                .appendTo(this.hourinput);
        }
        this.container.append('<span class="ui-karldatetimepicker-colon">:</span>');
        this.minuteinput = $('<select class="ui-karldatetimepicker-hourinput"></input>')
            .appendTo(this.container)
            .change(function(evt) {
                self.setMinute($(evt.target).val());
            });
        for (var i=0; i<4; i++) {
            var strmin = ('0' + i * 15).slice(-2);
            $('<option>')
                .val(strmin)
                .text(strmin)
                .appendTo(this.minuteinput);
        }
 
        // Set composite value from the input element's content.
        this.set(this.element.val());
    },

    // set the composite value (as string)
    set: function(value) {
        // Split the value
        // Everything before the first space goes to date, the rest to time
        var split_pos = value.search(' ');
        var timestr = value.substr(split_pos + 1);
        // Time is further split to hours and minutes by the colon
        var time_split_pos = timestr.search(':');
        this.composite_value = {
            datestr: value.substr(0, split_pos),
            hourstr: value.substr(split_pos + 1, time_split_pos).replace(/^0/, ''),
            minutestr: value.substr(split_pos + time_split_pos + 2)
        };
        // Sets all input values we manage
        this.dateinput.val(this.composite_value.datestr);
        this.hourinput.val(this.composite_value.hourstr);
        this.minuteinput.val(this.composite_value.minutestr);
        this.element.val(value);
        this.element.trigger('change.karldatetimepicker');
    },

    // Set date part (as string)
    setDate: function(value) {
        // Remember the value, so we are always in possession
        // of the full array of values we composite
        this.composite_value.datestr = value;
        this.dateinput.val(this.composite_value.datestr);
        this._updateComposite();
    },

    // Set hour part (as string)
    setHour: function(value) {
        // Remember the value, so we are always in possession
        // of the full array of values we composite
        this.composite_value.hourstr = value;
        this.hourinput.val(this.composite_value.hourstr);
        this._updateComposite();
    },

    // Set minute part (as string)
    setMinute: function(value) {
        // Remember the value, so we are always in possession
        // of the full array of values we composite
        this.composite_value.minutestr = value;
        this.minuteinput.val(this.composite_value.minutestr);
        this._updateComposite();
    },

    _updateComposite: function() {
        // Update the composite value, which will be submitted in the original
        // input.
        var value = this.composite_value.datestr + ' ' + 
                    this.composite_value.hourstr + ':' + this.composite_value.minutestr;
        this.element.val(value);
        this.element.trigger('change.karldatetimepicker');
    },

    // gets the value as a javascript Date object
    getAsDate: function() {
        // XXX how to handle invalid date exceptions?
        return new Date(Date.parse(this.element.val()));
    },

    // gets the value as a javascript Date object
    setAsDate: function(da) {
        var _pad = function(num) {
            var str = '0' + num;
            return str.substr(str.length-2, 2);
        }
        // Format the date as string
        // (Re: da.getMonth() + 1, thank you javascript for making my day, ha ha.)
        var datestring = _pad(da.getMonth() + 1) + '/' + _pad(da.getDate()) + '/' + da.getFullYear() +
            ' ' + _pad(da.getHours()) + ':' + _pad(da.getMinutes());
        // set the value
        this.set(datestring);
    },

    // limit minimum or maximum.
    // minval and maxval have to be javascript Date objects, or null.
    limitMinMax: function(minval, maxval) {
        var value = this.getAsDate();
        var set_value = null;
        if (minval && value < minval) {
            set_value = minval;
        }
        if (maxval && value > maxval) {
            set_value = maxval;
        }
        if (set_value != null) {
            // Element changed.
            this.setAsDate(set_value);
            this.dateinput.effect("pulsate", {times: 1}, 800);
            this.hourinput.effect("pulsate", {times: 1}, 800);
            this.minuteinput.effect("pulsate", {times: 1}, 800);
        }

    }

});

$.ui.karldatetimepicker.getter = "getAsDate";
$.extend($.ui.karldatetimepicker, {
    defaults: {
    }
});


/**
 * Dropdown menu
 *
 *  <li class="karldropdown">
 *     <a class="karldropdown-heading" href="#">Add</a>
 *     <ul class="karldropdown-menu">
 *       <li>
 *         <a href="#">Folder</a>
 *       </li>
 *       <li>
 *         <a href="#">Forum</a>
 *       </li>
 *       <li>
 *         <a href="#">File</a>
 *       </li>
 *     </ul>
 *   </li>
 *
 * It may appear on a menubar:
 *
 *   <ul class="menubar">
 *     <li>...</li>
 *     <li class="karldropdown">
 *     <li>...</li>
 *   </ul>
 *
 */

$.widget('ui.karldropdown', {

    _init: function() {
        var self = this;
        this._locate();

        // to be on the safe side...
        this.menu.hide();

        // add the dropdown indicator
        $('<div>')
            .attr('class', 'karldropdown-indicator ui-icon ui-icon-triangle-1-s')
            .insertBefore(this.menu);

        // bind the menu
        this.element
            .mouseenter(function() {self.show();})
            .mouseleave(function() {self.hide();});
        this.items
            .mouseover(function() {self.hoverItem(this);})

        // needed to control the item hovers
        this.current_item = null;
        this.padding_left = 0;
    },

    _locate: function() {
        this.heading = this.element.find('> .karldropdown-heading');
        this.menu = this.element.find('> .karldropdown-menu');
        this.items = this.menu.find('> li');
    },

    // --
    // Control
    // --
    
    // show the dropdown
    show: function() {
        // position and size it
        var top = this.element.height();
        this.menu
            .css('position', 'absolute')
            .css('left', 0)
            .css('top', top);
        // calculate the padding to fit first child's padding
        var first_child = this.element.find(':first');
        this.padding_left = Math.round(first_child.position().left +
                                parseFloat(first_child.css('padding-left')) || 0);
        this.resetAllItems();
        // show it
        this.menu
            .stop(true, true)
            .slideDown(150);
        // Make the item widths expand the menu
        // We would not need this if there were no IE
        var max_width = 0;
        this.items
            .each(function() {
                // XXX I don't like it!
                var width;
                if (jQuery.browser.msie) {
                    width = this.offsetWidth;
                } else {
                    width = $(this).width();
                }
                max_width = Math.max(max_width, width);
            })
            .each(function() {
                $(this)
                    .width(max_width)
            });
    },

    // hide the dropdown
    hide: function() {
        // Reset all items
        this.resetAllItems();
        this.current_item = null;
        this.menu
            .stop(true, true)
            .fadeOut(50);
    },

    // reset all items to initial state
    resetAllItems: function() {
        var self = this;
        this.items.each(function() {self.resetItem(this);});
    },

    // reset an item to initial state
    resetItem: function(item) {
        // Reset animation and css
        $(item)
            .stop(true, true)
            .css('backgroundColor', '#666666')
            .css('color', '#000000')
            .css('paddingLeft', this.padding_left)
            .css('paddingRight', '11px');
    },

    // hover an item
    hoverItem: function(item) {
        var self = this;
        // Lazy leaving of element eliminates juggling effects.
        // Prevent anything from happening if we return to same element.
        if (this.items.index(this.current_item) == this.items.index(item)) {
            return;
        }
        // If there was a previous item, leave it now.
        if (this.current_item) {
            this.leaveItem(this.current_item);
        }
        var item = $(item);
        item
            .stop(true, true)
            .animate({
                backgroundColor: '#cecece',
                color: '#ffffff'
            }, 100)
            .animate({
                paddingLeft: self.padding_left + 6,
                paddingRight: '5px'
            }, 150);
        this.current_item = item;
    },

    // leave an item
    leaveItem: function(item) {
        var self = this;
        var item = $(item);
        item
            .stop(true, true)
            .animate({
                paddingLeft: self.padding_left,
                paddingRight: '11px'
                }, 50)
            .css('backgroundColor', '#666666')
            .css('color', '#000000');
        this.current_item = null;
    }

});

$.extend($.ui.karldropdown, {
    defaults: {
    }
});

// preload active/hover state images
function initButtons() {
  var active  = new Image(), hover  = new Image(),
      pActive = new Image(), pHover = new Image();

  // find static link
  var url = $('link[rel="icon"]').attr("href").replace("favicon.ico", "");
  active.src  = url + 'button_active.png';
  hover.src   = url + 'button_hover.png';
  pActive.src = url + 'button_primary_active.png';
  pHover.src  = url + 'button_primary_hover.png';
}

/* auto create anon ids (used by calendar) */
jQuery.fn.identify = function() {
    var i = 0;
    return this.each(function() {
        if ($(this).attr('id')) return;
        do {
            i++;
            var id = 'anon_' + i;
        } while ($('#' + id).length > 0);

        $(this).attr('id', id);
    }).attr("id");
};

/** =CALENDAR TIME SLOT HOVER
----------------------------------------------- */
var hov = {};

function mouseOverHour(evt) {
  var elt = $(evt.target);
  if (!elt.hasClass('cal_hour_event')) {
    var elt = elt.parents(".cal_hour_event");
  }
  if (!elt) { return; }

  var id  = elt.identify("a");
  hov[id] = true;
  
  // only display if still hovered after some time
  setTimeout(function() {
    if (hov[id]) { 
      elt.addClass('hov'); 
      elt.next().addClass('hov_below');
    }
  }, 200);
}

function mouseOutHour(evt) {
  var elt = $(evt.target);
  if (!elt.hasClass('cal_hour_event')) {
    var elt = elt.parents(".cal_hour_event");
  }
  if (!elt) { return; }

  var id  = elt.identify("a");
  delete hov[id];

  // only hide if we've outed for number of time
  setTimeout(function() {
    if (!hov[id]) { 
      elt.removeClass('hov'); 
      elt.next().removeClass('hov_below');
    }
  }, 200);
}


function mouseOverDay(evt) {
  var elt = $(this);
  var id  = elt.identify("a");
  hov[id] = true;
  
  // only display if still hovered after some time
  setTimeout(function() {
    if (hov[id]) { elt.addClass('hov'); }
  }, 200);
}

function mouseOutDay(evt) {
  var elt = $(this);
  var id  = elt.identify("a");
  delete hov[id];

  // only hide if we've outed for number of time
  setTimeout(function() {
    if (!hov[id]) { elt.removeClass('hov');     }
  }, 200);
}

/** =CALENDAR TIME SCROLLING
----------------------------------------------- */
function scrollToTime() {
  var time = $('#cal_time');
  if (time.length == 0) { return; }

  // Scroll to current time for today
  if (time.hasClass('today')) {
    // find current time - determine % of day passed
    var curTime = new Date();

    // total minutes passed today & total mins in a day
    var mins = curTime.getHours() * 60 + curTime.getMinutes();
    var scrollDuration = 1000;

  // go to ~ 8:00am
  } else {
    var mins = 740;
    var scrollDuration = 0;
    time.css("visibility", "hidden");
  }

  var day  = 1440;
  var perc = parseInt(mins / day * 100);

  // get height of entire calendar and set position of time
  var calHeight = $('#cal_scroll').height();
  var top       = parseInt(calHeight * perc / 100);
  time.css('top', top + "px").show();

  // scroll to make time centered if possible
  var scrollPos = top - 250 > 0 ? top - 250 : 0;

  $("#cal_hours_scroll").scrollTo(scrollPos, { duration: scrollDuration });
}

/** =CALENDAR INIT JAVASCRIPT
----------------------------------------------- */
function initCalendar() {
  // rounded corners (monthly)
  if ($("#cal_month").length > 0) {
    DD_roundies.addRule('#cal_month .cal_event_pos_full a', '5px');
    DD_roundies.addRule('#cal_month .cal_event_pos_left a', '5px 0 0 5px');
    DD_roundies.addRule('#cal_month .cal_event_pos_right a', '0 5px 5px 0');
  }

  // rounded corners (daily/weekly)
  if ($("#all_day").length > 0) {
    DD_roundies.addRule('#all_day .cal_event_pos_full a', '5px');
    DD_roundies.addRule('#all_day .cal_event_pos_left a', '5px 0 0 5px');
    DD_roundies.addRule('#all_day .cal_event_pos_right a', '0 5px 5px 0');
    DD_roundies.addRule('#cal_scroll .cal_hour_event .cal_event_block', '7px');
  }

  // ALL VIEWS - calendar layer switcher
  $("#cal_picker").change(function() {
    var values = this.options[this.selectedIndex].value.split("?filter=");
    javascript:document.location = values[0] + "?filter=" + escape(values[1]);
  })

  // MONTH VIEW - hover to show (+) icon to add events
  $("#cal_month td").hover(mouseOverDay, mouseOutDay);
  $("#cal_month .with_tooltip").tooltip({ tip: '.tooltip', offset: [8, 50], predelay: 250});

  // WEEK/DAY VIEW - 
  var scrollHours = $("#cal_hours_scroll");
  scrollHours.mouseover(mouseOverHour);
  scrollHours.mouseout(mouseOutHour);
  $("#cal_scroll .all_day td").hover(mouseOverDay, mouseOutDay);

  // Week tooltips
  var calScroll = $("#cal_scroll");
  if (calScroll.hasClass('cal_week')) {
    $("#all_day .with_tooltip").tooltip({ tip: '.tooltip', offset: [8, -48], predelay: 250});
    $("#cal_scroll .cal_hour_event .with_tooltip").tooltip({ tip: '.tooltip', offset: [12, 5], predelay: 250});
  }

  scrollToTime();
}

// Add Event view only
function initNewEvent() {
  if ($("#startdate-field").length == 0 || $("#enddate-field").length == 0) { return; }
  
  // add the "all-day" checkbox
  var checkbox = '<span class="all_day">' +
                  '<input type="checkbox" id="cal_all_day" name="allDay" value="1" />' + 
                  '<label for="cal_all_day">All-day</label>' + 
                 '</span>';
  $("#startdate-field").append(checkbox);

  $("#cal_all_day").click(function() {
    // check - hide time input
    if (this.checked) {      
      $('#startdate-field select').hide();
      $('#startdate-field .ui-karldatetimepicker-colon').hide();
      $('#enddate-field select').hide();
      $('#enddate-field .ui-karldatetimepicker-colon').hide();
      
    // uncheck - show time inputs
    } else {
      $('#startdate-field select').show();
      $('#startdate-field .ui-karldatetimepicker-colon').show();
      $('#enddate-field select').show();
      $('#enddate-field .ui-karldatetimepicker-colon').show();
    }
  });
}
     
/** =CALENDAR SETUP
----------------------------------------------- */
function initCalendarSetup() {
  // add unique ids to edit links/forms
  $(".setup_group").each(function(i) {
    $(this).find("a.edit_action").each(function(j) {
      $(this).attr("id", "edit_" + i + "_" + j);
    });
    $(this).find("form.cal_edit").each(function(k) {
      $(this).attr("id", ("edit_" + i + "_" + k + "_form"));
    });
  });

  // toggle add layers/categories calendar form
  $(".add_button").click(function(eventObject) {   
    eventObject.preventDefault();
    var group = $(eventObject.target).parents(".setup_group");

    group.find(".add_button").hide("fast");
    group.find(".cal_add").show("slow");
  });
  $(".cal_add button[name=form.cancel]").click(function(eventObject) {
    eventObject.preventDefault();
    var validationErrors = $("div.portalMessage");
    if (validationErrors) { validationErrors.remove(); }

    var group = $(eventObject.target).parents(".setup_group");
    group.find(".add_button").show("fast");
    group.find(".cal_add").hide("slow");

    $(this).parents("form")[0].reset();
  });

  // automatically show form if submission failed with validation errors
  var fielderrors_target = $('#fielderrors_target').val();
  if (fielderrors_target.length > 0) {
    if (fielderrors_target == "__add_category__") {
        var formSelector = "#setup_add_category_form";
    } else if (fielderrors_target == "__add_layer__") {
        var formSelector = "#setup_add_layer_form";
    } else {
        var formSelector = "#edit_" + fielderrors_target + "_form";
    }
    $(formSelector).show();
  }

  // toggle edit layer/categories calendar form
  $(".cal_all .edit_action").click(function(eventObject) {
    eventObject.preventDefault();
    var group = $(eventObject.target).parents(".setup_group");
    
    group.find("form").hide("slow");
    group.find(".add_button").hide("fast");

    var formId = "#" + $(this).identify() + "_form"; 
    $(formId).show("slow");
  });
  $(".cal_edit button[name=form.cancel]").click(function(eventObject) {
    eventObject.preventDefault();
    var validationErrors = $("div.portalMessage");
    if (validationErrors) { validationErrors.remove(); }

    var group = $(eventObject.target).parents(".setup_group");
    group.find(".add_button").show("fast");
    group.find("form").hide("slow");

    $(this).parents("form")[0].reset();
  });

  // delete layer / category
  initCalendarLayersOrCategoriesDelete();

  if ($("select.category_paths").length > 0) { 
    initCalendarLayersEdit();
  }
}

function initCalendarLayersEdit() {
    // add category to a layer
    $('a.add').click(function(eventObject) {
      eventObject.preventDefault();

      var layers = $(this).parents("fieldset").find(".layers");
      var row = layers.find("tr:last");
      row.clone().appendTo(layers).find("option").removeAttr("selected");

      _updateRemoveLinks();
    });

    // remove category from a layer
    $('a.remove').live('click', function(eventObject) { 
      eventObject.preventDefault();

      $(this).parents('tr').remove();

      _updateRemoveLinks();
    });   

    // only show "Remove" if more than one category is present
    function _updateRemoveLinks() {
      $(".layers").each(function() {
        var elts = $(this).find('td a.remove');
        elts.css('display', elts.length > 1 ? "inline" : "none");
      })
    }
    
    // update remove links on page load
    _updateRemoveLinks();
}

function initCalendarLayersOrCategoriesDelete() {
    $('a.delete_category_action').bind('click', function(e) {
      if (confirm("Are you sure?")) {
        var category = this.id.substring(16); // delete_category_*
        $('#cal_delete_category_form > input[name=form.delete]').val(category);
        $('#cal_delete_category_form').submit();
      }
      return false;
    });

    $('a.delete_layer_action').bind('click', function(e) {
      if (confirm("Are you sure?")) {
        var layer = this.id.substring(13); // delete_layer_*
        $('#cal_delete_layer_form > input[name=form.delete]').val(layer);
        $('#cal_delete_layer_form').submit();
      }
      return false;
    });
}


// Initialize jquery
$(document).ready(function() {
    
    // Initialize tinymce live forms
    createLiveForms();

    var app_url = $("#karl-app-url")[0].content;
    var here_url = $("#karl-here-url")[0].content;

    $("#livesearch-input").karllivesearch({
        ajax: app_url + "/jquery_livesearch",
        match: function(typed) { return true; },
        insertText: function(obj) { return obj.title },
        wrapper: '<ul class="livesearch-list"></ul>',
        templateText: '<li class="<%= rowclass %>"><%= pre %><div class="item"><a href="<%= href %>"><%= title %></a></div><%= post %></li>', 
        minQueryNotice: {"pre": "", "post": "", "header": "", "href": "#", "rowclass": "notice",
                         "title":  "Words must contain at least 3 characters to narrow the search"}
    });

    var tagbox_data = window.karl_client_data && karl_client_data.tagbox || {};

    var _check_tagbox_data = function() {
        if (! tagbox_data.records) {
            throw 'karl_client_data.tagbox not specified or has no records.';
        }
    };
    var tagsearch_input = $("#tagsearch-input");

    // check karl_client_data.tagbox only if we have a tagbox in the page
    if (tagsearch_input.length > 0) _check_tagbox_data();
    tagsearch_input.karltagbox({
        validateRegexp: "^[a-zA-Z0-9\-\._]+$",
        ajax: app_url + "/jquery_tag_search",
        ajaxAdd: here_url + "jquery_tag_add",
        ajaxDel: here_url + "jquery_tag_del",
        prevals: tagbox_data.records,
        docid: tagbox_data.docid,
        showtag_url: app_url + '/showtag/',
        tagusers_url: app_url + '/tagusers.html'
    });

    var membersearch_input = $("#membersearch-input");
    // XXX this widget has no init data atm
    //if (box_input.length > 0) _check_tagbox_data();
    membersearch_input.karlmemberbox({
        ajax: here_url + "jquery_member_search",
        showtag_url: app_url + '/profiles/',
        name: 'users'
    });

    // quotable comments
    
    $('.blogComment').karlquotablecomment({
    });
    
    
    // Enable old style dropdowns
    enableOldStyleDropdowns();
    
    // initialize button
    if ($('.button').length > 0) { 
      initButtons(); 
      $("#form-submit").click(function() { 
        $("#form-cancel").attr("disabled", "disabled"); 
      });
      $("#form-cancel").click(function() { 
        $("#form-submit").attr("disabled", "disabled"); 
      });
      $("form.k3_genericForm").keyup(function(eventObj) { 
        if (eventObj.keyCode == 13) { $("#form-cancel").attr("disabled", "disabled"); }
      });
    }

    // rounded corners in IE on tags
    DD_roundies.addRule('.bit-box', '6px');

    /** =CALENDAR ATTACH EVENTS
    ----------------------------------------------- */
    if ($('table.cal').length > 0) { 
      initCalendar(); 
    }

    if ($("fieldset#calendar-category-field").length > 0) { 
      initNewEvent(); 
    }
    // calendar setup pages
    if ($('#setup_add_cal').length > 0) {
      initCalendarSetup();
    }
}); // END document ready handler

// For debugging and development.
// (only works on FF)
Karl.themeroller = function() {
    if (window.jquitr) {
        jquitr.addThemeRoller();
    } else {
        jquitr = {};
        jquitr.s = document.createElement('script');
        jquitr.s.src = 'http://jqueryui.com/themeroller/developertool/developertool.js.php';
        document.getElementsByTagName('head')[0].appendChild(jquitr.s); 
    }
};

})();                   // END CLOSURE Karl

