/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 80, indent: 4 */
/*jslint sub: true */

/*globals window navigator document console setTimeout $ */

(function ($) {

    "use strict";

    var log = function () {
        if (window.console && console.log) {
            // log for FireBug or WebKit console
            console.log(Array.prototype.slice.call(arguments));
        }
    };

    $.widget('popper.tagbox', {

        options: {
            prevals: null,
            validateRegexp: null,
            docid: null,
            showtag_url: null,
            tagusers_url: null,
            name: null,
            searchTagURL: null,
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
            this.addTagForm = el.children('form.addTag').first();
            this.addTagForm.bind('submit',
                $.proxy(this._addTag, this));
            $('.removeTag').live('click', 
                $.proxy(this._delTag, this));


            // Bind the autocomplete.
            this.elInput = el.find('input#newTag');
            this.elForm = el.find('form.addTag');
                    // XXX Remark... if you use an id inside a widget,
                    // you restrict that this widget can only appear once
                    // in a page. Using a class instead of an id
                    // would not introduce this (otherwise completely 
                    // unnecessary) restriction.
            // Do we have it? If no url, then we don't have.
            this.hasAutocomplete = this.options.autocompleteURL ? true : false;
            if (this.hasAutocomplete) {
                // Modify the behaviour to match that of old KARL!
                // We want TAB to cycle throught the options, just like DOWN.
                // In the autocomplete code, by default TAB would
                // do the same as what ENTER does.
                // We need to bind this event before autocomplete, to permit
                // us to steal the key event if needed.
                //
                // There is a "dirty trick" in the bag here, we need to prevent
                // a few keypresses after the keyup, otherwise various unwanted
                // things will happen. We do this just like ui.autocomplete does
                // the same, originally, when handling downs.
                this.preventNextKeypress = false;
                this.elInput
                    // the .tagbox is just a discrimintor here: it allows us
                    // to unbind the same event from destroy, while leave
                    // the same event of someone else intact.
                    .bind('keydown.tagbox', function (evt) {
                        if (evt.keyCode == $.ui.keyCode.TAB) {
                            var autocomplete =
                                self.elInput.data('autocomplete');
                            if (autocomplete.menu.active) {
                                autocomplete._move('next', evt);
                                // prevent
                                self.preventNextKeypress = true;
                            }
                            evt.preventDefault();
                            // make sure we don't get into autobox's keypress.
                            evt.stopImmediatePropagation();    
                        }
                    })
                    .bind('keypress.tagbox', function (evt) {
                        if (evt.keyCode == $.ui.keyCode.TAB) {
                            if (self.preventNextKeypress) {
                                // yeah...
                                self.preventNextKeypress = false;
                            } else {
                                var autocomplete =
                                    self.elInput.data('autocomplete');
                                autocomplete._move('next', evt);
                            }
                            evt.preventDefault();
                            evt.stopImmediatePropagation();
                        }
                    })
                // bind the autocomplete
                    .autocomplete({
                        source: this.options.autocompleteURL,
                        // start searching from 2nd character only
                        minLength: 2,     
                        // and, position it under the form, not under the input
                        // (needed as a consequence of using a markup 
                        // the way we do)
                        position: {
                            my: 'left top',
                            at: 'left bottom',
                            of: this.elForm,
                            collision: 'none none'
                        },
                        // in addition to positioning, we need to set
                        // the width of the element, otherwise it will
                        // look sloppy
                        open: function (evt, ui) {
                            var menu = self.elInput.data('autocomplete')
                                .menu.activeMenu;
                            menu.outerWidth(self.elForm.innerWidth());
                        }
                    });
                // ... And, "fix" the tab to work also on the dropdown
                var menu = this.elInput.data('autocomplete').menu;
                menu.activeMenu.bind('keydown', function (evt) {
                    log('lol');
                    if (evt.keyCode == $.ui.keyCode.TAB) {
                        log('TAB/menu!');
                        menu.next(evt);
                        evt.preventDefault();
                        evt.stopPropagation();
                    }
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
                    .autocomplete('destroy')
                    .unbind('keydown.tagbox')
                    .unbind('keypress.tagbox');
            }
        },

        _setOption: function (key, value) {
            console.log('Set Option');
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
                '<input id="newTag" type="text" name="tag"' +
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
            li += '<a href="/pg/taguser.html?tag=' + item.tag + '&docid=' +
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
            e.preventDefault();
            var self = this;
            var tagInput = self.addTagForm.find('#newTag').first();
            var newTag = tagInput.val();
            if (newTag) {
                if (!self._validateTag(newTag)) {
                    return false;
                }
                if (self.options.addTagURL) {
                    $.ajax({
                        url: self.options.addTagURL,
                        data: {'val': newTag},
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
            tagInput.val('');
            return false;
        },

        _addTagListItem: function (tag) {
            var self = this;
            self.tagList.append('<li><a href="/pg/showtag/' + tag +
                '" class="tag personal">' + tag + '</a>' +
                '<a title="Remove Tag" href="#" class="removeTag">x</a>' +
                '<a href="/pg/taguser.html?tag=' + tag +
                '" class="tagCounter">1</a>' + 
                '<input type="hidden" name="tags" value="' + tag + '"></li>');
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
            var tag = target.siblings('.tag')[0].innerText || null;
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
        }

    });

})(window.jQuery);
