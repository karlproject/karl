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
            this.addTagForm.bind('submit',
                $.proxy(this._addTag, this));
            $('.removeTag').live('click', 
                $.proxy(this._delTag, this));


            // Bind the autocomplete.
            this.elInput = el.find('input.newItem');
            this.elForm = el.find('form');
            // Do we have it? If no url, then we don't have.
            if (this.options.autocompleteURL) {
                // bind the autocomplete
                this.elInput
                    .autocomplete({
                        source: this.options.autocompleteURL,
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
                        focus: $.proxy(this._autocompleteFocus, this),
                        select: $.proxy(this._autocompleteSelect, this)
                    });
            }
        },

        _destroy: function () {
            this.addTagForm.unbind('submit',
                $.proxy(this._addTag, this));
            $('.removeTag').unbind('click', 
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
            var li = '<li><a href="/pg/showtag/' + item.tag + '" class="tag ' +
                personal + '">' + item.tag + '</a>';
            if (personal) {
                li += '<a title="Remove Tag" href="#" class="removeTag">x</a>';
            }
            li += '<a href="/pg/tagusers.html?tag=' + item.tag + '&docid=' +
                docid + '" class="tagCounter">' + item.count + '</a>' +
                '<input type="hidden" name="tags" value="' +
                item.tag + '"></li>';
            return li;
        },

        _renderTags: function (data) {
            var self = this;
            var ul = $('<ul></ul>');
            $.each(data.records, function (idx, item) {
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

        addTag: function (newTag) {
            // Tag can be a string, or a dict of value / label.
            // If it's a string, value == label considered.
            if (newTag.value === undefined) {
                newTag = {value: newTag, label: newTag};
            }
            var self = this;
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
        },

        _addTagListItem: function (tag) {
            // Value goes to the hidden input, label to the display. 
            var self = this;
            self.tagList.append('<li><a href="/pg/showtag/' + tag.value +
                '" class="tag personal">' + tag.label + '</a>' +
                '<a title="Remove Tag" href="#" class="removeTag">x</a>' +
                '<a href="/pg/tagusers.html?tag=' + tag.value +
                '" class="tagCounter">1</a>' + 
                '<input type="hidden" name="tags" value="' +
                    tag.value + '"></li>');
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
            var self = this;
            var target = $(e.target);
            
            var tag = target
                .closest('li').find('input[type="hidden"]')
                .attr('value');

            if (tag) {
                if (self.options.delTagURL) {
                    $.ajax({
                        url: self.options.delTagURL,
                        data: {'val': tag},
                        type: 'POST',
                        dataType: 'json',
                        success: function (data, textStatus, xhr) {
                            self._delTagListItem(target);
                            self._ajaxSuccess(data, textStatus, xhr, 'delete');
                        },
                        error: function (xhr, textStatus) {
                            self._ajaxError(xhr, textStatus);
                        }
                    });
                } else {
                    self._delTagListItem(target);
                }
            }
        },

        _delTagListItem: function (target) {
            target.closest('li').remove();
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
        }

    });



    $.widget('popper.addexistingmember',
             $.extend({}, $.popper.tagbox.prototype, {

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
            this.tagList.append('<li><a href="' +
                this.options.showLinkUrl + tag.value +
                '" class="item personal">' + tag.label + '</a>' +
                '<a title="Remove User" href="#" class="removeTag">x</a>' +
                '<input type="hidden" name="' + this.options.name +
                '" value="' + tag.value + '"></li>');
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
