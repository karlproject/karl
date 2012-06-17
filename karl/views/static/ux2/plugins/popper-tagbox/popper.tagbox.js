/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */

/*globals window navigator document setTimeout $ */

(function ($) {

    "use strict";

    var log = function () {
        var c = window.console;
        if (c && c.log) {
            // log for FireBug or WebKit console
            c.log(Array.prototype.slice.call(arguments));
        }
    };

    $.widget('popper.tagbox', {

        options: {
            prevals: null,
            validateRegexp: null,
            docid: null,
            name: null,
            addTagURL: null,
            delTagURL: null,
            partialForm: false,
            autocompleteURL: null  // autocomplete url, is optional.
        },

        _create: function () {
            var self = this,
                el = this.element,
                o = this.options;

            this.prevals = o.prevals ? o.prevals : this._getPrevals();
            el.addClass('tagbox');
            var tagbox_data = this.prevals;
            el.append(this._renderTags(tagbox_data));
            el.append(this._renderForm());

            this.tagList = el.children('ul');
            this.addTagForm = el.children('form').first();
            this.addTagForm.on('submit', $.proxy(this._addTag, this));
            el.on('click', '.removeTag', $.proxy(this._delTag, this));

            // Cache the docid locally.
            this.docid = tagbox_data.docid;
            // Cache the bubble values locally.
            // (needed for quick filtering of the autocomplete)
            this.personalBubbles = {};
            $.each(tagbox_data.records, function (index, item) {
                // personal bubbles only.
                if (item.snippet != 'nondeleteable') {
                    self.personalBubbles[item.value] = true;
                }
            });

            // Bind the autocomplete.
            this.elInput = el.find('input.newItem');
            this.elForm = el.find('form');
            // Do we have it? If no url, then we don't have.
            if (this.options.autocompleteURL) {
                // bind the autocomplete
                this.elInput
                    .autocomplete({
                        // source allows standard interface with filtering
                        source: function (request, response) {
                            $.ajax({
                                url: self.options.autocompleteURL,
                                data: request,
                                success: function (data) {
                                    response(
                                        // this method provides the filtering
                                        // of the result set
                                        self._filterAutocompleteResult(data)
                                    );
                                }
                            });
                        },
                        // start searching from 2nd character only
                        minLength: 2,     
                        // and, position it under the input
                        position: {
                            my: 'left top',
                            at: 'left bottom',
                            of: this.elInput,
                            // (offset to compensate the input's padding:)
                            offset: '-1px 2px', 
                            collision: 'none none'
                        },
                        // in addition to positioning, we need to set
                        // the width of the element, otherwise it will
                        // look sloppy
                        open: function (evt, ui) {
                            var menu = self.elInput.data('autocomplete')
                                .menu.activeMenu;
                            menu.outerWidth(self.elForm.innerWidth());
                        },
                        // event handlers wired to class methods as needed
                        focus: $.proxy(this._autocompleteFocus, this),
                        select: $.proxy(this._autocompleteSelect, this)
                    });
            }
        },

        _destroy: function () {
            this.addTagForm.off('submit', $.proxy(this._addTag, this));
            this.element.off('click', '.removeTag', 
                    $.proxy(this._delTag, this));
            if (this.hasAutocomplete) {
                this.elInput
                    .autocomplete('destroy');
            }
        },

        _setOption: function (key, value) {
            log('Set Option');
        },

        _getPrevals: function () {
            return window.head_data.panel_data.tagbox;
        },

        _renderForm: function () {
            var self = this;
            var form = '';
            if (!self.partialForm) {
                form += '<form action="#" class="addTag">';
            }
            form  += '<fieldset>' +
                '<input id="newTag" class="newItem" type="text" name="tag"' +
                ' placeholder="A tag to add" />' +
                '<button type="submit">New Tag</button>' +
                '</fieldset>' +
                '<div id="tagStatus"></div>';
            if (!self.partialForm) {
                form += '</form>';
            }
            return form;
        },

        _renderTag: function (item, docid) {
            var personal = (item.snippet !== 'nondeleteable') ? 'personal' : '';
            var li = '<li data-tagbox-bubble="' + item.value +
                '"><a href="/pg/showtag/' + item.value + '" class="tag ' +
                personal + '">' + item.label + '</a>';
            if (personal) {
                li += '<a title="Remove Tag" href="#" class="removeTag">x</a>' +
                      '<input type="hidden" name="tags" value="' +
                       item.value + '">'; 
            }
            li += '<a href="/pg/tagusers.html?tag=' + item.value + '&docid=' +
                docid + '" class="tagCounter">' +
                (item.count || 1) + '</a></li>';
            return li;
        },

        _renderTags: function (data) {
            var self = this;
            var ul = $('<ul></ul>');
            $.each(data.records, function (idx, item) {
                // item contains item.tag. 
                // We transform this to item.value and item.label.
                item.value = item.label = item.tag;
                var li = self._renderTag(item, data.docid);
                ul.append(li);
            });
            return ul;
        },

        _addTag: function (e) {
            var self = this;
            var newTag = this.elInput.val();
            if (newTag) {
                if (!self._validateTag(newTag)) {
                    return false;
                }
                this.addTag(newTag);
            }
            this.elInput.val('');
            // Make sure the dropdown gets closed. 
            if (this.options.autocompleteURL) {
                this.elInput.autocomplete('close');
            }
            return false;
        },

        _findExistingBubble: function (tag) {
            return this.element.find('[data-tagbox-bubble="' + tag + '"]');
        },

        _isOurOwnTag: function (tag) {
            // True if tag exists _and_ it is our own tag
            //    (i.e. we have added it already) 
            return this.personalBubbles[tag];
        },

        _isOurOwnBubble: function (bubble) {
            return bubble.find('.personal').length > 0;
        },

        addTag: function (newTag) {
            var self = this;
            // Tag can be a string, or a dict of value / label.
            // If it's a string, value == label considered.
            if (newTag.value === undefined) {
                newTag = {value: newTag, label: newTag};
            }
            // Is this a tag that we have added already?
            // Silently ignore if yes.
            if (! this._isOurOwnTag(newTag.value)) {
                if (this.options.addTagURL) {
                    $.ajax({
                        url: this.options.addTagURL,
                        data: {'val': newTag.value},
                        type: 'POST',
                        dataType: 'json',
                        success: function (data, textStatus, xhr) {
                            self._addTagListItem(newTag);
                            self._ajaxSuccess(data, textStatus, xhr, 'add');
                        },
                        error: function (xhr, textStatus) {
                            self._ajaxError(xhr, textStatus);
                        }
                    });
                } else {
                    self._addTagListItem(newTag);
                }
            }
        },

        _addTagListItem: function (tag) {
            // Value goes to the hidden input, label to the display. 
            tag.snippet = '';
            var newBubble = $(this._renderTag(tag, this.docid)); 
            // Need to check if we have this already?
            var existingBubble = this._findExistingBubble(tag.value);
            if (existingBubble.length === 0) {
                // Add a new bubble.
                this.tagList.append(newBubble);
            } else {
                // Replace the existing bubble.
                var count = existingBubble.find('.tagCounter').text();
                existingBubble.replaceWith(newBubble);
                // Updating the counter is needed as well.
                newBubble.find('.tagCounter').text('' + (Number(count) + 1));
            }
            // This is our personal bubble now, mark in the cache.
            this.personalBubbles[tag.value] = true;
            return;
        },

        _validateTag: function (tag) {
            if (this.options.validateRegexp) {
                if (tag.match(this.options.validateRegexp) === null) {
                    log('Value contains characters that ' +
                        'are not allowed in a tag.');
                    return false;
                }
            }
            return true;
        },

        _delTag: function (e) {
            var target = $(e.target);
            var tag = target
                .closest('li').data('tagbox-bubble');
            this.delTag(tag);
        },

        delTag: function (tag) {
            var self = this;
            if (tag) {
                if (this.options.delTagURL) {
                    $.ajax({
                        url: self.options.delTagURL,
                        data: {'val': tag},
                        type: 'POST',
                        dataType: 'json',
                        success: function (data, textStatus, xhr) {
                            self._delTagListItem(tag);
                            self._ajaxSuccess(data, textStatus, xhr, 'delete');
                        },
                        error: function (xhr, textStatus) {
                            self._ajaxError(xhr, textStatus);
                        }
                    });
                } else {
                    self._delTagListItem(tag);
                }
            }
        },

        _delTagListItem: function (tag) {
            // Silently ignore if this is not our own tag.
            if (this._isOurOwnTag(tag)) {
                var bubble = this._findExistingBubble(tag);
                var count = Number(bubble.find('.tagCounter').text() || 1);
                if (count > 1) {
                    // downgrade bubble to non-personal,
                    bubble.find('.personal').removeClass('personal');
                    bubble.find('.removeTag').remove();
                    bubble.find('input[type="hidden"]').remove();
                    // Updating the counter is needed as well.
                    bubble.find('.tagCounter').text('' + (count - 1));
                } else {
                    // Just mine.
                    bubble.remove();
                }
                // Mark this bubble as not ours, in the cache.
                delete this.personalBubbles[tag];
            }
        },

        _ajaxSuccess: function (data, textStatus, xhr, action) {
            var msg = '';
            switch (action) {
            case 'add':
                msg = 'Tag added!';
                break;
            case 'delete':
                msg = 'Tag removed!';
                break;
            }
            $('#tagStatus').html(msg)
                           .addClass('notification info')
                           .fadeIn('slow')
                           .delay(2000)
                           .fadeOut('slow');
        },

        _ajaxError: function (xhr, textStatus) {
            $('#tagStatus').html(textStatus)
                           .addClass('notification alert')
                           .fadeIn('slow')
                           .delay(2000)
                           .fadeOut('slow');
        },

        _autocompleteFocus: function (evt, ui) {
            // cycling around the dropdown shortcuts should do nothing.
            // (We prevent here to fill the input value with the
            // selection, which is not what we want. It is better
            // to let the user continue typing as needed.)
            return false;
        },

        _autocompleteSelect: function (evt, ui) {
            // Selecting from dropdown shortcuts to add the tag
            this.elInput.val('');
            this.addTag(ui.item.value);
            return false;
        },

        _filterAutocompleteResult: function (records) {
            var personalBubbles = this.personalBubbles;
            var result = [];
            $.each(records, function (index, item) {
                // support string or value/label dict
                var key = item.value || item;
                if (! personalBubbles[key]) {
                    result.push(item);
                }
            });
            return result;
        }

    });



    $.widget('popper.addexistingmember',
             $.extend({}, $.popper.tagbox.prototype, {
        
        widgetName: 'addexistingmember',

        options: $.extend({}, $.popper.tagbox.prototype.options, {
            partialForm: true
            //showLinkUrl: url of the "show member" link
        }),

        _create: function () {
            var self = this;
            $.popper.tagbox.prototype._create.call(this, arguments);
            if (this.options.showLinkUrl) {
                if (this.options.showLinkUrl.length > 0 &&
                        this.options.showLinkUrl
                            [this.options.showLinkUrl.length] != '/') {
                    this.options.showLinkUrl += '/';
                }
            }
        },

        _renderForm: function () {
            var self = this;
            var form = '';
            if (!self.partialForm) {
                form += '<form action="#" class="addTag">';
            }
            form  += '<fieldset>' +
                '<input class="newItem" type="text" name="' +
                        this.options.name + '"' +
                ' placeholder="A user to add" />' +
                '<button type="submit">Add User</button>' +
                '</fieldset>' +
                '<div class="userStatus"></div>';
            if (!self.partialForm) {
                form += '</form>';
            }
            return form;
        },


        _renderTag: function (item, docid) {
            throw new Error('No original tags in the add existing member.');
        },

        _addTagListItem: function (tag) {
            // Value goes to the hidden input, label to the display. 
            this.tagList.append('<li data-tagbox-bubble="' + tag.value +
                '"><a href="' + this.options.showLinkUrl + tag.value +
                '" class="item personal">' + tag.label + '</a>' +
                '<a title="Remove User" href="#" class="removeTag">x</a>' +
                '<input type="hidden" name="' + this.options.name +
                '" value="' + tag.value + '"></li>');
            this.personalBubbles[tag.value] = true;
            return;
        },

        _autocompleteSelect: function (evt, ui) {
            // Selecting from dropdown shortcuts to add the tag
            this.elInput.val('');
            // We add the item which is a value + label dict.
            // This would cause the value to be used in the hidden input / ajax,
            // and the label to be used in the bubble.
            this.addTag(ui.item);
            return false;
        },

        _addTag: function (e) {
            // Do not allow adding the input entered as a tag.
            // Just let the user select from the dropdown.
            // This is a main difference with the tags spec:
            // for users, only those users can be added who are
            // in the list.
            return false;
        }


    }));


})(window.jQuery);
